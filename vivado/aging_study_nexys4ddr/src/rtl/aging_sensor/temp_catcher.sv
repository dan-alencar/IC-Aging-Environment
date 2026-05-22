`timescale 1ns / 1ps

// XADC DRP polling state machine.
// Alternately reads die temperature (DRP address 0x00) and VCCINT (0x01).
//
// DRDY is a DRP-only signal: it fires exactly once per DEN assertion when the
// read result is available.  It does NOT fire spontaneously on conversion
// events (those are EOC/EOS).  Keeping DEN tied low would silence DRDY
// permanently, so this module drives DEN/DADDR and polls both channels in turn.
//
// Outputs are in millidegrees C (temp) and millivolts (vccint).
module temp_catcher (
    input  logic        clk,
    input  logic        reset,   // active-low
    input  logic        drdy,    // XADC DRDY — fires when a DRP read completes
    input  logic [15:0] do_data, // XADC DO — read result
    output logic [6:0]  daddr,   // XADC DADDR — DRP read address
    output logic        den,     // XADC DEN  — initiates a DRP read
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
    logic [31:0] placeholder_t;
    logic [31:0] placeholder_v;
    logic [7:0]  timeout;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            state         <= ASK_TEMP;
            daddr         <= 7'h0;
            den           <= 1'b1;
            placeholder_t <= '0;
            placeholder_v <= '0;
            timeout       <= '0;
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
                            // T(mK) = ADC_code * 503975 / 4096
                            placeholder_t <= (32'(do_data[15:4]) * 503975) >> 12;
                            state         <= ASK_VCC;
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
                            // V(mV) = ADC_code * 3000 / 4096
                            placeholder_v <= (32'(do_data[15:4]) * 3000) >> 12;
                            state         <= ASK_TEMP;
                        end
                    end
                end
            endcase
        end
    end

    // Millidegrees Kelvin → Celsius.
    // Clamp to 0 during power-on before the XADC settles.
    assign temp   = (placeholder_t[20:0] >= 21'd273150)
                    ? (placeholder_t[20:0] - 21'd273150)
                    : 21'd0;
    assign vccint = placeholder_v[20:0];

endmodule
