-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Wed Feb  5 19:11:24 2025
-- Host        : pop-os running 64-bit Pop!_OS 22.04 LTS
-- Command     : write_vhdl -force -mode funcsim
--               /home/mirai/Documents/Projects/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_DisplayController_0_0/design_1_DisplayController_0_0_sim_netlist.vhdl
-- Design      : design_1_DisplayController_0_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_DisplayController_0_0_DisplayController is
  port (
    seg4 : out STD_LOGIC;
    seg2 : out STD_LOGIC;
    seg3 : out STD_LOGIC;
    seg5 : out STD_LOGIC;
    seg6 : out STD_LOGIC;
    seg0 : out STD_LOGIC;
    seg1 : out STD_LOGIC;
    an : out STD_LOGIC_VECTOR ( 7 downto 0 );
    clk : in STD_LOGIC;
    reset : in STD_LOGIC;
    in3 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in2 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in1 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in0 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in7 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in6 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in5 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in4 : in STD_LOGIC_VECTOR ( 3 downto 0 )
  );
  attribute ORIG_REF_NAME : string;
  attribute ORIG_REF_NAME of design_1_DisplayController_0_0_DisplayController : entity is "DisplayController";
end design_1_DisplayController_0_0_DisplayController;

architecture STRUCTURE of design_1_DisplayController_0_0_DisplayController is
  signal \count[0]_i_2_n_0\ : STD_LOGIC;
  signal \count_reg[0]_i_1_n_0\ : STD_LOGIC;
  signal \count_reg[0]_i_1_n_1\ : STD_LOGIC;
  signal \count_reg[0]_i_1_n_2\ : STD_LOGIC;
  signal \count_reg[0]_i_1_n_3\ : STD_LOGIC;
  signal \count_reg[0]_i_1_n_4\ : STD_LOGIC;
  signal \count_reg[0]_i_1_n_5\ : STD_LOGIC;
  signal \count_reg[0]_i_1_n_6\ : STD_LOGIC;
  signal \count_reg[0]_i_1_n_7\ : STD_LOGIC;
  signal \count_reg[12]_i_1_n_0\ : STD_LOGIC;
  signal \count_reg[12]_i_1_n_1\ : STD_LOGIC;
  signal \count_reg[12]_i_1_n_2\ : STD_LOGIC;
  signal \count_reg[12]_i_1_n_3\ : STD_LOGIC;
  signal \count_reg[12]_i_1_n_4\ : STD_LOGIC;
  signal \count_reg[12]_i_1_n_5\ : STD_LOGIC;
  signal \count_reg[12]_i_1_n_6\ : STD_LOGIC;
  signal \count_reg[12]_i_1_n_7\ : STD_LOGIC;
  signal \count_reg[16]_i_1_n_3\ : STD_LOGIC;
  signal \count_reg[16]_i_1_n_6\ : STD_LOGIC;
  signal \count_reg[16]_i_1_n_7\ : STD_LOGIC;
  signal \count_reg[4]_i_1_n_0\ : STD_LOGIC;
  signal \count_reg[4]_i_1_n_1\ : STD_LOGIC;
  signal \count_reg[4]_i_1_n_2\ : STD_LOGIC;
  signal \count_reg[4]_i_1_n_3\ : STD_LOGIC;
  signal \count_reg[4]_i_1_n_4\ : STD_LOGIC;
  signal \count_reg[4]_i_1_n_5\ : STD_LOGIC;
  signal \count_reg[4]_i_1_n_6\ : STD_LOGIC;
  signal \count_reg[4]_i_1_n_7\ : STD_LOGIC;
  signal \count_reg[8]_i_1_n_0\ : STD_LOGIC;
  signal \count_reg[8]_i_1_n_1\ : STD_LOGIC;
  signal \count_reg[8]_i_1_n_2\ : STD_LOGIC;
  signal \count_reg[8]_i_1_n_3\ : STD_LOGIC;
  signal \count_reg[8]_i_1_n_4\ : STD_LOGIC;
  signal \count_reg[8]_i_1_n_5\ : STD_LOGIC;
  signal \count_reg[8]_i_1_n_6\ : STD_LOGIC;
  signal \count_reg[8]_i_1_n_7\ : STD_LOGIC;
  signal \count_reg_n_0_[0]\ : STD_LOGIC;
  signal \count_reg_n_0_[10]\ : STD_LOGIC;
  signal \count_reg_n_0_[11]\ : STD_LOGIC;
  signal \count_reg_n_0_[12]\ : STD_LOGIC;
  signal \count_reg_n_0_[13]\ : STD_LOGIC;
  signal \count_reg_n_0_[14]\ : STD_LOGIC;
  signal \count_reg_n_0_[1]\ : STD_LOGIC;
  signal \count_reg_n_0_[2]\ : STD_LOGIC;
  signal \count_reg_n_0_[3]\ : STD_LOGIC;
  signal \count_reg_n_0_[4]\ : STD_LOGIC;
  signal \count_reg_n_0_[5]\ : STD_LOGIC;
  signal \count_reg_n_0_[6]\ : STD_LOGIC;
  signal \count_reg_n_0_[7]\ : STD_LOGIC;
  signal \count_reg_n_0_[8]\ : STD_LOGIC;
  signal \count_reg_n_0_[9]\ : STD_LOGIC;
  signal p_0_in : STD_LOGIC_VECTOR ( 2 downto 0 );
  signal seg0_INST_0_i_10_n_0 : STD_LOGIC;
  signal seg0_INST_0_i_11_n_0 : STD_LOGIC;
  signal seg0_INST_0_i_12_n_0 : STD_LOGIC;
  signal seg0_INST_0_i_5_n_0 : STD_LOGIC;
  signal seg0_INST_0_i_6_n_0 : STD_LOGIC;
  signal seg0_INST_0_i_7_n_0 : STD_LOGIC;
  signal seg0_INST_0_i_8_n_0 : STD_LOGIC;
  signal seg0_INST_0_i_9_n_0 : STD_LOGIC;
  signal sel0 : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal \NLW_count_reg[16]_i_1_CO_UNCONNECTED\ : STD_LOGIC_VECTOR ( 3 downto 1 );
  signal \NLW_count_reg[16]_i_1_O_UNCONNECTED\ : STD_LOGIC_VECTOR ( 3 downto 2 );
  attribute SOFT_HLUTNM : string;
  attribute SOFT_HLUTNM of \an[0]_INST_0\ : label is "soft_lutpair3";
  attribute SOFT_HLUTNM of \an[1]_INST_0\ : label is "soft_lutpair3";
  attribute SOFT_HLUTNM of \an[2]_INST_0\ : label is "soft_lutpair4";
  attribute SOFT_HLUTNM of \an[3]_INST_0\ : label is "soft_lutpair4";
  attribute SOFT_HLUTNM of \an[4]_INST_0\ : label is "soft_lutpair5";
  attribute SOFT_HLUTNM of \an[5]_INST_0\ : label is "soft_lutpair5";
  attribute SOFT_HLUTNM of \an[6]_INST_0\ : label is "soft_lutpair6";
  attribute SOFT_HLUTNM of \an[7]_INST_0\ : label is "soft_lutpair6";
  attribute ADDER_THRESHOLD : integer;
  attribute ADDER_THRESHOLD of \count_reg[0]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \count_reg[12]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \count_reg[16]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \count_reg[4]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \count_reg[8]_i_1\ : label is 11;
  attribute SOFT_HLUTNM of seg0_INST_0 : label is "soft_lutpair2";
  attribute SOFT_HLUTNM of seg2_INST_0 : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of seg3_INST_0 : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of seg4_INST_0 : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of seg5_INST_0 : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of seg6_INST_0 : label is "soft_lutpair2";
