`timescale 1ns / 1ps

module temp_catcher(
    input clk,
    input reset,
    input wire drdy,
    input wire[15:0] do_data,
    output reg[15:0] daddr, // UPDATED: 16-bit address for SYSMON
    output reg den,
    output wire[23:0] temp,   // Expanded width to match your sensor_stream
    output wire[23:0] vccint  // Expanded width
    );

    reg[1:0] state;
    reg[31:0] placeholder[1:0];
    reg[7:0] timeout;
    
    parameter ASK_TEMP = 2'b00, GET_TEMP = 2'b01, ASK_VCC = 2'b10, GET_VCC = 2'b11;
    
    // SYSMON Addresses for UltraScale+
    localparam ADDR_TEMP   = 16'h0000;
    localparam ADDR_VCCINT = 16'h0001;

    always@(posedge clk or posedge reset) begin // Changed to posedge reset for consistency
        if(reset) begin
            state <= ASK_TEMP;
            daddr <= 16'h0;
            den <= 1'b1;
            placeholder[0] <= 32'b0;
            placeholder[1] <= 32'b0;
            timeout <= 7'b0;
        end
        else begin
            case(state)
            ASK_TEMP: begin
                den <= 1'b1;
                daddr <= ADDR_TEMP;
                timeout <= 0;
                state <= GET_TEMP;
                end
            GET_TEMP: begin
                den <= 1'b0;
                if(timeout == 8'hFF) state <= ASK_TEMP;
                else timeout <= timeout + 1;
                
                if (drdy) begin
                    state <= ASK_VCC;
                    // Transfer function may need tuning for US+, keeping original logic for now
                    placeholder[0] <= (do_data[15:4] * 503975) >> 12; 
                end
                end
            ASK_VCC: begin
                den <= 1'b1;
                timeout <= 0;
                daddr <= ADDR_VCCINT;
                state <= GET_VCC;
            end
            GET_VCC: begin
                den <= 1'b0;
                if(timeout == 8'hFF) state <= ASK_VCC;
                else timeout <= timeout + 1;
                
                if(drdy) begin
                    state <= ASK_TEMP;
                    placeholder[1] <= (do_data[15:4] * 3000) >> 12;
                end
            end
            endcase
        end
    end
    
    assign temp = placeholder[0] - 273150;
    assign vccint = placeholder[1];
    
endmodule