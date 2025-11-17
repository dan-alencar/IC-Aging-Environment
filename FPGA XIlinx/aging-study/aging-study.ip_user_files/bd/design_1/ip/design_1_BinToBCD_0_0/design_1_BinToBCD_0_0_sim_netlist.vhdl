-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Wed Feb  5 19:11:34 2025
-- Host        : pop-os running 64-bit Pop!_OS 22.04 LTS
-- Command     : write_vhdl -force -mode funcsim
--               /home/mirai/Documents/Projects/Aging-main/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_BinToBCD_0_0/design_1_BinToBCD_0_0_sim_netlist.vhdl
-- Design      : design_1_BinToBCD_0_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_BinToBCD_0_0_BinToBCD is
  port (
    un : out STD_LOGIC_VECTOR ( 3 downto 0 );
    dec : out STD_LOGIC_VECTOR ( 3 downto 0 );
    cent : out STD_LOGIC_VECTOR ( 3 downto 0 );
    mil : out STD_LOGIC_VECTOR ( 3 downto 0 );
    bil : out STD_LOGIC_VECTOR ( 3 downto 0 );
    tril : out STD_LOGIC_VECTOR ( 3 downto 0 );
    quadr : out STD_LOGIC_VECTOR ( 1 downto 0 );
    clk : in STD_LOGIC;
    bin : in STD_LOGIC_VECTOR ( 19 downto 0 )
  );
  attribute ORIG_REF_NAME : string;
  attribute ORIG_REF_NAME of design_1_BinToBCD_0_0_BinToBCD : entity is "BinToBCD";
end design_1_BinToBCD_0_0_BinToBCD;

architecture STRUCTURE of design_1_BinToBCD_0_0_BinToBCD is
  signal \bil[3]_i_10_n_0\ : STD_LOGIC;
  signal \bil[3]_i_11_n_0\ : STD_LOGIC;
  signal \bil[3]_i_12_n_0\ : STD_LOGIC;
  signal \bil[3]_i_13_n_0\ : STD_LOGIC;
  signal \bil[3]_i_14_n_0\ : STD_LOGIC;
  signal \bil[3]_i_15_n_0\ : STD_LOGIC;
  signal \bil[3]_i_16_n_0\ : STD_LOGIC;
  signal \bil[3]_i_17_n_0\ : STD_LOGIC;
  signal \bil[3]_i_2_n_0\ : STD_LOGIC;
  signal \bil[3]_i_3_n_0\ : STD_LOGIC;
  signal \bil[3]_i_4_n_0\ : STD_LOGIC;
  signal \bil[3]_i_5_n_0\ : STD_LOGIC;
  signal \bil[3]_i_6_n_0\ : STD_LOGIC;
  signal \bil[3]_i_7_n_0\ : STD_LOGIC;
  signal \bil[3]_i_8_n_0\ : STD_LOGIC;
  signal \bil[3]_i_9_n_0\ : STD_LOGIC;
  signal \cent[3]_i_10_n_0\ : STD_LOGIC;
  signal \cent[3]_i_11_n_0\ : STD_LOGIC;
  signal \cent[3]_i_12_n_0\ : STD_LOGIC;
  signal \cent[3]_i_13_n_0\ : STD_LOGIC;
  signal \cent[3]_i_14_n_0\ : STD_LOGIC;
  signal \cent[3]_i_15_n_0\ : STD_LOGIC;
  signal \cent[3]_i_16_n_0\ : STD_LOGIC;
  signal \cent[3]_i_17_n_0\ : STD_LOGIC;
  signal \cent[3]_i_18_n_0\ : STD_LOGIC;
  signal \cent[3]_i_19_n_0\ : STD_LOGIC;
  signal \cent[3]_i_20_n_0\ : STD_LOGIC;
  signal \cent[3]_i_21_n_0\ : STD_LOGIC;
  signal \cent[3]_i_22_n_0\ : STD_LOGIC;
  signal \cent[3]_i_23_n_0\ : STD_LOGIC;
  signal \cent[3]_i_24_n_0\ : STD_LOGIC;
  signal \cent[3]_i_2_n_0\ : STD_LOGIC;
  signal \cent[3]_i_3_n_0\ : STD_LOGIC;
  signal \cent[3]_i_4_n_0\ : STD_LOGIC;
  signal \cent[3]_i_5_n_0\ : STD_LOGIC;
  signal \cent[3]_i_6_n_0\ : STD_LOGIC;
  signal \cent[3]_i_7_n_0\ : STD_LOGIC;
  signal \cent[3]_i_8_n_0\ : STD_LOGIC;
  signal \cent[3]_i_9_n_0\ : STD_LOGIC;
  signal \dec[3]_i_10_n_0\ : STD_LOGIC;
  signal \dec[3]_i_11_n_0\ : STD_LOGIC;
  signal \dec[3]_i_13_n_0\ : STD_LOGIC;
  signal \dec[3]_i_14_n_0\ : STD_LOGIC;
  signal \dec[3]_i_15_n_0\ : STD_LOGIC;
  signal \dec[3]_i_16_n_0\ : STD_LOGIC;
  signal \dec[3]_i_17_n_0\ : STD_LOGIC;
  signal \dec[3]_i_18_n_0\ : STD_LOGIC;
  signal \dec[3]_i_20_n_0\ : STD_LOGIC;
  signal \dec[3]_i_22_n_0\ : STD_LOGIC;
  signal \dec[3]_i_23_n_0\ : STD_LOGIC;
  signal \dec[3]_i_24_n_0\ : STD_LOGIC;
  signal \dec[3]_i_25_n_0\ : STD_LOGIC;
  signal \dec[3]_i_2_n_0\ : STD_LOGIC;
  signal \dec[3]_i_30_n_0\ : STD_LOGIC;
  signal \dec[3]_i_3_n_0\ : STD_LOGIC;
  signal \dec[3]_i_4_n_0\ : STD_LOGIC;
  signal \dec[3]_i_5_n_0\ : STD_LOGIC;
  signal \dec[3]_i_6_n_0\ : STD_LOGIC;
  signal \dec[3]_i_7_n_0\ : STD_LOGIC;
  signal \dec[3]_i_8_n_0\ : STD_LOGIC;
  signal \dec[3]_i_9_n_0\ : STD_LOGIC;
  signal \mil[3]_i_10_n_0\ : STD_LOGIC;
  signal \mil[3]_i_11_n_0\ : STD_LOGIC;
  signal \mil[3]_i_12_n_0\ : STD_LOGIC;
  signal \mil[3]_i_13_n_0\ : STD_LOGIC;
  signal \mil[3]_i_14_n_0\ : STD_LOGIC;
  signal \mil[3]_i_15_n_0\ : STD_LOGIC;
  signal \mil[3]_i_16_n_0\ : STD_LOGIC;
  signal \mil[3]_i_17_n_0\ : STD_LOGIC;
  signal \mil[3]_i_18_n_0\ : STD_LOGIC;
  signal \mil[3]_i_19_n_0\ : STD_LOGIC;
  signal \mil[3]_i_20_n_0\ : STD_LOGIC;
  signal \mil[3]_i_21_n_0\ : STD_LOGIC;
  signal \mil[3]_i_22_n_0\ : STD_LOGIC;
  signal \mil[3]_i_23_n_0\ : STD_LOGIC;
  signal \mil[3]_i_24_n_0\ : STD_LOGIC;
  signal \mil[3]_i_25_n_0\ : STD_LOGIC;
  signal \mil[3]_i_26_n_0\ : STD_LOGIC;
  signal \mil[3]_i_27_n_0\ : STD_LOGIC;
  signal \mil[3]_i_28_n_0\ : STD_LOGIC;
  signal \mil[3]_i_29_n_0\ : STD_LOGIC;
  signal \mil[3]_i_2_n_0\ : STD_LOGIC;
  signal \mil[3]_i_30_n_0\ : STD_LOGIC;
  signal \mil[3]_i_31_n_0\ : STD_LOGIC;
  signal \mil[3]_i_32_n_0\ : STD_LOGIC;
  signal \mil[3]_i_33_n_0\ : STD_LOGIC;
  signal \mil[3]_i_36_n_0\ : STD_LOGIC;
  signal \mil[3]_i_37_n_0\ : STD_LOGIC;
  signal \mil[3]_i_38_n_0\ : STD_LOGIC;
  signal \mil[3]_i_39_n_0\ : STD_LOGIC;
  signal \mil[3]_i_3_n_0\ : STD_LOGIC;
  signal \mil[3]_i_40_n_0\ : STD_LOGIC;
  signal \mil[3]_i_41_n_0\ : STD_LOGIC;
  signal \mil[3]_i_4_n_0\ : STD_LOGIC;
  signal \mil[3]_i_5_n_0\ : STD_LOGIC;
  signal \mil[3]_i_6_n_0\ : STD_LOGIC;
  signal \mil[3]_i_7_n_0\ : STD_LOGIC;
  signal \mil[3]_i_8_n_0\ : STD_LOGIC;
  signal \mil[3]_i_9_n_0\ : STD_LOGIC;
  signal \p_0_in__0\ : STD_LOGIC_VECTOR ( 2 downto 1 );
  signal \p_0_in__11\ : STD_LOGIC_VECTOR ( 2 to 2 );
  signal \p_0_in__12\ : STD_LOGIC_VECTOR ( 2 to 2 );
  signal \p_0_in__13\ : STD_LOGIC_VECTOR ( 2 to 2 );
  signal \p_0_in__14\ : STD_LOGIC_VECTOR ( 2 to 2 );
  signal \p_0_in__2\ : STD_LOGIC_VECTOR ( 2 to 2 );
  signal \p_0_in__3\ : STD_LOGIC_VECTOR ( 3 downto 1 );
  signal \p_0_in__5\ : STD_LOGIC_VECTOR ( 2 downto 1 );
  signal \p_0_in__6\ : STD_LOGIC_VECTOR ( 3 downto 1 );
  signal \p_0_in__8\ : STD_LOGIC_VECTOR ( 2 downto 1 );
  signal \p_0_in__9\ : STD_LOGIC_VECTOR ( 2 downto 1 );
  signal p_0_out : STD_LOGIC_VECTOR ( 3 downto 1 );
  signal p_1_out : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal p_2_out : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal p_3_out : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal p_4_out : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal p_5_out : STD_LOGIC_VECTOR ( 3 downto 0 );
  signal p_6_out : STD_LOGIC_VECTOR ( 1 downto 0 );
  signal tril1 : STD_LOGIC;
  signal \tril[2]_i_2_n_0\ : STD_LOGIC;
  signal \tril[2]_i_3_n_0\ : STD_LOGIC;
  signal \tril[2]_i_4_n_0\ : STD_LOGIC;
  signal \tril[2]_i_5_n_0\ : STD_LOGIC;
  signal \tril[2]_i_6_n_0\ : STD_LOGIC;
  signal \tril[2]_i_7_n_0\ : STD_LOGIC;
  signal \tril[2]_i_8_n_0\ : STD_LOGIC;
  signal \tril[3]_i_10_n_0\ : STD_LOGIC;
  signal \tril[3]_i_11_n_0\ : STD_LOGIC;
  signal \tril[3]_i_12_n_0\ : STD_LOGIC;
  signal \tril[3]_i_13_n_0\ : STD_LOGIC;
  signal \tril[3]_i_14_n_0\ : STD_LOGIC;
  signal \tril[3]_i_15_n_0\ : STD_LOGIC;
  signal \tril[3]_i_2_n_0\ : STD_LOGIC;
  signal \tril[3]_i_3_n_0\ : STD_LOGIC;
  signal \tril[3]_i_4_n_0\ : STD_LOGIC;
  signal \tril[3]_i_5_n_0\ : STD_LOGIC;
  signal \tril[3]_i_6_n_0\ : STD_LOGIC;
  signal \tril[3]_i_8_n_0\ : STD_LOGIC;
  signal \tril[3]_i_9_n_0\ : STD_LOGIC;
  signal \un[3]_i_10_n_0\ : STD_LOGIC;
  signal \un[3]_i_3_n_0\ : STD_LOGIC;
  signal \un[3]_i_4_n_0\ : STD_LOGIC;
  signal \un[3]_i_5_n_0\ : STD_LOGIC;
  signal \un[3]_i_8_n_0\ : STD_LOGIC;
  attribute SOFT_HLUTNM : string;
  attribute SOFT_HLUTNM of \bil[3]_i_15\ : label is "soft_lutpair7";
  attribute SOFT_HLUTNM of \bil[3]_i_16\ : label is "soft_lutpair5";
  attribute SOFT_HLUTNM of \bil[3]_i_4\ : label is "soft_lutpair10";
  attribute SOFT_HLUTNM of \cent[3]_i_12\ : label is "soft_lutpair15";
  attribute SOFT_HLUTNM of \cent[3]_i_15\ : label is "soft_lutpair15";
  attribute SOFT_HLUTNM of \cent[3]_i_16\ : label is "soft_lutpair13";
  attribute SOFT_HLUTNM of \cent[3]_i_17\ : label is "soft_lutpair13";
  attribute SOFT_HLUTNM of \cent[3]_i_3\ : label is "soft_lutpair12";
  attribute SOFT_HLUTNM of \cent[3]_i_5\ : label is "soft_lutpair12";
  attribute SOFT_HLUTNM of \dec[3]_i_22\ : label is "soft_lutpair5";
  attribute SOFT_HLUTNM of \dec[3]_i_25\ : label is "soft_lutpair6";
  attribute SOFT_HLUTNM of \dec[3]_i_3\ : label is "soft_lutpair9";
  attribute SOFT_HLUTNM of \dec[3]_i_5\ : label is "soft_lutpair9";
  attribute SOFT_HLUTNM of \mil[3]_i_10\ : label is "soft_lutpair2";
  attribute SOFT_HLUTNM of \mil[3]_i_17\ : label is "soft_lutpair17";
  attribute SOFT_HLUTNM of \mil[3]_i_18\ : label is "soft_lutpair17";
  attribute SOFT_HLUTNM of \mil[3]_i_19\ : label is "soft_lutpair3";
  attribute SOFT_HLUTNM of \mil[3]_i_21\ : label is "soft_lutpair4";
  attribute SOFT_HLUTNM of \mil[3]_i_22\ : label is "soft_lutpair3";
  attribute SOFT_HLUTNM of \mil[3]_i_25\ : label is "soft_lutpair4";
  attribute SOFT_HLUTNM of \mil[3]_i_31\ : label is "soft_lutpair6";
  attribute SOFT_HLUTNM of \mil[3]_i_33\ : label is "soft_lutpair8";
  attribute SOFT_HLUTNM of \mil[3]_i_34\ : label is "soft_lutpair8";
  attribute SOFT_HLUTNM of \mil[3]_i_42\ : label is "soft_lutpair7";
  attribute SOFT_HLUTNM of \mil[3]_i_8\ : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of \tril[2]_i_6\ : label is "soft_lutpair10";
  attribute SOFT_HLUTNM of \tril[2]_i_7\ : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of \tril[3]_i_10\ : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of \tril[3]_i_12\ : label is "soft_lutpair14";
  attribute SOFT_HLUTNM of \tril[3]_i_14\ : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of \tril[3]_i_2\ : label is "soft_lutpair2";
  attribute SOFT_HLUTNM of \tril[3]_i_3\ : label is "soft_lutpair11";
  attribute SOFT_HLUTNM of \tril[3]_i_4\ : label is "soft_lutpair11";
  attribute SOFT_HLUTNM of \tril[3]_i_8\ : label is "soft_lutpair14";
  attribute SOFT_HLUTNM of \un[3]_i_11\ : label is "soft_lutpair16";
  attribute SOFT_HLUTNM of \un[3]_i_9\ : label is "soft_lutpair16";
