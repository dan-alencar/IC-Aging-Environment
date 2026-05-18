`timescale 1ns / 1ps

// XADC DRP polling state machine.
// Alternately reads die temperature (address 0x00) and VCCINT (address 0x01).
// Outputs are in millidegrees C (temp) and millivolts (vccint).
module temp_catcher (
    input  logic        clk,
    input  logic        reset,   // active-low
    input  logic        drdy,
    input  logic [15:0] do_data,
    output logic [6:0]  daddr,
    output logic        den,
    output logic [20:0] temp,
    output logic [20:0] vccint
);
    typedef enum logic [1:0] {
        ASK_TEMP = 2'b00,
        GET_TEMP = 2'b01,
        ASK_VCC  = 2'b10,
        GET_VCC  = 2'b11
    } state_t;

    state_t      state;
    logic [31:0] placeholder [2];  // [0] = temp raw, [1] = vccint raw
    logic [7:0]  timeout;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            state          <= ASK_TEMP;
            daddr          <= 7'h0;
            den            <= 1'b1;
            placeholder[0] <= '0;
            placeholder[1] <= '0;
            timeout        <= '0;
        end else begin
            case (state)
                ASK_TEMP: begin
                    den     <= 1'b1;
                    daddr   <= 7'h00;
                    timeout <= '0;
                    state   <= GET_TEMP;
                end
                GET_TEMP: begin
                    den <= 1'b0;
                    if (timeout == 8'h7F) begin
                        state <= ASK_TEMP;  // watchdog: retry
                    end else begin
                        timeout <= timeout + 1'b1;
                        if (drdy) begin
                            // Xilinx XADC temp formula: T(K) = ADC_code * 503.975 / 4096
                            // Result in millidegrees Kelvin, converted to milli-C below.
                            placeholder[0] <= (32'(do_data[15:4]) * 503975) >> 12;
                            state          <= ASK_VCC;
                        end
                    end
                end
                ASK_VCC: begin
                    den     <= 1'b1;
                    daddr   <= 7'h01;
                    timeout <= '0;
                    state   <= GET_VCC;
                end
                GET_VCC: begin
                    den <= 1'b0;
                    if (timeout == 8'h7F) begin
                        state <= ASK_VCC;  // watchdog: retry
                    end else begin
                        timeout <= timeout + 1'b1;
                        if (drdy) begin
                            // VCCINT formula: V(mV) = ADC_code * 3000 / 4096
                            placeholder[1] <= (32'(do_data[15:4]) * 3000) >> 12;
                            state          <= ASK_TEMP;
                        end
                    end
                end
            endcase
        end
    end

    // Convert millidegrees Kelvin → millidegrees Celsius
    assign temp   = placeholder[0][20:0] - 21'd273150;
    assign vccint = placeholder[1][20:0];

endmodule
