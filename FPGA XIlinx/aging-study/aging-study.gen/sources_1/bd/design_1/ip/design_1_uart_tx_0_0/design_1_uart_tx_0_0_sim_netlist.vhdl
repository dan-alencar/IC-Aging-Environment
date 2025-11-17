-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Wed Feb  5 19:12:28 2025
-- Host        : pop-os running 64-bit Pop!_OS 22.04 LTS
-- Command     : write_vhdl -force -mode funcsim
--               /home/mirai/Documents/Projects/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_uart_tx_0_0/design_1_uart_tx_0_0_sim_netlist.vhdl
-- Design      : design_1_uart_tx_0_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_uart_tx_0_0_uart_tx is
  port (
    tx_busy_reg_0 : out STD_LOGIC;
    tx : out STD_LOGIC;
    send : in STD_LOGIC;
    clk : in STD_LOGIC;
    data : in STD_LOGIC_VECTOR ( 7 downto 0 );
    reset : in STD_LOGIC
  );
  attribute ORIG_REF_NAME : string;
  attribute ORIG_REF_NAME of design_1_uart_tx_0_0_uart_tx : entity is "uart_tx";
end design_1_uart_tx_0_0_uart_tx;

architecture STRUCTURE of design_1_uart_tx_0_0_uart_tx is
  signal counter : STD_LOGIC_VECTOR ( 13 downto 0 );
  signal counter0 : STD_LOGIC_VECTOR ( 13 downto 1 );
  signal \counter0_carry__0_n_0\ : STD_LOGIC;
  signal \counter0_carry__0_n_1\ : STD_LOGIC;
  signal \counter0_carry__0_n_2\ : STD_LOGIC;
  signal \counter0_carry__0_n_3\ : STD_LOGIC;
  signal \counter0_carry__1_n_0\ : STD_LOGIC;
  signal \counter0_carry__1_n_1\ : STD_LOGIC;
  signal \counter0_carry__1_n_2\ : STD_LOGIC;
  signal \counter0_carry__1_n_3\ : STD_LOGIC;
  signal counter0_carry_n_0 : STD_LOGIC;
  signal counter0_carry_n_1 : STD_LOGIC;
  signal counter0_carry_n_2 : STD_LOGIC;
  signal counter0_carry_n_3 : STD_LOGIC;
  signal \counter[13]_i_1_n_0\ : STD_LOGIC;
  signal frame : STD_LOGIC_VECTOR ( 9 downto 1 );
  signal \index[0]_i_1_n_0\ : STD_LOGIC;
  signal \index[1]_i_1_n_0\ : STD_LOGIC;
  signal \index[2]_i_1_n_0\ : STD_LOGIC;
  signal \index[3]_i_1_n_0\ : STD_LOGIC;
  signal \index[3]_i_2_n_0\ : STD_LOGIC;
  signal index_reg : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal p_1_in : STD_LOGIC_VECTOR ( 13 downto 0 );
  signal sendant : STD_LOGIC;
  signal \^tx\ : STD_LOGIC;
  signal tx17_out : STD_LOGIC;
  signal \tx1__8\ : STD_LOGIC;
  signal tx2_in : STD_LOGIC;
  signal tx_busy4_in : STD_LOGIC;
  signal tx_busy_i_1_n_0 : STD_LOGIC;
  signal tx_busy_i_2_n_0 : STD_LOGIC;
  signal \^tx_busy_reg_0\ : STD_LOGIC;
  signal tx_i_1_n_0 : STD_LOGIC;
  signal tx_i_2_n_0 : STD_LOGIC;
  signal tx_i_3_n_0 : STD_LOGIC;
  signal tx_i_6_n_0 : STD_LOGIC;
  signal tx_i_7_n_0 : STD_LOGIC;
  signal tx_i_8_n_0 : STD_LOGIC;
  signal tx_i_9_n_0 : STD_LOGIC;
  signal \NLW_counter0_carry__2_CO_UNCONNECTED\ : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal \NLW_counter0_carry__2_O_UNCONNECTED\ : STD_LOGIC_VECTOR ( 3 downto 1 );
  attribute ADDER_THRESHOLD : integer;
  attribute ADDER_THRESHOLD of counter0_carry : label is 35;
  attribute ADDER_THRESHOLD of \counter0_carry__0\ : label is 35;
  attribute ADDER_THRESHOLD of \counter0_carry__1\ : label is 35;
  attribute ADDER_THRESHOLD of \counter0_carry__2\ : label is 35;
  attribute SOFT_HLUTNM : string;
  attribute SOFT_HLUTNM of \index[0]_i_1\ : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of \index[1]_i_1\ : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of \index[3]_i_2\ : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of tx_busy_i_2 : label is "soft_lutpair2";
  attribute SOFT_HLUTNM of tx_busy_i_3 : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of tx_i_5 : label is "soft_lutpair2";
