-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Mon Mar 31 17:08:15 2025
-- Host        : mirai-note running 64-bit Arch Linux
-- Command     : write_vhdl -force -mode funcsim
--               /home/mirai/Documentos/Projects/projeto_marco/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_temp_catcher_0_0/design_1_temp_catcher_0_0_sim_netlist.vhdl
-- Design      : design_1_temp_catcher_0_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_temp_catcher_0_0_temp_catcher is
  port (
    den : out STD_LOGIC;
    reset_0 : out STD_LOGIC;
    daddr : out STD_LOGIC_VECTOR ( 0 to 0 );
    \FSM_sequential_state_reg[1]_0\ : out STD_LOGIC;
    drdy_0 : out STD_LOGIC;
    temp : out STD_LOGIC_VECTOR ( 19 downto 0 );
    \FSM_sequential_state_reg[0]_0\ : out STD_LOGIC;
    placeholder : out STD_LOGIC;
    clk : in STD_LOGIC;
    reset : in STD_LOGIC;
    drdy : in STD_LOGIC;
    \temp[16]_INST_0_i_6\ : in STD_LOGIC;
    \vccint[11]_INST_0_i_1\ : in STD_LOGIC;
    P : in STD_LOGIC_VECTOR ( 18 downto 0 )
  );
  attribute ORIG_REF_NAME : string;
  attribute ORIG_REF_NAME of design_1_temp_catcher_0_0_temp_catcher : entity is "temp_catcher";
end design_1_temp_catcher_0_0_temp_catcher;

architecture STRUCTURE of design_1_temp_catcher_0_0_temp_catcher is
  signal \FSM_sequential_state[0]_i_1_n_0\ : STD_LOGIC;
  signal \FSM_sequential_state[0]_i_2_n_0\ : STD_LOGIC;
  signal \FSM_sequential_state[1]_i_1_n_0\ : STD_LOGIC;
  signal \FSM_sequential_state_reg_n_0_[1]\ : STD_LOGIC;
  signal \^daddr\ : STD_LOGIC_VECTOR ( 0 to 0 );
  signal \daddr[0]_i_1_n_0\ : STD_LOGIC;
  signal den_i_1_n_0 : STD_LOGIC;
  signal \^reset_0\ : STD_LOGIC;
  signal sel0 : STD_LOGIC_VECTOR ( 6 downto 0 );
  signal state : STD_LOGIC_VECTOR ( 0 to 0 );
  signal \temp[0]_INST_0_i_1_n_0\ : STD_LOGIC;
  signal \temp[0]_INST_0_i_2_n_0\ : STD_LOGIC;
  signal \temp[0]_INST_0_i_3_n_0\ : STD_LOGIC;
  signal \temp[0]_INST_0_i_4_n_0\ : STD_LOGIC;
  signal \temp[0]_INST_0_i_5_n_0\ : STD_LOGIC;
  signal \temp[0]_INST_0_n_0\ : STD_LOGIC;
  signal \temp[0]_INST_0_n_1\ : STD_LOGIC;
  signal \temp[0]_INST_0_n_2\ : STD_LOGIC;
  signal \temp[0]_INST_0_n_3\ : STD_LOGIC;
  signal \temp[12]_INST_0_i_1_n_0\ : STD_LOGIC;
  signal \temp[12]_INST_0_i_2_n_0\ : STD_LOGIC;
  signal \temp[12]_INST_0_i_3_n_0\ : STD_LOGIC;
  signal \temp[12]_INST_0_i_4_n_0\ : STD_LOGIC;
  signal \temp[12]_INST_0_i_5_n_0\ : STD_LOGIC;
  signal \temp[12]_INST_0_i_6_n_0\ : STD_LOGIC;
  signal \temp[12]_INST_0_i_7_n_0\ : STD_LOGIC;
  signal \temp[12]_INST_0_n_0\ : STD_LOGIC;
  signal \temp[12]_INST_0_n_1\ : STD_LOGIC;
  signal \temp[12]_INST_0_n_2\ : STD_LOGIC;
  signal \temp[12]_INST_0_n_3\ : STD_LOGIC;
  signal \temp[16]_INST_0_i_1_n_0\ : STD_LOGIC;
  signal \temp[16]_INST_0_i_2_n_0\ : STD_LOGIC;
  signal \temp[16]_INST_0_i_3_n_0\ : STD_LOGIC;
  signal \temp[16]_INST_0_i_4_n_0\ : STD_LOGIC;
  signal \temp[16]_INST_0_i_5_n_0\ : STD_LOGIC;
  signal \temp[16]_INST_0_n_1\ : STD_LOGIC;
  signal \temp[16]_INST_0_n_2\ : STD_LOGIC;
  signal \temp[16]_INST_0_n_3\ : STD_LOGIC;
  signal \temp[4]_INST_0_i_1_n_0\ : STD_LOGIC;
  signal \temp[4]_INST_0_i_2_n_0\ : STD_LOGIC;
  signal \temp[4]_INST_0_i_3_n_0\ : STD_LOGIC;
  signal \temp[4]_INST_0_i_4_n_0\ : STD_LOGIC;
  signal \temp[4]_INST_0_n_0\ : STD_LOGIC;
  signal \temp[4]_INST_0_n_1\ : STD_LOGIC;
  signal \temp[4]_INST_0_n_2\ : STD_LOGIC;
  signal \temp[4]_INST_0_n_3\ : STD_LOGIC;
  signal \temp[8]_INST_0_i_1_n_0\ : STD_LOGIC;
  signal \temp[8]_INST_0_i_2_n_0\ : STD_LOGIC;
  signal \temp[8]_INST_0_i_3_n_0\ : STD_LOGIC;
  signal \temp[8]_INST_0_i_4_n_0\ : STD_LOGIC;
  signal \temp[8]_INST_0_i_5_n_0\ : STD_LOGIC;
  signal \temp[8]_INST_0_i_6_n_0\ : STD_LOGIC;
  signal \temp[8]_INST_0_n_0\ : STD_LOGIC;
  signal \temp[8]_INST_0_n_1\ : STD_LOGIC;
  signal \temp[8]_INST_0_n_2\ : STD_LOGIC;
  signal \temp[8]_INST_0_n_3\ : STD_LOGIC;
  signal timeout : STD_LOGIC_VECTOR ( 5 downto 0 );
  signal \timeout[5]_i_1_n_0\ : STD_LOGIC;
  signal \timeout[5]_i_3_n_0\ : STD_LOGIC;
  signal \timeout[6]_i_1_n_0\ : STD_LOGIC;
  signal \NLW_temp[16]_INST_0_CO_UNCONNECTED\ : STD_LOGIC_VECTOR ( 3 to 3 );
  attribute SOFT_HLUTNM : string;
  attribute SOFT_HLUTNM of \FSM_sequential_state[0]_i_1\ : label is "soft_lutpair2";
  attribute SOFT_HLUTNM of \FSM_sequential_state[1]_i_1\ : label is "soft_lutpair3";
  attribute FSM_ENCODED_STATES : string;
  attribute FSM_ENCODED_STATES of \FSM_sequential_state_reg[0]\ : label is "GET_TEMP:01,GET_VCC:11,ASK_VCC:10,ASK_TEMP:00";
  attribute FSM_ENCODED_STATES of \FSM_sequential_state_reg[1]\ : label is "GET_TEMP:01,GET_VCC:11,ASK_VCC:10,ASK_TEMP:00";
  attribute SOFT_HLUTNM of \daddr[0]_i_1\ : label is "soft_lutpair3";
  attribute SOFT_HLUTNM of \temp[16]_INST_0_i_7\ : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of \timeout[1]_i_1\ : label is "soft_lutpair4";
  attribute SOFT_HLUTNM of \timeout[2]_i_1\ : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of \timeout[3]_i_1\ : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of \timeout[5]_i_2\ : label is "soft_lutpair4";
  attribute SOFT_HLUTNM of \timeout[6]_i_1\ : label is "soft_lutpair2";
  attribute SOFT_HLUTNM of \vccint[11]_INST_0_i_2\ : label is "soft_lutpair1";