begin
\bil[0]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"609F996600FF9F60"
    )
        port map (
      I0 => \mil[3]_i_2_n_0\,
      I1 => \mil[3]_i_3_n_0\,
      I2 => \mil[3]_i_4_n_0\,
      I3 => \mil[3]_i_5_n_0\,
      I4 => \mil[3]_i_6_n_0\,
      I5 => \mil[3]_i_7_n_0\,
      O => p_4_out(0)
    );
\bil[1]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A419941A62955686"
    )
        port map (
      I0 => \bil[3]_i_2_n_0\,
      I1 => \bil[3]_i_3_n_0\,
      I2 => \bil[3]_i_6_n_0\,
      I3 => \bil[3]_i_5_n_0\,
      I4 => \bil[3]_i_4_n_0\,
      I5 => \bil[3]_i_7_n_0\,
      O => p_4_out(1)
    );
\bil[2]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0D810643722EB89C"
    )
        port map (
      I0 => \bil[3]_i_2_n_0\,
      I1 => \bil[3]_i_5_n_0\,
      I2 => \bil[3]_i_3_n_0\,
      I3 => \bil[3]_i_6_n_0\,
      I4 => \bil[3]_i_4_n_0\,
      I5 => \bil[3]_i_7_n_0\,
      O => p_4_out(2)
    );
\bil[3]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0254152080314C08"
    )
        port map (
      I0 => \bil[3]_i_2_n_0\,
      I1 => \bil[3]_i_3_n_0\,
      I2 => \bil[3]_i_4_n_0\,
      I3 => \bil[3]_i_5_n_0\,
      I4 => \bil[3]_i_6_n_0\,
      I5 => \bil[3]_i_7_n_0\,
      O => p_4_out(3)
    );
\bil[3]_i_10\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \cent[3]_i_21_n_0\,
      I1 => \mil[3]_i_23_n_0\,
      I2 => \mil[3]_i_24_n_0\,
      I3 => \mil[3]_i_25_n_0\,
      I4 => \mil[3]_i_26_n_0\,
      I5 => \mil[3]_i_20_n_0\,
      O => \bil[3]_i_10_n_0\
    );
\bil[3]_i_11\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"C03E03E0C0F803E0"
    )
        port map (
      I0 => \mil[3]_i_24_n_0\,
      I1 => \bil[3]_i_16_n_0\,
      I2 => \bil[3]_i_13_n_0\,
      I3 => \bil[3]_i_14_n_0\,
      I4 => \bil[3]_i_15_n_0\,
      I5 => \bil[3]_i_12_n_0\,
      O => \bil[3]_i_11_n_0\
    );
\bil[3]_i_12\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"F6"
    )
        port map (
      I0 => \mil[3]_i_24_n_0\,
      I1 => \mil[3]_i_25_n_0\,
      I2 => \mil[3]_i_20_n_0\,
      O => \bil[3]_i_12_n_0\
    );
\bil[3]_i_13\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"78"
    )
        port map (
      I0 => \mil[3]_i_39_n_0\,
      I1 => \bil[3]_i_17_n_0\,
      I2 => \mil[3]_i_40_n_0\,
      O => \bil[3]_i_13_n_0\
    );
\bil[3]_i_14\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0FC00FC00FC03F80"
    )
        port map (
      I0 => bin(14),
      I1 => bin(17),
      I2 => bin(18),
      I3 => bin(19),
      I4 => bin(16),
      I5 => bin(15),
      O => \bil[3]_i_14_n_0\
    );
\bil[3]_i_15\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"F000E000"
    )
        port map (
      I0 => bin(15),
      I1 => bin(16),
      I2 => bin(19),
      I3 => bin(18),
      I4 => bin(17),
      O => \bil[3]_i_15_n_0\
    );
\bil[3]_i_16\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"9B32303C"
    )
        port map (
      I0 => \mil[3]_i_32_n_0\,
      I1 => \mil[3]_i_39_n_0\,
      I2 => \mil[3]_i_40_n_0\,
      I3 => \mil[3]_i_37_n_0\,
      I4 => \mil[3]_i_38_n_0\,
      O => \bil[3]_i_16_n_0\
    );
\bil[3]_i_17\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"BEBBBBBEEEEEEEEE"
    )
        port map (
      I0 => \mil[3]_i_38_n_0\,
      I1 => \p_0_in__3\(3),
      I2 => bin(13),
      I3 => \mil[3]_i_36_n_0\,
      I4 => bin(14),
      I5 => \p_0_in__3\(2),
      O => \bil[3]_i_17_n_0\
    );
\bil[3]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \mil[3]_i_7_n_0\,
      I1 => \mil[3]_i_17_n_0\,
      I2 => \mil[3]_i_11_n_0\,
      I3 => \mil[3]_i_16_n_0\,
      I4 => \mil[3]_i_18_n_0\,
      I5 => \mil[3]_i_3_n_0\,
      O => \bil[3]_i_2_n_0\
    );
