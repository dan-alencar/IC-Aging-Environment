-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Fri Apr 25 14:18:17 2025
-- Host        : alisson.lesc.ufc.br running 64-bit unknown
-- Command     : write_vhdl -force -mode funcsim
--               /home/alisson/Downloads/aging_mirai_tensao/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_controller_controller_0_0/design_1_controller_controller_0_0_sim_netlist.vhdl
-- Design      : design_1_controller_controller_0_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_controller_controller_0_0_controller_controller is
  port (
    display_value : out STD_LOGIC_VECTOR ( 15 downto 0 );
    psen : out STD_LOGIC;
    send : out STD_LOGIC;
    change : out STD_LOGIC;
    clk : in STD_LOGIC;
    reset : in STD_LOGIC;
    psdone : in STD_LOGIC;
    alarm : in STD_LOGIC
  );
  attribute ORIG_REF_NAME : string;
  attribute ORIG_REF_NAME of design_1_controller_controller_0_0_controller_controller : entity is "controller_controller";
end design_1_controller_controller_0_0_controller_controller;

architecture STRUCTURE of design_1_controller_controller_0_0_controller_controller is
  signal \FSM_sequential_state[1]_i_1_n_0\ : STD_LOGIC;
  signal \^change\ : STD_LOGIC;
  signal change_enable : STD_LOGIC;
  signal \change_enable__0\ : STD_LOGIC;
  signal change_i_1_n_0 : STD_LOGIC;
  signal \display_value_reg[15]_i_1_n_0\ : STD_LOGIC;
  signal \inc_count[0]_i_2_n_0\ : STD_LOGIC;
  signal inc_count_reg : STD_LOGIC_VECTOR ( 15 downto 0 );
  signal \inc_count_reg[0]_i_1_n_0\ : STD_LOGIC;
  signal \inc_count_reg[0]_i_1_n_1\ : STD_LOGIC;
  signal \inc_count_reg[0]_i_1_n_2\ : STD_LOGIC;
  signal \inc_count_reg[0]_i_1_n_3\ : STD_LOGIC;
  signal \inc_count_reg[0]_i_1_n_4\ : STD_LOGIC;
  signal \inc_count_reg[0]_i_1_n_5\ : STD_LOGIC;
  signal \inc_count_reg[0]_i_1_n_6\ : STD_LOGIC;
  signal \inc_count_reg[0]_i_1_n_7\ : STD_LOGIC;
  signal \inc_count_reg[12]_i_1_n_1\ : STD_LOGIC;
  signal \inc_count_reg[12]_i_1_n_2\ : STD_LOGIC;
  signal \inc_count_reg[12]_i_1_n_3\ : STD_LOGIC;
  signal \inc_count_reg[12]_i_1_n_4\ : STD_LOGIC;
  signal \inc_count_reg[12]_i_1_n_5\ : STD_LOGIC;
  signal \inc_count_reg[12]_i_1_n_6\ : STD_LOGIC;
  signal \inc_count_reg[12]_i_1_n_7\ : STD_LOGIC;
  signal \inc_count_reg[4]_i_1_n_0\ : STD_LOGIC;
  signal \inc_count_reg[4]_i_1_n_1\ : STD_LOGIC;
  signal \inc_count_reg[4]_i_1_n_2\ : STD_LOGIC;
  signal \inc_count_reg[4]_i_1_n_3\ : STD_LOGIC;
  signal \inc_count_reg[4]_i_1_n_4\ : STD_LOGIC;
  signal \inc_count_reg[4]_i_1_n_5\ : STD_LOGIC;
  signal \inc_count_reg[4]_i_1_n_6\ : STD_LOGIC;
  signal \inc_count_reg[4]_i_1_n_7\ : STD_LOGIC;
  signal \inc_count_reg[8]_i_1_n_0\ : STD_LOGIC;
  signal \inc_count_reg[8]_i_1_n_1\ : STD_LOGIC;
  signal \inc_count_reg[8]_i_1_n_2\ : STD_LOGIC;
  signal \inc_count_reg[8]_i_1_n_3\ : STD_LOGIC;
  signal \inc_count_reg[8]_i_1_n_4\ : STD_LOGIC;
  signal \inc_count_reg[8]_i_1_n_5\ : STD_LOGIC;
  signal \inc_count_reg[8]_i_1_n_6\ : STD_LOGIC;
  signal \inc_count_reg[8]_i_1_n_7\ : STD_LOGIC;
  signal next_state : STD_LOGIC_VECTOR ( 1 downto 0 );
  signal \next_state__0\ : STD_LOGIC_VECTOR ( 1 downto 0 );
  signal psen_reg_i_1_n_0 : STD_LOGIC;
  signal psen_reg_i_2_n_0 : STD_LOGIC;
  signal sig_ant : STD_LOGIC;
  signal \signal\ : STD_LOGIC;
  signal \signal__0\ : STD_LOGIC;
  signal state : STD_LOGIC_VECTOR ( 1 to 1 );
  signal \NLW_inc_count_reg[12]_i_1_CO_UNCONNECTED\ : STD_LOGIC_VECTOR ( 3 to 3 );
  attribute XILINX_LEGACY_PRIM : string;
  attribute XILINX_LEGACY_PRIM of \FSM_sequential_next_state_reg[0]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP : string;
  attribute XILINX_TRANSFORM_PINMAP of \FSM_sequential_next_state_reg[0]\ : label is "VCC:GE GND:CLR";
  attribute SOFT_HLUTNM : string;
  attribute SOFT_HLUTNM of \FSM_sequential_next_state_reg[0]_i_1\ : label is "soft_lutpair0";
  attribute XILINX_LEGACY_PRIM of \FSM_sequential_next_state_reg[1]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \FSM_sequential_next_state_reg[1]\ : label is "VCC:GE GND:CLR";
  attribute SOFT_HLUTNM of \FSM_sequential_next_state_reg[1]_i_1\ : label is "soft_lutpair0";
  attribute FSM_ENCODED_STATES : string;
  attribute FSM_ENCODED_STATES of \FSM_sequential_state_reg[0]\ : label is "iSTATE:10,iSTATE0:01,iSTATE1:11,iSTATE2:00";
  attribute FSM_ENCODED_STATES of \FSM_sequential_state_reg[1]\ : label is "iSTATE:10,iSTATE0:01,iSTATE1:11,iSTATE2:00";
  attribute OPT_MODIFIED : string;
  attribute OPT_MODIFIED of change_enable_reg : label is "MLO";
  attribute XILINX_LEGACY_PRIM of change_enable_reg : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of change_enable_reg : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[0]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[0]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[10]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[10]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[11]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[11]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[12]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[12]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[13]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[13]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[14]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[14]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[15]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[15]\ : label is "VCC:GE GND:CLR";
  attribute SOFT_HLUTNM of \display_value_reg[15]_i_1\ : label is "soft_lutpair1";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[1]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[1]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[2]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[2]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[3]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[3]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[4]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[4]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[5]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[5]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[6]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[6]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[7]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[7]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[8]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[8]\ : label is "VCC:GE GND:CLR";
  attribute XILINX_LEGACY_PRIM of \display_value_reg[9]\ : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of \display_value_reg[9]\ : label is "VCC:GE GND:CLR";
  attribute ADDER_THRESHOLD : integer;
  attribute ADDER_THRESHOLD of \inc_count_reg[0]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \inc_count_reg[12]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \inc_count_reg[4]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \inc_count_reg[8]_i_1\ : label is 11;
  attribute XILINX_LEGACY_PRIM of psen_reg : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of psen_reg : label is "VCC:GE GND:CLR";
  attribute SOFT_HLUTNM of psen_reg_i_1 : label is "soft_lutpair2";
  attribute SOFT_HLUTNM of psen_reg_i_2 : label is "soft_lutpair1";
  attribute OPT_MODIFIED of signal_reg : label is "MLO";
  attribute XILINX_LEGACY_PRIM of signal_reg : label is "LD";
  attribute XILINX_TRANSFORM_PINMAP of signal_reg : label is "VCC:GE GND:CLR";