begin
\an[0]_INST_0\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"FE"
    )
        port map (
      I0 => p_0_in(1),
      I1 => p_0_in(2),
      I2 => p_0_in(0),
      O => an(0)
    );
\an[1]_INST_0\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"EF"
    )
        port map (
      I0 => p_0_in(1),
      I1 => p_0_in(2),
      I2 => p_0_in(0),
      O => an(1)
    );
\an[2]_INST_0\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"EF"
    )
        port map (
      I0 => p_0_in(2),
      I1 => p_0_in(0),
      I2 => p_0_in(1),
      O => an(2)
    );
\an[3]_INST_0\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"F7"
    )
        port map (
      I0 => p_0_in(1),
      I1 => p_0_in(0),
      I2 => p_0_in(2),
      O => an(3)
    );
\an[4]_INST_0\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"EF"
    )
        port map (
      I0 => p_0_in(1),
      I1 => p_0_in(0),
      I2 => p_0_in(2),
      O => an(4)
    );
\an[5]_INST_0\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"F7"
    )
        port map (
      I0 => p_0_in(2),
      I1 => p_0_in(0),
      I2 => p_0_in(1),
      O => an(5)
    );
\an[6]_INST_0\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"F7"
    )
        port map (
      I0 => p_0_in(1),
      I1 => p_0_in(2),
      I2 => p_0_in(0),
      O => an(6)
    );