begin
  daddr(0) <= \^daddr\(0);
  reset_0 <= \^reset_0\;
\FSM_sequential_state[0]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"0BFF"
    )
        port map (
      I0 => \FSM_sequential_state[0]_i_2_n_0\,
      I1 => sel0(6),
      I2 => drdy,
      I3 => state(0),
      O => \FSM_sequential_state[0]_i_1_n_0\
    );
\FSM_sequential_state[0]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"7FFFFFFFFFFFFFFF"
    )
        port map (
      I0 => sel0(4),
      I1 => sel0(2),
      I2 => sel0(0),
      I3 => sel0(1),
      I4 => sel0(3),
      I5 => sel0(5),
      O => \FSM_sequential_state[0]_i_2_n_0\
    );
\FSM_sequential_state[1]_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"78"
    )
        port map (
      I0 => state(0),
      I1 => drdy,
      I2 => \FSM_sequential_state_reg_n_0_[1]\,
      O => \FSM_sequential_state[1]_i_1_n_0\
    );
\FSM_sequential_state_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => \^reset_0\,
      D => \FSM_sequential_state[0]_i_1_n_0\,
      Q => state(0)
    );
\FSM_sequential_state_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => \^reset_0\,
      D => \FSM_sequential_state[1]_i_1_n_0\,
      Q => \FSM_sequential_state_reg_n_0_[1]\
    );
\daddr[0]_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"B8"
    )
        port map (
      I0 => \^daddr\(0),
      I1 => state(0),
      I2 => \FSM_sequential_state_reg_n_0_[1]\,
      O => \daddr[0]_i_1_n_0\
    );
\daddr[0]_i_2\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => reset,
      O => \^reset_0\
    );
\daddr_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => \^reset_0\,
      D => \daddr[0]_i_1_n_0\,
      Q => \^daddr\(0)
    );
den_i_1: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => state(0),
      O => den_i_1_n_0
    );
den_reg: unisim.vcomponents.FDPE
     port map (
      C => clk,
      CE => '1',
      D => den_i_1_n_0,
      PRE => \^reset_0\,
      Q => den
    );
\p_0_out__0_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"80"
    )
        port map (
      I0 => \FSM_sequential_state_reg_n_0_[1]\,
      I1 => state(0),
      I2 => drdy,
      O => placeholder
    );