begin
  change <= \^change\;
\FSM_sequential_next_state_reg[0]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => \next_state__0\(0),
      G => psen_reg_i_2_n_0,
      GE => '1',
      Q => next_state(0)
    );
\FSM_sequential_next_state_reg[0]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"7770"
    )
        port map (
      I0 => psdone,
      I1 => \signal__0\,
      I2 => alarm,
      I3 => state(1),
      O => \next_state__0\(0)
    );
\FSM_sequential_next_state_reg[1]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => \next_state__0\(1),
      G => psen_reg_i_2_n_0,
      GE => '1',
      Q => next_state(1)
    );
\FSM_sequential_next_state_reg[1]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"7707"
    )
        port map (
      I0 => psdone,
      I1 => \signal__0\,
      I2 => alarm,
      I3 => state(1),
      O => \next_state__0\(1)
    );
\FSM_sequential_state[1]_i_1\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => reset,
      O => \FSM_sequential_state[1]_i_1_n_0\
    );
\FSM_sequential_state_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => next_state(0),
      Q => \signal__0\
    );
\FSM_sequential_state_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => next_state(1),
      Q => state(1)
    );
change_enable_reg: unisim.vcomponents.LDCE
    generic map(
      INIT => '0',
      IS_G_INVERTED => '1'
    )
        port map (
      CLR => '0',
      D => \change_enable__0\,
      G => state(1),
      GE => '1',
      Q => change_enable
    );
