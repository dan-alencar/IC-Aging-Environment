`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Module Name: sysmon_monitor_fixed
// Description: System Monitor with UART output
//              Uses xadc_wiz_0 (System Management Wizard)
//              Fixed trigger detection and DRP timing
//////////////////////////////////////////////////////////////////////////////////

module sysmon_monitor_fixed #(
    parameter int CLK_FREQ = 100000000, 
    parameter int BAUD_RATE = 125000 
)(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        aging_alarm,
    input  logic [15:0] aging_count,
    input  logic        i_trigger,
    output logic        tx_out,
    output logic        tx_active,
    
    // Debug outputs - connect to VIO at top level if needed
    output logic [15:0] debug_temp,
    output logic [15:0] debug_vcc,
    output logic [2:0]  debug_state
);

    // =========================================================================
    // XADC/SYSMON IP Instance
    // =========================================================================
    logic [7:0]  daddr;
    logic        den;
    logic [15:0] do_data;
    logic        drdy;

    xadc_wiz_0 sysmon_inst (
        .dclk_in(clk), 
        .reset_in(~rst_n),
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
    // Trigger Edge Detection
    // =========================================================================
    logic trig_prev;
    logic trig_edge;
    
    always_ff @(posedge clk) begin
        if (!rst_n)
            trig_prev <= 1'b0;
        else
            trig_prev <= i_trigger;
    end
    
    assign trig_edge = i_trigger & ~trig_prev;

    // =========================================================================
    // State Machine - Read XADC then transmit
    // =========================================================================
    logic [15:0] reg_temp, reg_vcc;
    logic [15:0] timeout_cnt;
    localparam TIMEOUT_MAX = 16'd50000;

    typedef enum logic [2:0] {
        IDLE,
        READ_TEMP,
        WAIT_TEMP,
        READ_VCC,
        WAIT_VCC,
        SEND_PACKET
    } state_t;
    
    state_t state;
    
    // Debug outputs
    assign debug_temp = reg_temp;
    assign debug_vcc = reg_vcc;
    assign debug_state = state;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            state <= IDLE;
            den <= 1'b0;
            daddr <= 8'h00;
            reg_temp <= 16'h0000;
            reg_vcc <= 16'h0000;
            timeout_cnt <= 16'd0;
        end else begin
            case (state)
                IDLE: begin
                    den <= 1'b0;
                    timeout_cnt <= 16'd0;
                    if (trig_edge) begin
                        daddr <= 8'h00;
                        den <= 1'b1;
                        state <= READ_TEMP;
                    end
                end

                READ_TEMP: begin
                    den <= 1'b0;
                    timeout_cnt <= 16'd0;
                    state <= WAIT_TEMP;
                end
                
                WAIT_TEMP: begin
                    if (drdy) begin
                        reg_temp <= do_data;
                        daddr <= 8'h01;
                        den <= 1'b1;
                        state <= READ_VCC;
                        timeout_cnt <= 16'd0;
                    end else if (timeout_cnt >= TIMEOUT_MAX) begin
                        state <= IDLE;
                    end else begin
                        timeout_cnt <= timeout_cnt + 1;
                    end
                end
                
                READ_VCC: begin
                    den <= 1'b0;
                    timeout_cnt <= 16'd0;
                    state <= WAIT_VCC;
                end

                WAIT_VCC: begin
                    if (drdy) begin
                        reg_vcc <= do_data;
                        state <= SEND_PACKET;
                        timeout_cnt <= 16'd0;
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
                
                default: state <= IDLE;
            endcase
        end
    end

    // =========================================================================
    // UART Transmitter - 9 byte packet
    // =========================================================================
    localparam CYCLES_PER_BIT = CLK_FREQ / BAUD_RATE;
    localparam BYTE_DELAY = CYCLES_PER_BIT * 12;
    
    logic [3:0]  tx_state;
    logic [31:0] baud_counter;
    logic [3:0]  bit_index;
    logic [9:0]  tx_shift_reg;
    logic [3:0]  byte_index;
    logic [31:0] byte_delay_counter;
    logic [7:0]  current_byte;
    
    localparam TX_IDLE       = 4'd0;
    localparam TX_START_BYTE = 4'd1;
    localparam TX_SEND_BITS  = 4'd2;
    localparam TX_BYTE_DELAY = 4'd3;
    localparam TX_DONE       = 4'd4;

    always_comb begin
        case (byte_index)
            0: current_byte = reg_temp[7:0];
            1: current_byte = reg_temp[15:8];
            2: current_byte = 8'h00;
            3: current_byte = aging_count[7:0];
            4: current_byte = aging_count[15:8];
            5: current_byte = reg_vcc[7:0];
            6: current_byte = reg_vcc[15:8];
            7: current_byte = 8'h00;
            8: current_byte = {7'b0, aging_alarm};
            default: current_byte = 8'h00;
        endcase
    end

    always_ff @(posedge clk) begin
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
                    
                    if (state == SEND_PACKET) begin
                        tx_active <= 1'b1;
                        tx_state <= TX_START_BYTE;
                    end
                end
                
                TX_START_BYTE: begin
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
                        tx_out <= tx_shift_reg[0];
                        tx_shift_reg <= {1'b1, tx_shift_reg[9:1]};
                        
                        if (bit_index < 9) begin
                            bit_index <= bit_index + 1;
                        end else begin
                            if (byte_index < 8) begin
                                byte_index <= byte_index + 1;
                                byte_delay_counter <= 0;
                                tx_state <= TX_BYTE_DELAY;
                            end else begin
                                tx_state <= TX_DONE;
                            end
                        end
                    end
                end
                
                TX_BYTE_DELAY: begin
                    tx_out <= 1'b1;
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