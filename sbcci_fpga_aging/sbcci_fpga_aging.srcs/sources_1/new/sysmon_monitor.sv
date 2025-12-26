`timescale 1ns / 1ps

module sysmon_monitor #(
    parameter int CLK_FREQ = 100000000, 
    parameter int BAUD_RATE = 125000 
)(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        aging_alarm,
    input  logic [15:0] aging_count,
    input  logic        i_trigger,
    output logic        tx_out,
    output logic        tx_active
);

    // =========================================================================
    // XADC System Monitor
    // =========================================================================
    logic [7:0]  daddr;
    logic        den;
    logic [15:0] do_data;
    logic        drdy;

    xadc_wiz_0 sysmon_inst (
        .dclk_in(clk), 
        .reset_in(!rst_n),
        .daddr_in(daddr),
        .den_in(den),
        .dwe_in(1'b0),
        .di_in(16'h0),
        .do_out(do_data),
        .drdy_out(drdy),
        .vp(1'b0), 
        .vn(1'b0),
        .busy_out(),
        .channel_out(),
        .eoc_out(),
        .eos_out(),
        .alarm_out()
    );

    // =========================================================================
    // Trigger Synchronization
    // =========================================================================
    logic [2:0] trig_sync;
    logic       trig_stable;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trig_sync <= 3'b000;
        end else begin
            trig_sync <= {trig_sync[1:0], i_trigger};
        end
    end
    
    assign trig_stable = trig_sync[2] & trig_sync[1] & trig_sync[0];

    // =========================================================================
    // State Machine - Read XADC
    // =========================================================================
    logic [15:0] reg_temp, reg_vcc;
    logic [15:0] timeout_cnt;
    localparam TIMEOUT_MAX = 16'd10000;

    typedef enum logic [2:0] {
        IDLE,
        READ_TEMP,
        WAIT_TEMP,
        READ_VCC,
        WAIT_VCC,
        SEND_PACKET
    } state_t;
    
    state_t state;
    logic triggered;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            den <= 0;
            daddr <= 0;
            reg_temp <= 0;
            reg_vcc <= 0;
            timeout_cnt <= 0;
            triggered <= 0;
        end else begin
            case (state)
                IDLE: begin
                    timeout_cnt <= 0;
                    if (trig_stable && !triggered) begin
                        daddr <= 8'h00; 
                        den <= 1; 
                        state <= READ_TEMP;
                        triggered <= 1;
                    end else if (!trig_stable) begin
                        triggered <= 0;
                    end
                end

                READ_TEMP: begin
                    den <= 0;
                    timeout_cnt <= 0;
                    state <= WAIT_TEMP;
                end
                
                WAIT_TEMP: begin
                    if (drdy) begin
                        reg_temp <= do_data;
                        daddr <= 8'h01; 
                        den <= 1; 
                        state <= READ_VCC;
                        timeout_cnt <= 0;
                    end else if (timeout_cnt >= TIMEOUT_MAX) begin
                        state <= IDLE;
                    end else begin
                        timeout_cnt <= timeout_cnt + 1;
                    end
                end
                
                READ_VCC: begin
                    den <= 0;
                    timeout_cnt <= 0;
                    state <= WAIT_VCC;
                end

                WAIT_VCC: begin
                    if (drdy) begin
                        reg_vcc <= do_data;
                        state <= SEND_PACKET;
                        timeout_cnt <= 0;
                    end else if (timeout_cnt >= TIMEOUT_MAX) begin
                        state <= IDLE;
                    end else begin
                        timeout_cnt <= timeout_cnt + 1;
                    end
                end
                
                SEND_PACKET: begin
                    if (!tx_active) begin
                        state <= IDLE;
                    end
                end
            endcase
        end
    end

    // =========================================================================
    // UART Transmitter - SIMPLE, PROVEN DESIGN
    // =========================================================================
    localparam CYCLES_PER_BIT = CLK_FREQ / BAUD_RATE;
    localparam BYTE_DELAY = CYCLES_PER_BIT * 12; // 12 bit-times between bytes
    
    logic [3:0]  tx_state;
    logic [31:0] baud_counter;
    logic [3:0]  bit_index;
    logic [9:0]  tx_shift_reg;
    logic [3:0]  byte_index;
    logic [31:0] byte_delay_counter;
    logic [7:0]  current_byte;
    
    // State definitions
    localparam TX_IDLE       = 4'd0;
    localparam TX_START_BYTE = 4'd1;
    localparam TX_SEND_BITS  = 4'd2;
    localparam TX_BYTE_DELAY = 4'd3;
    localparam TX_DONE       = 4'd4;

    // Current byte selection
    always_comb begin
        case (byte_index)
            0: current_byte = reg_temp[7:0];      // Temp Low
            1: current_byte = reg_temp[15:8];     // Temp High
            2: current_byte = 8'h00;              // Padding
            3: current_byte = aging_count[7:0];   // Slack Low
            4: current_byte = aging_count[15:8];  // Slack High
            5: current_byte = reg_vcc[7:0];       // VCC Low
            6: current_byte = reg_vcc[15:8];      // VCC High
            7: current_byte = 8'h00;              // Padding
            8: current_byte = {7'b0, aging_alarm};// Alarm
            default: current_byte = 8'h00;
        endcase
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_state <= TX_IDLE;
            tx_out <= 1'b1;
            tx_active <= 1'b0;
            baud_counter <= 0;
            bit_index <= 0;
            byte_index <= 0;
            byte_delay_counter <= 0;
            tx_shift_reg <= 10'h3FF;
        end else begin
            case (tx_state)
                TX_IDLE: begin
                    tx_out <= 1'b1;
                    tx_active <= 1'b0;
                    byte_index <= 0;
                    baud_counter <= 0;
                    bit_index <= 0;
                    
                    // Start transmission when state machine requests it
                    if (state == SEND_PACKET) begin
                        tx_active <= 1'b1;
                        tx_state <= TX_START_BYTE;
                    end
                end
                
                TX_START_BYTE: begin
                    // Load shift register: {Stop, Data[7:0], Start}
                    tx_shift_reg <= {1'b1, current_byte, 1'b0};
                    bit_index <= 0;
                    baud_counter <= 0;
                    tx_state <= TX_SEND_BITS;
                end
                
                TX_SEND_BITS: begin
                    if (baud_counter < CYCLES_PER_BIT - 1) begin
                        baud_counter <= baud_counter + 1;
                    end else begin
                        baud_counter <= 0;
                        
                        // Output current bit
                        tx_out <= tx_shift_reg[0];
                        tx_shift_reg <= {1'b1, tx_shift_reg[9:1]}; // Shift right
                        
                        if (bit_index < 9) begin
                            bit_index <= bit_index + 1;
                        end else begin
                            // Byte complete
                            if (byte_index < 8) begin
                                byte_index <= byte_index + 1;
                                byte_delay_counter <= 0;
                                tx_state <= TX_BYTE_DELAY;
                            end else begin
                                // All 9 bytes sent
                                tx_state <= TX_DONE;
                            end
                        end
                    end
                end
                
                TX_BYTE_DELAY: begin
                    tx_out <= 1'b1; // Idle between bytes
                    if (byte_delay_counter < BYTE_DELAY) begin
                        byte_delay_counter <= byte_delay_counter + 1;
                    end else begin
                        tx_state <= TX_START_BYTE;
                    end
                end
                
                TX_DONE: begin
                    tx_out <= 1'b1;
                    tx_active <= 1'b0;
                    tx_state <= TX_IDLE;
                end
                
                default: tx_state <= TX_IDLE;
            endcase
        end
    end

endmodule