change_enable_reg_i_1: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => \signal__0\,
      O => \change_enable__0\
    );
change_i_1: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => change_enable,
      I1 => \^change\,
      O => change_i_1_n_0
    );
change_reg: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => change_i_1_n_0,
      Q => \^change\,
      R => '0'
    );
\display_value_reg[0]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(0),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(0)
    );
\display_value_reg[10]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(10),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(10)
    );
\display_value_reg[11]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(11),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(11)
    );
\display_value_reg[12]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(12),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(12)
    );
\display_value_reg[13]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(13),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(13)
    );
\display_value_reg[14]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(14),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(14)
    );
\display_value_reg[15]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(15),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(15)
    );
\display_value_reg[15]_i_1\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => \signal__0\,
      I1 => state(1),
      O => \display_value_reg[15]_i_1_n_0\
    );
\display_value_reg[1]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(1),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(1)
    );
\display_value_reg[2]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(2),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(2)
    );
\display_value_reg[3]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(3),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(3)
    );
\display_value_reg[4]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(4),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(4)
    );
\display_value_reg[5]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(5),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(5)
    );
\display_value_reg[6]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(6),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(6)
    );
\display_value_reg[7]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(7),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(7)
    );
\display_value_reg[8]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(8),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(8)
    );
\display_value_reg[9]\: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => inc_count_reg(9),
      G => \display_value_reg[15]_i_1_n_0\,
      GE => '1',
      Q => display_value(9)
    );
\inc_count[0]_i_2\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => inc_count_reg(0),
      O => \inc_count[0]_i_2_n_0\
    );
\inc_count_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[0]_i_1_n_7\,
      Q => inc_count_reg(0)
    );
\inc_count_reg[0]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => '0',
      CO(3) => \inc_count_reg[0]_i_1_n_0\,
      CO(2) => \inc_count_reg[0]_i_1_n_1\,
      CO(1) => \inc_count_reg[0]_i_1_n_2\,
      CO(0) => \inc_count_reg[0]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0001",
      O(3) => \inc_count_reg[0]_i_1_n_4\,
      O(2) => \inc_count_reg[0]_i_1_n_5\,
      O(1) => \inc_count_reg[0]_i_1_n_6\,
      O(0) => \inc_count_reg[0]_i_1_n_7\,
      S(3 downto 1) => inc_count_reg(3 downto 1),
      S(0) => \inc_count[0]_i_2_n_0\
    );
\inc_count_reg[10]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[8]_i_1_n_5\,
      Q => inc_count_reg(10)
    );
\inc_count_reg[11]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[8]_i_1_n_4\,
      Q => inc_count_reg(11)
    );
\inc_count_reg[12]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[12]_i_1_n_7\,
      Q => inc_count_reg(12)
    );
\inc_count_reg[12]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \inc_count_reg[8]_i_1_n_0\,
      CO(3) => \NLW_inc_count_reg[12]_i_1_CO_UNCONNECTED\(3),
      CO(2) => \inc_count_reg[12]_i_1_n_1\,
      CO(1) => \inc_count_reg[12]_i_1_n_2\,
      CO(0) => \inc_count_reg[12]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3) => \inc_count_reg[12]_i_1_n_4\,
      O(2) => \inc_count_reg[12]_i_1_n_5\,
      O(1) => \inc_count_reg[12]_i_1_n_6\,
      O(0) => \inc_count_reg[12]_i_1_n_7\,
      S(3 downto 0) => inc_count_reg(15 downto 12)
    );
\inc_count_reg[13]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[12]_i_1_n_6\,
      Q => inc_count_reg(13)
    );
\inc_count_reg[14]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[12]_i_1_n_5\,
      Q => inc_count_reg(14)
    );
\inc_count_reg[15]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[12]_i_1_n_4\,
      Q => inc_count_reg(15)
    );
\inc_count_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[0]_i_1_n_6\,
      Q => inc_count_reg(1)
    );
\inc_count_reg[2]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[0]_i_1_n_5\,
      Q => inc_count_reg(2)
    );
\inc_count_reg[3]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[0]_i_1_n_4\,
      Q => inc_count_reg(3)
    );
\inc_count_reg[4]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[4]_i_1_n_7\,
      Q => inc_count_reg(4)
    );
\inc_count_reg[4]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \inc_count_reg[0]_i_1_n_0\,
      CO(3) => \inc_count_reg[4]_i_1_n_0\,
      CO(2) => \inc_count_reg[4]_i_1_n_1\,
      CO(1) => \inc_count_reg[4]_i_1_n_2\,
      CO(0) => \inc_count_reg[4]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3) => \inc_count_reg[4]_i_1_n_4\,
      O(2) => \inc_count_reg[4]_i_1_n_5\,
      O(1) => \inc_count_reg[4]_i_1_n_6\,
      O(0) => \inc_count_reg[4]_i_1_n_7\,
      S(3 downto 0) => inc_count_reg(7 downto 4)
    );
