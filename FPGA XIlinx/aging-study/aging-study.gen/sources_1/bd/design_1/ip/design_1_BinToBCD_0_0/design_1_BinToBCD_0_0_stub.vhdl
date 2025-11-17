-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Wed Feb  5 19:11:33 2025
-- Host        : pop-os running 64-bit Pop!_OS 22.04 LTS
-- Command     : write_vhdl -force -mode synth_stub
--               /home/mirai/Documents/Projects/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_BinToBCD_0_0/design_1_BinToBCD_0_0_stub.vhdl
-- Design      : design_1_BinToBCD_0_0
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity design_1_BinToBCD_0_0 is
  Port ( 
    clk : in STD_LOGIC;
    bin : in STD_LOGIC_VECTOR ( 20 downto 0 );
    un : out STD_LOGIC_VECTOR ( 3 downto 0 );
    dec : out STD_LOGIC_VECTOR ( 3 downto 0 );
    cent : out STD_LOGIC_VECTOR ( 3 downto 0 );
    mil : out STD_LOGIC_VECTOR ( 3 downto 0 );
    bil : out STD_LOGIC_VECTOR ( 3 downto 0 );
    tril : out STD_LOGIC_VECTOR ( 3 downto 0 );
    quadr : out STD_LOGIC_VECTOR ( 3 downto 0 );
    quint : out STD_LOGIC_VECTOR ( 3 downto 0 )
  );

  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_BinToBCD_0_0 : entity is "design_1_BinToBCD_0_0,BinToBCD,{}";
  attribute CORE_GENERATION_INFO : string;
  attribute CORE_GENERATION_INFO of design_1_BinToBCD_0_0 : entity is "design_1_BinToBCD_0_0,BinToBCD,{x_ipProduct=Vivado 2024.2,x_ipVendor=xilinx.com,x_ipLibrary=module_ref,x_ipName=BinToBCD,x_ipVersion=1.0,x_ipCoreRevision=1,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_BinToBCD_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_BinToBCD_0_0 : entity is "module_ref";
end design_1_BinToBCD_0_0;

architecture stub of design_1_BinToBCD_0_0 is
  attribute syn_black_box : boolean;
  attribute black_box_pad_pin : string;
  attribute syn_black_box of stub : architecture is true;
  attribute black_box_pad_pin of stub : architecture is "clk,bin[20:0],un[3:0],dec[3:0],cent[3:0],mil[3:0],bil[3:0],tril[3:0],quadr[3:0],quint[3:0]";
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of clk : signal is "xilinx.com:signal:clock:1.0 clk CLK";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of clk : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of clk : signal is "XIL_INTERFACENAME clk, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of stub : architecture is "BinToBCD,Vivado 2024.2";
begin
end;
