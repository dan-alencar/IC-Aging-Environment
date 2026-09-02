// N-channel packet serializer for the experimental multi-sensor branch.
//
// The single-sensor 9/15-byte packets have no channel-ID field and rely on
// fixed zero-padding bytes for framing -- neither extends cleanly to N
// channels. This is a small, separate, self-framed protocol used only on
// this branch (it does not touch PROTOCOL.md's existing formats):
//
//   Byte:  0    1    2    3   4   5    6   7   8    9 .. 9+2N-1   9+2N        9+2N+1
//          0xAA 0x55 LEN  TL  TM  TH   VL  VM  VH   [SLACK0..N-1] ALARM_BITS  CHECKSUM
//
//   LEN      = number of bytes from TL through ALARM_BITS inclusive (6 + 2N + 1)
//   TL/TM/TH = shared temp reading, 24-bit LE (matches both devices' native
//              width: Nexys4's temp_raw is a 21-bit millidegree value,
//              SBCCI's sysmon_temp is a 16-bit raw XADC code -- both fit
//              zero-extended into 24 bits, same convention the single-
//              sensor sensor_stream.v/.sv already uses)
//   VL/VM/VH = shared VCCINT reading, 24-bit LE, same rationale
//   SLACKi   = channel i's display_value, 16-bit LE, in channel order
//   ALARM_BITS = one bit per channel (bit i = channel i's current alarm),
//                packed LSB-first; only the low NUM_CHANNELS bits are valid
//   CHECKSUM = XOR of every byte from LEN through ALARM_BITS inclusive
//
// Paced the same way as sensor_stream.v/.sv: one byte every COUNT cycles
// (~one UART byte period at the configured baud), latched whole on the
// rising edge of `sendin` so the packet is a self-consistent snapshot.
module multi_sensor_stream #(
    parameter int NUM_CHANNELS = 4,
    parameter int BAUDRATE     = 9600,
    parameter int CLK_FREQ     = 100000000
) (
    input  logic                    clk,
    input  logic                    reset,     // active-low
    input  logic                    sendin,
    input  logic [23:0]             temp,
    input  logic [23:0]             vccint,
    input  logic [15:0]             slack [NUM_CHANNELS-1:0],
    input  logic [NUM_CHANNELS-1:0] alarm,
    output logic                    send,
    output logic [7:0]              data
);

    localparam int TOTAL_BYTES = 10 + 2 * NUM_CHANNELS; // sync(2)+len(1)+temp(3)+vcc(3)+slack(2N)+alarm(1)+cksum(1)
    localparam int LEN_FIELD   = 7 + 2 * NUM_CHANNELS;  // temp(3)+vcc(3)+slack(2N)+alarm(1)
    localparam int SEL_WIDTH   = $clog2(TOTAL_BYTES + 1);
    localparam int COUNT       = (CLK_FREQ / BAUDRATE) * 10;

    function automatic logic [7:0] pack_alarm();
        logic [7:0] a;
        a = 8'h00;
        for (int i = 0; i < NUM_CHANNELS; i++) a[i] = alarm[i];
        return a;
    endfunction

    function automatic logic [7:0] compute_checksum();
        logic [7:0] c;
        c = LEN_FIELD[7:0];
        c = c ^ temp[7:0]   ^ temp[15:8]   ^ temp[23:16];
        c = c ^ vccint[7:0] ^ vccint[15:8] ^ vccint[23:16];
        for (int i = 0; i < NUM_CHANNELS; i++)
            c = c ^ slack[i][7:0] ^ slack[i][15:8];
        c = c ^ pack_alarm();
        return c;
    endfunction

    logic [7:0] pkt_buf [0:TOTAL_BYTES-1];
    logic [SEL_WIDTH-1:0] sel;
    logic [31:0] counter;
    logic sendant, send_tx, enable;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) sendant <= 1'b0;
        else        sendant <= sendin;
    end
    assign send_tx = sendin && !sendant;

    // Latch the whole frame on the trigger edge -- guarantees a
    // self-consistent snapshot across every field, same principle as
    // sensor_stream.v/.sv's single latch-then-walk approach.
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            for (int i = 0; i < TOTAL_BYTES; i++) pkt_buf[i] <= 8'h00;
        end else if (send_tx) begin
            pkt_buf[0] <= 8'hAA;
            pkt_buf[1] <= 8'h55;
            pkt_buf[2] <= LEN_FIELD[7:0];
            pkt_buf[3] <= temp[7:0];
            pkt_buf[4] <= temp[15:8];
            pkt_buf[5] <= temp[23:16];
            pkt_buf[6] <= vccint[7:0];
            pkt_buf[7] <= vccint[15:8];
            pkt_buf[8] <= vccint[23:16];
            for (int i = 0; i < NUM_CHANNELS; i++) begin
                pkt_buf[9 + 2*i]     <= slack[i][7:0];
                pkt_buf[9 + 2*i + 1] <= slack[i][15:8];
            end
            pkt_buf[9 + 2*NUM_CHANNELS]  <= pack_alarm();
            pkt_buf[10 + 2*NUM_CHANNELS] <= compute_checksum();
        end
    end

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            sel     <= '0;
            counter <= '0;
            enable  <= 1'b0;
            send    <= 1'b0;
            data    <= 8'h00;
        end else begin
            send <= 1'b0;
            if (send_tx) begin
                enable  <= 1'b1;
                sel     <= '0;
                counter <= '0;
            end else if (enable) begin
                if (counter >= COUNT - 1) begin
                    counter <= '0;
                    if (sel < TOTAL_BYTES) begin
                        data <= pkt_buf[sel];
                        send <= 1'b1;
                        sel  <= sel + 1'b1;
                    end
                    if (sel == TOTAL_BYTES - 1) enable <= 1'b0;
                end else begin
                    counter <= counter + 1'b1;
                end
            end
        end
    end

endmodule
