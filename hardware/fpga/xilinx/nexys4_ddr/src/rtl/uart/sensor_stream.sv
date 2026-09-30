`timescale 1ns / 1ps

// UART serialiser — 15-byte packet (9600 baud, 100 MHz clock).
//
// All inputs are LATCHED at the rising edge of sendin so that every byte of
// the packet comes from the same consistent snapshot.  Previously the live
// inputs were sampled per-byte, which caused garbage temp/voltage values
// whenever the XADC updated or a new sweep completed mid-packet.
//
// Packet layout (Little Endian):
//   Byte  0-2 : temp[23:0]         (XADC temperature, millidegrees C)
//   Byte  3-4 : sensor[15:0]       (phase step count from controller)
//   Byte  5-7 : vccint[23:0]       (XADC VCCINT, millivolts)
//   Byte  8   : {7'b0, failure}    (functional failure latch bit)
//   Byte  9-10: wrong[15:0]        (adder canary: last wrong result)
//   Byte 11-12: correct[15:0]      (adder canary: expected result at alarm)
//   Byte 13-14: error_count[15:0]  (running canary mismatch count, saturates)
module sensor_stream (
    input  logic [23:0] temp,
    input  logic [23:0] vccint,
    input  logic [15:0] sensor,
    input  logic        failure,
    input  logic [15:0] wrong,
    input  logic [15:0] correct,
    input  logic [15:0] error_count,
    input  logic        reset,   // active-low
    input  logic        clk,
    input  logic        sendin,
    output logic        send,
    output logic [7:0]  data
);
    localparam int BAUDRATE  = 9600;
    localparam int CLK_FREQ  = 100_000_000;
    localparam int COUNT     = (CLK_FREQ / BAUDRATE) * 10;

    // --- Latched snapshot captured at the rising edge of sendin ---
    logic [23:0] lat_temp, lat_vccint;
    logic [15:0] lat_sensor, lat_wrong, lat_correct, lat_error_count;
    logic        lat_failure;

    logic [16:0] counter;
    logic [3:0]  sel;
    logic        sendant;
    logic        enable;
    logic        send_tx;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) sendant <= 1'b0;
        else        sendant <= sendin;
    end

    assign send_tx = !sendant && sendin;

    // Latch all measurement inputs on the rising edge that starts a new packet.
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            lat_temp        <= '0;
            lat_vccint      <= '0;
            lat_sensor      <= '0;
            lat_failure     <= 1'b0;
            lat_wrong       <= '0;
            lat_correct     <= '0;
            lat_error_count <= '0;
        end else if (send_tx) begin
            lat_temp        <= temp;
            lat_vccint      <= vccint;
            lat_sensor      <= sensor;
            lat_failure     <= failure;
            lat_wrong       <= wrong;
            lat_correct     <= correct;
            lat_error_count <= error_count;
        end
    end

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            counter <= '0;
            sel     <= '0;
            send    <= 1'b0;
            data    <= '0;
            enable  <= 1'b0;
        end else if (send_tx) begin
            enable <= 1'b1;
        end else if (enable) begin
            if (counter >= COUNT) begin
                sel     <= (sel > 4'd14) ? 4'd0 : sel + 1'b1;
                counter <= '0;
                case (sel)
                    4'd0:  begin data <= lat_temp[7:0];             send <= 1'b1; end
                    4'd1:  begin data <= lat_temp[15:8];            send <= 1'b1; end
                    4'd2:  begin data <= lat_temp[23:16];           send <= 1'b1; end
                    4'd3:  begin data <= lat_sensor[7:0];           send <= 1'b1; end
                    4'd4:  begin data <= lat_sensor[15:8];          send <= 1'b1; end
                    4'd5:  begin data <= lat_vccint[7:0];           send <= 1'b1; end
                    4'd6:  begin data <= lat_vccint[15:8];          send <= 1'b1; end
                    4'd7:  begin data <= lat_vccint[23:16];         send <= 1'b1; end
                    4'd8:  begin data <= {7'b0, lat_failure};       send <= 1'b1; end
                    4'd9:  begin data <= lat_wrong[7:0];            send <= 1'b1; end
                    4'd10: begin data <= lat_wrong[15:8];           send <= 1'b1; end
                    4'd11: begin data <= lat_correct[7:0];          send <= 1'b1; end
                    4'd12: begin data <= lat_correct[15:8];         send <= 1'b1; end
                    4'd13: begin data <= lat_error_count[7:0];      send <= 1'b1; end
                    4'd14: begin data <= lat_error_count[15:8];     send <= 1'b1; end
                    default: begin data <= 8'h00; enable <= 1'b0; end
                endcase
            end else begin
                counter <= counter + 1'b1;
                send    <= 1'b0;
            end
        end
    end

endmodule