\bil[3]_i_3\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => \bil[3]_i_8_n_0\,
      I1 => \tril[3]_i_5_n_0\,
      O => \bil[3]_i_3_n_0\
    );
\bil[3]_i_4\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"581A"
    )
        port map (
      I0 => \tril[3]_i_4_n_0\,
      I1 => \tril[3]_i_3_n_0\,
      I2 => \tril[3]_i_2_n_0\,
      I3 => \tril[3]_i_5_n_0\,
      O => \bil[3]_i_4_n_0\
    );
\bil[3]_i_5\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"F8"
    )
        port map (
      I0 => \bil[3]_i_4_n_0\,
      I1 => \tril[2]_i_2_n_0\,
      I2 => \tril[2]_i_3_n_0\,
      O => \bil[3]_i_5_n_0\
    );
\bil[3]_i_6\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \mil[3]_i_11_n_0\,
      I1 => \bil[3]_i_9_n_0\,
      I2 => \bil[3]_i_10_n_0\,
      I3 => \tril[3]_i_2_n_0\,
      I4 => \bil[3]_i_11_n_0\,
      I5 => \mil[3]_i_9_n_0\,
      O => \bil[3]_i_6_n_0\
    );
\bil[3]_i_7\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \mil[3]_i_3_n_0\,
      I1 => \mil[3]_i_8_n_0\,
      I2 => \mil[3]_i_9_n_0\,
      I3 => \tril[3]_i_5_n_0\,
      I4 => \mil[3]_i_10_n_0\,
      I5 => \mil[3]_i_11_n_0\,
      O => \bil[3]_i_7_n_0\
    );
\bil[3]_i_8\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0FC00FC00FC03F80"
    )
        port map (
      I0 => \mil[3]_i_9_n_0\,
      I1 => \tril[3]_i_9_n_0\,
      I2 => \tril[3]_i_8_n_0\,
      I3 => \tril[3]_i_10_n_0\,
      I4 => \tril[3]_i_11_n_0\,
      I5 => \bil[3]_i_10_n_0\,
      O => \bil[3]_i_8_n_0\
    );
\bil[3]_i_9\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"24CACD3005028F2C"
    )
        port map (
      I0 => \bil[3]_i_12_n_0\,
      I1 => \bil[3]_i_13_n_0\,
      I2 => \bil[3]_i_14_n_0\,
      I3 => \bil[3]_i_15_n_0\,
      I4 => \bil[3]_i_16_n_0\,
      I5 => \mil[3]_i_24_n_0\,
      O => \bil[3]_i_9_n_0\
    );
\bil_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_4_out(0),
      Q => bil(0),
      R => '0'
    );
\bil_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_4_out(1),
      Q => bil(1),
      R => '0'
    );
\bil_reg[2]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_4_out(2),
      Q => bil(2),
      R => '0'
    );
\bil_reg[3]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_4_out(3),
      Q => bil(3),
      R => '0'
    );
\cent[0]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"4D3AA17C4B3001EC"
    )
        port map (
      I0 => \dec[3]_i_2_n_0\,
      I1 => \dec[3]_i_3_n_0\,
      I2 => \dec[3]_i_4_n_0\,
      I3 => \dec[3]_i_5_n_0\,
      I4 => \dec[3]_i_6_n_0\,
      I5 => \dec[3]_i_7_n_0\,
      O => p_2_out(0)
    );
\cent[1]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A0C55A035B3005EC"
    )
        port map (
      I0 => \cent[3]_i_2_n_0\,
      I1 => \cent[3]_i_3_n_0\,
      I2 => \cent[3]_i_4_n_0\,
      I3 => \cent[3]_i_5_n_0\,
      I4 => \cent[3]_i_6_n_0\,
      I5 => \cent[3]_i_7_n_0\,
      O => p_2_out(1)
    );
\cent[2]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"1995546642A5518A"
    )
        port map (
      I0 => \cent[3]_i_2_n_0\,
      I1 => \cent[3]_i_3_n_0\,
      I2 => \cent[3]_i_4_n_0\,
      I3 => \cent[3]_i_5_n_0\,
      I4 => \cent[3]_i_6_n_0\,
      I5 => \cent[3]_i_7_n_0\,
      O => p_2_out(2)
    );
\cent[3]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"41200148070AA0D0"
    )
        port map (
      I0 => \cent[3]_i_2_n_0\,
      I1 => \cent[3]_i_3_n_0\,
      I2 => \cent[3]_i_4_n_0\,
      I3 => \cent[3]_i_5_n_0\,
      I4 => \cent[3]_i_6_n_0\,
      I5 => \cent[3]_i_7_n_0\,
      O => p_2_out(3)
    );
\cent[3]_i_10\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \dec[3]_i_9_n_0\,
      I1 => \dec[3]_i_15_n_0\,
      I2 => \dec[3]_i_16_n_0\,
      I3 => \dec[3]_i_17_n_0\,
      I4 => \dec[3]_i_18_n_0\,
      I5 => \cent[3]_i_13_n_0\,
      O => \cent[3]_i_10_n_0\
    );
\cent[3]_i_11\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \cent[3]_i_10_n_0\,
      I1 => \mil[3]_i_12_n_0\,
      I2 => \mil[3]_i_13_n_0\,
      I3 => \mil[3]_i_14_n_0\,
      I4 => \mil[3]_i_15_n_0\,
      I5 => \cent[3]_i_8_n_0\,
      O => \cent[3]_i_11_n_0\
    );
\cent[3]_i_12\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => \dec[3]_i_17_n_0\,
      I1 => \dec[3]_i_16_n_0\,
      O => \cent[3]_i_12_n_0\
    );
\cent[3]_i_13\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"33939333CC3636CC"
    )
        port map (
      I0 => bin(7),
      I1 => \p_0_in__8\(2),
      I2 => bin(8),
      I3 => \cent[3]_i_24_n_0\,
      I4 => bin(9),
      I5 => \dec[3]_i_20_n_0\,
      O => \cent[3]_i_13_n_0\
    );
\cent[3]_i_14\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"3FB3B33FCCFEFECC"
    )
        port map (
      I0 => \cent[3]_i_13_n_0\,
      I1 => \dec[3]_i_18_n_0\,
      I2 => \dec[3]_i_16_n_0\,
      I3 => \cent[3]_i_18_n_0\,
      I4 => \cent[3]_i_19_n_0\,
      I5 => \dec[3]_i_17_n_0\,
      O => \cent[3]_i_14_n_0\
    );
\cent[3]_i_15\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => \cent[3]_i_19_n_0\,
      I1 => \cent[3]_i_18_n_0\,
      I2 => \dec[3]_i_16_n_0\,
      I3 => \dec[3]_i_17_n_0\,
      O => \cent[3]_i_15_n_0\
    );
\cent[3]_i_16\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => \mil[3]_i_14_n_0\,
      I1 => \mil[3]_i_13_n_0\,
      O => \cent[3]_i_16_n_0\
    );
\cent[3]_i_17\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => \cent[3]_i_21_n_0\,
      I1 => \cent[3]_i_22_n_0\,
      I2 => \mil[3]_i_13_n_0\,
      I3 => \mil[3]_i_14_n_0\,
      O => \cent[3]_i_17_n_0\
    );
\cent[3]_i_18\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \cent[3]_i_19_n_0\,
      I1 => \dec[3]_i_22_n_0\,
      I2 => \dec[3]_i_23_n_0\,
      I3 => \dec[3]_i_24_n_0\,
      I4 => \dec[3]_i_25_n_0\,
      I5 => \mil[3]_i_28_n_0\,
      O => \cent[3]_i_18_n_0\
    );
\cent[3]_i_19\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => bin(9),
      I1 => \p_0_in__5\(1),
      I2 => bin(11),
      I3 => \dec[3]_i_30_n_0\,
      I4 => \p_0_in__5\(2),
      I5 => bin(10),
      O => \cent[3]_i_19_n_0\
    );
\cent[3]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"609F00FF99669F60"
    )
        port map (
      I0 => \dec[3]_i_8_n_0\,
      I1 => \dec[3]_i_9_n_0\,
      I2 => \dec[3]_i_4_n_0\,
      I3 => \dec[3]_i_14_n_0\,
      I4 => \dec[3]_i_10_n_0\,
      I5 => \dec[3]_i_11_n_0\,
      O => \cent[3]_i_2_n_0\
    );
\cent[3]_i_20\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A4255A9292A4495A"
    )
        port map (
      I0 => \mil[3]_i_20_n_0\,
      I1 => \bil[3]_i_15_n_0\,
      I2 => \bil[3]_i_14_n_0\,
      I3 => \bil[3]_i_13_n_0\,
      I4 => \bil[3]_i_16_n_0\,
      I5 => \mil[3]_i_24_n_0\,
      O => \cent[3]_i_20_n_0\
    );
\cent[3]_i_21\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \cent[3]_i_19_n_0\,
      I1 => \dec[3]_i_22_n_0\,
      I2 => \dec[3]_i_23_n_0\,
      I3 => \dec[3]_i_24_n_0\,
      I4 => \dec[3]_i_25_n_0\,
      I5 => \mil[3]_i_28_n_0\,
      O => \cent[3]_i_21_n_0\
    );
\cent[3]_i_22\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \cent[3]_i_21_n_0\,
      I1 => \mil[3]_i_23_n_0\,
      I2 => \mil[3]_i_24_n_0\,
      I3 => \mil[3]_i_25_n_0\,
      I4 => \mil[3]_i_26_n_0\,
      I5 => \mil[3]_i_20_n_0\,
      O => \cent[3]_i_22_n_0\
    );
\cent[3]_i_23\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"92C3492CC3492C34"
    )
        port map (
      I0 => \bil[3]_i_16_n_0\,
      I1 => \bil[3]_i_15_n_0\,
      I2 => \bil[3]_i_13_n_0\,
      I3 => \bil[3]_i_14_n_0\,
      I4 => \mil[3]_i_24_n_0\,
      I5 => \mil[3]_i_20_n_0\,
      O => \cent[3]_i_23_n_0\
    );
\cent[3]_i_24\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => bin(9),
      I1 => \p_0_in__5\(1),
      I2 => bin(11),
      I3 => \dec[3]_i_30_n_0\,
      I4 => \p_0_in__5\(2),
      I5 => bin(10),
      O => \cent[3]_i_24_n_0\
    );
