`timescale 1ns / 1ps

module sysmon_monitor #(
    parameter int CLK_FREQ = 100000000, 
    parameter int BAUD_RATE = 125000 
)(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        aging_alarm,
    input  logic [15:0] aging_count,
    input  logic        i_trigger,    // Signal from Controller to start reading
    output logic        tx_out,
    output logic        tx_active
);

    // =========================================================================
    // 1. SYSTEM MONITOR DRP INTERFACE
    // =========================================================================
    // The IP requires us to "read" registers via addresses.
    // Address 0x00 = Temperature
    // Address 0x01 = VCCINT
    
    logic [7:0]  daddr;
    logic        den;
    logic [15:0] do_data;
    logic        drdy;
    logic        busy;
    logic        ip_alarm;

    // Instantiating the IP you provided (xadc_wiz_0)
    xadc_wiz_0 sysmon_inst (
        .dclk_in(clk), 
        .reset_in(!rst_n),      // Active High Reset
        .daddr_in(daddr),       // Address to read
        .den_in(den),           // Enable signal
        .dwe_in(1'b0),          // Write Enable (0 = Read)
        .di_in(16'h0),          // Data Input (unused for read)
        .do_out(do_data),       // Data Output (Result)
        .drdy_out(drdy),        // Data Ready Flag
        .vp(1'b0), 
        .vn(1'b0),
        .busy_out(busy),
        .channel_out(),
        .eoc_out(),
        .eos_out(),
        .alarm_out(ip_alarm)
    );

    // =========================================================================
    // 2. STATE MACHINE: TRIGGER -> READ TEMP -> READ VCC -> SEND
    // =========================================================================
    logic [15:0] reg_temp, reg_vcc;
    logic        trig_prev;
    wire         trig_pulse = i_trigger && !trig_prev;

    typedef enum logic [2:0] {
        IDLE,
        READ_TEMP,  // Set Address 0x00
        WAIT_TEMP,  // Wait for Data
        READ_VCC,   // Set Address 0x01
        WAIT_VCC,   // Wait for Data
        SEND_PACKET // Transmit UART
    } state_t;
    
    state_t state;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            den <= 0; daddr <= 0;
            reg_temp <= 0; reg_vcc <= 0;
            trig_prev <= 0;
        end else begin
            trig_prev <= i_trigger; // Edge detection

            case (state)
                IDLE: begin
                    if (trig_pulse) begin
                        // 1. Start Read Temperature (Addr 0x00)
                        daddr <= 8'h00; 
                        den <= 1; 
                        state <= READ_TEMP;
                    end
                end

                READ_TEMP: begin
                    den <= 0; // Pulse enable for 1 cycle only
                    state <= WAIT_TEMP;
                end
                
                WAIT_TEMP: begin
                    if (drdy) begin
                        reg_temp <= do_data; // Store Temp
                        // 2. Start Read VCCINT (Addr 0x01)
                        daddr <= 8'h01; 
                        den <= 1; 
                        state <= READ_VCC;
                    end
                end
                
                READ_VCC: begin
                    den <= 0;
                    state <= WAIT_VCC;
                end

                WAIT_VCC: begin
                    if (drdy) begin
                        reg_vcc <= do_data; // Store VCC
                        state <= SEND_PACKET;
                    end
                end
                
                SEND_PACKET: begin
                    if (!tx_active) state <= IDLE;
                end
            endcase
        end
    end

    // =========================================================================
    // 3. PACKET SERIALIZER
    // =========================================================================
    logic [3:0] byte_idx;
    logic       start_tx, busy_internal;
    logic [7:0] tx_byte;
    logic       sending_started;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_active <= 0;
            byte_idx <= 0; start_tx <= 0;
            sending_started <= 0;
        end else begin
            // Start Transmission
            if (state == SEND_PACKET && !sending_started) begin
                tx_active <= 1;
                byte_idx <= 0; 
                start_tx <= 1;
                sending_started <= 1;
            end 
            // Reset flag when done
            else if (state != SEND_PACKET) begin
                sending_started <= 0;
            end
            // Handle Byte Serialization
            else if (tx_active) begin
                start_tx <= 0;
                if (!busy_internal && !start_tx) begin
                    if (byte_idx == 7) begin
                        tx_active <= 0; // All bytes sent
                    end else begin
                        byte_idx <= byte_idx + 1;
                        start_tx <= 1;
                    end
                end
            end
        end
    end

    // Packet Mux
    always_comb begin
        case (byte_idx)
            0: tx_byte = 8'h1A; // Header
            1: tx_byte = reg_temp[15:8];
            2: tx_byte = reg_temp[7:0];
            3: tx_byte = reg_vcc[15:8];
            4: tx_byte = reg_vcc[7:0];
            5: tx_byte = aging_count[15:8]; 
            6: tx_byte = aging_count[7:0];  
            7: tx_byte = {7'b0, aging_alarm};
            default: tx_byte = 8'h00;
        endcase
    end

    // =========================================================================
    // 4. UART DRIVER
    // =========================================================================
    int unsigned baud_cnt;
    int unsigned bit_cnt;
    logic [9:0] shifter; 
    localparam int CYCLES_PER_BIT = CLK_FREQ / BAUD_RATE;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx_out <= 1;
            busy_internal <= 0;
        end else begin
            if (start_tx) begin
                shifter <= {1'b1, tx_byte, 1'b0}; // Stop(1) + Data + Start(0)
                tx_out <= 0; // Start Bit
                busy_internal <= 1; baud_cnt <= 0; bit_cnt <= 0;
            end else if (busy_internal) begin
                if (baud_cnt < CYCLES_PER_BIT-1) baud_cnt++;
                else begin
                    baud_cnt <= 0;
                    if (bit_cnt < 9) begin
                        tx_out <= shifter[1]; // Shift out next bit
                        shifter <= {1'b1, shifter[9:1]};
                        bit_cnt++;
                    end else begin
                         busy_internal <= 0;
                         tx_out <= 1; // Idle
                    end
                end
            end
        end
    end
endmodule