-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Mon Mar 31 17:08:15 2025
-- Host        : mirai-note running 64-bit Arch Linux
-- Command     : write_vhdl -force -mode synth_stub
--               /home/mirai/Documentos/Projects/projeto_marco/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_temp_catcher_0_0/design_1_temp_catcher_0_0_stub.vhdl
-- Design      : design_1_temp_catcher_0_0
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity design_1_temp_catcher_0_0 is
  Port ( 
    clk : in STD_LOGIC;
    reset : in STD_LOGIC;
    drdy : in STD_LOGIC;
    do_data : in STD_LOGIC_VECTOR ( 15 downto 0 );
    daddr : out STD_LOGIC_VECTOR ( 6 downto 0 );
    den : out STD_LOGIC;
    temp : out STD_LOGIC_VECTOR ( 20 downto 0 );
    vccint : out STD_LOGIC_VECTOR ( 20 downto 0 )
  );

  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_temp_catcher_0_0 : entity is "design_1_temp_catcher_0_0,temp_catcher,{}";
  attribute CORE_GENERATION_INFO : string;
  attribute CORE_GENERATION_INFO of design_1_temp_catcher_0_0 : entity is "design_1_temp_catcher_0_0,temp_catcher,{x_ipProduct=Vivado 2024.2,x_ipVendor=xilinx.com,x_ipLibrary=module_ref,x_ipName=temp_catcher,x_ipVersion=1.0,x_ipCoreRevision=1,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED,ASK_TEMP=00,GET_TEMP=01,ASK_VCC=10,GET_VCC=11}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_temp_catcher_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_temp_catcher_0_0 : entity is "module_ref";
end design_1_temp_catcher_0_0;

architecture stub of design_1_temp_catcher_0_0 is
  attribute syn_black_box : boolean;
  attribute black_box_pad_pin : string;
  attribute syn_black_box of stub : architecture is true;
  attribute black_box_pad_pin of stub : architecture is "clk,reset,drdy,do_data[15:0],daddr[6:0],den,temp[20:0],vccint[20:0]";
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of clk : signal is "xilinx.com:signal:clock:1.0 clk CLK";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of clk : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of clk : signal is "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0";
  attribute X_INTERFACE_INFO of reset : signal is "xilinx.com:signal:reset:1.0 reset RST";
  attribute X_INTERFACE_MODE of reset : signal is "slave";
  attribute X_INTERFACE_PARAMETER of reset : signal is "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of stub : architecture is "temp_catcher,Vivado 2024.2";
begin
end;
