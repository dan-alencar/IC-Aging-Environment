`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Module Name: temp_catcher
// Description: Triggered System Monitor Interface (Aligned with sysmon_monitor)
//              1. Waits for Trigger
//              2. Reads Temp
//              3. Reads VCCINT
//              4. Signals measure_done
//////////////////////////////////////////////////////////////////////////////////

module temp_catcher(
    input wire clk,
    input wire reset,
    
    // SYSMON Interface
    input wire drdy,
    input wire [15:0] do_data,
    output reg [7:0] daddr,
    output reg den,
    
    // Control / Data Interface
    input wire trigger,          // Start measurement sequence
    output reg measure_done,     // Pulse when both reads are complete
    output wire [20:0] temp,
    output wire [20:0] vccint
    );

    // =========================================================================
    // Registers & Constants
    // =========================================================================
    reg [2:0] state;
    reg [15:0] timeout_cnt;
    
    // Raw registers to store data
    reg [15:0] raw_temp_data;
    reg [15:0] raw_vcc_data;

    // States
    localparam IDLE      = 3'd0;
    localparam READ_TEMP = 3'd1; // State where DEN is Low, waiting to go to WAIT
    localparam WAIT_TEMP = 3'd2;
    localparam READ_VCC  = 3'd3;
    localparam WAIT_VCC  = 3'd4;
    localparam DONE      = 3'd5;
    
    // Timeout Safety (10,000 cycles @ 100MHz = 100us)
    localparam TIMEOUT_MAX = 16'd10000;

    // =========================================================================
    // State Machine
    // =========================================================================
    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            state <= IDLE;
            daddr <= 8'h00;
            den <= 1'b0;
            timeout_cnt <= 0;
            raw_temp_data <= 0;
            raw_vcc_data <= 0;
            measure_done <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    measure_done <= 1'b0;
                    timeout_cnt <= 0;
                    
                    if (trigger) begin
                        // Setup read for TEMPERATURE (0x00)
                        daddr <= 8'h00;
                        den <= 1'b1;         // Pulse High
                        state <= READ_TEMP;
                    end
                end

                READ_TEMP: begin
                    den <= 1'b0;             // Return Low (1-cycle pulse complete)
                    timeout_cnt <= 0;
                    state <= WAIT_TEMP;
                end

                WAIT_TEMP: begin
                    if (drdy) begin
                        raw_temp_data <= do_data; // Latch Temp
                        
                        // Immediately setup read for VCCINT (0x01)
                        daddr <= 8'h01;
                        den <= 1'b1;         // Pulse High
                        state <= READ_VCC;
                        
                        timeout_cnt <= 0;
                    end else if (timeout_cnt >= TIMEOUT_MAX) begin
                        state <= IDLE;       // Abort on timeout
                    end else begin
                        timeout_cnt <= timeout_cnt + 1;
                    end
                end

                READ_VCC: begin
                    den <= 1'b0;             // Return Low
                    timeout_cnt <= 0;
                    state <= WAIT_VCC;
                end

                WAIT_VCC: begin
                    if (drdy) begin
                        raw_vcc_data <= do_data; // Latch VCC
                        state <= DONE;
                        timeout_cnt <= 0;
                    end else if (timeout_cnt >= TIMEOUT_MAX) begin
                        state <= IDLE;
                    end else begin
                        timeout_cnt <= timeout_cnt + 1;
                    end
                end
                
                DONE: begin
                    measure_done <= 1'b1;    // Signal completion
                    state <= IDLE;
                end
                
                default: state <= IDLE;
            endcase
        end
    end

    // =========================================================================
    // Data Conversion (Pipeline)
    // =========================================================================
    // Temperature: ((ADC * 507590) / 65536) - 279420
    wire [31:0] temp_calc;
    assign temp_calc = (raw_temp_data * 507590) >> 16;
    assign temp = (temp_calc > 279420) ? (temp_calc - 279420) : 21'd0;

    // VCCINT: (ADC * 3000) / 4096
    assign vccint = (raw_vcc_data * 3000) >> 12;

endmodule