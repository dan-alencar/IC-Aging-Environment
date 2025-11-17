-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Wed May 14 18:07:50 2025
-- Host        : pop-os running 64-bit Pop!_OS 24.04 LTS
-- Command     : write_vhdl -force -mode funcsim
--               /home/mirai/Documents/Projects/Aging_Fase2/failure_catch/aging_failure_holder/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_sensor_stream_0_0/design_1_sensor_stream_0_0_sim_netlist.vhdl
-- Design      : design_1_sensor_stream_0_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_sensor_stream_0_0_sensor_stream is
  port (
    data : out STD_LOGIC_VECTOR ( 7 downto 0 );
    send : out STD_LOGIC;
    sendin : in STD_LOGIC;
    clk : in STD_LOGIC;
    failure : in STD_LOGIC;
    temp : in STD_LOGIC_VECTOR ( 23 downto 0 );
    sensor : in STD_LOGIC_VECTOR ( 15 downto 0 );
    vccint : in STD_LOGIC_VECTOR ( 23 downto 0 );
    reset : in STD_LOGIC
  );
  attribute ORIG_REF_NAME : string;
  attribute ORIG_REF_NAME of design_1_sensor_stream_0_0_sensor_stream : entity is "sensor_stream";
end design_1_sensor_stream_0_0_sensor_stream;