p_0_out_i_1: unisim.vcomponents.LUT3
    generic map(
      INIT => X"08"
    )
        port map (
      I0 => state(0),
      I1 => drdy,
      I2 => \FSM_sequential_state_reg_n_0_[1]\,
      O => \FSM_sequential_state_reg[0]_0\
    );
\temp[0]_INST_0\: unisim.vcomponents.CARRY4
     port map (
      CI => '0',
      CO(3) => \temp[0]_INST_0_n_0\,
      CO(2) => \temp[0]_INST_0_n_1\,
      CO(1) => \temp[0]_INST_0_n_2\,
      CO(0) => \temp[0]_INST_0_n_3\,
      CYINIT => '0',
      DI(3 downto 2) => B"00",
      DI(1) => \temp[0]_INST_0_i_1_n_0\,
      DI(0) => '0',
      O(3 downto 0) => temp(3 downto 0),
      S(3) => \temp[0]_INST_0_i_2_n_0\,
      S(2) => \temp[0]_INST_0_i_3_n_0\,
      S(1) => \temp[0]_INST_0_i_4_n_0\,
      S(0) => \temp[0]_INST_0_i_5_n_0\
    );
\temp[0]_INST_0_i_1\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(1),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[0]_INST_0_i_1_n_0\
    );
\temp[0]_INST_0_i_2\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(3),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[0]_INST_0_i_2_n_0\
    );
\temp[0]_INST_0_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(2),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[0]_INST_0_i_3_n_0\
    );
\temp[0]_INST_0_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"7"
    )
        port map (
      I0 => \temp[16]_INST_0_i_6\,
      I1 => P(1),
      O => \temp[0]_INST_0_i_4_n_0\
    );
\temp[0]_INST_0_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(0),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[0]_INST_0_i_5_n_0\
    );
\temp[12]_INST_0\: unisim.vcomponents.CARRY4
     port map (
      CI => \temp[8]_INST_0_n_0\,
      CO(3) => \temp[12]_INST_0_n_0\,
      CO(2) => \temp[12]_INST_0_n_1\,
      CO(1) => \temp[12]_INST_0_n_2\,
      CO(0) => \temp[12]_INST_0_n_3\,
      CYINIT => '0',
      DI(3) => \temp[12]_INST_0_i_1_n_0\,
      DI(2) => \temp[12]_INST_0_i_2_n_0\,
      DI(1) => '0',
      DI(0) => \temp[12]_INST_0_i_3_n_0\,
      O(3 downto 0) => temp(15 downto 12),
      S(3) => \temp[12]_INST_0_i_4_n_0\,
      S(2) => \temp[12]_INST_0_i_5_n_0\,
      S(1) => \temp[12]_INST_0_i_6_n_0\,
      S(0) => \temp[12]_INST_0_i_7_n_0\
    );
\temp[12]_INST_0_i_1\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(15),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[12]_INST_0_i_1_n_0\
    );
\temp[12]_INST_0_i_2\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(14),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[12]_INST_0_i_2_n_0\
    );
\temp[12]_INST_0_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(12),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[12]_INST_0_i_3_n_0\
    );
\temp[12]_INST_0_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"7"
    )
        port map (
      I0 => \temp[16]_INST_0_i_6\,
      I1 => P(15),
      O => \temp[12]_INST_0_i_4_n_0\
    );
\temp[12]_INST_0_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"7"
    )
        port map (
      I0 => \temp[16]_INST_0_i_6\,
      I1 => P(14),
      O => \temp[12]_INST_0_i_5_n_0\
    );
\temp[12]_INST_0_i_6\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(13),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[12]_INST_0_i_6_n_0\
    );
\temp[12]_INST_0_i_7\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"7"
    )
        port map (
      I0 => \temp[16]_INST_0_i_6\,
      I1 => P(12),
      O => \temp[12]_INST_0_i_7_n_0\
    );
\temp[16]_INST_0\: unisim.vcomponents.CARRY4
     port map (
      CI => \temp[12]_INST_0_n_0\,
      CO(3) => \NLW_temp[16]_INST_0_CO_UNCONNECTED\(3),
      CO(2) => \temp[16]_INST_0_n_1\,
      CO(1) => \temp[16]_INST_0_n_2\,
      CO(0) => \temp[16]_INST_0_n_3\,
      CYINIT => '0',
      DI(3 downto 2) => B"00",
      DI(1) => \temp[16]_INST_0_i_1_n_0\,
      DI(0) => \temp[16]_INST_0_i_2_n_0\,
      O(3 downto 0) => temp(19 downto 16),
      S(3) => '1',
      S(2) => \temp[16]_INST_0_i_3_n_0\,
      S(1) => \temp[16]_INST_0_i_4_n_0\,
      S(0) => \temp[16]_INST_0_i_5_n_0\
    );
\temp[16]_INST_0_i_1\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(17),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[16]_INST_0_i_1_n_0\
    );
\temp[16]_INST_0_i_2\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(16),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[16]_INST_0_i_2_n_0\
    );
\temp[16]_INST_0_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(18),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[16]_INST_0_i_3_n_0\
    );
\temp[16]_INST_0_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"7"
    )
        port map (
      I0 => \temp[16]_INST_0_i_6\,
      I1 => P(17),
      O => \temp[16]_INST_0_i_4_n_0\
    );
