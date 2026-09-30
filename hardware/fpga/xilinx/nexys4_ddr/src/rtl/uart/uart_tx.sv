`timescale 1ns / 1ps

// 8N1 UART transmitter.
// Frames: start bit (0), 8 data bits LSB-first, stop bit (1).
// send is edge-triggered (rising edge starts a frame); ignored when tx_busy.
module uart_tx (
    input  logic       clk,
    input  logic       reset,   // active-low
    input  logic       send,
    input  logic [7:0] data,
    output logic       tx,
    output logic       tx_busy
);
    localparam int BAUDRATE  = 9600;
    localparam int CLK_FREQ  = 100_000_000;
    localparam int COUNT     = CLK_FREQ / BAUDRATE;

    logic [3:0]  index;
    logic [15:0] counter;
    logic [9:0]  frame;
    logic        sendant;
    logic        send_tx;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) sendant <= 1'b0;
        else        sendant <= send;
    end

    assign send_tx = !sendant && send;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            tx      <= 1'b1;
            tx_busy <= 1'b0;
            counter <= '0;
            index   <= '0;
            frame   <= '0;
        end else if (send_tx && !tx_busy) begin
            frame   <= {1'b1, data, 1'b0};  // stop | data[7:0] | start
            tx_busy <= 1'b1;
            index   <= '0;
            tx      <= 1'b0;                 // start bit
            counter <= COUNT;
        end else if (tx_busy) begin
            if (counter >= COUNT) begin
                if (index < 4'd9) begin
                    index <= index + 1'b1;
                    tx    <= frame[index];
                end else begin
                    tx_busy <= 1'b0;
                    tx      <= 1'b1;         // idle / stop bit
                end
                counter <= '0;
            end else begin
                counter <= counter + 1'b1;
            end
        end
    end

endmodule