architecture STRUCTURE of design_1_sensor_stream_0_0_sensor_stream is
  signal counter : STD_LOGIC;
  signal \counter1__10\ : STD_LOGIC;
  signal \counter[0]_i_3_n_0\ : STD_LOGIC;
  signal \counter[0]_i_4_n_0\ : STD_LOGIC;
  signal \counter[0]_i_5_n_0\ : STD_LOGIC;
  signal \counter[0]_i_6_n_0\ : STD_LOGIC;
  signal \counter[0]_i_7_n_0\ : STD_LOGIC;
  signal \counter[12]_i_2_n_0\ : STD_LOGIC;
  signal \counter[12]_i_3_n_0\ : STD_LOGIC;
  signal \counter[12]_i_4_n_0\ : STD_LOGIC;
  signal \counter[12]_i_5_n_0\ : STD_LOGIC;
  signal \counter[16]_i_2_n_0\ : STD_LOGIC;
  signal \counter[4]_i_2_n_0\ : STD_LOGIC;
  signal \counter[4]_i_3_n_0\ : STD_LOGIC;
  signal \counter[4]_i_4_n_0\ : STD_LOGIC;
  signal \counter[4]_i_5_n_0\ : STD_LOGIC;
  signal \counter[8]_i_2_n_0\ : STD_LOGIC;
  signal \counter[8]_i_3_n_0\ : STD_LOGIC;
  signal \counter[8]_i_4_n_0\ : STD_LOGIC;
  signal \counter[8]_i_5_n_0\ : STD_LOGIC;
  signal counter_reg : STD_LOGIC_VECTOR ( 16 downto 5 );
  signal \counter_reg[0]_i_2_n_0\ : STD_LOGIC;
  signal \counter_reg[0]_i_2_n_1\ : STD_LOGIC;
  signal \counter_reg[0]_i_2_n_2\ : STD_LOGIC;
  signal \counter_reg[0]_i_2_n_3\ : STD_LOGIC;
  signal \counter_reg[0]_i_2_n_4\ : STD_LOGIC;
  signal \counter_reg[0]_i_2_n_5\ : STD_LOGIC;
  signal \counter_reg[0]_i_2_n_6\ : STD_LOGIC;
  signal \counter_reg[0]_i_2_n_7\ : STD_LOGIC;
  signal \counter_reg[12]_i_1_n_0\ : STD_LOGIC;
  signal \counter_reg[12]_i_1_n_1\ : STD_LOGIC;
  signal \counter_reg[12]_i_1_n_2\ : STD_LOGIC;
  signal \counter_reg[12]_i_1_n_3\ : STD_LOGIC;
  signal \counter_reg[12]_i_1_n_4\ : STD_LOGIC;
  signal \counter_reg[12]_i_1_n_5\ : STD_LOGIC;
  signal \counter_reg[12]_i_1_n_6\ : STD_LOGIC;
  signal \counter_reg[12]_i_1_n_7\ : STD_LOGIC;
  signal \counter_reg[16]_i_1_n_7\ : STD_LOGIC;
  signal \counter_reg[4]_i_1_n_0\ : STD_LOGIC;
  signal \counter_reg[4]_i_1_n_1\ : STD_LOGIC;
  signal \counter_reg[4]_i_1_n_2\ : STD_LOGIC;
  signal \counter_reg[4]_i_1_n_3\ : STD_LOGIC;
  signal \counter_reg[4]_i_1_n_4\ : STD_LOGIC;
  signal \counter_reg[4]_i_1_n_5\ : STD_LOGIC;
  signal \counter_reg[4]_i_1_n_6\ : STD_LOGIC;
  signal \counter_reg[4]_i_1_n_7\ : STD_LOGIC;
  signal \counter_reg[8]_i_1_n_0\ : STD_LOGIC;
  signal \counter_reg[8]_i_1_n_1\ : STD_LOGIC;
  signal \counter_reg[8]_i_1_n_2\ : STD_LOGIC;
  signal \counter_reg[8]_i_1_n_3\ : STD_LOGIC;
  signal \counter_reg[8]_i_1_n_4\ : STD_LOGIC;
  signal \counter_reg[8]_i_1_n_5\ : STD_LOGIC;
  signal \counter_reg[8]_i_1_n_6\ : STD_LOGIC;
  signal \counter_reg[8]_i_1_n_7\ : STD_LOGIC;
  signal \counter_reg_n_0_[0]\ : STD_LOGIC;
  signal \counter_reg_n_0_[1]\ : STD_LOGIC;
  signal \counter_reg_n_0_[2]\ : STD_LOGIC;
  signal \counter_reg_n_0_[3]\ : STD_LOGIC;
  signal \counter_reg_n_0_[4]\ : STD_LOGIC;
  signal \data[0]_i_2_n_0\ : STD_LOGIC;
  signal \data[0]_i_3_n_0\ : STD_LOGIC;
  signal \data[0]_i_4_n_0\ : STD_LOGIC;
  signal \data[1]_i_2_n_0\ : STD_LOGIC;
  signal \data[1]_i_3_n_0\ : STD_LOGIC;
  signal \data[2]_i_2_n_0\ : STD_LOGIC;
  signal \data[2]_i_3_n_0\ : STD_LOGIC;
  signal \data[3]_i_2_n_0\ : STD_LOGIC;
  signal \data[3]_i_3_n_0\ : STD_LOGIC;
  signal \data[4]_i_2_n_0\ : STD_LOGIC;
  signal \data[4]_i_3_n_0\ : STD_LOGIC;
  signal \data[5]_i_2_n_0\ : STD_LOGIC;
  signal \data[5]_i_3_n_0\ : STD_LOGIC;
  signal \data[6]_i_2_n_0\ : STD_LOGIC;
  signal \data[6]_i_3_n_0\ : STD_LOGIC;
  signal \data[7]_i_3_n_0\ : STD_LOGIC;
  signal \data[7]_i_4_n_0\ : STD_LOGIC;
  signal data_0 : STD_LOGIC_VECTOR ( 7 downto 0 );
  signal enable : STD_LOGIC;
  signal enable_i_1_n_0 : STD_LOGIC;
  signal p_0_in : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal sel : STD_LOGIC;
  signal sel_reg : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal \^send\ : STD_LOGIC;
  signal send_i_1_n_0 : STD_LOGIC;
  signal send_i_2_n_0 : STD_LOGIC;
  signal send_i_3_n_0 : STD_LOGIC;
  signal send_i_5_n_0 : STD_LOGIC;
  signal send_i_6_n_0 : STD_LOGIC;
  signal send_i_7_n_0 : STD_LOGIC;
  signal sendant : STD_LOGIC;
  signal \NLW_counter_reg[16]_i_1_CO_UNCONNECTED\ : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal \NLW_counter_reg[16]_i_1_O_UNCONNECTED\ : STD_LOGIC_VECTOR ( 3 downto 1 );
  attribute ADDER_THRESHOLD : integer;
  attribute ADDER_THRESHOLD of \counter_reg[0]_i_2\ : label is 11;
  attribute ADDER_THRESHOLD of \counter_reg[12]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \counter_reg[16]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \counter_reg[4]_i_1\ : label is 11;
  attribute ADDER_THRESHOLD of \counter_reg[8]_i_1\ : label is 11;
  attribute SOFT_HLUTNM : string;
  attribute SOFT_HLUTNM of \data[0]_i_3\ : label is "soft_lutpair2";
  attribute SOFT_HLUTNM of \sel[0]_i_1\ : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of \sel[1]_i_1\ : label is "soft_lutpair2";
  attribute SOFT_HLUTNM of \sel[2]_i_1\ : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of \sel[3]_i_1\ : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of send_i_5 : label is "soft_lutpair1";