\temp[16]_INST_0_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"7"
    )
        port map (
      I0 => \temp[16]_INST_0_i_6\,
      I1 => P(16),
      O => \temp[16]_INST_0_i_5_n_0\
    );
\temp[16]_INST_0_i_7\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"FF40"
    )
        port map (
      I0 => \FSM_sequential_state_reg_n_0_[1]\,
      I1 => drdy,
      I2 => state(0),
      I3 => \temp[16]_INST_0_i_6\,
      O => \FSM_sequential_state_reg[1]_0\
    );
\temp[4]_INST_0\: unisim.vcomponents.CARRY4
     port map (
      CI => \temp[0]_INST_0_n_0\,
      CO(3) => \temp[4]_INST_0_n_0\,
      CO(2) => \temp[4]_INST_0_n_1\,
      CO(1) => \temp[4]_INST_0_n_2\,
      CO(0) => \temp[4]_INST_0_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3 downto 0) => temp(7 downto 4),
      S(3) => \temp[4]_INST_0_i_1_n_0\,
      S(2) => \temp[4]_INST_0_i_2_n_0\,
      S(1) => \temp[4]_INST_0_i_3_n_0\,
      S(0) => \temp[4]_INST_0_i_4_n_0\
    );
\temp[4]_INST_0_i_1\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(7),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[4]_INST_0_i_1_n_0\
    );
\temp[4]_INST_0_i_2\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(6),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[4]_INST_0_i_2_n_0\
    );
\temp[4]_INST_0_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(5),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[4]_INST_0_i_3_n_0\
    );
\temp[4]_INST_0_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(4),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[4]_INST_0_i_4_n_0\
    );
\temp[8]_INST_0\: unisim.vcomponents.CARRY4
     port map (
      CI => \temp[4]_INST_0_n_0\,
      CO(3) => \temp[8]_INST_0_n_0\,
      CO(2) => \temp[8]_INST_0_n_1\,
      CO(1) => \temp[8]_INST_0_n_2\,
      CO(0) => \temp[8]_INST_0_n_3\,
      CYINIT => '0',
      DI(3) => '0',
      DI(2) => \temp[8]_INST_0_i_1_n_0\,
      DI(1) => '0',
      DI(0) => \temp[8]_INST_0_i_2_n_0\,
      O(3 downto 0) => temp(11 downto 8),
      S(3) => \temp[8]_INST_0_i_3_n_0\,
      S(2) => \temp[8]_INST_0_i_4_n_0\,
      S(1) => \temp[8]_INST_0_i_5_n_0\,
      S(0) => \temp[8]_INST_0_i_6_n_0\
    );
\temp[8]_INST_0_i_1\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(10),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[8]_INST_0_i_1_n_0\
    );
\temp[8]_INST_0_i_2\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(8),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[8]_INST_0_i_2_n_0\
    );
\temp[8]_INST_0_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(11),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[8]_INST_0_i_3_n_0\
    );
\temp[8]_INST_0_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"7"
    )
        port map (
      I0 => \temp[16]_INST_0_i_6\,
      I1 => P(10),
      O => \temp[8]_INST_0_i_4_n_0\
    );
\temp[8]_INST_0_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => P(9),
      I1 => \temp[16]_INST_0_i_6\,
      O => \temp[8]_INST_0_i_5_n_0\
    );
\temp[8]_INST_0_i_6\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"7"
    )
        port map (
      I0 => \temp[16]_INST_0_i_6\,
      I1 => P(8),
      O => \temp[8]_INST_0_i_6_n_0\
    );
\timeout[0]_i_1\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => state(0),
      I1 => sel0(0),
      O => timeout(0)
    );
\timeout[1]_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"48"
    )
        port map (
      I0 => sel0(0),
      I1 => state(0),
      I2 => sel0(1),
      O => timeout(1)
    );
\timeout[2]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"7080"
    )
        port map (
      I0 => sel0(0),
      I1 => sel0(1),
      I2 => state(0),
      I3 => sel0(2),
      O => timeout(2)
    );
\timeout[3]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"7F008000"
    )
        port map (
      I0 => sel0(1),
      I1 => sel0(0),
      I2 => sel0(2),
      I3 => state(0),
      I4 => sel0(3),
      O => timeout(3)
    );
\timeout[4]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"7FFF000080000000"
    )
        port map (
      I0 => sel0(2),
      I1 => sel0(0),
      I2 => sel0(1),
      I3 => sel0(3),
      I4 => state(0),
      I5 => sel0(4),
      O => timeout(4)
    );
\timeout[5]_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"DF"
    )
        port map (
      I0 => sel0(6),
      I1 => \FSM_sequential_state[0]_i_2_n_0\,
      I2 => state(0),
      O => \timeout[5]_i_1_n_0\
    );
\timeout[5]_i_2\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"84"
    )
        port map (
      I0 => \timeout[5]_i_3_n_0\,
      I1 => state(0),
      I2 => sel0(5),
      O => timeout(5)
    );
\timeout[5]_i_3\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"7FFFFFFF"
    )
        port map (
      I0 => sel0(3),
      I1 => sel0(1),
      I2 => sel0(0),
      I3 => sel0(2),
      I4 => sel0(4),
      O => \timeout[5]_i_3_n_0\
    );