\an[7]_INST_0\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"7F"
    )
        port map (
      I0 => p_0_in(2),
      I1 => p_0_in(0),
      I2 => p_0_in(1),
      O => an(7)
    );
\count[0]_i_2\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => \count_reg_n_0_[0]\,
      O => \count[0]_i_2_n_0\
    );
\count_reg[0]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[0]_i_1_n_7\,
      Q => \count_reg_n_0_[0]\
    );
\count_reg[0]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => '0',
      CO(3) => \count_reg[0]_i_1_n_0\,
      CO(2) => \count_reg[0]_i_1_n_1\,
      CO(1) => \count_reg[0]_i_1_n_2\,
      CO(0) => \count_reg[0]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0001",
      O(3) => \count_reg[0]_i_1_n_4\,
      O(2) => \count_reg[0]_i_1_n_5\,
      O(1) => \count_reg[0]_i_1_n_6\,
      O(0) => \count_reg[0]_i_1_n_7\,
      S(3) => \count_reg_n_0_[3]\,
      S(2) => \count_reg_n_0_[2]\,
      S(1) => \count_reg_n_0_[1]\,
      S(0) => \count[0]_i_2_n_0\
    );
\count_reg[10]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[8]_i_1_n_5\,
      Q => \count_reg_n_0_[10]\
    );
\count_reg[11]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[8]_i_1_n_4\,
      Q => \count_reg_n_0_[11]\
    );
\count_reg[12]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[12]_i_1_n_7\,
      Q => \count_reg_n_0_[12]\
    );
\count_reg[12]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \count_reg[8]_i_1_n_0\,
      CO(3) => \count_reg[12]_i_1_n_0\,
      CO(2) => \count_reg[12]_i_1_n_1\,
      CO(1) => \count_reg[12]_i_1_n_2\,
      CO(0) => \count_reg[12]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3) => \count_reg[12]_i_1_n_4\,
      O(2) => \count_reg[12]_i_1_n_5\,
      O(1) => \count_reg[12]_i_1_n_6\,
      O(0) => \count_reg[12]_i_1_n_7\,
      S(3) => p_0_in(0),
      S(2) => \count_reg_n_0_[14]\,
      S(1) => \count_reg_n_0_[13]\,
      S(0) => \count_reg_n_0_[12]\
    );
\count_reg[13]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[12]_i_1_n_6\,
      Q => \count_reg_n_0_[13]\
    );
\count_reg[14]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[12]_i_1_n_5\,
      Q => \count_reg_n_0_[14]\
    );
\count_reg[15]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[12]_i_1_n_4\,
      Q => p_0_in(0)
    );