begin
  send <= \^send\;
\counter[0]_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"A2"
    )
        port map (
      I0 => enable,
      I1 => sendin,
      I2 => sendant,
      O => counter
    );
\counter[0]_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => \counter_reg_n_0_[0]\,
      I1 => \counter1__10\,
      O => \counter[0]_i_3_n_0\
    );
\counter[0]_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => \counter_reg_n_0_[3]\,
      I1 => \counter1__10\,
      O => \counter[0]_i_4_n_0\
    );
\counter[0]_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => \counter_reg_n_0_[2]\,
      I1 => \counter1__10\,
      O => \counter[0]_i_5_n_0\
    );
\counter[0]_i_6\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => \counter_reg_n_0_[1]\,
      I1 => \counter1__10\,
      O => \counter[0]_i_6_n_0\
    );
\counter[0]_i_7\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => \counter_reg_n_0_[0]\,
      I1 => \counter1__10\,
      O => \counter[0]_i_7_n_0\
    );
\counter[12]_i_2\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(15),
      I1 => \counter1__10\,
      O => \counter[12]_i_2_n_0\
    );
\counter[12]_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(14),
      I1 => \counter1__10\,
      O => \counter[12]_i_3_n_0\
    );
\counter[12]_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(13),
      I1 => \counter1__10\,
      O => \counter[12]_i_4_n_0\
    );
\counter[12]_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(12),
      I1 => \counter1__10\,
      O => \counter[12]_i_5_n_0\
    );
\counter[16]_i_2\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(16),
      I1 => \counter1__10\,
      O => \counter[16]_i_2_n_0\
    );
\counter[4]_i_2\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(7),
      I1 => \counter1__10\,
      O => \counter[4]_i_2_n_0\
    );
\counter[4]_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(6),
      I1 => \counter1__10\,
      O => \counter[4]_i_3_n_0\
    );
\counter[4]_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(5),
      I1 => \counter1__10\,
      O => \counter[4]_i_4_n_0\
    );
\counter[4]_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => \counter_reg_n_0_[4]\,
      I1 => \counter1__10\,
      O => \counter[4]_i_5_n_0\
    );
\counter[8]_i_2\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(11),
      I1 => \counter1__10\,
      O => \counter[8]_i_2_n_0\
    );
\counter[8]_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(10),
      I1 => \counter1__10\,
      O => \counter[8]_i_3_n_0\
    );
\counter[8]_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(9),
      I1 => \counter1__10\,
      O => \counter[8]_i_4_n_0\
    );
\counter[8]_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => counter_reg(8),
      I1 => \counter1__10\,
      O => \counter[8]_i_5_n_0\
    );
\counter_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[0]_i_2_n_7\,
      Q => \counter_reg_n_0_[0]\
    );
\counter_reg[0]_i_2\: unisim.vcomponents.CARRY4
     port map (
      CI => '0',
      CO(3) => \counter_reg[0]_i_2_n_0\,
      CO(2) => \counter_reg[0]_i_2_n_1\,
      CO(1) => \counter_reg[0]_i_2_n_2\,
      CO(0) => \counter_reg[0]_i_2_n_3\,
      CYINIT => '0',
      DI(3 downto 1) => B"000",
      DI(0) => \counter[0]_i_3_n_0\,
      O(3) => \counter_reg[0]_i_2_n_4\,
      O(2) => \counter_reg[0]_i_2_n_5\,
      O(1) => \counter_reg[0]_i_2_n_6\,
      O(0) => \counter_reg[0]_i_2_n_7\,
      S(3) => \counter[0]_i_4_n_0\,
      S(2) => \counter[0]_i_5_n_0\,
      S(1) => \counter[0]_i_6_n_0\,
      S(0) => \counter[0]_i_7_n_0\
    );