begin
  tx <= \^tx\;
  tx_busy_reg_0 <= \^tx_busy_reg_0\;
counter0_carry: unisim.vcomponents.CARRY4
     port map (
      CI => '0',
      CO(3) => counter0_carry_n_0,
      CO(2) => counter0_carry_n_1,
      CO(1) => counter0_carry_n_2,
      CO(0) => counter0_carry_n_3,
      CYINIT => counter(0),
      DI(3 downto 0) => B"0000",
      O(3 downto 0) => counter0(4 downto 1),
      S(3 downto 0) => counter(4 downto 1)
    );
\counter0_carry__0\: unisim.vcomponents.CARRY4
     port map (
      CI => counter0_carry_n_0,
      CO(3) => \counter0_carry__0_n_0\,
      CO(2) => \counter0_carry__0_n_1\,
      CO(1) => \counter0_carry__0_n_2\,
      CO(0) => \counter0_carry__0_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3 downto 0) => counter0(8 downto 5),
      S(3 downto 0) => counter(8 downto 5)
    );
\counter0_carry__1\: unisim.vcomponents.CARRY4
     port map (
      CI => \counter0_carry__0_n_0\,
      CO(3) => \counter0_carry__1_n_0\,
      CO(2) => \counter0_carry__1_n_1\,
      CO(1) => \counter0_carry__1_n_2\,
      CO(0) => \counter0_carry__1_n_3\,
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3 downto 0) => counter0(12 downto 9),
      S(3 downto 0) => counter(12 downto 9)
    );
\counter0_carry__2\: unisim.vcomponents.CARRY4
     port map (
      CI => \counter0_carry__1_n_0\,
      CO(3 downto 0) => \NLW_counter0_carry__2_CO_UNCONNECTED\(3 downto 0),
      CYINIT => '0',
      DI(3 downto 0) => B"0000",
      O(3 downto 1) => \NLW_counter0_carry__2_O_UNCONNECTED\(3 downto 1),
      O(0) => counter0(13),
      S(3 downto 1) => B"000",
      S(0) => counter(13)
    );
\counter[0]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"11111011"
    )
        port map (
      I0 => \tx1__8\,
      I1 => counter(0),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => p_1_in(0)
    );
\counter[10]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"44444044"
    )
        port map (
      I0 => \tx1__8\,
      I1 => counter0(10),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => p_1_in(10)
    );
\counter[11]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"04FF0404"
    )
        port map (
      I0 => sendant,
      I1 => send,
      I2 => \^tx_busy_reg_0\,
      I3 => \tx1__8\,
      I4 => counter0(11),
      O => p_1_in(11)
    );
\counter[12]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"44444044"
    )
        port map (
      I0 => \tx1__8\,
      I1 => counter0(12),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => p_1_in(12)
    );
\counter[13]_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"F4"
    )
        port map (
      I0 => sendant,
      I1 => send,
      I2 => \^tx_busy_reg_0\,
      O => \counter[13]_i_1_n_0\
    );
