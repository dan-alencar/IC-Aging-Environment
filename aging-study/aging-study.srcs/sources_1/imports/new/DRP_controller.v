`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/10/2025 12:29:21 PM
// Design Name: 
// Module Name: DRP_controller
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


module DRP_controller(
    input wire clk,
    input wire rst,
    output reg [15:0] di_in,
    input wire[15:0] do_out,
    output reg [6:0] daddr_in,
    output reg den_in,
    output reg dwe_in,
    input wire drdy_out,
    output reg [15:0] temperature_celsius
    );
    
    // Local parameters for DRP
    localparam ADDR_TEMP = 7'h00; // Address for temperature register

    // Internal registers
    reg [15:0] raw_temperature; // Raw temperature from DRP
    reg [31:0] scaled_temperature; // Scaled temperature

    // DRP interface management
    always @(negedge rst) begin // não finalizado
        den_in = 1;
        dwe_in = 0;
        daddr_in = ADDR_TEMP;
        di_in = 16'b0;
    end
    
    always @(posedge clk) begin
        if (drdy_out) begin
            // Capture the raw temperature data
            raw_temperature <= do_out;
        end
    end

    // Conversion to Celsius (assuming formula from XADC documentation)
    // T(C) = (raw_temp / 4096.0) * 503.975 - 273.15
    always @(*) begin
        scaled_temperature = (raw_temperature * 503975) >> 12; // Multiply and scale
        temperature_celsius = scaled_temperature - 27315; // Subtract offset]
    end
    
endmodule
