`timescale 1ns / 1ps

// 8N1 UART receiver at 9600 baud, 100 MHz clock.
// Detects the start bit, samples each data bit at its mid-point, then
// pulses valid=1 for exactly one clk cycle when a complete byte arrives.
// rx is synchronised to clk with a 2-FF chain before processing.
module uart_rx (
    input  logic       clk,
    input  logic       reset,   // active-low
    input  logic       rx,
    output logic       valid,
    output logic [7:0] data
);
    localparam int CLK_FREQ = 100_000_000;
    localparam int BAUDRATE = 9600;
    localparam int FULL     = CLK_FREQ / BAUDRATE;  // 10416 cycles per bit
    localparam int HALF     = FULL / 2;              // 5208  — mid-start-bit sample

    typedef enum logic [1:0] {IDLE, START, DATA, STOP} state_t;

    state_t      state;
    logic [15:0] counter;
    logic [2:0]  bit_idx;
    logic [7:0]  shift;
    logic        rx1, rx2;   // 2-FF synchroniser for async rx input

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            rx1 <= 1'b1;
            rx2 <= 1'b1;
        end else begin
            rx1 <= rx;
            rx2 <= rx1;
        end
    end

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            state   <= IDLE;
            counter <= '0;
            bit_idx <= '0;
            shift   <= '0;
            valid   <= 1'b0;
            data    <= '0;
        end else begin
            valid <= 1'b0;   // single-cycle pulse only

            case (state)
                IDLE: begin
                    if (!rx2) begin   // falling edge = start of start bit
                        counter <= '0;
                        state   <= START;
                    end
                end

                START: begin
                    // Wait to mid-start-bit, then verify it is still low
                    if (counter >= HALF[15:0]) begin
                        counter <= '0;
                        bit_idx <= '0;
                        state   <= rx2 ? IDLE : DATA;   // abort on glitch
                    end else
                        counter <= counter + 1'b1;
                end

                DATA: begin
                    // Sample at full-bit interval from mid-start-bit
                    if (counter >= FULL[15:0]) begin
                        shift   <= {rx2, shift[7:1]};   // LSB-first shift-in
                        counter <= '0;
                        if (bit_idx == 3'd7)
                            state <= STOP;
                        else
                            bit_idx <= bit_idx + 1'b1;
                    end else
                        counter <= counter + 1'b1;
                end

                STOP: begin
                    if (counter >= FULL[15:0]) begin
                        if (rx2) begin   // valid stop bit high
                            data  <= shift;
                            valid <= 1'b1;
                        end
                        counter <= '0;
                        state   <= IDLE;
                    end else
                        counter <= counter + 1'b1;
                end
            endcase
        end
    end
endmodule
