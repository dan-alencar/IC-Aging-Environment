`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 29.05.2024 18:29:43
// Design Name: 
// Module Name: BINtoBCD
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


module BinToBCD(clk,bin,un,dec,cent,mil,bil,tril,quadr,quint
    );
	
	input clk;
	input [20:0] bin;
	output reg [3:0] quint = 0;
	output reg [3:0] quadr = 0;
	output reg [3:0] tril = 0;
	output reg [3:0] bil = 0;
	output reg [3:0] mil = 0;
	output reg [3:0] cent = 0 ;
	output reg [3:0] dec = 0;
	output reg [3:0] un = 0;
	
	integer i;
	
	always@(posedge clk) begin
		quint=0;
		quadr=0;
		tril=0;
		bil=0;
		mil=0;
		cent=0;
		dec=0;
		un=0;
		
		for (i=19;i>=0;i=i-1)
		begin
			if(quint>=5) begin
				quint = quint+3;
			end
			if(quadr>=5) begin
				quadr = quadr+3;
			end
			if(tril>=5) begin
				tril = tril+3;
			end
			if(bil>=5) begin
				bil = bil+3;
			end
			if(mil>=5) begin
				mil = mil+3;
			end
			if(cent>=5) begin
				cent = cent+3;
			end
			if (dec>=5) begin
				dec = dec+3;
			end
			if (un >=5) begin
				un = un +3;
			end
			
			quint = quint << 1;
			quint[0] = quadr[3];
			
			quadr = quadr << 1;
			quadr[0] = tril[3];
			
			tril = tril << 1;
			tril[0] = bil[3];
			
			bil = bil << 1;
			bil[0] = mil[3];
			
			mil = mil << 1;
			mil[0] = cent[3];
			
			cent = cent << 1;
			cent[0] = dec[3];
			
			dec = dec << 1;
			dec[0] = un[3];
			
			un = un << 1;
			un[0] = bin[i];
			
		end
	end
	
endmodule

