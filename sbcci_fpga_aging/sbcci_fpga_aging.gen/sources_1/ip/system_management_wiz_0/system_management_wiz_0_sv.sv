// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// -------------------------------------------------------------------------------
// This file contains confidential and proprietary information
// of AMD and is protected under U.S. and international copyright
// and other intellectual property laws.
//
// DISCLAIMER
// This disclaimer is not a license and does not grant any
// rights to the materials distributed herewith. Except as
// otherwise provided in a valid license issued to you by
// AMD, and to the maximum extent permitted by applicable
// law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
// WITH ALL FAULTS, AND AMD HEREBY DISCLAIMS ALL WARRANTIES
// AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
// BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
// INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
// (2) AMD shall not be liable (whether in contract or tort,
// including negligence, or under any other theory of
// liability) for any loss or damage of any kind or nature
// related to, arising under or in connection with these
// materials, including for any direct, or any indirect,
// special, incidental, or consequential loss or damage
// (including loss of data, profits, goodwill, or any type of
// loss or damage suffered as a result of any action brought
// by a third party) even if such damage or loss was
// reasonably foreseeable or AMD had been advised of the
// possibility of the same.
//
// CRITICAL APPLICATIONS
// AMD products are not designed or intended to be fail-
// safe, or for use in any application requiring fail-safe
// performance, such as life-support or safety devices or
// systems, Class III medical devices, nuclear facilities,
// applications related to the deployment of airbags, or any
// other applications that could lead to death, personal
// injury, or severe property or environmental damage
// (individually and collectively, "Critical
// Applications"). Customer assumes the sole risk and
// liability of any use of AMD products in Critical
// Applications, subject only to applicable laws and
// regulations governing limitations on product liability.
//
// THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
// PART OF THIS FILE AT ALL TIMES.
//
// DO NOT MODIFY THIS FILE.

// MODULE VLNV: xilinx.com:ip:system_management_wiz:1.3

`timescale 1ps / 1ps

`include "vivado_interfaces.svh"

module system_management_wiz_0_sv (
  (* X_INTERFACE_IGNORE = "true" *)
  input wire [15:0] di_in,
  (* X_INTERFACE_IGNORE = "true" *)
  input wire [7:0] daddr_in,
  (* X_INTERFACE_IGNORE = "true" *)
  input wire den_in,
  (* X_INTERFACE_IGNORE = "true" *)
  input wire dwe_in,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire drdy_out,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire [15:0] do_out,
  (* X_INTERFACE_IGNORE = "true" *)
  input wire dclk_in,
  (* X_INTERFACE_IGNORE = "true" *)
  input wire reset_in,
  (* X_INTERFACE_IGNORE = "true" *)
  input wire vp,
  (* X_INTERFACE_IGNORE = "true" *)
  input wire vn,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire user_temp_alarm_out,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire vccint_alarm_out,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire vccaux_alarm_out,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire ot_out,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire [5:0] channel_out,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire eoc_out,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire alarm_out,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire eos_out,
  (* X_INTERFACE_IGNORE = "true" *)
  output wire busy_out
);

  system_management_wiz_0 inst (
    .di_in(di_in),
    .daddr_in(daddr_in),
    .den_in(den_in),
    .dwe_in(dwe_in),
    .drdy_out(drdy_out),
    .do_out(do_out),
    .dclk_in(dclk_in),
    .reset_in(reset_in),
    .vp(vp),
    .vn(vn),
    .user_temp_alarm_out(user_temp_alarm_out),
    .vccint_alarm_out(vccint_alarm_out),
    .vccaux_alarm_out(vccaux_alarm_out),
    .ot_out(ot_out),
    .channel_out(channel_out),
    .eoc_out(eoc_out),
    .alarm_out(alarm_out),
    .eos_out(eos_out),
    .busy_out(busy_out)
  );

endmodule
