-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Thu May 15 18:03:29 2025
-- Host        : pop-os running 64-bit Pop!_OS 24.04 LTS
-- Command     : write_vhdl -force -mode funcsim
--               /home/mirai/Documents/Projects/Aging_Fase2/failure_catch/aging_failure_holder/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_failure_holder_0_0/design_1_failure_holder_0_0_sim_netlist.vhdl
-- Design      : design_1_failure_holder_0_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_failure_holder_0_0_failure_holder is
  port (
    held : out STD_LOGIC;
    ff1 : in STD_LOGIC;
    reset : in STD_LOGIC;
    ff2 : in STD_LOGIC
  );
  attribute ORIG_REF_NAME : string;
  attribute ORIG_REF_NAME of design_1_failure_holder_0_0_failure_holder : entity is "failure_holder";
end design_1_failure_holder_0_0_failure_holder;

architecture STRUCTURE of design_1_failure_holder_0_0_failure_holder is
  signal \^held\ : STD_LOGIC;
  signal held_i_1_n_0 : STD_LOGIC;
  signal held_i_2_n_0 : STD_LOGIC;
begin
  held <= \^held\;
held_i_1: unisim.vcomponents.LUT2
    generic map(
      INIT => X"B"
    )
        port map (
      I0 => \^held\,
      I1 => ff1,
      O => held_i_1_n_0
    );
held_i_2: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => reset,
      O => held_i_2_n_0
    );
held_reg: unisim.vcomponents.FDCE
     port map (
      C => ff2,
      CE => '1',
      CLR => held_i_2_n_0,
      D => held_i_1_n_0,
      Q => \^held\
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_failure_holder_0_0 is
  port (
    ff1 : in STD_LOGIC;
    ff2 : in STD_LOGIC;
    reset : in STD_LOGIC;
    held : out STD_LOGIC
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of design_1_failure_holder_0_0 : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_failure_holder_0_0 : entity is "design_1_failure_holder_0_0,failure_holder,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_failure_holder_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_failure_holder_0_0 : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of design_1_failure_holder_0_0 : entity is "failure_holder,Vivado 2024.2";
end design_1_failure_holder_0_0;

architecture STRUCTURE of design_1_failure_holder_0_0 is
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of reset : signal is "xilinx.com:signal:reset:1.0 reset RST";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of reset : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of reset : signal is "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0";
begin
inst: entity work.design_1_failure_holder_0_0_failure_holder
     port map (
      ff1 => ff1,
      ff2 => ff2,
      held => held,
      reset => reset
    );
end STRUCTURE;