\counter[13]_i_2\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"04FF0404"
    )
        port map (
      I0 => sendant,
      I1 => send,
      I2 => \^tx_busy_reg_0\,
      I3 => \tx1__8\,
      I4 => counter0(13),
      O => p_1_in(13)
    );
\counter[1]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"44444044"
    )
        port map (
      I0 => \tx1__8\,
      I1 => counter0(1),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => p_1_in(1)
    );
\counter[2]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"44444044"
    )
        port map (
      I0 => \tx1__8\,
      I1 => counter0(2),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => p_1_in(2)
    );
\counter[3]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"44444044"
    )
        port map (
      I0 => \tx1__8\,
      I1 => counter0(3),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => p_1_in(3)
    );
\counter[4]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"04FF0404"
    )
        port map (
      I0 => sendant,
      I1 => send,
      I2 => \^tx_busy_reg_0\,
      I3 => \tx1__8\,
      I4 => counter0(4),
      O => p_1_in(4)
    );
\counter[5]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"04FF0404"
    )
        port map (
      I0 => sendant,
      I1 => send,
      I2 => \^tx_busy_reg_0\,
      I3 => \tx1__8\,
      I4 => counter0(5),
      O => p_1_in(5)
    );
\counter[6]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"44444044"
    )
        port map (
      I0 => \tx1__8\,
      I1 => counter0(6),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => p_1_in(6)
    );
\counter[7]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"04FF0404"
    )
        port map (
      I0 => sendant,
      I1 => send,
      I2 => \^tx_busy_reg_0\,
      I3 => \tx1__8\,
      I4 => counter0(7),
      O => p_1_in(7)
    );
\counter[8]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"44444044"
    )
        port map (
      I0 => \tx1__8\,
      I1 => counter0(8),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => p_1_in(8)
    );
\counter[9]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"44444044"
    )
        port map (
      I0 => \tx1__8\,
      I1 => counter0(9),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => p_1_in(9)
    );
\counter_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(0),
      Q => counter(0)
    );
\counter_reg[10]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(10),
      Q => counter(10)
    );
\counter_reg[11]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(11),
      Q => counter(11)
    );
\counter_reg[12]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(12),
      Q => counter(12)
    );
\counter_reg[13]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(13),
      Q => counter(13)
    );
\counter_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(1),
      Q => counter(1)
    );
\counter_reg[2]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(2),
      Q => counter(2)
    );
\counter_reg[3]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(3),
      Q => counter(3)
    );
\counter_reg[4]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(4),
      Q => counter(4)
    );
\counter_reg[5]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(5),
      Q => counter(5)
    );
\counter_reg[6]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(6),
      Q => counter(6)
    );
\counter_reg[7]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(7),
      Q => counter(7)
    );
\counter_reg[8]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(8),
      Q => counter(8)
    );
\counter_reg[9]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \counter[13]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => p_1_in(9),
      Q => counter(9)
    );
\frame[9]_i_1\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"04"
    )
        port map (
      I0 => \^tx_busy_reg_0\,
      I1 => send,
      I2 => sendant,
      O => tx17_out
    );
\frame_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => tx17_out,
      CLR => tx_i_2_n_0,
      D => data(0),
      Q => frame(1)
    );
\frame_reg[2]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => tx17_out,
      CLR => tx_i_2_n_0,
      D => data(1),
      Q => frame(2)
    );
\frame_reg[3]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => tx17_out,
      CLR => tx_i_2_n_0,
      D => data(2),
      Q => frame(3)
    );
\frame_reg[4]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => tx17_out,
      CLR => tx_i_2_n_0,
      D => data(3),
      Q => frame(4)
    );
\frame_reg[5]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => tx17_out,
      CLR => tx_i_2_n_0,
      D => data(4),
      Q => frame(5)
    );
