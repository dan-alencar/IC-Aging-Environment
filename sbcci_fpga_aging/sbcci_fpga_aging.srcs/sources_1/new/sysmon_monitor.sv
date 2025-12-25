`timescale 1ns / 1ps

module sysmon_monitor #(
    parameter int CLK_FREQ = 100000000, 
    parameter int BAUD_RATE = 125000 // Matches your Router config
)(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        aging_alarm,
    input  logic [15:0] aging_count,
    output logic        tx_out,
    output logic        tx_active
);

    // =========================================================================
    // 1. SYSMON ACQUISITION (SLOWED DOWN CLOCK)
    // =========================================================================
    logic [15:0] do_data;
    logic        drdy, den;
    logic [15:0] reg_temp, reg_vcc;
    logic [7:0]  daddr; // Was [6:0]

    // 2. Fix the SYSMONE4 Parameters
    SYSMONE4 #(
        .COMMON_N_SOURCE(16'hFFFF), 
        .INIT_40(16'h0000), 
        .INIT_41(16'h2000), // FIXED: Bit 0 was '1' (Power Down). Now '0' (Active).
        .INIT_42(16'h1400), // FIXED: Clock Divider 20. 100MHz/20 = 5MHz (Safe for ADC).
        .INIT_48(16'h0003), 
        .INIT_49(16'h0000)
    ) sysmon_inst (
        .DCLK(clk), 
        .RESET(!rst_n), 
        .DADDR(daddr), 
        .DEN(den), 
        .DWE(1'b0), 
        .DI(16'h0), 
        .DO(do_data), 
        .DRDY(drdy), 
        .EOS(), 
        .VP(1'b0), 
        .VN(1'b0)
    );
    
    // =========================================================================
    // 2. STATE MACHINE (With Debug Message Injection)
    // =========================================================================
    typedef enum {IDLE, WAIT_TEMP, WAIT_VCC, SEND_PACKET, SEND_DEBUG} state_t;
    state_t state;
    
    int unsigned timer;
    int unsigned debug_timer;
    logic send_debug_flag;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE; timer <= 0; den <= 0; daddr <= 0;
            reg_temp <= 0; reg_vcc <= 0;
            debug_timer <= 0; send_debug_flag <= 0;
        end else begin
            // 1Hz Debug Timer
            if (debug_timer >= CLK_FREQ) begin
                debug_timer <= 0;
                send_debug_flag <= 1; // Trigger "ALIVE" message
            end else begin
                debug_timer <= debug_timer + 1;
            end

            case (state)
                IDLE: begin
                    if (send_debug_flag) begin
                        send_debug_flag <= 0;
                        state <= SEND_DEBUG; // Priority to Debug Msg
                    end
                    else if (timer >= CLK_FREQ/10) begin // 10Hz Sensor Update
                        timer <= 0;
                        daddr <= 7'h00; den <= 1; // Read Temp
                        state <= WAIT_TEMP;
                    end else begin
                        timer <= timer + 1;
                    end
                end
                
                WAIT_TEMP: begin
                    den <= 0;
                    if (drdy) begin
                        reg_temp <= do_data;
                        daddr <= 7'h01; den <= 1; // Read Vcc
                        state <= WAIT_VCC;
                    end
                end
                
                WAIT_VCC: begin
                    den <= 0;
                    if (drdy) begin
                        reg_vcc <= do_data;
                        state <= SEND_PACKET;
                    end
                end
                
                SEND_PACKET: if (!tx_active) state <= IDLE;
                SEND_DEBUG:  if (!tx_active) state <= IDLE;
            endcase
        end
    end

    // =========================================================================
    // 3. PACKET SERIALIZER (Binary + Text Debug)
    // =========================================================================
    // Debug String: "[FPGA] ALIVE\n" (13 chars)
    // Packet: [1A]... (8 chars)
    
    logic [3:0] byte_idx;
    logic       start_tx, busy_internal;
    logic [7:0] tx_byte;
    logic [7:0] debug_str [0:12]; // " [FPGA] ALIVE\n"
    
    // Initialize String (SystemVerilog)
    initial begin
        debug_str[0]="["; debug_str[1]="F"; debug_str[2]="P"; debug_str[3]="G";
        debug_str[4]="A"; debug_str[5]="]"; debug_str[6]=" "; debug_str[7]="A";
        debug_str[8]="L"; debug_str[9]="I"; debug_str[10]="V"; debug_str[11]="E";
        debug_str[12]=8'h0A; // Newline
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_active <= 0; byte_idx <= 0; start_tx <= 0;
        end else begin
            // Trigger Transmission
            if ((state == SEND_PACKET || state == SEND_DEBUG) && !tx_active) begin
                tx_active <= 1; byte_idx <= 0; start_tx <= 1;
            end 
            else if (tx_active) begin
                start_tx <= 0;
                if (!busy_internal && !start_tx) begin
                    // Determine Max Length based on packet type
                    int max_len = (state == SEND_DEBUG) ? 12 : 7;
                    
                    if (byte_idx == max_len) begin
                        tx_active <= 0; // Done
                    end else begin
                        byte_idx <= byte_idx + 1;
                        start_tx <= 1;
                    end
                end
            end
        end
    end

    // Data Mux
    always_comb begin
        if (state == SEND_DEBUG) begin
            tx_byte = debug_str[byte_idx];
        end else begin
            // Standard Aging Packet
            case (byte_idx)
                0: tx_byte = 8'h1A;
                1: tx_byte = reg_temp[15:8];
                2: tx_byte = reg_temp[7:0];
                3: tx_byte = reg_vcc[15:8];
                4: tx_byte = reg_vcc[7:0];
                5: tx_byte = aging_count[15:8]; 
                6: tx_byte = aging_count[7:0];  
                7: tx_byte = {7'b0, aging_alarm};
                default: tx_byte = 8'h00;
            endcase
        end
    end

    // =========================================================================
    // 4. UART DRIVER
    // =========================================================================
    int unsigned baud_cnt;
    int unsigned bit_cnt;
    logic [8:0] shifter; 
    localparam int CYCLES_PER_BIT = CLK_FREQ / BAUD_RATE;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_out <= 1; busy_internal <= 0;
        end else begin
            if (start_tx) begin
                shifter <= {1'b1, tx_byte}; 
                tx_out <= 0; 
                busy_internal <= 1; baud_cnt <= 0; bit_cnt <= 0;
            end else if (busy_internal) begin
                if (baud_cnt < CYCLES_PER_BIT-1) baud_cnt++;
                else begin
                    baud_cnt <= 0;
                    if (bit_cnt < 9) begin
                        tx_out <= shifter[0];
                        shifter <= shifter >> 1;
                        bit_cnt++;
                    end else busy_internal <= 0;
                end
            end
        end
    end
endmodule