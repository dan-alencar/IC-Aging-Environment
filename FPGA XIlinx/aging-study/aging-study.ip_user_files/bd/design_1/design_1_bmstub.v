// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// -------------------------------------------------------------------------------

`timescale 1 ps / 1 ps

(* BLOCK_STUB = "true" *)
module design_1 (
  CA,
  CB,
  CC,
  CD,
  CE,
  CF,
  CG,
  DP,
  AN,
  reset,
  tx,
  CLK100MHZ,
  rx
);

  (* X_INTERFACE_IGNORE = "true" *)
  output CA;
  (* X_INTERFACE_IGNORE = "true" *)
  output CB;
  (* X_INTERFACE_IGNORE = "true" *)
  output CC;
  (* X_INTERFACE_IGNORE = "true" *)
  output CD;
  (* X_INTERFACE_IGNORE = "true" *)
  output CE;
  (* X_INTERFACE_IGNORE = "true" *)
  output CF;
  (* X_INTERFACE_IGNORE = "true" *)
  output CG;
  (* X_INTERFACE_IGNORE = "true" *)
  output DP;
  (* X_INTERFACE_IGNORE = "true" *)
  output [7:0]AN;
  (* X_INTERFACE_IGNORE = "true" *)
  input reset;
  (* X_INTERFACE_IGNORE = "true" *)
  output tx;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 CLK.CLK100MHZ CLK" *)
  (* X_INTERFACE_MODE = "slave CLK.CLK100MHZ" *)
  (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME CLK.CLK100MHZ, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, ASSOCIATED_RESET reset, INSERT_VIP 0" *)
  input CLK100MHZ;
  (* X_INTERFACE_IGNORE = "true" *)
  input rx;

  // stub module has no contents

endmodule
