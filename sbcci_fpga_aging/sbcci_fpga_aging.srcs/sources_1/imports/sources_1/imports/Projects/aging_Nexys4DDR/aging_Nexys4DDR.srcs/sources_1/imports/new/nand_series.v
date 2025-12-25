`timescale 1ns / 1ps

module not_series(
    input clk,
    input test_bit,
    output reg start,
    output critpath
    );

    parameter size = 19; // Adjust this size to tune your delay line length
    
    // Wire array for the chain
    wire [(size):0] connection;
    
    // The start of the chain is the registered start signal
    assign connection[0] = start;
    
    genvar i;
    generate
        for(i = 0; i < (size); i = i+1) begin : lut_chain
            // CRITICAL: DONT_TOUCH prevents Vivado from optimizing these inverters away
            (* DONT_TOUCH = "yes" *)
            LUT1 #(
                .INIT(2'b01) // 2'b01 = Inverter Logic (~I0)
            ) INV (
                .O(connection[i + 1]), // Output
                .I0(connection[i])     // Input
            );
        end
    endgenerate
    
    always @(posedge clk) begin
        start <= test_bit;
        // In original design, inverted_bit was registered but not output. 
        // Keeping logic minimal as per original intent.
    end
    
    // The final output of the chain
    assign critpath = connection[(size)];
    
endmodule