\timeout[6]_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"B0"
    )
        port map (
      I0 => sel0(6),
      I1 => \FSM_sequential_state[0]_i_2_n_0\,
      I2 => state(0),
      O => \timeout[6]_i_1_n_0\
    );
\timeout_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \timeout[5]_i_1_n_0\,
      CLR => \^reset_0\,
      D => timeout(0),
      Q => sel0(0)
    );
\timeout_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \timeout[5]_i_1_n_0\,
      CLR => \^reset_0\,
      D => timeout(1),
      Q => sel0(1)
    );
\timeout_reg[2]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \timeout[5]_i_1_n_0\,
      CLR => \^reset_0\,
      D => timeout(2),
      Q => sel0(2)
    );
\timeout_reg[3]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \timeout[5]_i_1_n_0\,
      CLR => \^reset_0\,
      D => timeout(3),
      Q => sel0(3)
    );
\timeout_reg[4]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \timeout[5]_i_1_n_0\,
      CLR => \^reset_0\,
      D => timeout(4),
      Q => sel0(4)
    );
\timeout_reg[5]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \timeout[5]_i_1_n_0\,
      CLR => \^reset_0\,
      D => timeout(5),
      Q => sel0(5)
    );
\timeout_reg[6]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => \^reset_0\,
      D => \timeout[6]_i_1_n_0\,
      Q => sel0(6)
    );