\frame_reg[6]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => tx17_out,
      CLR => tx_i_2_n_0,
      D => data(5),
      Q => frame(6)
    );
\frame_reg[7]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => tx17_out,
      CLR => tx_i_2_n_0,
      D => data(6),
      Q => frame(7)
    );
\frame_reg[8]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => tx17_out,
      CLR => tx_i_2_n_0,
      D => data(7),
      Q => frame(8)
    );
\frame_reg[9]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => tx17_out,
      CLR => tx_i_2_n_0,
      D => '1',
      Q => frame(9)
    );
\index[0]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"5545"
    )
        port map (
      I0 => index_reg(0),
      I1 => sendant,
      I2 => send,
      I3 => \^tx_busy_reg_0\,
      O => \index[0]_i_1_n_0\
    );
\index[1]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"66666066"
    )
        port map (
      I0 => index_reg(1),
      I1 => index_reg(0),
      I2 => sendant,
      I3 => send,
      I4 => \^tx_busy_reg_0\,
      O => \index[1]_i_1_n_0\
    );
\index[2]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"6A6A6A6A6A006A6A"
    )
        port map (
      I0 => index_reg(2),
      I1 => index_reg(1),
      I2 => index_reg(0),
      I3 => sendant,
      I4 => send,
      I5 => \^tx_busy_reg_0\,
      O => \index[2]_i_1_n_0\
    );
\index[3]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"F0004444"
    )
        port map (
      I0 => sendant,
      I1 => send,
      I2 => \tx1__8\,
      I3 => tx_busy_i_2_n_0,
      I4 => \^tx_busy_reg_0\,
      O => \index[3]_i_1_n_0\
    );
\index[3]_i_2\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"00006AAA"
    )
        port map (
      I0 => index_reg(3),
      I1 => index_reg(2),
      I2 => index_reg(0),
      I3 => index_reg(1),
      I4 => tx17_out,
      O => \index[3]_i_2_n_0\
    );
\index_reg[0]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \index[3]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => \index[0]_i_1_n_0\,
      Q => index_reg(0)
    );
\index_reg[1]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \index[3]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => \index[1]_i_1_n_0\,
      Q => index_reg(1)
    );
\index_reg[2]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \index[3]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => \index[2]_i_1_n_0\,
      Q => index_reg(2)
    );
\index_reg[3]\: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => \index[3]_i_1_n_0\,
      CLR => tx_i_2_n_0,
      D => \index[3]_i_2_n_0\,
      Q => index_reg(3)
    );
sendant_reg: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => tx_i_2_n_0,
      D => send,
      Q => sendant
    );
tx_busy_i_1: unisim.vcomponents.LUT6
    generic map(
      INIT => X"F0FF4444FFFF4444"
    )
        port map (
      I0 => sendant,
      I1 => send,
      I2 => tx_busy_i_2_n_0,
      I3 => tx_busy4_in,
      I4 => \^tx_busy_reg_0\,
      I5 => \tx1__8\,
      O => tx_busy_i_1_n_0
    );
tx_busy_i_2: unisim.vcomponents.LUT4
    generic map(
      INIT => X"01FF"
    )
        port map (
      I0 => index_reg(0),
      I1 => index_reg(1),
      I2 => index_reg(2),
      I3 => index_reg(3),
      O => tx_busy_i_2_n_0
    );
tx_busy_i_3: unisim.vcomponents.LUT4
    generic map(
      INIT => X"1000"
    )
        port map (
      I0 => index_reg(1),
      I1 => index_reg(2),
      I2 => index_reg(0),
      I3 => index_reg(3),
      O => tx_busy4_in
    );
tx_busy_reg: unisim.vcomponents.FDCE
     port map (
      C => clk,
      CE => '1',
      CLR => tx_i_2_n_0,
      D => tx_busy_i_1_n_0,
      Q => \^tx_busy_reg_0\
    );
