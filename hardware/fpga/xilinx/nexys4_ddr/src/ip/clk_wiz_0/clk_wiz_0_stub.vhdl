-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2025.2.1 (lin64) Build 6403652 Thu Mar 19 13:47:00 MDT 2026
-- Date        : Thu Jun 11 11:44:27 2026
-- Host        : marceau-lesc running 64-bit Linux Mint 22.3
-- Command     : write_vhdl -force -mode synth_stub
--               /home/marceau/Documents/GitHub/IC-Aging-Environment/vivado/aging_study_nexys4ddr/src/ip/clk_wiz_0/clk_wiz_0_stub.vhdl
-- Design      : clk_wiz_0
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xcau15p-ubva368-2-e
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity clk_wiz_0 is
  Port ( 
    clk_en : out STD_LOGIC;
    sensor0 : out STD_LOGIC;
    clk_sys : out STD_LOGIC;
    reset : in STD_LOGIC;
    locked : out STD_LOGIC;
    clk_in1 : in STD_LOGIC;
    psclk : in STD_LOGIC;
    psen : in STD_LOGIC;
    psincdec : in STD_LOGIC;
    psdone : out STD_LOGIC
  );

  attribute CORE_GENERATION_INFO : string;
  attribute CORE_GENERATION_INFO of clk_wiz_0 : entity is "clk_wiz_0,clk_wiz_v6_0_16_0_0,{component_name=clk_wiz_0,use_phase_alignment=true,use_min_o_jitter=false,use_max_i_jitter=false,use_dyn_phase_shift=true,use_inclk_switchover=false,use_dyn_reconfig=false,enable_axi=0,feedback_source=FDBK_AUTO,PRIMITIVE=MMCM,num_out_clk=3,clkin1_period=10.000,clkin2_period=10.000,use_power_down=false,use_reset=true,use_locked=true,use_inclk_stopped=false,feedback_type=SINGLE,CLOCK_MGR_TYPE=NA,manual_override=false}";
end clk_wiz_0;

architecture stub of clk_wiz_0 is
  attribute syn_black_box : boolean;
  attribute black_box_pad_pin : string;
  attribute syn_black_box of stub : architecture is true;
  attribute black_box_pad_pin of stub : architecture is "clk_en,sensor0,clk_sys,reset,locked,clk_in1,psclk,psen,psincdec,psdone";
begin
end;