\inc_count_reg[5]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[4]_i_1_n_6\,
      Q => inc_count_reg(5)
    );
\inc_count_reg[6]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[4]_i_1_n_5\,
      Q => inc_count_reg(6)
    );
\inc_count_reg[7]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[4]_i_1_n_4\,
      Q => inc_count_reg(7)
    );
\inc_count_reg[8]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[8]_i_1_n_7\,
      Q => inc_count_reg(8)
    );
\inc_count_reg[8]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \inc_count_reg[4]_i_1_n_0\,
      CO(3) => \inc_count_reg[8]_i_1_n_0\,
      CO(2) => \inc_count_reg[8]_i_1_n_1\,
      CO(1) => \inc_count_reg[8]_i_1_n_2\,
      CO(0) => \inc_count_reg[8]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3) => \inc_count_reg[8]_i_1_n_4\,
      O(2) => \inc_count_reg[8]_i_1_n_5\,
      O(1) => \inc_count_reg[8]_i_1_n_6\,
      O(0) => \inc_count_reg[8]_i_1_n_7\,
      S(3 downto 0) => inc_count_reg(11 downto 8)
    );
\inc_count_reg[9]\: unisim.vcomponents.FDCE
     port map (
      C => psdone,
      CE => '1',
      CLR => \FSM_sequential_state[1]_i_1_n_0\,
      D => \inc_count_reg[8]_i_1_n_6\,
      Q => inc_count_reg(9)
    );
psen_reg: unisim.vcomponents.LDCE
    generic map(
      INIT => '0'
    )
        port map (
      CLR => '0',
      D => psen_reg_i_1_n_0,
      G => psen_reg_i_2_n_0,
      GE => '1',
      Q => psen
    );
psen_reg_i_1: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => state(1),
      I1 => \signal__0\,
      O => psen_reg_i_1_n_0
    );
psen_reg_i_2: unisim.vcomponents.LUT2
    generic map(
      INIT => X"B"
    )
        port map (
      I0 => state(1),
      I1 => \signal__0\,
      O => psen_reg_i_2_n_0
    );
send_INST_0: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => \signal\,
      I1 => sig_ant,
      O => send
    );
sig_ant_reg: unisim.vcomponents.FDRE
     port map (
      C => clk,
      CE => '1',
      D => \signal\,
      Q => sig_ant,
      R => '0'
    );
signal_reg: unisim.vcomponents.LDCE
    generic map(
      INIT => '0',
      IS_G_INVERTED => '1'
    )
        port map (
      CLR => '0',
      D => \signal__0\,
      G => state(1),
      GE => '1',
      Q => \signal\
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_controller_controller_0_0 is
  port (
    clk : in STD_LOGIC;
    reset : in STD_LOGIC;
    alarm : in STD_LOGIC;
    psdone : in STD_LOGIC;
    display_value : out STD_LOGIC_VECTOR ( 15 downto 0 );
    change : out STD_LOGIC;
    psincdec : out STD_LOGIC;
    send : out STD_LOGIC;
    psen : out STD_LOGIC
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of design_1_controller_controller_0_0 : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_controller_controller_0_0 : entity is "design_1_controller_controller_0_0,controller_controller,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_controller_controller_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_controller_controller_0_0 : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of design_1_controller_controller_0_0 : entity is "controller_controller,Vivado 2024.2";
end design_1_controller_controller_0_0;

architecture STRUCTURE of design_1_controller_controller_0_0 is
  signal \<const0>\ : STD_LOGIC;
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of clk : signal is "xilinx.com:signal:clock:1.0 clk CLK";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of clk : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of clk : signal is "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN /clk_wiz_0_clk_out1, INSERT_VIP 0";
  attribute X_INTERFACE_INFO of reset : signal is "xilinx.com:signal:reset:1.0 reset RST";
  attribute X_INTERFACE_MODE of reset : signal is "slave";
  attribute X_INTERFACE_PARAMETER of reset : signal is "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0";
begin
  psincdec <= \<const0>\;
GND: unisim.vcomponents.GND
     port map (
      G => \<const0>\
    );
inst: entity work.design_1_controller_controller_0_0_controller_controller
     port map (
      alarm => alarm,
      change => change,
      clk => clk,
      display_value(15 downto 0) => display_value(15 downto 0),
      psdone => psdone,
      psen => psen,
      reset => reset,
      send => send
    );
end STRUCTURE;