\counter_reg[10]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[8]_i_1_n_5\,
      Q => counter_reg(10)
    );
\counter_reg[11]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[8]_i_1_n_4\,
      Q => counter_reg(11)
    );
\counter_reg[12]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[12]_i_1_n_7\,
      Q => counter_reg(12)
    );
\counter_reg[12]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \counter_reg[8]_i_1_n_0\,
      CO(3) => \counter_reg[12]_i_1_n_0\,
      CO(2) => \counter_reg[12]_i_1_n_1\,
      CO(1) => \counter_reg[12]_i_1_n_2\,
      CO(0) => \counter_reg[12]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3) => \counter_reg[12]_i_1_n_4\,
      O(2) => \counter_reg[12]_i_1_n_5\,
      O(1) => \counter_reg[12]_i_1_n_6\,
      O(0) => \counter_reg[12]_i_1_n_7\,
      S(3) => \counter[12]_i_2_n_0\,
      S(2) => \counter[12]_i_3_n_0\,
      S(1) => \counter[12]_i_4_n_0\,
      S(0) => \counter[12]_i_5_n_0\
    );
\counter_reg[13]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[12]_i_1_n_6\,
      Q => counter_reg(13)
    );
\counter_reg[14]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[12]_i_1_n_5\,
      Q => counter_reg(14)
    );
\counter_reg[15]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[12]_i_1_n_4\,
      Q => counter_reg(15)
    );
\counter_reg[16]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[16]_i_1_n_7\,
      Q => counter_reg(16)
    );
\counter_reg[16]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \counter_reg[12]_i_1_n_0\,
      CO(3 downto 0) => \NLW_counter_reg[16]_i_1_CO_UNCONNECTED\(3 downto 0),
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3 downto 1) => \NLW_counter_reg[16]_i_1_O_UNCONNECTED\(3 downto 1),
      O(0) => \counter_reg[16]_i_1_n_7\,
      S(3 downto 1) => B"000",
      S(0) => \counter[16]_i_2_n_0\
    );
\counter_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[0]_i_2_n_6\,
      Q => \counter_reg_n_0_[1]\
    );
\counter_reg[2]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[0]_i_2_n_5\,
      Q => \counter_reg_n_0_[2]\
    );
\counter_reg[3]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[0]_i_2_n_4\,
      Q => \counter_reg_n_0_[3]\
    );
\counter_reg[4]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[4]_i_1_n_7\,
      Q => \counter_reg_n_0_[4]\
    );
\counter_reg[4]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \counter_reg[0]_i_2_n_0\,
      CO(3) => \counter_reg[4]_i_1_n_0\,
      CO(2) => \counter_reg[4]_i_1_n_1\,
      CO(1) => \counter_reg[4]_i_1_n_2\,
      CO(0) => \counter_reg[4]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3) => \counter_reg[4]_i_1_n_4\,
      O(2) => \counter_reg[4]_i_1_n_5\,
      O(1) => \counter_reg[4]_i_1_n_6\,
      O(0) => \counter_reg[4]_i_1_n_7\,
      S(3) => \counter[4]_i_2_n_0\,
      S(2) => \counter[4]_i_3_n_0\,
      S(1) => \counter[4]_i_4_n_0\,
      S(0) => \counter[4]_i_5_n_0\
    );
\counter_reg[5]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[4]_i_1_n_6\,
      Q => counter_reg(5)
    );
\counter_reg[6]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[4]_i_1_n_5\,
      Q => counter_reg(6)
    );
\counter_reg[7]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[4]_i_1_n_4\,
      Q => counter_reg(7)
    );
\counter_reg[8]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[8]_i_1_n_7\,
      Q => counter_reg(8)
    );