\cent[3]_i_3\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => \cent[3]_i_8_n_0\,
      I1 => \cent[3]_i_9_n_0\,
      I2 => \cent[3]_i_10_n_0\,
      I3 => \cent[3]_i_11_n_0\,
      O => \cent[3]_i_3_n_0\
    );
\cent[3]_i_4\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \dec[3]_i_10_n_0\,
      I1 => \cent[3]_i_12_n_0\,
      I2 => \cent[3]_i_13_n_0\,
      I3 => \cent[3]_i_14_n_0\,
      I4 => \cent[3]_i_15_n_0\,
      I5 => \dec[3]_i_9_n_0\,
      O => \cent[3]_i_4_n_0\
    );
\cent[3]_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => \cent[3]_i_11_n_0\,
      I1 => \cent[3]_i_10_n_0\,
      O => \cent[3]_i_5_n_0\
    );
\cent[3]_i_6\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \cent[3]_i_4_n_0\,
      I1 => \cent[3]_i_16_n_0\,
      I2 => \cent[3]_i_8_n_0\,
      I3 => \cent[3]_i_9_n_0\,
      I4 => \cent[3]_i_17_n_0\,
      I5 => \cent[3]_i_10_n_0\,
      O => \cent[3]_i_6_n_0\
    );
\cent[3]_i_7\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"933336CC"
    )
        port map (
      I0 => \dec[3]_i_2_n_0\,
      I1 => \dec[3]_i_3_n_0\,
      I2 => \dec[3]_i_4_n_0\,
      I3 => \dec[3]_i_5_n_0\,
      I4 => \dec[3]_i_6_n_0\,
      O => \cent[3]_i_7_n_0\
    );
\cent[3]_i_8\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"33939333CC3636CC"
    )
        port map (
      I0 => \cent[3]_i_13_n_0\,
      I1 => \dec[3]_i_18_n_0\,
      I2 => \dec[3]_i_16_n_0\,
      I3 => \cent[3]_i_18_n_0\,
      I4 => \cent[3]_i_19_n_0\,
      I5 => \dec[3]_i_17_n_0\,
      O => \cent[3]_i_8_n_0\
    );
\cent[3]_i_9\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \cent[3]_i_8_n_0\,
      I1 => \cent[3]_i_20_n_0\,
      I2 => \cent[3]_i_21_n_0\,
      I3 => \cent[3]_i_22_n_0\,
      I4 => \cent[3]_i_23_n_0\,
      I5 => \mil[3]_i_13_n_0\,
      O => \cent[3]_i_9_n_0\
    );
\cent_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_2_out(0),
      Q => cent(0),
      R => '0'
    );
\cent_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_2_out(1),
      Q => cent(1),
      R => '0'
    );
\cent_reg[2]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_2_out(2),
      Q => cent(2),
      R => '0'
    );
\cent_reg[3]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_2_out(3),
      Q => cent(3),
      R => '0'
    );
\dec[0]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"3C93933C3C36363C"
    )
        port map (
      I0 => bin(1),
      I1 => \p_0_in__14\(2),
      I2 => \un[3]_i_3_n_0\,
      I3 => \un[3]_i_4_n_0\,
      I4 => bin(3),
      I5 => bin(2),
      O => p_1_out(0)
    );
\dec[1]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A0C55A035B3005EC"
    )
        port map (
      I0 => \dec[3]_i_2_n_0\,
      I1 => \dec[3]_i_3_n_0\,
      I2 => \dec[3]_i_4_n_0\,
      I3 => \dec[3]_i_5_n_0\,
      I4 => \dec[3]_i_6_n_0\,
      I5 => \dec[3]_i_7_n_0\,
      O => p_1_out(1)
    );
\dec[2]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"1995546642A5518A"
    )
        port map (
      I0 => \dec[3]_i_2_n_0\,
      I1 => \dec[3]_i_3_n_0\,
      I2 => \dec[3]_i_4_n_0\,
      I3 => \dec[3]_i_5_n_0\,
      I4 => \dec[3]_i_6_n_0\,
      I5 => \dec[3]_i_7_n_0\,
      O => p_1_out(2)
    );
\dec[3]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"41200148070AA0D0"
    )
        port map (
      I0 => \dec[3]_i_2_n_0\,
      I1 => \dec[3]_i_3_n_0\,
      I2 => \dec[3]_i_4_n_0\,
      I3 => \dec[3]_i_5_n_0\,
      I4 => \dec[3]_i_6_n_0\,
      I5 => \dec[3]_i_7_n_0\,
      O => p_1_out(3)
    );
\dec[3]_i_10\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => bin(5),
      I1 => \p_0_in__9\(1),
      I2 => bin(7),
      I3 => \un[3]_i_10_n_0\,
      I4 => \p_0_in__9\(2),
      I5 => bin(6),
      O => \dec[3]_i_10_n_0\
    );
\dec[3]_i_11\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \dec[3]_i_10_n_0\,
      I1 => \cent[3]_i_12_n_0\,
      I2 => \cent[3]_i_13_n_0\,
      I3 => \cent[3]_i_14_n_0\,
      I4 => \cent[3]_i_15_n_0\,
      I5 => \dec[3]_i_9_n_0\,
      O => \dec[3]_i_11_n_0\
    );
\dec[3]_i_12\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => bin(7),
      I1 => \un[3]_i_10_n_0\,
      I2 => bin(6),
      I3 => \dec[3]_i_13_n_0\,
      O => \p_0_in__11\(2)
    );
\dec[3]_i_13\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => bin(6),
      I1 => \p_0_in__8\(1),
      I2 => bin(8),
      I3 => \dec[3]_i_20_n_0\,
      I4 => \p_0_in__8\(2),
      I5 => bin(7),
      O => \dec[3]_i_13_n_0\
    );
\dec[3]_i_14\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => \cent[3]_i_13_n_0\,
      I1 => \cent[3]_i_14_n_0\,
      I2 => \dec[3]_i_9_n_0\,
      I3 => \dec[3]_i_8_n_0\,
      O => \dec[3]_i_14_n_0\
    );
\dec[3]_i_15\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A419941A62955686"
    )
        port map (
      I0 => \cent[3]_i_19_n_0\,
      I1 => \dec[3]_i_22_n_0\,
      I2 => \dec[3]_i_23_n_0\,
      I3 => \dec[3]_i_24_n_0\,
      I4 => \dec[3]_i_25_n_0\,
      I5 => \mil[3]_i_28_n_0\,
      O => \dec[3]_i_15_n_0\
    );
\dec[3]_i_16\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E360FB0C83CCB2C"
    )
        port map (
      I0 => bin(8),
      I1 => \p_0_in__6\(1),
      I2 => bin(10),
      I3 => \p_0_in__6\(2),
      I4 => \p_0_in__6\(3),
      I5 => bin(9),
      O => \dec[3]_i_16_n_0\
    );
\dec[3]_i_17\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E3E0FB0C8FCCB2C"
    )
        port map (
      I0 => \dec[3]_i_16_n_0\,
      I1 => \mil[3]_i_27_n_0\,
      I2 => \mil[3]_i_28_n_0\,
      I3 => \mil[3]_i_29_n_0\,
      I4 => \mil[3]_i_30_n_0\,
      I5 => \cent[3]_i_19_n_0\,
      O => \dec[3]_i_17_n_0\
    );
\dec[3]_i_18\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"281157EA3129C246"
    )
        port map (
      I0 => \dec[3]_i_24_n_0\,
      I1 => \dec[3]_i_22_n_0\,
      I2 => \dec[3]_i_23_n_0\,
      I3 => \dec[3]_i_25_n_0\,
      I4 => \mil[3]_i_28_n_0\,
      I5 => \cent[3]_i_19_n_0\,
      O => \dec[3]_i_18_n_0\
    );
\dec[3]_i_19\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A419941A62955686"
    )
        port map (
      I0 => bin(9),
      I1 => \p_0_in__5\(1),
      I2 => bin(11),
      I3 => \dec[3]_i_30_n_0\,
      I4 => \p_0_in__5\(2),
      I5 => bin(10),
      O => \p_0_in__8\(1)
    );
\dec[3]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"33939333CC3636CC"
    )
        port map (
      I0 => bin(3),
      I1 => \p_0_in__12\(2),
      I2 => bin(4),
      I3 => \un[3]_i_8_n_0\,
      I4 => bin(5),
      I5 => \un[3]_i_5_n_0\,
      O => \dec[3]_i_2_n_0\
    );
\dec[3]_i_20\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E3E0FB0C8FCCB2C"
    )
        port map (
      I0 => bin(8),
      I1 => \p_0_in__6\(1),
      I2 => bin(10),
      I3 => \p_0_in__6\(2),
      I4 => \p_0_in__6\(3),
      I5 => bin(9),
      O => \dec[3]_i_20_n_0\
    );
\dec[3]_i_21\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"281157EA3129C246"
    )
        port map (
      I0 => \dec[3]_i_30_n_0\,
      I1 => \p_0_in__5\(1),
      I2 => bin(11),
      I3 => \p_0_in__5\(2),
      I4 => bin(10),
      I5 => bin(9),
      O => \p_0_in__8\(2)
    );
\dec[3]_i_22\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"11989A56"
    )
        port map (
      I0 => \mil[3]_i_32_n_0\,
      I1 => \mil[3]_i_39_n_0\,
      I2 => \mil[3]_i_40_n_0\,
      I3 => \mil[3]_i_37_n_0\,
      I4 => \mil[3]_i_38_n_0\,
      O => \dec[3]_i_22_n_0\
    );
\dec[3]_i_23\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E360FB0C83CCB2C"
    )
        port map (
      I0 => bin(11),
      I1 => \p_0_in__3\(1),
      I2 => bin(13),
      I3 => \p_0_in__3\(2),
      I4 => \p_0_in__3\(3),
      I5 => bin(12),
      O => \dec[3]_i_23_n_0\
    );
\dec[3]_i_24\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E3E0FB0C8FCCB2C"
    )
        port map (
      I0 => \dec[3]_i_23_n_0\,
      I1 => \mil[3]_i_38_n_0\,
      I2 => \mil[3]_i_37_n_0\,
      I3 => \mil[3]_i_39_n_0\,
      I4 => \mil[3]_i_40_n_0\,
      I5 => \mil[3]_i_32_n_0\,
      O => \dec[3]_i_24_n_0\
    );