\count_reg[16]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[16]_i_1_n_7\,
      Q => p_0_in(1)
    );
\count_reg[16]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \count_reg[12]_i_1_n_0\,
      CO(3 downto 1) => \NLW_count_reg[16]_i_1_CO_UNCONNECTED\(3 downto 1),
      CO(0) => \count_reg[16]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3 downto 2) => \NLW_count_reg[16]_i_1_O_UNCONNECTED\(3 downto 2),
      O(1) => \count_reg[16]_i_1_n_6\,
      O(0) => \count_reg[16]_i_1_n_7\,
      S(3 downto 2) => B"00",
      S(1 downto 0) => p_0_in(2 downto 1)
    );
\count_reg[17]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[16]_i_1_n_6\,
      Q => p_0_in(2)
    );
\count_reg[1]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[0]_i_1_n_6\,
      Q => \count_reg_n_0_[1]\
    );
\count_reg[2]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[0]_i_1_n_5\,
      Q => \count_reg_n_0_[2]\
    );
\count_reg[3]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[0]_i_1_n_4\,
      Q => \count_reg_n_0_[3]\
    );
\count_reg[4]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[4]_i_1_n_7\,
      Q => \count_reg_n_0_[4]\
    );
\count_reg[4]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \count_reg[0]_i_1_n_0\,
      CO(3) => \count_reg[4]_i_1_n_0\,
      CO(2) => \count_reg[4]_i_1_n_1\,
      CO(1) => \count_reg[4]_i_1_n_2\,
      CO(0) => \count_reg[4]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3) => \count_reg[4]_i_1_n_4\,
      O(2) => \count_reg[4]_i_1_n_5\,
      O(1) => \count_reg[4]_i_1_n_6\,
      O(0) => \count_reg[4]_i_1_n_7\,
      S(3) => \count_reg_n_0_[7]\,
      S(2) => \count_reg_n_0_[6]\,
      S(1) => \count_reg_n_0_[5]\,
      S(0) => \count_reg_n_0_[4]\
    );
\count_reg[5]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[4]_i_1_n_6\,
      Q => \count_reg_n_0_[5]\
    );
\count_reg[6]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[4]_i_1_n_5\,
      Q => \count_reg_n_0_[6]\
    );
\count_reg[7]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[4]_i_1_n_4\,
      Q => \count_reg_n_0_[7]\
    );
\count_reg[8]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[8]_i_1_n_7\,
      Q => \count_reg_n_0_[8]\
    );
\count_reg[8]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \count_reg[4]_i_1_n_0\,
      CO(3) => \count_reg[8]_i_1_n_0\,
      CO(2) => \count_reg[8]_i_1_n_1\,
      CO(1) => \count_reg[8]_i_1_n_2\,
      CO(0) => \count_reg[8]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3) => \count_reg[8]_i_1_n_4\,
      O(2) => \count_reg[8]_i_1_n_5\,
      O(1) => \count_reg[8]_i_1_n_6\,
      O(0) => \count_reg[8]_i_1_n_7\,
      S(3) => \count_reg_n_0_[11]\,
      S(2) => \count_reg_n_0_[10]\,
      S(1) => \count_reg_n_0_[9]\,
      S(0) => \count_reg_n_0_[8]\
    );
\count_reg[9]\: unisim.vcomponents.FDCE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      CLR => reset,
      D => \count_reg[8]_i_1_n_6\,
      Q => \count_reg_n_0_[9]\
    );
seg0_INST_0: unisim.vcomponents.LUT4
    generic map(
      INIT => X"2094"
    )
        port map (
      I0 => sel0(3),
      I1 => sel0(2),
      I2 => sel0(0),
      I3 => sel0(1),
      O => seg0
    );
seg0_INST_0_i_1: unisim.vcomponents.MUXF7
     port map (
      I0 => seg0_INST_0_i_5_n_0,
      I1 => seg0_INST_0_i_6_n_0,
      O => sel0(3),
      S => p_0_in(2)
    );