\counter_reg[8]_i_1\: unisim.vcomponents.CARRY4
     port map (
      CI => \counter_reg[4]_i_1_n_0\,
      CO(3) => \counter_reg[8]_i_1_n_0\,
      CO(2) => \counter_reg[8]_i_1_n_1\,
      CO(1) => \counter_reg[8]_i_1_n_2\,
      CO(0) => \counter_reg[8]_i_1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3) => \counter_reg[8]_i_1_n_4\,
      O(2) => \counter_reg[8]_i_1_n_5\,
      O(1) => \counter_reg[8]_i_1_n_6\,
      O(0) => \counter_reg[8]_i_1_n_7\,
      S(3) => \counter[8]_i_2_n_0\,
      S(2) => \counter[8]_i_3_n_0\,
      S(1) => \counter[8]_i_4_n_0\,
      S(0) => \counter[8]_i_5_n_0\
    );
\counter_reg[9]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => counter,
      CLR => send_i_2_n_0,
      D => \counter_reg[8]_i_1_n_6\,
      Q => counter_reg(9)
    );
\data[0]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"00000C0CFF00AAAA"
    )
        port map (
      I0 => \data[0]_i_2_n_0\,
      I1 => failure,
      I2 => \data[0]_i_3_n_0\,
      I3 => \data[0]_i_4_n_0\,
      I4 => sel_reg(2),
      I5 => sel_reg(3),
      O => data_0(0)
    );
\data[0]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => temp(8),
      I1 => sensor(0),
      I2 => temp(0),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => temp(16),
      O => \data[0]_i_2_n_0\
    );
\data[0]_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"E"
    )
        port map (
      I0 => sel_reg(1),
      I1 => sel_reg(0),
      O => \data[0]_i_3_n_0\
    );
\data[0]_i_4\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => vccint(0),
      I1 => vccint(16),
      I2 => sensor(8),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => vccint(8),
      O => \data[0]_i_4_n_0\
    );
\data[1]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"0A0C"
    )
        port map (
      I0 => \data[1]_i_2_n_0\,
      I1 => \data[1]_i_3_n_0\,
      I2 => sel_reg(3),
      I3 => sel_reg(2),
      O => data_0(1)
    );
\data[1]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => vccint(1),
      I1 => vccint(17),
      I2 => sensor(9),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => vccint(9),
      O => \data[1]_i_2_n_0\
    );
\data[1]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => temp(9),
      I1 => sensor(1),
      I2 => temp(1),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => temp(17),
      O => \data[1]_i_3_n_0\
    );
\data[2]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"0A0C"
    )
        port map (
      I0 => \data[2]_i_2_n_0\,
      I1 => \data[2]_i_3_n_0\,
      I2 => sel_reg(3),
      I3 => sel_reg(2),
      O => data_0(2)
    );
\data[2]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => vccint(2),
      I1 => vccint(18),
      I2 => sensor(10),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => vccint(10),
      O => \data[2]_i_2_n_0\
    );
\data[2]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => temp(10),
      I1 => sensor(2),
      I2 => temp(2),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => temp(18),
      O => \data[2]_i_3_n_0\
    );
\data[3]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"0A0C"
    )
        port map (
      I0 => \data[3]_i_2_n_0\,
      I1 => \data[3]_i_3_n_0\,
      I2 => sel_reg(3),
      I3 => sel_reg(2),
      O => data_0(3)
    );
\data[3]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => vccint(3),
      I1 => vccint(19),
      I2 => sensor(11),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => vccint(11),
      O => \data[3]_i_2_n_0\
    );
\data[3]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => temp(11),
      I1 => sensor(3),
      I2 => temp(3),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => temp(19),
      O => \data[3]_i_3_n_0\
    );
\data[4]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"0A0C"
    )
        port map (
      I0 => \data[4]_i_2_n_0\,
      I1 => \data[4]_i_3_n_0\,
      I2 => sel_reg(3),
      I3 => sel_reg(2),
      O => data_0(4)
    );
\data[4]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => vccint(4),
      I1 => vccint(20),
      I2 => sensor(12),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => vccint(12),
      O => \data[4]_i_2_n_0\
    );
