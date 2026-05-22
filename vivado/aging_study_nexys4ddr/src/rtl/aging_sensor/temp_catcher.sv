`timescale 1ns / 1ps

// XADC channel monitor — captures temperature and VCCINT from the continuous
// sequencer without issuing any DRP reads.
//
// Root cause of the previous DRP-polling design: in continuous sequencer mode
// DRDY fires after every averaging-complete conversion AND after every DRP
// read.  The old state machine could not distinguish the two, so it routinely
// captured the wrong channel's data (temperature slot got VAUXP[0] values;
// VCCINT slot got the temperature ADC code, which the 3 V formula turned into
// a plausible-looking ~1.86 V reading).
//
// Fix: never assert DEN.  With DEN tied low, every DRDY pulse is a
// conversion-complete event.  CHANNEL[4:0] identifies which channel the
// averaged result belongs to; DO carries that result.
//
// XADC configuration required in nexys4_aging_top:
//   INIT_48 must have bit 0 (temperature) AND bit 1 (VCCINT) set.
//   DEN must be tied to 0; CHANNEL must be connected to this module.
//
// Outputs are in millidegrees C (temp) and millivolts (vccint).
module temp_catcher (
    input  logic        clk,
    input  logic        reset,    // active-low
    input  logic        drdy,     // XADC DRDY — fires when an averaged result is ready
    input  logic [4:0]  channel,  // XADC CHANNEL — identifies the just-averaged channel
    input  logic [15:0] do_data,  // XADC DO — the averaged conversion result
    output logic [20:0] temp,
    output logic [20:0] vccint
);
    logic [31:0] placeholder_t;
    logic [31:0] placeholder_v;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            placeholder_t <= '0;
            placeholder_v <= '0;
        end else if (drdy) begin
            case (channel)
                // Xilinx XADC channel 0: on-die temperature
                // T(mK) = ADC_code * 503975 / 4096  (millidegrees Kelvin)
                5'h00: placeholder_t <= (32'(do_data[15:4]) * 503975) >> 12;
                // Xilinx XADC channel 1: VCCINT (internal attenuator 1/3)
                // V(mV) = ADC_code * 3000 / 4096
                5'h01: placeholder_v <= (32'(do_data[15:4]) * 3000)   >> 12;
                default: ;
            endcase
        end
    end

    // Millidegrees Kelvin → Celsius.
    // Clamp to 0 if the raw value would underflow the 21-bit unsigned
    // subtraction (e.g. XADC not yet settled at power-on).
    assign temp   = (placeholder_t[20:0] >= 21'd273150)
                    ? (placeholder_t[20:0] - 21'd273150)
                    : 21'd0;
    assign vccint = placeholder_v[20:0];

endmodule