seg0_INST_0_i_10: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AFA0CFCFAFA0C0C0"
    )
        port map (
      I0 => in7(0),
      I1 => in6(0),
      I2 => p_0_in(1),
      I3 => in5(0),
      I4 => p_0_in(0),
      I5 => in4(0),
      O => seg0_INST_0_i_10_n_0
    );
seg0_INST_0_i_11: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AFA0CFCFAFA0C0C0"
    )
        port map (
      I0 => in3(1),
      I1 => in2(1),
      I2 => p_0_in(1),
      I3 => in1(1),
      I4 => p_0_in(0),
      I5 => in0(1),
      O => seg0_INST_0_i_11_n_0
    );
seg0_INST_0_i_12: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AFA0CFCFAFA0C0C0"
    )
        port map (
      I0 => in7(1),
      I1 => in6(1),
      I2 => p_0_in(1),
      I3 => in5(1),
      I4 => p_0_in(0),
      I5 => in4(1),
      O => seg0_INST_0_i_12_n_0
    );
seg0_INST_0_i_2: unisim.vcomponents.MUXF7
     port map (
      I0 => seg0_INST_0_i_7_n_0,
      I1 => seg0_INST_0_i_8_n_0,
      O => sel0(2),
      S => p_0_in(2)
    );
seg0_INST_0_i_3: unisim.vcomponents.MUXF7
     port map (
      I0 => seg0_INST_0_i_9_n_0,
      I1 => seg0_INST_0_i_10_n_0,
      O => sel0(0),
      S => p_0_in(2)
    );
seg0_INST_0_i_4: unisim.vcomponents.MUXF7
     port map (
      I0 => seg0_INST_0_i_11_n_0,
      I1 => seg0_INST_0_i_12_n_0,
      O => sel0(1),
      S => p_0_in(2)
    );
seg0_INST_0_i_5: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AFA0CFCFAFA0C0C0"
    )
        port map (
      I0 => in3(3),
      I1 => in2(3),
      I2 => p_0_in(1),
      I3 => in1(3),
      I4 => p_0_in(0),
      I5 => in0(3),
      O => seg0_INST_0_i_5_n_0
    );
seg0_INST_0_i_6: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AFA0CFCFAFA0C0C0"
    )
        port map (
      I0 => in7(3),
      I1 => in6(3),
      I2 => p_0_in(1),
      I3 => in5(3),
      I4 => p_0_in(0),
      I5 => in4(3),
      O => seg0_INST_0_i_6_n_0
    );
seg0_INST_0_i_7: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AFA0CFCFAFA0C0C0"
    )
        port map (
      I0 => in3(2),
      I1 => in2(2),
      I2 => p_0_in(1),
      I3 => in1(2),
      I4 => p_0_in(0),
      I5 => in0(2),
      O => seg0_INST_0_i_7_n_0
    );
seg0_INST_0_i_8: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AFA0CFCFAFA0C0C0"
    )
        port map (
      I0 => in7(2),
      I1 => in6(2),
      I2 => p_0_in(1),
      I3 => in5(2),
      I4 => p_0_in(0),
      I5 => in4(2),
      O => seg0_INST_0_i_8_n_0
    );
seg0_INST_0_i_9: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AFA0CFCFAFA0C0C0"
    )
        port map (
      I0 => in3(0),
      I1 => in2(0),
      I2 => p_0_in(1),
      I3 => in1(0),
      I4 => p_0_in(0),
      I5 => in0(0),
      O => seg0_INST_0_i_9_n_0
    );
seg1_INST_0: unisim.vcomponents.LUT4
    generic map(
      INIT => X"AC48"
    )
        port map (
      I0 => sel0(3),
      I1 => sel0(2),
      I2 => sel0(0),
      I3 => sel0(1),
      O => seg1
    );