\dec[3]_i_25\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"3266318C"
    )
        port map (
      I0 => \mil[3]_i_40_n_0\,
      I1 => \mil[3]_i_37_n_0\,
      I2 => \mil[3]_i_38_n_0\,
      I3 => \mil[3]_i_39_n_0\,
      I4 => \mil[3]_i_32_n_0\,
      O => \dec[3]_i_25_n_0\
    );
\dec[3]_i_26\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A494A51A62566186"
    )
        port map (
      I0 => bin(11),
      I1 => \p_0_in__3\(1),
      I2 => bin(13),
      I3 => \p_0_in__3\(2),
      I4 => \p_0_in__3\(3),
      I5 => bin(12),
      O => \p_0_in__6\(1)
    );
\dec[3]_i_27\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"660511F84561981A"
    )
        port map (
      I0 => \p_0_in__3\(1),
      I1 => bin(13),
      I2 => \p_0_in__3\(3),
      I3 => \p_0_in__3\(2),
      I4 => bin(12),
      I5 => bin(11),
      O => \p_0_in__6\(2)
    );
\dec[3]_i_28\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"2008174424011280"
    )
        port map (
      I0 => bin(11),
      I1 => bin(12),
      I2 => \p_0_in__3\(2),
      I3 => \p_0_in__3\(1),
      I4 => bin(13),
      I5 => \p_0_in__3\(3),
      O => \p_0_in__6\(3)
    );
\dec[3]_i_29\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"9A56119811989A56"
    )
        port map (
      I0 => bin(12),
      I1 => \p_0_in__3\(2),
      I2 => \p_0_in__3\(3),
      I3 => bin(13),
      I4 => \mil[3]_i_36_n_0\,
      I5 => bin(14),
      O => \p_0_in__5\(1)
    );
\dec[3]_i_3\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => \dec[3]_i_8_n_0\,
      I1 => \dec[3]_i_9_n_0\,
      I2 => \dec[3]_i_10_n_0\,
      I3 => \dec[3]_i_11_n_0\,
      O => \dec[3]_i_3_n_0\
    );
\dec[3]_i_30\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E3E0FB0C8FCCB2C"
    )
        port map (
      I0 => bin(11),
      I1 => \p_0_in__3\(1),
      I2 => bin(13),
      I3 => \p_0_in__3\(2),
      I4 => \p_0_in__3\(3),
      I5 => bin(12),
      O => \dec[3]_i_30_n_0\
    );
\dec[3]_i_31\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"233266661331C88C"
    )
        port map (
      I0 => \p_0_in__3\(3),
      I1 => bin(13),
      I2 => \mil[3]_i_36_n_0\,
      I3 => bin(14),
      I4 => \p_0_in__3\(2),
      I5 => bin(12),
      O => \p_0_in__5\(2)
    );
\dec[3]_i_32\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A4255A9292A4495A"
    )
        port map (
      I0 => bin(14),
      I1 => bin(19),
      I2 => bin(18),
      I3 => bin(17),
      I4 => bin(16),
      I5 => bin(15),
      O => \p_0_in__3\(1)
    );
\dec[3]_i_33\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"92C3492CC3492C34"
    )
        port map (
      I0 => bin(16),
      I1 => bin(19),
      I2 => bin(17),
      I3 => bin(18),
      I4 => bin(15),
      I5 => bin(14),
      O => \p_0_in__3\(2)
    );
\dec[3]_i_34\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0821104242088410"
    )
        port map (
      I0 => bin(14),
      I1 => bin(15),
      I2 => bin(16),
      I3 => bin(19),
      I4 => bin(18),
      I5 => bin(17),
      O => \p_0_in__3\(3)
    );
\dec[3]_i_4\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"33939333CC3636CC"
    )
        port map (
      I0 => bin(4),
      I1 => \p_0_in__11\(2),
      I2 => bin(5),
      I3 => \dec[3]_i_13_n_0\,
      I4 => bin(6),
      I5 => \un[3]_i_8_n_0\,
      O => \dec[3]_i_4_n_0\
    );
\dec[3]_i_5\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => \dec[3]_i_11_n_0\,
      I1 => \dec[3]_i_10_n_0\,
      O => \dec[3]_i_5_n_0\
    );
\dec[3]_i_6\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"60FF99FFFF66FF60"
    )
        port map (
      I0 => \dec[3]_i_8_n_0\,
      I1 => \dec[3]_i_9_n_0\,
      I2 => \dec[3]_i_4_n_0\,
      I3 => \dec[3]_i_14_n_0\,
      I4 => \dec[3]_i_10_n_0\,
      I5 => \dec[3]_i_11_n_0\,
      O => \dec[3]_i_6_n_0\
    );
\dec[3]_i_7\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"33939333CC3636CC"
    )
        port map (
      I0 => bin(2),
      I1 => \p_0_in__13\(2),
      I2 => bin(3),
      I3 => \un[3]_i_5_n_0\,
      I4 => bin(4),
      I5 => \un[3]_i_4_n_0\,
      O => \dec[3]_i_7_n_0\
    );
\dec[3]_i_8\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \dec[3]_i_9_n_0\,
      I1 => \dec[3]_i_15_n_0\,
      I2 => \dec[3]_i_16_n_0\,
      I3 => \dec[3]_i_17_n_0\,
      I4 => \dec[3]_i_18_n_0\,
      I5 => \cent[3]_i_13_n_0\,
      O => \dec[3]_i_8_n_0\
    );
\dec[3]_i_9\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => bin(6),
      I1 => \p_0_in__8\(1),
      I2 => bin(8),
      I3 => \dec[3]_i_20_n_0\,
      I4 => \p_0_in__8\(2),
      I5 => bin(7),
      O => \dec[3]_i_9_n_0\
    );
\dec_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_1_out(0),
      Q => dec(0),
      R => '0'
    );
\dec_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_1_out(1),
      Q => dec(1),
      R => '0'
    );
\dec_reg[2]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_1_out(2),
      Q => dec(2),
      R => '0'
    );
\dec_reg[3]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_1_out(3),
      Q => dec(3),
      R => '0'
    );
\mil[0]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"4D3AA17C4B3001EC"
    )
        port map (
      I0 => \cent[3]_i_2_n_0\,
      I1 => \cent[3]_i_3_n_0\,
      I2 => \cent[3]_i_4_n_0\,
      I3 => \cent[3]_i_5_n_0\,
      I4 => \cent[3]_i_6_n_0\,
      I5 => \cent[3]_i_7_n_0\,
      O => p_3_out(0)
    );
\mil[1]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"900F0F96690F0F90"
    )
        port map (
      I0 => \mil[3]_i_2_n_0\,
      I1 => \mil[3]_i_3_n_0\,
      I2 => \mil[3]_i_4_n_0\,
      I3 => \mil[3]_i_5_n_0\,
      I4 => \mil[3]_i_6_n_0\,
      I5 => \mil[3]_i_7_n_0\,
      O => p_3_out(1)
    );
\mil[2]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"00F6F00F0FF0F900"
    )
        port map (
      I0 => \mil[3]_i_2_n_0\,
      I1 => \mil[3]_i_3_n_0\,
      I2 => \mil[3]_i_4_n_0\,
      I3 => \mil[3]_i_7_n_0\,
      I4 => \mil[3]_i_6_n_0\,
      I5 => \mil[3]_i_5_n_0\,
      O => p_3_out(2)
    );
\mil[3]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0696990000669606"
    )
        port map (
      I0 => \mil[3]_i_2_n_0\,
      I1 => \mil[3]_i_3_n_0\,
      I2 => \mil[3]_i_4_n_0\,
      I3 => \mil[3]_i_5_n_0\,
      I4 => \mil[3]_i_6_n_0\,
      I5 => \mil[3]_i_7_n_0\,
      O => p_3_out(3)
    );
\mil[3]_i_10\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"6318318C"
    )
        port map (
      I0 => \tril[3]_i_9_n_0\,
      I1 => \tril[3]_i_8_n_0\,
      I2 => \tril[3]_i_10_n_0\,
      I3 => \tril[3]_i_11_n_0\,
      I4 => \bil[3]_i_10_n_0\,
      O => \mil[3]_i_10_n_0\
    );
\mil[3]_i_11\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \cent[3]_i_8_n_0\,
      I1 => \cent[3]_i_20_n_0\,
      I2 => \cent[3]_i_21_n_0\,
      I3 => \cent[3]_i_22_n_0\,
      I4 => \cent[3]_i_23_n_0\,
      I5 => \mil[3]_i_13_n_0\,
      O => \mil[3]_i_11_n_0\
    );
\mil[3]_i_12\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A419941A62955686"
    )
        port map (
      I0 => \cent[3]_i_21_n_0\,
      I1 => \mil[3]_i_23_n_0\,
      I2 => \mil[3]_i_24_n_0\,
      I3 => \mil[3]_i_25_n_0\,
      I4 => \mil[3]_i_26_n_0\,
      I5 => \mil[3]_i_20_n_0\,
      O => \mil[3]_i_12_n_0\
    );
\mil[3]_i_13\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E360FB0C83CCB2C"
    )
        port map (
      I0 => \dec[3]_i_16_n_0\,
      I1 => \mil[3]_i_27_n_0\,
      I2 => \mil[3]_i_28_n_0\,
      I3 => \mil[3]_i_29_n_0\,
      I4 => \mil[3]_i_30_n_0\,
      I5 => \cent[3]_i_19_n_0\,
      O => \mil[3]_i_13_n_0\
    );
\mil[3]_i_14\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E3E0FB0C8FCCB2C"
    )
        port map (
      I0 => \mil[3]_i_13_n_0\,
      I1 => \mil[3]_i_19_n_0\,
      I2 => \mil[3]_i_20_n_0\,
      I3 => \mil[3]_i_21_n_0\,
      I4 => \mil[3]_i_22_n_0\,
      I5 => \cent[3]_i_21_n_0\,
      O => \mil[3]_i_14_n_0\
    );