tx_i_1: unisim.vcomponents.LUT6
    generic map(
      INIT => X"2333333320000000"
    )
        port map (
      I0 => tx_i_3_n_0,
      I1 => tx17_out,
      I2 => \tx1__8\,
      I3 => tx2_in,
      I4 => \^tx_busy_reg_0\,
      I5 => \^tx\,
      O => tx_i_1_n_0
    );
tx_i_2: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => reset,
      O => tx_i_2_n_0
    );
tx_i_3: unisim.vcomponents.LUT6
    generic map(
      INIT => X"FFE200E2FFFFFFFF"
    )
        port map (
      I0 => tx_i_6_n_0,
      I1 => index_reg(2),
      I2 => tx_i_7_n_0,
      I3 => index_reg(3),
      I4 => tx_i_8_n_0,
      I5 => tx_busy_i_2_n_0,
      O => tx_i_3_n_0
    );
tx_i_4: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AAAAAAAA88888880"
    )
        port map (
      I0 => counter(13),
      I1 => counter(11),
      I2 => tx_i_9_n_0,
      I3 => counter(8),
      I4 => counter(9),
      I5 => counter(12),
      O => \tx1__8\
    );
tx_i_5: unisim.vcomponents.LUT3
    generic map(
      INIT => X"57"
    )
        port map (
      I0 => index_reg(3),
      I1 => index_reg(2),
      I2 => index_reg(1),
      O => tx2_in
    );
tx_i_6: unisim.vcomponents.LUT5
    generic map(
      INIT => X"AFC0A0C0"
    )
        port map (
      I0 => frame(3),
      I1 => frame(2),
      I2 => index_reg(1),
      I3 => index_reg(0),
      I4 => frame(1),
      O => tx_i_6_n_0
    );
tx_i_7: unisim.vcomponents.LUT6
    generic map(
      INIT => X"AFA0CFCFAFA0C0C0"
    )
        port map (
      I0 => frame(7),
      I1 => frame(6),
      I2 => index_reg(1),
      I3 => frame(5),
      I4 => index_reg(0),
      I5 => frame(4),
      O => tx_i_7_n_0
    );
tx_i_8: unisim.vcomponents.LUT3
    generic map(
      INIT => X"B8"
    )
        port map (
      I0 => frame(9),
      I1 => index_reg(0),
      I2 => frame(8),
      O => tx_i_8_n_0
    );
tx_i_9: unisim.vcomponents.LUT5
    generic map(
      INIT => X"FEEEAAAA"
    )
        port map (
      I0 => counter(10),
      I1 => counter(6),
      I2 => counter(5),
      I3 => counter(4),
      I4 => counter(7),
      O => tx_i_9_n_0
    );
tx_reg: unisim.vcomponents.FDPE
     port map (
      C => clk,
      CE => '1',
      D => tx_i_1_n_0,
      PRE => tx_i_2_n_0,
      Q => \^tx\
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_uart_tx_0_0 is
  port (
    clk : in STD_LOGIC;
    reset : in STD_LOGIC;
    send : in STD_LOGIC;
    data : in STD_LOGIC_VECTOR ( 7 downto 0 );
    tx : out STD_LOGIC;
    tx_busy : out STD_LOGIC
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of design_1_uart_tx_0_0 : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_uart_tx_0_0 : entity is "design_1_uart_tx_0_0,uart_tx,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_uart_tx_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_uart_tx_0_0 : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of design_1_uart_tx_0_0 : entity is "uart_tx,Vivado 2024.2";
end design_1_uart_tx_0_0;

architecture STRUCTURE of design_1_uart_tx_0_0 is
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
inst: entity work.design_1_uart_tx_0_0_uart_tx
     port map (
      clk => clk,
      data(7 downto 0) => data(7 downto 0),
      reset => reset,
      send => send,
      tx => tx,
      tx_busy_reg_0 => tx_busy
    );
end STRUCTURE;
