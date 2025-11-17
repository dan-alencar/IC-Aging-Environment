-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Fri Apr 25 14:25:14 2025
-- Host        : alisson.lesc.ufc.br running 64-bit unknown
-- Command     : write_vhdl -force -mode funcsim
--               /home/alisson/Downloads/aging_mirai_tensao/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_modern_sensible_0_0/design_1_modern_sensible_0_0_sim_netlist.vhdl
-- Design      : design_1_modern_sensible_0_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_modern_sensible_0_0_modern_sensible is
  port (
    ff1_out : out STD_LOGIC;
    alarm : out STD_LOGIC;
    in_sensor : in STD_LOGIC;
    psclk : in STD_LOGIC;
    reset : in STD_LOGIC;
    sclk : in STD_LOGIC;
    clk_en : in STD_LOGIC
  );
  attribute ORIG_REF_NAME : string;
  attribute ORIG_REF_NAME of design_1_modern_sensible_0_0_modern_sensible : entity is "modern_sensible";
end design_1_modern_sensible_0_0_modern_sensible;

architecture STRUCTURE of design_1_modern_sensible_0_0_modern_sensible is
  signal \^ff1\ : STD_LOGIC;
  signal \^ff1_out\ : STD_LOGIC;
  signal xor_out : STD_LOGIC;
  attribute AREA_GROUP : string;
  attribute AREA_GROUP of FF1 : label is "sensor";
  attribute BOX_TYPE : string;
  attribute BOX_TYPE of FF1 : label is "PRIMITIVE";
  attribute DONT_TOUCH : boolean;
  attribute DONT_TOUCH of FF1 : label is std.standard.true;
  attribute U_SET : string;
  attribute U_SET of FF1 : label is "sensor";
  attribute AREA_GROUP of FF2 : label is "sensor";
  attribute BOX_TYPE of FF2 : label is "PRIMITIVE";
  attribute DONT_TOUCH of FF2 : label is std.standard.true;
  attribute U_SET of FF2 : label is "sensor";
  attribute AREA_GROUP of FF3 : label is "sensor";
  attribute BOX_TYPE of FF3 : label is "PRIMITIVE";
  attribute DONT_TOUCH of FF3 : label is std.standard.true;
  attribute U_SET of FF3 : label is "sensor";
  attribute AREA_GROUP of XOR1 : label is "sensor";
  attribute BOX_TYPE of XOR1 : label is "PRIMITIVE";
  attribute DONT_TOUCH of XOR1 : label is std.standard.true;
  attribute U_SET of XOR1 : label is "sensor";
  attribute XILINX_LEGACY_PRIM : string;
  attribute XILINX_LEGACY_PRIM of XOR1 : label is "LUT2_L";
  attribute XILINX_TRANSFORM_PINMAP : string;
  attribute XILINX_TRANSFORM_PINMAP of XOR1 : label is "LO:O";
begin
  ff1_out <= \^ff1_out\;
FF1: unisim.vcomponents.FDCE
    generic map(
      INIT => '0',
      IS_CLR_INVERTED => '0',
      IS_C_INVERTED => '0',
      IS_D_INVERTED => '0'
    )
        port map (
      C => psclk,
      CE => '1',
      CLR => reset,
      D => in_sensor,
      Q => \^ff1\
    );
FF2: unisim.vcomponents.FDCE
    generic map(
      INIT => '0',
      IS_CLR_INVERTED => '0',
      IS_C_INVERTED => '0',
      IS_D_INVERTED => '0'
    )
        port map (
      C => sclk,
      CE => '1',
      CLR => reset,
      D => in_sensor,
      Q => \^ff1_out\
    );
FF3: unisim.vcomponents.FDCE
    generic map(
      INIT => '0',
      IS_CLR_INVERTED => '0',
      IS_C_INVERTED => '0',
      IS_D_INVERTED => '0'
    )
        port map (
      C => clk_en,
      CE => '1',
      CLR => reset,
      D => xor_out,
      Q => alarm
    );
XOR1: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => \^ff1\,
      I1 => \^ff1_out\,
      O => xor_out
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_modern_sensible_0_0 is
  port (
    sclk : in STD_LOGIC;
    psclk : in STD_LOGIC;
    in_sensor : in STD_LOGIC;
    reset : in STD_LOGIC;
    clk_en : in STD_LOGIC;
    alarm : out STD_LOGIC;
    ff1_out : out STD_LOGIC
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of design_1_modern_sensible_0_0 : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_modern_sensible_0_0 : entity is "design_1_modern_sensible_0_0,modern_sensible,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_modern_sensible_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_modern_sensible_0_0 : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of design_1_modern_sensible_0_0 : entity is "modern_sensible,Vivado 2024.2";
end design_1_modern_sensible_0_0;

architecture STRUCTURE of design_1_modern_sensible_0_0 is
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of reset : signal is "xilinx.com:signal:reset:1.0 reset RST";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of reset : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of reset : signal is "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0";
begin
inst: entity work.design_1_modern_sensible_0_0_modern_sensible
     port map (
      alarm => alarm,
      clk_en => clk_en,
      ff1_out => ff1_out,
      in_sensor => in_sensor,
      psclk => psclk,
      reset => reset,
      sclk => sclk
    );
end STRUCTURE;