\mil[3]_i_15\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"281157EA3129C246"
    )
        port map (
      I0 => \mil[3]_i_25_n_0\,
      I1 => \mil[3]_i_23_n_0\,
      I2 => \mil[3]_i_24_n_0\,
      I3 => \mil[3]_i_26_n_0\,
      I4 => \mil[3]_i_20_n_0\,
      I5 => \cent[3]_i_21_n_0\,
      O => \mil[3]_i_15_n_0\
    );
\mil[3]_i_16\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \mil[3]_i_11_n_0\,
      I1 => \bil[3]_i_9_n_0\,
      I2 => \bil[3]_i_10_n_0\,
      I3 => \tril[3]_i_2_n_0\,
      I4 => \bil[3]_i_11_n_0\,
      I5 => \mil[3]_i_9_n_0\,
      O => \mil[3]_i_16_n_0\
    );
\mil[3]_i_17\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => \tril[3]_i_5_n_0\,
      I1 => \mil[3]_i_9_n_0\,
      O => \mil[3]_i_17_n_0\
    );
\mil[3]_i_18\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"9A"
    )
        port map (
      I0 => \mil[3]_i_8_n_0\,
      I1 => \mil[3]_i_9_n_0\,
      I2 => \tril[3]_i_5_n_0\,
      O => \mil[3]_i_18_n_0\
    );
\mil[3]_i_19\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"A51A6186"
    )
        port map (
      I0 => \mil[3]_i_24_n_0\,
      I1 => \bil[3]_i_14_n_0\,
      I2 => \bil[3]_i_13_n_0\,
      I3 => \bil[3]_i_15_n_0\,
      I4 => \bil[3]_i_16_n_0\,
      O => \mil[3]_i_19_n_0\
    );
\mil[3]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \mil[3]_i_3_n_0\,
      I1 => \mil[3]_i_8_n_0\,
      I2 => \mil[3]_i_9_n_0\,
      I3 => \tril[3]_i_5_n_0\,
      I4 => \mil[3]_i_10_n_0\,
      I5 => \mil[3]_i_11_n_0\,
      O => \mil[3]_i_2_n_0\
    );
\mil[3]_i_20\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"33939333CC3636CC"
    )
        port map (
      I0 => \mil[3]_i_28_n_0\,
      I1 => \dec[3]_i_25_n_0\,
      I2 => \dec[3]_i_23_n_0\,
      I3 => \mil[3]_i_31_n_0\,
      I4 => \mil[3]_i_32_n_0\,
      I5 => \dec[3]_i_24_n_0\,
      O => \mil[3]_i_20_n_0\
    );
\mil[3]_i_21\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"6318318C"
    )
        port map (
      I0 => \bil[3]_i_13_n_0\,
      I1 => \bil[3]_i_14_n_0\,
      I2 => \bil[3]_i_15_n_0\,
      I3 => \bil[3]_i_16_n_0\,
      I4 => \mil[3]_i_24_n_0\,
      O => \mil[3]_i_21_n_0\
    );
\mil[3]_i_22\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"21084210"
    )
        port map (
      I0 => \mil[3]_i_24_n_0\,
      I1 => \bil[3]_i_16_n_0\,
      I2 => \bil[3]_i_13_n_0\,
      I3 => \bil[3]_i_14_n_0\,
      I4 => \bil[3]_i_15_n_0\,
      O => \mil[3]_i_22_n_0\
    );
\mil[3]_i_23\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"20CBCD300402CF3C"
    )
        port map (
      I0 => \mil[3]_i_32_n_0\,
      I1 => \mil[3]_i_33_n_0\,
      I2 => \p_0_in__0\(1),
      I3 => \p_0_in__0\(2),
      I4 => \mil[3]_i_36_n_0\,
      I5 => \mil[3]_i_37_n_0\,
      O => \mil[3]_i_23_n_0\
    );
\mil[3]_i_24\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E360FB0C83CCB2C"
    )
        port map (
      I0 => \dec[3]_i_23_n_0\,
      I1 => \mil[3]_i_38_n_0\,
      I2 => \mil[3]_i_37_n_0\,
      I3 => \mil[3]_i_39_n_0\,
      I4 => \mil[3]_i_40_n_0\,
      I5 => \mil[3]_i_32_n_0\,
      O => \mil[3]_i_24_n_0\
    );
\mil[3]_i_25\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"0FB0CB2C"
    )
        port map (
      I0 => \mil[3]_i_24_n_0\,
      I1 => \bil[3]_i_14_n_0\,
      I2 => \bil[3]_i_13_n_0\,
      I3 => \bil[3]_i_15_n_0\,
      I4 => \bil[3]_i_16_n_0\,
      O => \mil[3]_i_25_n_0\
    );
\mil[3]_i_26\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"C03E03E0C07C03E0"
    )
        port map (
      I0 => \mil[3]_i_37_n_0\,
      I1 => \mil[3]_i_36_n_0\,
      I2 => \mil[3]_i_33_n_0\,
      I3 => \p_0_in__0\(1),
      I4 => \p_0_in__0\(2),
      I5 => \mil[3]_i_32_n_0\,
      O => \mil[3]_i_26_n_0\
    );
\mil[3]_i_27\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"A494A51A62566186"
    )
        port map (
      I0 => \dec[3]_i_23_n_0\,
      I1 => \mil[3]_i_38_n_0\,
      I2 => \mil[3]_i_37_n_0\,
      I3 => \mil[3]_i_39_n_0\,
      I4 => \mil[3]_i_40_n_0\,
      I5 => \mil[3]_i_32_n_0\,
      O => \mil[3]_i_27_n_0\
    );
\mil[3]_i_28\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"33939333CC3636CC"
    )
        port map (
      I0 => bin(10),
      I1 => \p_0_in__5\(2),
      I2 => bin(11),
      I3 => \mil[3]_i_41_n_0\,
      I4 => bin(12),
      I5 => \dec[3]_i_30_n_0\,
      O => \mil[3]_i_28_n_0\
    );
\mil[3]_i_29\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"660511F84561981A"
    )
        port map (
      I0 => \mil[3]_i_38_n_0\,
      I1 => \mil[3]_i_37_n_0\,
      I2 => \mil[3]_i_40_n_0\,
      I3 => \mil[3]_i_39_n_0\,
      I4 => \mil[3]_i_32_n_0\,
      I5 => \dec[3]_i_23_n_0\,
      O => \mil[3]_i_29_n_0\
    );
\mil[3]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \cent[3]_i_10_n_0\,
      I1 => \mil[3]_i_12_n_0\,
      I2 => \mil[3]_i_13_n_0\,
      I3 => \mil[3]_i_14_n_0\,
      I4 => \mil[3]_i_15_n_0\,
      I5 => \cent[3]_i_8_n_0\,
      O => \mil[3]_i_3_n_0\
    );
\mil[3]_i_30\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"2008174424011280"
    )
        port map (
      I0 => \dec[3]_i_23_n_0\,
      I1 => \mil[3]_i_32_n_0\,
      I2 => \mil[3]_i_39_n_0\,
      I3 => \mil[3]_i_38_n_0\,
      I4 => \mil[3]_i_37_n_0\,
      I5 => \mil[3]_i_40_n_0\,
      O => \mil[3]_i_30_n_0\
    );
\mil[3]_i_31\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"BB3230FC"
    )
        port map (
      I0 => \mil[3]_i_32_n_0\,
      I1 => \mil[3]_i_39_n_0\,
      I2 => \mil[3]_i_40_n_0\,
      I3 => \mil[3]_i_37_n_0\,
      I4 => \mil[3]_i_38_n_0\,
      O => \mil[3]_i_31_n_0\
    );
\mil[3]_i_32\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"303C9B329B32303C"
    )
        port map (
      I0 => bin(12),
      I1 => \p_0_in__3\(2),
      I2 => \p_0_in__3\(3),
      I3 => bin(13),
      I4 => \mil[3]_i_36_n_0\,
      I5 => bin(14),
      O => \mil[3]_i_32_n_0\
    );
\mil[3]_i_33\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"0FB0CB2C"
    )
        port map (
      I0 => bin(15),
      I1 => bin(18),
      I2 => bin(17),
      I3 => bin(19),
      I4 => bin(16),
      O => \mil[3]_i_33_n_0\
    );
\mil[3]_i_34\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"B02C"
    )
        port map (
      I0 => bin(16),
      I1 => bin(19),
      I2 => bin(18),
      I3 => bin(17),
      O => \p_0_in__0\(1)
    );
\mil[3]_i_35\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"E0"
    )
        port map (
      I0 => bin(17),
      I1 => bin(18),
      I2 => bin(19),
      O => \p_0_in__0\(2)
    );
\mil[3]_i_36\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E8FF038380EE3F0"
    )
        port map (
      I0 => bin(14),
      I1 => bin(19),
      I2 => bin(18),
      I3 => bin(17),
      I4 => bin(16),
      I5 => bin(15),
      O => \mil[3]_i_36_n_0\
    );
\mil[3]_i_37\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"33939333CC3636CC"
    )
        port map (
      I0 => bin(13),
      I1 => \p_0_in__2\(2),
      I2 => bin(14),
      I3 => \mil[3]_i_33_n_0\,
      I4 => bin(15),
      I5 => \mil[3]_i_36_n_0\,
      O => \mil[3]_i_37_n_0\
    );
\mil[3]_i_38\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"20CBCD300402CF3C"
    )
        port map (
      I0 => bin(14),
      I1 => bin(17),
      I2 => bin(18),
      I3 => bin(19),
      I4 => bin(16),
      I5 => bin(15),
      O => \mil[3]_i_38_n_0\
    );
\mil[3]_i_39\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"C03E03E0C07C03E0"
    )
        port map (
      I0 => bin(15),
      I1 => bin(16),
      I2 => bin(17),
      I3 => bin(18),
      I4 => bin(19),
      I5 => bin(14),
      O => \mil[3]_i_39_n_0\
    );
\mil[3]_i_4\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"933336CC"
    )
        port map (
      I0 => \cent[3]_i_2_n_0\,
      I1 => \cent[3]_i_3_n_0\,
      I2 => \cent[3]_i_4_n_0\,
      I3 => \cent[3]_i_5_n_0\,
      I4 => \cent[3]_i_6_n_0\,
      O => \mil[3]_i_4_n_0\
    );
\mil[3]_i_40\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E0000F000301000"
    )
        port map (
      I0 => bin(14),
      I1 => bin(15),
      I2 => bin(18),
      I3 => bin(17),
      I4 => bin(19),
      I5 => bin(16),
      O => \mil[3]_i_40_n_0\
    );
