`timescale 1ns / 1ps

// 8-digit time-multiplexed 7-segment display controller.
// Multiplexes at ~381 Hz (18-bit counter at 100 MHz → ~762 Hz half-period,
// MSB 3 bits select 1-of-8 digits).
module DisplayController (
    input  logic        clk,
    input  logic        reset,   // active-high
    input  logic [3:0]  in0, in1, in2, in3,  // right 4 digits (AN[3:0])
    input  logic [3:0]  in4, in5, in6, in7,  // left  4 digits (AN[7:4])
    output logic        seg0, seg1, seg2, seg3, seg4, seg5, seg6,
    output logic        dp,
    output logic [7:0]  an
);
    localparam int N = 18;

    logic [N-1:0] count;

    always_ff @(posedge clk or posedge reset) begin
        if (reset) count <= '0;
        else       count <= count + 1'b1;
    end

    // --- Digit select (combinational) ---
    logic [3:0] sseg;
    logic [7:0] an_temp;

    always_comb begin
        case (count[N-1:N-3])
            3'b000: begin sseg = in0; an_temp = 8'b1111_1110; end
            3'b001: begin sseg = in1; an_temp = 8'b1111_1101; end
            3'b010: begin sseg = in2; an_temp = 8'b1111_1011; end
            3'b011: begin sseg = in3; an_temp = 8'b1111_0111; end
            3'b100: begin sseg = in4; an_temp = 8'b1110_1111; end
            3'b101: begin sseg = in5; an_temp = 8'b1101_1111; end
            3'b110: begin sseg = in6; an_temp = 8'b1011_1111; end
            3'b111: begin sseg = in7; an_temp = 8'b0111_1111; end
        endcase
    end

    assign an = an_temp;

    // --- 7-segment decoder (combinational) ---
    logic [6:0] sseg_temp;

    always_comb begin
        case (sseg)
            4'h0: sseg_temp = 7'b100_0000;  // 0
            4'h1: sseg_temp = 7'b111_1001;  // 1
            4'h2: sseg_temp = 7'b010_0100;  // 2
            4'h3: sseg_temp = 7'b011_0000;  // 3
            4'h4: sseg_temp = 7'b001_1001;  // 4
            4'h5: sseg_temp = 7'b001_0010;  // 5
            4'h6: sseg_temp = 7'b000_0010;  // 6
            4'h7: sseg_temp = 7'b111_1000;  // 7
            4'h8: sseg_temp = 7'b000_0000;  // 8
            4'h9: sseg_temp = 7'b001_0000;  // 9
            4'hA: sseg_temp = 7'b000_1000;  // A
            4'hB: sseg_temp = 7'b000_0011;  // B
            4'hC: sseg_temp = 7'b100_0110;  // C
            4'hD: sseg_temp = 7'b010_0001;  // D
            4'hE: sseg_temp = 7'b000_0110;  // E
            4'hF: sseg_temp = 7'b000_1110;  // F
            default: sseg_temp = 7'b011_1111;  // dash
        endcase
    end

    assign {seg6, seg5, seg4, seg3, seg2, seg1, seg0} = sseg_temp;
    assign dp = 1'b1;  // decimal point always off

endmodule
