`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05/14/2026 03:07:40 PM
// Design Name: 
// Module Name: carry ripple adder
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


`timescale 1ns / 1ps

(* DONT_TOUCH = "yes" *)
module ripple_carry_adder #(
    parameter WIDTH = 256
)(
    input  logic clk,
    input  logic reset_n,
    output logic error_flag,
    output logic [WIDTH-1:0] sum_debug
);


    reg [WIDTH-1:0] op_a;
    reg [WIDTH-1:0] op_b;
    wire [WIDTH-1:0] combined_sum;

 
    (* DONT_TOUCH = "yes" *)
    assign combined_sum = op_a + op_b;

    always @(posedge clk) begin
        if (!reset_n) begin
            op_a <= 0;
            op_b <= 0;
            error_flag <= 0;
        end else begin

            op_a <= op_a + 1;
    
            op_b <= {WIDTH{1'b1}}; 
            
     
            if (combined_sum != (op_a + op_b))
                error_flag <= 1'b1;
            else
                error_flag <= 1'b0;
        end
    end

    assign sum_debug = combined_sum;

endmodule