\mil[3]_i_41\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"30FCBB32BB3230FC"
    )
        port map (
      I0 => bin(12),
      I1 => \p_0_in__3\(2),
      I2 => \p_0_in__3\(3),
      I3 => bin(13),
      I4 => \mil[3]_i_36_n_0\,
      I5 => bin(14),
      O => \mil[3]_i_41_n_0\
    );
\mil[3]_i_42\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"6318318C"
    )
        port map (
      I0 => bin(17),
      I1 => bin(18),
      I2 => bin(19),
      I3 => bin(16),
      I4 => bin(15),
      O => \p_0_in__2\(2)
    );
\mil[3]_i_5\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => \mil[3]_i_11_n_0\,
      I1 => \mil[3]_i_16_n_0\,
      I2 => \mil[3]_i_3_n_0\,
      I3 => \mil[3]_i_2_n_0\,
      O => \mil[3]_i_5_n_0\
    );
\mil[3]_i_6\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => \mil[3]_i_7_n_0\,
      I1 => \mil[3]_i_17_n_0\,
      I2 => \mil[3]_i_11_n_0\,
      I3 => \mil[3]_i_16_n_0\,
      I4 => \mil[3]_i_18_n_0\,
      I5 => \mil[3]_i_3_n_0\,
      O => \mil[3]_i_6_n_0\
    );
\mil[3]_i_7\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \cent[3]_i_4_n_0\,
      I1 => \cent[3]_i_16_n_0\,
      I2 => \cent[3]_i_8_n_0\,
      I3 => \cent[3]_i_9_n_0\,
      I4 => \cent[3]_i_17_n_0\,
      I5 => \cent[3]_i_10_n_0\,
      O => \mil[3]_i_7_n_0\
    );
\mil[3]_i_8\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"A51A6186"
    )
        port map (
      I0 => \bil[3]_i_10_n_0\,
      I1 => \tril[3]_i_8_n_0\,
      I2 => \tril[3]_i_9_n_0\,
      I3 => \tril[3]_i_10_n_0\,
      I4 => \tril[3]_i_11_n_0\,
      O => \mil[3]_i_8_n_0\
    );
\mil[3]_i_9\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E360FB0C83CCB2C"
    )
        port map (
      I0 => \mil[3]_i_13_n_0\,
      I1 => \mil[3]_i_19_n_0\,
      I2 => \mil[3]_i_20_n_0\,
      I3 => \mil[3]_i_21_n_0\,
      I4 => \mil[3]_i_22_n_0\,
      I5 => \cent[3]_i_21_n_0\,
      O => \mil[3]_i_9_n_0\
    );
\mil_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_3_out(0),
      Q => mil(0),
      R => '0'
    );
\mil_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_3_out(1),
      Q => mil(1),
      R => '0'
    );
\mil_reg[2]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_3_out(2),
      Q => mil(2),
      R => '0'
    );
\mil_reg[3]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_3_out(3),
      Q => mil(3),
      R => '0'
    );
\quadr[0]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"7800FF0087870000"
    )
        port map (
      I0 => \bil[3]_i_4_n_0\,
      I1 => \tril[2]_i_2_n_0\,
      I2 => \tril[2]_i_3_n_0\,
      I3 => \tril[3]_i_6_n_0\,
      I4 => \tril[2]_i_5_n_0\,
      I5 => \tril[2]_i_6_n_0\,
      O => p_6_out(0)
    );
\quadr[1]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"E3F80000"
    )
        port map (
      I0 => \tril[2]_i_2_n_0\,
      I1 => \tril[3]_i_2_n_0\,
      I2 => \tril[3]_i_3_n_0\,
      I3 => \tril[3]_i_4_n_0\,
      I4 => \tril[2]_i_5_n_0\,
      O => p_6_out(1)
    );
\quadr_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_6_out(0),
      Q => quadr(0),
      R => '0'
    );
\quadr_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_6_out(1),
      Q => quadr(1),
      R => '0'
    );
\tril[0]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E9336B0C8333C2C"
    )
        port map (
      I0 => \bil[3]_i_2_n_0\,
      I1 => \bil[3]_i_3_n_0\,
      I2 => \bil[3]_i_6_n_0\,
      I3 => \bil[3]_i_5_n_0\,
      I4 => \bil[3]_i_4_n_0\,
      I5 => \bil[3]_i_7_n_0\,
      O => p_5_out(0)
    );
\tril[1]_i_1\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => tril1,
      I1 => \tril[2]_i_4_n_0\,
      O => p_5_out(1)
    );
\tril[2]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"8787780000877878"
    )
        port map (
      I0 => \bil[3]_i_4_n_0\,
      I1 => \tril[2]_i_2_n_0\,
      I2 => \tril[2]_i_3_n_0\,
      I3 => \tril[2]_i_4_n_0\,
      I4 => \tril[2]_i_5_n_0\,
      I5 => \tril[2]_i_6_n_0\,
      O => p_5_out(2)
    );
\tril[2]_i_2\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"E9D77FEEA957FFEA"
    )
        port map (
      I0 => \bil[3]_i_8_n_0\,
      I1 => \mil[3]_i_8_n_0\,
      I2 => \mil[3]_i_9_n_0\,
      I3 => \tril[2]_i_7_n_0\,
      I4 => \mil[3]_i_10_n_0\,
      I5 => \mil[3]_i_11_n_0\,
      O => \tril[2]_i_2_n_0\
    );
\tril[2]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"CDF3320C320C320C"
    )
        port map (
      I0 => \tril[3]_i_11_n_0\,
      I1 => \tril[3]_i_10_n_0\,
      I2 => \tril[3]_i_9_n_0\,
      I3 => \tril[3]_i_8_n_0\,
      I4 => \bil[3]_i_8_n_0\,
      I5 => \tril[2]_i_8_n_0\,
      O => \tril[2]_i_3_n_0\
    );
\tril[2]_i_4\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E8FF038380EE3F0"
    )
        port map (
      I0 => \bil[3]_i_7_n_0\,
      I1 => \tril[3]_i_4_n_0\,
      I2 => \tril[3]_i_3_n_0\,
      I3 => \tril[3]_i_2_n_0\,
      I4 => \tril[3]_i_5_n_0\,
      I5 => \bil[3]_i_6_n_0\,
      O => \tril[2]_i_4_n_0\
    );
\tril[2]_i_5\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"FF3CFB2C00000000"
    )
        port map (
      I0 => \tril[3]_i_11_n_0\,
      I1 => \tril[3]_i_10_n_0\,
      I2 => \tril[3]_i_9_n_0\,
      I3 => \tril[3]_i_8_n_0\,
      I4 => \bil[3]_i_10_n_0\,
      I5 => \tril[3]_i_4_n_0\,
      O => \tril[2]_i_5_n_0\
    );
\tril[2]_i_6\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"A02C"
    )
        port map (
      I0 => \tril[2]_i_8_n_0\,
      I1 => \tril[3]_i_4_n_0\,
      I2 => \tril[3]_i_3_n_0\,
      I3 => \tril[3]_i_2_n_0\,
      O => \tril[2]_i_6_n_0\
    );
\tril[2]_i_7\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"21084210"
    )
        port map (
      I0 => \bil[3]_i_10_n_0\,
      I1 => \tril[3]_i_11_n_0\,
      I2 => \tril[3]_i_9_n_0\,
      I3 => \tril[3]_i_8_n_0\,
      I4 => \tril[3]_i_10_n_0\,
      O => \tril[2]_i_7_n_0\
    );
\tril[2]_i_8\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"F9CFF3FCF18FE3F8"
    )
        port map (
      I0 => \bil[3]_i_10_n_0\,
      I1 => \tril[3]_i_11_n_0\,
      I2 => \tril[3]_i_9_n_0\,
      I3 => \tril[3]_i_8_n_0\,
      I4 => \tril[3]_i_10_n_0\,
      I5 => \mil[3]_i_9_n_0\,
      O => \tril[2]_i_8_n_0\
    );
\tril[3]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"E3E71C181C181C18"
    )
        port map (
      I0 => \tril[3]_i_2_n_0\,
      I1 => \tril[3]_i_3_n_0\,
      I2 => \tril[3]_i_4_n_0\,
      I3 => \tril[3]_i_5_n_0\,
      I4 => \tril[3]_i_6_n_0\,
      I5 => tril1,
      O => p_5_out(3)
    );
\tril[3]_i_10\: unisim.vcomponents.LUT3
    generic map(
      INIT => X"E0"
    )
        port map (
      I0 => \bil[3]_i_14_n_0\,
      I1 => \bil[3]_i_13_n_0\,
      I2 => \bil[3]_i_15_n_0\,
      O => \tril[3]_i_10_n_0\
    );
\tril[3]_i_11\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E8FF038380EE3F0"
    )
        port map (
      I0 => \mil[3]_i_20_n_0\,
      I1 => \bil[3]_i_15_n_0\,
      I2 => \bil[3]_i_14_n_0\,
      I3 => \bil[3]_i_13_n_0\,
      I4 => \bil[3]_i_16_n_0\,
      I5 => \mil[3]_i_24_n_0\,
      O => \tril[3]_i_11_n_0\
    );
\tril[3]_i_12\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"320C"
    )
        port map (
      I0 => \bil[3]_i_16_n_0\,
      I1 => \bil[3]_i_15_n_0\,
      I2 => \bil[3]_i_13_n_0\,
      I3 => \bil[3]_i_14_n_0\,
      O => \tril[3]_i_12_n_0\
    );
\tril[3]_i_13\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"F9CFF3FCF18FE3F8"
    )
        port map (
      I0 => \mil[3]_i_24_n_0\,
      I1 => \bil[3]_i_16_n_0\,
      I2 => \bil[3]_i_13_n_0\,
      I3 => \bil[3]_i_14_n_0\,
      I4 => \bil[3]_i_15_n_0\,
      I5 => \mil[3]_i_20_n_0\,
      O => \tril[3]_i_13_n_0\
    );
\tril[3]_i_14\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"FFEF0EF0"
    )
        port map (
      I0 => \mil[3]_i_23_n_0\,
      I1 => \mil[3]_i_24_n_0\,
      I2 => \bil[3]_i_15_n_0\,
      I3 => \bil[3]_i_13_n_0\,
      I4 => \bil[3]_i_14_n_0\,
      O => \tril[3]_i_14_n_0\
    );