\data[4]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => temp(12),
      I1 => sensor(4),
      I2 => temp(4),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => temp(20),
      O => \data[4]_i_3_n_0\
    );
\data[5]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"0A0C"
    )
        port map (
      I0 => \data[5]_i_2_n_0\,
      I1 => \data[5]_i_3_n_0\,
      I2 => sel_reg(3),
      I3 => sel_reg(2),
      O => data_0(5)
    );
\data[5]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => vccint(5),
      I1 => vccint(21),
      I2 => sensor(13),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => vccint(13),
      O => \data[5]_i_2_n_0\
    );
\data[5]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => temp(13),
      I1 => sensor(5),
      I2 => temp(5),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => temp(21),
      O => \data[5]_i_3_n_0\
    );
\data[6]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"0A0C"
    )
        port map (
      I0 => \data[6]_i_2_n_0\,
      I1 => \data[6]_i_3_n_0\,
      I2 => sel_reg(3),
      I3 => sel_reg(2),
      O => data_0(6)
    );
\data[6]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => vccint(6),
      I1 => vccint(22),
      I2 => sensor(14),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => vccint(14),
      O => \data[6]_i_2_n_0\
    );
\data[6]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => temp(14),
      I1 => sensor(6),
      I2 => temp(6),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => temp(22),
      O => \data[6]_i_3_n_0\
    );
\data[7]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"8808"
    )
        port map (
      I0 => \counter1__10\,
      I1 => enable,
      I2 => sendin,
      I3 => sendant,
      O => sel
    );
\data[7]_i_2\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"0A0C"
    )
        port map (
      I0 => \data[7]_i_3_n_0\,
      I1 => \data[7]_i_4_n_0\,
      I2 => sel_reg(3),
      I3 => sel_reg(2),
      O => data_0(7)
    );
\data[7]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => vccint(7),
      I1 => vccint(23),
      I2 => sensor(15),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => vccint(15),
      O => \data[7]_i_3_n_0\
    );
\data[7]_i_4\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CCFFAAF0CC00AAF0"
    )
        port map (
      I0 => temp(15),
      I1 => sensor(7),
      I2 => temp(7),
      I3 => sel_reg(0),
      I4 => sel_reg(1),
      I5 => temp(23),
      O => \data[7]_i_4_n_0\
    );
\data_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => data_0(0),
      Q => data(0)
    );
\data_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => data_0(1),
      Q => data(1)
    );
\data_reg[2]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => data_0(2),
      Q => data(2)
    );
\data_reg[3]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => data_0(3),
      Q => data(3)
    );
\data_reg[4]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => data_0(4),
      Q => data(4)
    );
\data_reg[5]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => data_0(5),
      Q => data(5)
    );
\data_reg[6]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => data_0(6),
      Q => data(6)
    );
\data_reg[7]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => data_0(7),
      Q => data(7)
    );
enable_i_1: unisim.vcomponents.LUT6
    generic map(
      INIT => X"7F00FFFF7F007F00"
    )
        port map (
      I0 => \counter1__10\,
      I1 => sel_reg(3),
      I2 => send_i_5_n_0,
      I3 => enable,
      I4 => sendant,
      I5 => sendin,
      O => enable_i_1_n_0
    );
enable_reg: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => send_i_2_n_0,
      D => enable_i_1_n_0,
      Q => enable
    );
\sel[0]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"001F"
    )
        port map (
      I0 => sel_reg(1),
      I1 => sel_reg(2),
      I2 => sel_reg(3),
      I3 => sel_reg(0),
      O => p_0_in(0)
    );
\sel[1]_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"14"
    )
        port map (
      I0 => sel_reg(3),
      I1 => sel_reg(1),
      I2 => sel_reg(0),
      O => p_0_in(1)
    );
\sel[2]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"1444"
    )
        port map (
      I0 => sel_reg(3),
      I1 => sel_reg(2),
      I2 => sel_reg(1),
      I3 => sel_reg(0),
      O => p_0_in(2)
    );