\vccint[11]_INST_0_i_2\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"FF80"
    )
        port map (
      I0 => drdy,
      I1 => state(0),
      I2 => \FSM_sequential_state_reg_n_0_[1]\,
      I3 => \vccint[11]_INST_0_i_1\,
      O => drdy_0
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_temp_catcher_0_0 is
  port (
    clk : in STD_LOGIC;
    reset : in STD_LOGIC;
    drdy : in STD_LOGIC;
    do_data : in STD_LOGIC_VECTOR ( 15 downto 0 );
    daddr : out STD_LOGIC_VECTOR ( 6 downto 0 );
    den : out STD_LOGIC;
    temp : out STD_LOGIC_VECTOR ( 20 downto 0 );
    vccint : out STD_LOGIC_VECTOR ( 20 downto 0 )
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of design_1_temp_catcher_0_0 : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_temp_catcher_0_0 : entity is "design_1_temp_catcher_0_0,temp_catcher,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_temp_catcher_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_temp_catcher_0_0 : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of design_1_temp_catcher_0_0 : entity is "temp_catcher,Vivado 2024.2";
end design_1_temp_catcher_0_0;

architecture STRUCTURE of design_1_temp_catcher_0_0 is
  signal \<const0>\ : STD_LOGIC;
  signal \^daddr\ : STD_LOGIC_VECTOR ( 0 to 0 );
  signal inst_n_1 : STD_LOGIC;
  signal inst_n_25 : STD_LOGIC;
  signal inst_n_3 : STD_LOGIC;
  signal inst_n_4 : STD_LOGIC;
  signal \p_0_out__0_n_100\ : STD_LOGIC;
  signal \p_0_out__0_n_101\ : STD_LOGIC;
  signal \p_0_out__0_n_102\ : STD_LOGIC;
  signal \p_0_out__0_n_103\ : STD_LOGIC;
  signal \p_0_out__0_n_104\ : STD_LOGIC;
  signal \p_0_out__0_n_105\ : STD_LOGIC;
  signal \p_0_out__0_n_82\ : STD_LOGIC;
  signal \p_0_out__0_n_83\ : STD_LOGIC;
  signal \p_0_out__0_n_84\ : STD_LOGIC;
  signal \p_0_out__0_n_85\ : STD_LOGIC;
  signal \p_0_out__0_n_86\ : STD_LOGIC;
  signal \p_0_out__0_n_87\ : STD_LOGIC;
  signal \p_0_out__0_n_88\ : STD_LOGIC;
  signal \p_0_out__0_n_89\ : STD_LOGIC;
  signal \p_0_out__0_n_90\ : STD_LOGIC;
  signal \p_0_out__0_n_91\ : STD_LOGIC;
  signal \p_0_out__0_n_92\ : STD_LOGIC;
  signal \p_0_out__0_n_93\ : STD_LOGIC;
  signal \p_0_out__0_n_94\ : STD_LOGIC;
  signal \p_0_out__0_n_95\ : STD_LOGIC;
  signal \p_0_out__0_n_96\ : STD_LOGIC;
  signal \p_0_out__0_n_97\ : STD_LOGIC;
  signal \p_0_out__0_n_98\ : STD_LOGIC;
  signal \p_0_out__0_n_99\ : STD_LOGIC;
  signal \p_0_out__1\ : STD_LOGIC_VECTOR ( 30 downto 12 );
  signal p_0_out_n_100 : STD_LOGIC;
  signal p_0_out_n_101 : STD_LOGIC;
  signal p_0_out_n_102 : STD_LOGIC;
  signal p_0_out_n_103 : STD_LOGIC;
  signal p_0_out_n_104 : STD_LOGIC;
  signal p_0_out_n_105 : STD_LOGIC;
  signal p_0_out_n_94 : STD_LOGIC;
  signal p_0_out_n_95 : STD_LOGIC;
  signal p_0_out_n_96 : STD_LOGIC;
  signal p_0_out_n_97 : STD_LOGIC;
  signal p_0_out_n_98 : STD_LOGIC;
  signal p_0_out_n_99 : STD_LOGIC;
  signal placeholder : STD_LOGIC;
  signal \^temp\ : STD_LOGIC_VECTOR ( 20 downto 0 );
  signal \temp[16]_INST_0_i_6_n_0\ : STD_LOGIC;
  signal \^vccint\ : STD_LOGIC_VECTOR ( 11 downto 0 );
  signal \vccint[11]_INST_0_i_1_n_0\ : STD_LOGIC;
  signal NLW_p_0_out_CARRYCASCOUT_UNCONNECTED : STD_LOGIC;
  signal NLW_p_0_out_MULTSIGNOUT_UNCONNECTED : STD_LOGIC;
  signal NLW_p_0_out_OVERFLOW_UNCONNECTED : STD_LOGIC;
  signal NLW_p_0_out_PATTERNBDETECT_UNCONNECTED : STD_LOGIC;
  signal NLW_p_0_out_PATTERNDETECT_UNCONNECTED : STD_LOGIC;
  signal NLW_p_0_out_UNDERFLOW_UNCONNECTED : STD_LOGIC;
  signal NLW_p_0_out_ACOUT_UNCONNECTED : STD_LOGIC_VECTOR ( 29 downto 0 );
  signal NLW_p_0_out_BCOUT_UNCONNECTED : STD_LOGIC_VECTOR ( 17 downto 0 );
  signal NLW_p_0_out_CARRYOUT_UNCONNECTED : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal NLW_p_0_out_P_UNCONNECTED : STD_LOGIC_VECTOR ( 47 downto 31 );
  signal NLW_p_0_out_PCOUT_UNCONNECTED : STD_LOGIC_VECTOR ( 47 downto 0 );
  signal \NLW_p_0_out__0_CARRYCASCOUT_UNCONNECTED\ : STD_LOGIC;
  signal \NLW_p_0_out__0_MULTSIGNOUT_UNCONNECTED\ : STD_LOGIC;
  signal \NLW_p_0_out__0_OVERFLOW_UNCONNECTED\ : STD_LOGIC;
  signal \NLW_p_0_out__0_PATTERNBDETECT_UNCONNECTED\ : STD_LOGIC;
  signal \NLW_p_0_out__0_PATTERNDETECT_UNCONNECTED\ : STD_LOGIC;
  signal \NLW_p_0_out__0_UNDERFLOW_UNCONNECTED\ : STD_LOGIC;
  signal \NLW_p_0_out__0_ACOUT_UNCONNECTED\ : STD_LOGIC_VECTOR ( 29 downto 0 );
  signal \NLW_p_0_out__0_BCOUT_UNCONNECTED\ : STD_LOGIC_VECTOR ( 17 downto 0 );
  signal \NLW_p_0_out__0_CARRYOUT_UNCONNECTED\ : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal \NLW_p_0_out__0_P_UNCONNECTED\ : STD_LOGIC_VECTOR ( 47 downto 24 );
  signal \NLW_p_0_out__0_PCOUT_UNCONNECTED\ : STD_LOGIC_VECTOR ( 47 downto 0 );
  attribute METHODOLOGY_DRC_VIOS : string;
  attribute METHODOLOGY_DRC_VIOS of p_0_out : label is "{SYNTH-12 {cell *THIS*}}";
  attribute METHODOLOGY_DRC_VIOS of \p_0_out__0\ : label is "{SYNTH-12 {cell *THIS*}}";
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
  daddr(6) <= \<const0>\;
  daddr(5) <= \<const0>\;
  daddr(4) <= \<const0>\;
  daddr(3) <= \<const0>\;
  daddr(2) <= \<const0>\;
  daddr(1) <= \<const0>\;
  daddr(0) <= \^daddr\(0);
  temp(20) <= \^temp\(20);
  temp(19) <= \^temp\(20);
  temp(18 downto 0) <= \^temp\(18 downto 0);
  vccint(20) <= \<const0>\;
  vccint(19) <= \<const0>\;
  vccint(18) <= \<const0>\;
  vccint(17) <= \<const0>\;
  vccint(16) <= \<const0>\;
  vccint(15) <= \<const0>\;
  vccint(14) <= \<const0>\;
  vccint(13) <= \<const0>\;
  vccint(12) <= \<const0>\;
  vccint(11 downto 0) <= \^vccint\(11 downto 0);
GND: unisim.vcomponents.GND
     port map (
      G => \<const0>\
    );
inst: entity work.design_1_temp_catcher_0_0_temp_catcher
     port map (
      \FSM_sequential_state_reg[0]_0\ => inst_n_25,
      \FSM_sequential_state_reg[1]_0\ => inst_n_3,
      P(18 downto 0) => \p_0_out__1\(30 downto 12),
      clk => clk,
      daddr(0) => \^daddr\(0),
      den => den,
      drdy => drdy,
      drdy_0 => inst_n_4,
      placeholder => placeholder,
      reset => reset,
      reset_0 => inst_n_1,
      temp(19) => \^temp\(20),
      temp(18 downto 0) => \^temp\(18 downto 0),
      \temp[16]_INST_0_i_6\ => \temp[16]_INST_0_i_6_n_0\,
      \vccint[11]_INST_0_i_1\ => \vccint[11]_INST_0_i_1_n_0\
    );
p_0_out: unisim.vcomponents.DSP48E1
    generic map(
      ACASCREG => 0,
      ADREG => 1,
      ALUMODEREG => 0,
      AREG => 0,
      AUTORESET_PATDET => "NO_RESET",
      A_INPUT => "DIRECT",
      BCASCREG => 0,
      BREG => 0,
      B_INPUT => "DIRECT",
      CARRYINREG => 0,
      CARRYINSELREG => 0,
      CREG => 1,
      DREG => 1,
      INMODEREG => 0,
      MASK => X"3FFFFFFFFFFF",
      MREG => 0,
      OPMODEREG => 0,
      PATTERN => X"000000000000",
      PREG => 1,
      SEL_MASK => "MASK",
      SEL_PATTERN => "PATTERN",
      USE_DPORT => false,
      USE_MULT => "MULTIPLY",
      USE_PATTERN_DETECT => "NO_PATDET",
      USE_SIMD => "ONE48"
    )
        port map (
      A(29 downto 0) => B"000000000001111011000010100111",
      ACIN(29 downto 0) => B"000000000000000000000000000000",
      ACOUT(29 downto 0) => NLW_p_0_out_ACOUT_UNCONNECTED(29 downto 0),
      ALUMODE(3 downto 0) => B"0000",
      B(17 downto 12) => B"000000",
      B(11 downto 0) => do_data(15 downto 4),
      BCIN(17 downto 0) => B"000000000000000000",
      BCOUT(17 downto 0) => NLW_p_0_out_BCOUT_UNCONNECTED(17 downto 0),
      C(47 downto 0) => B"111111111111111111111111111111111111111111111111",
      CARRYCASCIN => '0',
      CARRYCASCOUT => NLW_p_0_out_CARRYCASCOUT_UNCONNECTED,
      CARRYIN => '0',
      CARRYINSEL(2 downto 0) => B"000",
      CARRYOUT(3 downto 0) => NLW_p_0_out_CARRYOUT_UNCONNECTED(3 downto 0),
      CEA1 => '0',
      CEA2 => '0',
      CEAD => '0',
      CEALUMODE => '0',
      CEB1 => '0',
      CEB2 => '0',
      CEC => '0',
      CECARRYIN => '0',
      CECTRL => '0',
      CED => '0',
      CEINMODE => '0',
      CEM => '0',
      CEP => inst_n_25,
      CLK => clk,
      D(24 downto 0) => B"0000000000000000000000000",
      INMODE(4 downto 0) => B"00000",
      MULTSIGNIN => '0',
      MULTSIGNOUT => NLW_p_0_out_MULTSIGNOUT_UNCONNECTED,
      OPMODE(6 downto 0) => B"0000101",
      OVERFLOW => NLW_p_0_out_OVERFLOW_UNCONNECTED,
      P(47 downto 31) => NLW_p_0_out_P_UNCONNECTED(47 downto 31),
      P(30 downto 12) => \p_0_out__1\(30 downto 12),
      P(11) => p_0_out_n_94,
      P(10) => p_0_out_n_95,
      P(9) => p_0_out_n_96,
      P(8) => p_0_out_n_97,
      P(7) => p_0_out_n_98,
      P(6) => p_0_out_n_99,
      P(5) => p_0_out_n_100,
      P(4) => p_0_out_n_101,
      P(3) => p_0_out_n_102,
      P(2) => p_0_out_n_103,
      P(1) => p_0_out_n_104,
      P(0) => p_0_out_n_105,
      PATTERNBDETECT => NLW_p_0_out_PATTERNBDETECT_UNCONNECTED,
      PATTERNDETECT => NLW_p_0_out_PATTERNDETECT_UNCONNECTED,
      PCIN(47 downto 0) => B"000000000000000000000000000000000000000000000000",
      PCOUT(47 downto 0) => NLW_p_0_out_PCOUT_UNCONNECTED(47 downto 0),
      RSTA => '0',
      RSTALLCARRYIN => '0',
      RSTALUMODE => '0',
      RSTB => '0',
      RSTC => '0',
      RSTCTRL => '0',
      RSTD => '0',
      RSTINMODE => '0',
      RSTM => '0',
      RSTP => '0',
      UNDERFLOW => NLW_p_0_out_UNDERFLOW_UNCONNECTED
    );
\p_0_out__0\: unisim.vcomponents.DSP48E1
    generic map(
      ACASCREG => 0,
      ADREG => 1,
      ALUMODEREG => 0,
      AREG => 0,
      AUTORESET_PATDET => "NO_RESET",
      A_INPUT => "DIRECT",
      BCASCREG => 0,
      BREG => 0,
      B_INPUT => "DIRECT",
      CARRYINREG => 0,
      CARRYINSELREG => 0,
      CREG => 1,
      DREG => 1,
      INMODEREG => 0,
      MASK => X"3FFFFFFFFFFF",
      MREG => 0,
      OPMODEREG => 0,
      PATTERN => X"000000000000",
      PREG => 1,
      SEL_MASK => "MASK",
      SEL_PATTERN => "PATTERN",
      USE_DPORT => false,
      USE_MULT => "MULTIPLY",
      USE_PATTERN_DETECT => "NO_PATDET",
      USE_SIMD => "ONE48"
    )
        port map (
      A(29 downto 12) => B"000000000000000000",
      A(11 downto 0) => do_data(15 downto 4),
      ACIN(29 downto 0) => B"000000000000000000000000000000",
      ACOUT(29 downto 0) => \NLW_p_0_out__0_ACOUT_UNCONNECTED\(29 downto 0),
      ALUMODE(3 downto 0) => B"0000",
      B(17 downto 0) => B"000000101110111000",
      BCIN(17 downto 0) => B"000000000000000000",
      BCOUT(17 downto 0) => \NLW_p_0_out__0_BCOUT_UNCONNECTED\(17 downto 0),
      C(47 downto 0) => B"111111111111111111111111111111111111111111111111",
      CARRYCASCIN => '0',
      CARRYCASCOUT => \NLW_p_0_out__0_CARRYCASCOUT_UNCONNECTED\,
      CARRYIN => '0',
      CARRYINSEL(2 downto 0) => B"000",
      CARRYOUT(3 downto 0) => \NLW_p_0_out__0_CARRYOUT_UNCONNECTED\(3 downto 0),
      CEA1 => '0',
      CEA2 => '0',
      CEAD => '0',
      CEALUMODE => '0',
      CEB1 => '0',
      CEB2 => '0',
      CEC => '0',
      CECARRYIN => '0',
      CECTRL => '0',
      CED => '0',
      CEINMODE => '0',
      CEM => '0',
      CEP => placeholder,
      CLK => clk,
      D(24 downto 0) => B"0000000000000000000000000",
      INMODE(4 downto 0) => B"00000",
      MULTSIGNIN => '0',
      MULTSIGNOUT => \NLW_p_0_out__0_MULTSIGNOUT_UNCONNECTED\,
      OPMODE(6 downto 0) => B"0000101",
      OVERFLOW => \NLW_p_0_out__0_OVERFLOW_UNCONNECTED\,
      P(47 downto 24) => \NLW_p_0_out__0_P_UNCONNECTED\(47 downto 24),
      P(23) => \p_0_out__0_n_82\,
      P(22) => \p_0_out__0_n_83\,
      P(21) => \p_0_out__0_n_84\,
      P(20) => \p_0_out__0_n_85\,
      P(19) => \p_0_out__0_n_86\,
      P(18) => \p_0_out__0_n_87\,
      P(17) => \p_0_out__0_n_88\,
      P(16) => \p_0_out__0_n_89\,
      P(15) => \p_0_out__0_n_90\,
      P(14) => \p_0_out__0_n_91\,
      P(13) => \p_0_out__0_n_92\,
      P(12) => \p_0_out__0_n_93\,
      P(11) => \p_0_out__0_n_94\,
      P(10) => \p_0_out__0_n_95\,
      P(9) => \p_0_out__0_n_96\,
      P(8) => \p_0_out__0_n_97\,
      P(7) => \p_0_out__0_n_98\,
      P(6) => \p_0_out__0_n_99\,
      P(5) => \p_0_out__0_n_100\,
      P(4) => \p_0_out__0_n_101\,
      P(3) => \p_0_out__0_n_102\,
      P(2) => \p_0_out__0_n_103\,
      P(1) => \p_0_out__0_n_104\,
      P(0) => \p_0_out__0_n_105\,
      PATTERNBDETECT => \NLW_p_0_out__0_PATTERNBDETECT_UNCONNECTED\,
      PATTERNDETECT => \NLW_p_0_out__0_PATTERNDETECT_UNCONNECTED\,
      PCIN(47 downto 0) => B"000000000000000000000000000000000000000000000000",
      PCOUT(47 downto 0) => \NLW_p_0_out__0_PCOUT_UNCONNECTED\(47 downto 0),
      RSTA => '0',
      RSTALLCARRYIN => '0',
      RSTALUMODE => '0',
      RSTB => '0',
      RSTC => '0',
      RSTCTRL => '0',
      RSTD => '0',
      RSTINMODE => '0',
      RSTM => '0',
      RSTP => '0',
      UNDERFLOW => \NLW_p_0_out__0_UNDERFLOW_UNCONNECTED\
    );
\temp[16]_INST_0_i_6\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => inst_n_1,
      D => inst_n_3,
      Q => \temp[16]_INST_0_i_6_n_0\
    );
\vccint[0]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_93\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(0)
    );
\vccint[10]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_83\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(10)
    );
\vccint[11]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_82\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(11)
    );
\vccint[11]_INST_0_i_1\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => inst_n_1,
      D => inst_n_4,
      Q => \vccint[11]_INST_0_i_1_n_0\
    );
\vccint[1]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_92\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(1)
    );
\vccint[2]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_91\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(2)
    );
\vccint[3]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_90\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(3)
    );
\vccint[4]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_89\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(4)
    );
\vccint[5]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_88\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(5)
    );
\vccint[6]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_87\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(6)
    );
\vccint[7]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_86\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(7)
    );
\vccint[8]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_85\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(8)
    );
\vccint[9]_INST_0\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \p_0_out__0_n_84\,
      I1 => \vccint[11]_INST_0_i_1_n_0\,
      O => \^vccint\(9)
    );
end STRUCTURE;