\tril[3]_i_15\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"F9CFF3FCF18FE3F8"
    )
        port map (
      I0 => \mil[3]_i_37_n_0\,
      I1 => \mil[3]_i_36_n_0\,
      I2 => \mil[3]_i_33_n_0\,
      I3 => \p_0_in__0\(1),
      I4 => \p_0_in__0\(2),
      I5 => \mil[3]_i_32_n_0\,
      O => \tril[3]_i_15_n_0\
    );
\tril[3]_i_2\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"0FB0CB2C"
    )
        port map (
      I0 => \bil[3]_i_10_n_0\,
      I1 => \tril[3]_i_8_n_0\,
      I2 => \tril[3]_i_9_n_0\,
      I3 => \tril[3]_i_10_n_0\,
      I4 => \tril[3]_i_11_n_0\,
      O => \tril[3]_i_2_n_0\
    );
\tril[3]_i_3\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"8878"
    )
        port map (
      I0 => \tril[3]_i_12_n_0\,
      I1 => \tril[3]_i_13_n_0\,
      I2 => \tril[3]_i_10_n_0\,
      I3 => \tril[3]_i_14_n_0\,
      O => \tril[3]_i_3_n_0\
    );
\tril[3]_i_4\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"8"
    )
        port map (
      I0 => \tril[3]_i_14_n_0\,
      I1 => \tril[3]_i_10_n_0\,
      O => \tril[3]_i_4_n_0\
    );
\tril[3]_i_5\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0E8FF038380EE3F0"
    )
        port map (
      I0 => \mil[3]_i_9_n_0\,
      I1 => \tril[3]_i_10_n_0\,
      I2 => \tril[3]_i_8_n_0\,
      I3 => \tril[3]_i_9_n_0\,
      I4 => \tril[3]_i_11_n_0\,
      I5 => \bil[3]_i_10_n_0\,
      O => \tril[3]_i_5_n_0\
    );
\tril[3]_i_6\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"EFCFCBCEC3FCF3BC"
    )
        port map (
      I0 => \bil[3]_i_7_n_0\,
      I1 => \tril[3]_i_2_n_0\,
      I2 => \tril[3]_i_3_n_0\,
      I3 => \tril[3]_i_4_n_0\,
      I4 => \bil[3]_i_6_n_0\,
      I5 => \tril[3]_i_5_n_0\,
      O => \tril[3]_i_6_n_0\
    );
\tril[3]_i_7\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0FC00FC00FC03F80"
    )
        port map (
      I0 => \bil[3]_i_7_n_0\,
      I1 => \tril[3]_i_2_n_0\,
      I2 => \tril[3]_i_3_n_0\,
      I3 => \tril[3]_i_4_n_0\,
      I4 => \tril[3]_i_5_n_0\,
      I5 => \bil[3]_i_6_n_0\,
      O => tril1
    );
\tril[3]_i_8\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"A02C"
    )
        port map (
      I0 => \tril[3]_i_15_n_0\,
      I1 => \bil[3]_i_15_n_0\,
      I2 => \bil[3]_i_14_n_0\,
      I3 => \bil[3]_i_13_n_0\,
      O => \tril[3]_i_8_n_0\
    );
\tril[3]_i_9\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"00EFEE00F0EE0EF0"
    )
        port map (
      I0 => \mil[3]_i_23_n_0\,
      I1 => \mil[3]_i_24_n_0\,
      I2 => \bil[3]_i_14_n_0\,
      I3 => \bil[3]_i_13_n_0\,
      I4 => \bil[3]_i_15_n_0\,
      I5 => \bil[3]_i_16_n_0\,
      O => \tril[3]_i_9_n_0\
    );
\tril_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_5_out(0),
      Q => tril(0),
      R => '0'
    );
\tril_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_5_out(1),
      Q => tril(1),
      R => '0'
    );
\tril_reg[2]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_5_out(2),
      Q => tril(2),
      R => '0'
    );
\tril_reg[3]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_5_out(3),
      Q => tril(3),
      R => '0'
    );
\un[1]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"9615159656949456"
    )
        port map (
      I0 => bin(1),
      I1 => \p_0_in__14\(2),
      I2 => \un[3]_i_3_n_0\,
      I3 => \un[3]_i_4_n_0\,
      I4 => bin(3),
      I5 => bin(2),
      O => p_0_out(1)
    );
\un[2]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"296C39683968296C"
    )
        port map (
      I0 => bin(1),
      I1 => bin(2),
      I2 => \un[3]_i_3_n_0\,
      I3 => \p_0_in__14\(2),
      I4 => \un[3]_i_4_n_0\,
      I5 => bin(3),
      O => p_0_out(2)
    );
\un[3]_i_1\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"2C50502C08353508"
    )
        port map (
      I0 => bin(1),
      I1 => \p_0_in__14\(2),
      I2 => \un[3]_i_3_n_0\,
      I3 => \un[3]_i_4_n_0\,
      I4 => bin(3),
      I5 => bin(2),
      O => p_0_out(3)
    );
\un[3]_i_10\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"3FB3B33FCCFEFECC"
    )
        port map (
      I0 => bin(7),
      I1 => \p_0_in__8\(2),
      I2 => bin(8),
      I3 => \cent[3]_i_24_n_0\,
      I4 => bin(9),
      I5 => \dec[3]_i_20_n_0\,
      O => \un[3]_i_10_n_0\
    );
\un[3]_i_11\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => bin(9),
      I1 => \cent[3]_i_24_n_0\,
      I2 => bin(8),
      I3 => \dec[3]_i_20_n_0\,
      O => \p_0_in__9\(2)
    );
\un[3]_i_2\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => bin(4),
      I1 => \un[3]_i_5_n_0\,
      I2 => bin(3),
      I3 => \un[3]_i_4_n_0\,
      O => \p_0_in__14\(2)
    );
\un[3]_i_3\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"3FB3B33FCCFEFECC"
    )
        port map (
      I0 => bin(2),
      I1 => \p_0_in__13\(2),
      I2 => bin(3),
      I3 => \un[3]_i_5_n_0\,
      I4 => bin(4),
      I5 => \un[3]_i_4_n_0\,
      O => \un[3]_i_3_n_0\
    );
\un[3]_i_4\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"3FB3B33FCCFEFECC"
    )
        port map (
      I0 => bin(3),
      I1 => \p_0_in__12\(2),
      I2 => bin(4),
      I3 => \un[3]_i_8_n_0\,
      I4 => bin(5),
      I5 => \un[3]_i_5_n_0\,
      O => \un[3]_i_4_n_0\
    );
\un[3]_i_5\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"3FB3B33FCCFEFECC"
    )
        port map (
      I0 => bin(4),
      I1 => \p_0_in__11\(2),
      I2 => bin(5),
      I3 => \dec[3]_i_13_n_0\,
      I4 => bin(6),
      I5 => \un[3]_i_8_n_0\,
      O => \un[3]_i_5_n_0\
    );
\un[3]_i_6\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => bin(5),
      I1 => \un[3]_i_8_n_0\,
      I2 => bin(4),
      I3 => \un[3]_i_5_n_0\,
      O => \p_0_in__13\(2)
    );
\un[3]_i_7\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"6966"
    )
        port map (
      I0 => bin(6),
      I1 => \dec[3]_i_13_n_0\,
      I2 => bin(5),
      I3 => \un[3]_i_8_n_0\,
      O => \p_0_in__12\(2)
    );
\un[3]_i_8\: unisim.vcomponents.LUT6
    generic map(
      INIT => X"0EB33EB0C83FFC2C"
    )
        port map (
      I0 => bin(5),
      I1 => \p_0_in__9\(1),
      I2 => bin(7),
      I3 => \un[3]_i_10_n_0\,
      I4 => \p_0_in__9\(2),
      I5 => bin(6),
      O => \un[3]_i_8_n_0\
    );
\un[3]_i_9\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"6"
    )
        port map (
      I0 => \dec[3]_i_20_n_0\,
      I1 => bin(8),
      O => \p_0_in__9\(1)
    );
\un_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => bin(0),
      Q => un(0),
      R => '0'
    );
\un_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_0_out(1),
      Q => un(1),
      R => '0'
    );
\un_reg[2]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_0_out(2),
      Q => un(2),
      R => '0'
    );
\un_reg[3]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => p_0_out(3),
      Q => un(3),
      R => '0'
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_BinToBCD_0_0 is
  port (
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
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of design_1_BinToBCD_0_0 : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_BinToBCD_0_0 : entity is "design_1_BinToBCD_0_0,BinToBCD,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_BinToBCD_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_BinToBCD_0_0 : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of design_1_BinToBCD_0_0 : entity is "BinToBCD,Vivado 2024.2";
end design_1_BinToBCD_0_0;

architecture STRUCTURE of design_1_BinToBCD_0_0 is
  signal \<const0>\ : STD_LOGIC;
  signal \^quadr\ : STD_LOGIC_VECTOR ( 1 downto 0 );
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of clk : signal is "xilinx.com:signal:clock:1.0 clk CLK";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of clk : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of clk : signal is "XIL_INTERFACENAME clk, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN design_1_CLK100MHZ, INSERT_VIP 0";
begin
  quadr(3) <= \<const0>\;
  quadr(2) <= \<const0>\;
  quadr(1 downto 0) <= \^quadr\(1 downto 0);
  quint(3) <= \<const0>\;
  quint(2) <= \<const0>\;
  quint(1) <= \<const0>\;
  quint(0) <= \<const0>\;
GND: unisim.vcomponents.GND
     port map (
      G => \<const0>\
    );
inst: entity work.design_1_BinToBCD_0_0_BinToBCD
     port map (
      bil(3 downto 0) => bil(3 downto 0),
      bin(19 downto 0) => bin(19 downto 0),
      cent(3 downto 0) => cent(3 downto 0),
      clk => clk,
      dec(3 downto 0) => dec(3 downto 0),
      mil(3 downto 0) => mil(3 downto 0),
      quadr(1 downto 0) => \^quadr\(1 downto 0),
      tril(3 downto 0) => tril(3 downto 0),
      un(3 downto 0) => un(3 downto 0)
    );
end STRUCTURE;
