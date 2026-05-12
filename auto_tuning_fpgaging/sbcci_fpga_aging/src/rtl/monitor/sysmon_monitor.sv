`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Module Name: sysmon_reader
// Description: XADC reader for temperature and VCCINT
//////////////////////////////////////////////////////////////////////////////////

module sysmon_reader (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        trigger,
    output reg  [15:0] temp_data,
    output reg  [15:0] vccint_data,
    output reg         read_done,
    output wire        busy
);

    reg  [7:0]  daddr;
    reg         den;
    wire [15:0] do_data;
    wire        drdy;

    xadc_wiz_0 sysmon_inst (
        .dclk_in(clk), 
        .reset_in(~rst_n),
        .daddr_in(daddr),
        .den_in(den),
        .dwe_in(1'b0),
        .di_in(16'h0),
        .do_out(do_data),
        .drdy_out(drdy),
        .vp(1'b0), 
        .vn(1'b0),
        .busy_out(),
        .channel_out(),
        .eoc_out(),
        .eos_out(),
        .alarm_out()
    );

    localparam IDLE      = 3'd0;
    localparam REQ_TEMP  = 3'd1;
    localparam WAIT_TEMP = 3'd2;
    localparam REQ_VCC   = 3'd3;
    localparam WAIT_VCC  = 3'd4;
    localparam DONE      = 3'd5;
    
    reg [2:0]  state;
    reg [15:0] timeout;
    reg        trig_prev;
    wire       trig_edge;
    
    assign trig_edge = trigger & ~trig_prev;
    assign busy = (state != IDLE);

    always @(posedge clk) begin
        if (!rst_n) begin
            state <= IDLE;
            daddr <= 8'h00;
            den <= 1'b0;
            temp_data <= 16'h0000;
            vccint_data <= 16'h0000;
            timeout <= 16'd0;
            trig_prev <= 1'b0;
            read_done <= 1'b0;
        end else begin
            trig_prev <= trigger;
            read_done <= 1'b0;
            
            case (state)
                IDLE: begin
                    den <= 1'b0;
                    timeout <= 16'd0;
                    if (trig_edge) begin
                        daddr <= 8'h00;
                        den <= 1'b1;
                        state <= REQ_TEMP;
                    end
                end
                
                REQ_TEMP: begin
                    den <= 1'b0;
                    state <= WAIT_TEMP;
                end
                
                WAIT_TEMP: begin
                    if (drdy) begin
                        temp_data <= do_data;
                        daddr <= 8'h01;
                        den <= 1'b1;
                        state <= REQ_VCC;
                    end else if (timeout >= 16'd50000) begin
                        state <= IDLE;
                    end else begin
                        timeout <= timeout + 1;
                    end
                end
                
                REQ_VCC: begin
                    den <= 1'b0;
                    timeout <= 16'd0;
                    state <= WAIT_VCC;
                end
                
                WAIT_VCC: begin
                    if (drdy) begin
                        vccint_data <= do_data;
                        state <= DONE;
                    end else if (timeout >= 16'd50000) begin
                        state <= IDLE;
                    end else begin
                        timeout <= timeout + 1;
                    end
                end
                
                DONE: begin
                    read_done <= 1'b1;
                    state <= IDLE;
                end
                
                default: state <= IDLE;
            endcase
        end
    end

endmodule