seg2_INST_0: unisim.vcomponents.LUT4
    generic map(
      INIT => X"A210"
    )
        port map (
      I0 => sel0(3),
      I1 => sel0(0),
      I2 => sel0(1),
      I3 => sel0(2),
      O => seg2
    );
seg3_INST_0: unisim.vcomponents.LUT4
    generic map(
      INIT => X"C214"
    )
        port map (
      I0 => sel0(3),
      I1 => sel0(2),
      I2 => sel0(0),
      I3 => sel0(1),
      O => seg3
    );
seg4_INST_0: unisim.vcomponents.LUT4
    generic map(
      INIT => X"5710"
    )
        port map (
      I0 => sel0(3),
      I1 => sel0(1),
      I2 => sel0(2),
      I3 => sel0(0),
      O => seg4
    );
seg5_INST_0: unisim.vcomponents.LUT4
    generic map(
      INIT => X"5190"
    )
        port map (
      I0 => sel0(3),
      I1 => sel0(2),
      I2 => sel0(0),
      I3 => sel0(1),
      O => seg5
    );
seg6_INST_0: unisim.vcomponents.LUT4
    generic map(
      INIT => X"4025"
    )
        port map (
      I0 => sel0(3),
      I1 => sel0(0),
      I2 => sel0(2),
      I3 => sel0(1),
      O => seg6
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_DisplayController_0_0 is
  port (
    clk : in STD_LOGIC;
    reset : in STD_LOGIC;
    in0 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in1 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in2 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in3 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in4 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in5 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in6 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    in7 : in STD_LOGIC_VECTOR ( 3 downto 0 );
    seg0 : out STD_LOGIC;
    seg1 : out STD_LOGIC;
    seg2 : out STD_LOGIC;
    seg3 : out STD_LOGIC;
    seg4 : out STD_LOGIC;
    seg5 : out STD_LOGIC;
    seg6 : out STD_LOGIC;
    dp : out STD_LOGIC;
    an : out STD_LOGIC_VECTOR ( 7 downto 0 )
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of design_1_DisplayController_0_0 : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_DisplayController_0_0 : entity is "design_1_DisplayController_0_0,DisplayController,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_DisplayController_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_DisplayController_0_0 : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of design_1_DisplayController_0_0 : entity is "DisplayController,Vivado 2024.2";
end design_1_DisplayController_0_0;

architecture STRUCTURE of design_1_DisplayController_0_0 is
  signal \<const1>\ : STD_LOGIC;
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of clk : signal is "xilinx.com:signal:clock:1.0 clk CLK";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of clk : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of clk : signal is "XIL_INTERFACENAME clk, ASSOCIATED_RESET reset, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0";
  attribute X_INTERFACE_INFO of reset : signal is "xilinx.com:signal:reset:1.0 reset RST";
  attribute X_INTERFACE_MODE of reset : signal is "slave";
  attribute X_INTERFACE_PARAMETER of reset : signal is "XIL_INTERFACENAME reset, POLARITY ACTIVE_LOW, INSERT_VIP 0";
begin
  dp <= \<const1>\;
VCC: unisim.vcomponents.VCC
     port map (
      P => \<const1>\
    );
inst: entity work.design_1_DisplayController_0_0_DisplayController
     port map (
      an(7 downto 0) => an(7 downto 0),
      clk => clk,
      in0(3 downto 0) => in0(3 downto 0),
      in1(3 downto 0) => in1(3 downto 0),
      in2(3 downto 0) => in2(3 downto 0),
      in3(3 downto 0) => in3(3 downto 0),
      in4(3 downto 0) => in4(3 downto 0),
      in5(3 downto 0) => in5(3 downto 0),
      in6(3 downto 0) => in6(3 downto 0),
      in7(3 downto 0) => in7(3 downto 0),
      reset => reset,
      seg0 => seg0,
      seg1 => seg1,
      seg2 => seg2,
      seg3 => seg3,
      seg4 => seg4,
      seg5 => seg5,
      seg6 => seg6
    );
end STRUCTURE;