\sel[3]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"4002"
    )
        port map (
      I0 => sel_reg(3),
      I1 => sel_reg(2),
      I2 => sel_reg(1),
      I3 => sel_reg(0),
      O => p_0_in(3)
    );
\sel_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => p_0_in(0),
      Q => sel_reg(0)
    );
\sel_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => p_0_in(1),
      Q => sel_reg(1)
    );
\sel_reg[2]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => p_0_in(2),
      Q => sel_reg(2)
    );
\sel_reg[3]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => sel,
      CLR => send_i_2_n_0,
      D => p_0_in(3),
      Q => sel_reg(3)
    );
send_i_1: unisim.vcomponents.LUT6
    generic map(
      INIT => X"EEEEEEEE04440404"
    )
        port map (
      I0 => send_i_3_n_0,
      I1 => \counter1__10\,
      I2 => sel_reg(3),
      I3 => send_i_5_n_0,
      I4 => reset,
      I5 => \^send\,
      O => send_i_1_n_0
    );
send_i_2: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => reset,
      O => send_i_2_n_0
    );
send_i_3: unisim.vcomponents.LUT3
    generic map(
      INIT => X"4F"
    )
        port map (
      I0 => sendant,
      I1 => sendin,
      I2 => enable,
      O => send_i_3_n_0
    );
send_i_4: unisim.vcomponents.LUT6
    generic map(
      INIT => X"8888888880808000"
    )
        port map (
      I0 => counter_reg(16),
      I1 => counter_reg(15),
      I2 => counter_reg(12),
      I3 => counter_reg(11),
      I4 => send_i_6_n_0,
      I5 => send_i_7_n_0,
      O => \counter1__10\
    );
send_i_5: unisim.vcomponents.LUT3
    generic map(
      INIT => X"FE"
    )
        port map (
      I0 => sel_reg(0),
      I1 => sel_reg(1),
      I2 => sel_reg(2),
      O => send_i_5_n_0
    );
send_i_6: unisim.vcomponents.LUT6
    generic map(
      INIT => X"8880808080808080"
    )
        port map (
      I0 => counter_reg(10),
      I1 => counter_reg(9),
      I2 => counter_reg(8),
      I3 => counter_reg(7),
      I4 => counter_reg(6),
      I5 => counter_reg(5),
      O => send_i_6_n_0
    );
send_i_7: unisim.vcomponents.LUT2
    generic map(
      INIT => X"E"
    )
        port map (
      I0 => counter_reg(13),
      I1 => counter_reg(14),
      O => send_i_7_n_0
    );
send_reg: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => send_i_2_n_0,
      D => send_i_1_n_0,
      Q => \^send\
    );
sendant_reg: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => send_i_2_n_0,
      D => sendin,
      Q => sendant
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_sensor_stream_0_0 is
  port (
    temp : in STD_LOGIC_VECTOR ( 23 downto 0 );
    vccint : in STD_LOGIC_VECTOR ( 23 downto 0 );
    sensor : in STD_LOGIC_VECTOR ( 15 downto 0 );
    failure : in STD_LOGIC;
    reset : in STD_LOGIC;
    clk : in STD_LOGIC;
    sendin : in STD_LOGIC;
    send : out STD_LOGIC;
    data : out STD_LOGIC_VECTOR ( 7 downto 0 )
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of design_1_sensor_stream_0_0 : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_sensor_stream_0_0 : entity is "design_1_sensor_stream_0_0,sensor_stream,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_sensor_stream_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_sensor_stream_0_0 : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of design_1_sensor_stream_0_0 : entity is "sensor_stream,Vivado 2024.2";
end design_1_sensor_stream_0_0;

architecture STRUCTURE of design_1_sensor_stream_0_0 is
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
inst: entity work.design_1_sensor_stream_0_0_sensor_stream
     port map (
      clk => clk,
      data(7 downto 0) => data(7 downto 0),
      failure => failure,
      reset => reset,
      send => send,
      sendin => sendin,
      sensor(15 downto 0) => sensor(15 downto 0),
      temp(23 downto 0) => temp(23 downto 0),
      vccint(23 downto 0) => vccint(23 downto 0)
    );
end STRUCTURE;
