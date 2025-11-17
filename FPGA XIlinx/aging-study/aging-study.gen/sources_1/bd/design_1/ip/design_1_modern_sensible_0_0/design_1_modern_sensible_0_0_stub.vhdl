-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Fri Apr 25 14:25:14 2025
-- Host        : alisson.lesc.ufc.br running 64-bit unknown
-- Command     : write_vhdl -force -mode synth_stub
--               /home/alisson/Downloads/aging_mirai_tensao/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_modern_sensible_0_0/design_1_modern_sensible_0_0_stub.vhdl
-- Design      : design_1_modern_sensible_0_0
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity design_1_modern_sensible_0_0 is
  Port ( 
    sclk : in STD_LOGIC;
    psclk : in STD_LOGIC;
    in_sensor : in STD_LOGIC;
    reset : in STD_LOGIC;
    clk_en : in STD_LOGIC;
    alarm : out STD_LOGIC;
    ff1_out : out STD_LOGIC
  );

  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_modern_sensible_0_0 : entity is "design_1_modern_sensible_0_0,modern_sensible,{}";
  attribute CORE_GENERATION_INFO : string;
  attribute CORE_GENERATION_INFO of design_1_modern_sensible_0_0 : entity is "design_1_modern_sensible_0_0,modern_sensible,{x_ipProduct=Vivado 2024.2,x_ipVendor=xilinx.com,x_ipLibrary=module_ref,x_ipName=modern_sensible,x_ipVersion=1.0,x_ipCoreRevision=1,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_modern_sensible_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_modern_sensible_0_0 : entity is "module_ref";
end design_1_modern_sensible_0_0;

architecture stub of design_1_modern_sensible_0_0 is
  attribute syn_black_box : boolean;
  attribute black_box_pad_pin : string;
  attribute syn_black_box of stub : architecture is true;
  attribute black_box_pad_pin of stub : architecture is "sclk,psclk,in_sensor,reset,clk_en,alarm,ff1_out";
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of reset : signal is "xilinx.com:signal:reset:1.0 reset RST";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of reset : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of reset : signal is "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of stub : architecture is "modern_sensible,Vivado 2024.2";
begin
end;
