-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
-- Date        : Fri Apr 25 13:46:59 2025
-- Host        : alisson.lesc.ufc.br running 64-bit unknown
-- Command     : write_vhdl -force -mode funcsim
--               /home/alisson/Downloads/aging_mirai_tensao/Aging-dynamic/vivado_project/aging-study/aging-study.gen/sources_1/bd/design_1/ip/design_1_not_series_0_0/design_1_not_series_0_0_sim_netlist.vhdl
-- Design      : design_1_not_series_0_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a100tcsg324-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_not_series_0_0_not_series is
  port (
    start : out STD_LOGIC;
    critpath : out STD_LOGIC;
    test_bit : in STD_LOGIC;
    clk : in STD_LOGIC
  );
  attribute ORIG_REF_NAME : string;
  attribute ORIG_REF_NAME of design_1_not_series_0_0_not_series : entity is "not_series";
end design_1_not_series_0_0_not_series;

architecture STRUCTURE of design_1_not_series_0_0_not_series is
  signal connection_1 : STD_LOGIC;
  signal connection_10 : STD_LOGIC;
  signal connection_11 : STD_LOGIC;
  signal connection_12 : STD_LOGIC;
  signal connection_13 : STD_LOGIC;
  signal connection_14 : STD_LOGIC;
  signal connection_15 : STD_LOGIC;
  signal connection_16 : STD_LOGIC;
  signal connection_17 : STD_LOGIC;
  signal connection_18 : STD_LOGIC;
  signal connection_19 : STD_LOGIC;
  signal connection_2 : STD_LOGIC;
  signal connection_20 : STD_LOGIC;
  signal connection_21 : STD_LOGIC;
  signal connection_22 : STD_LOGIC;
  signal connection_23 : STD_LOGIC;
  signal connection_24 : STD_LOGIC;
  signal connection_25 : STD_LOGIC;
  signal connection_26 : STD_LOGIC;
  signal connection_27 : STD_LOGIC;
  signal connection_28 : STD_LOGIC;
  signal connection_29 : STD_LOGIC;
  signal connection_3 : STD_LOGIC;
  signal connection_30 : STD_LOGIC;
  signal connection_31 : STD_LOGIC;
  signal connection_32 : STD_LOGIC;
  signal connection_33 : STD_LOGIC;
  signal connection_34 : STD_LOGIC;
  signal connection_35 : STD_LOGIC;
  signal connection_36 : STD_LOGIC;
  signal connection_37 : STD_LOGIC;
  signal connection_38 : STD_LOGIC;
  signal connection_39 : STD_LOGIC;
  signal connection_4 : STD_LOGIC;
  signal connection_40 : STD_LOGIC;
  signal connection_41 : STD_LOGIC;
  signal connection_42 : STD_LOGIC;
  signal connection_43 : STD_LOGIC;
  signal connection_44 : STD_LOGIC;
  signal connection_45 : STD_LOGIC;
  signal connection_46 : STD_LOGIC;
  signal connection_47 : STD_LOGIC;
  signal connection_48 : STD_LOGIC;
  signal connection_49 : STD_LOGIC;
  signal connection_5 : STD_LOGIC;
  signal connection_6 : STD_LOGIC;
  signal connection_7 : STD_LOGIC;
  signal connection_8 : STD_LOGIC;
  signal connection_9 : STD_LOGIC;
  signal \^start\ : STD_LOGIC;
  attribute BOX_TYPE : string;
  attribute BOX_TYPE of \genblk1[0].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH : boolean;
  attribute DONT_TOUCH of \genblk1[0].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM : string;
  attribute XILINX_LEGACY_PRIM of \genblk1[0].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP : string;
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[0].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[10].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[10].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[10].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[10].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[11].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[11].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[11].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[11].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[12].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[12].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[12].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[12].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[13].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[13].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[13].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[13].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[14].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[14].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[14].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[14].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[15].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[15].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[15].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[15].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[16].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[16].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[16].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[16].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[17].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[17].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[17].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[17].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[18].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[18].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[18].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[18].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[19].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[19].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[19].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[19].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[1].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[1].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[1].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[1].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[20].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[20].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[20].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[20].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[21].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[21].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[21].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[21].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[22].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[22].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[22].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[22].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[23].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[23].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[23].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[23].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[24].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[24].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[24].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[24].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[25].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[25].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[25].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[25].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[26].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[26].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[26].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[26].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[27].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[27].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[27].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[27].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[28].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[28].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[28].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[28].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[29].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[29].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[29].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[29].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[2].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[2].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[2].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[2].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[30].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[30].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[30].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[30].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[31].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[31].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[31].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[31].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[32].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[32].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[32].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[32].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[33].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[33].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[33].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[33].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[34].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[34].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[34].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[34].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[35].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[35].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[35].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[35].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[36].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[36].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[36].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[36].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[37].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[37].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[37].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[37].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[38].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[38].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[38].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[38].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[39].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[39].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[39].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[39].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[3].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[3].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[3].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[3].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[40].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[40].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[40].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[40].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[41].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[41].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[41].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[41].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[42].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[42].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[42].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[42].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[43].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[43].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[43].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[43].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[44].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[44].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[44].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[44].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[45].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[45].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[45].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[45].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[46].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[46].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[46].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[46].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[47].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[47].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[47].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[47].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[48].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[48].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[48].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[48].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[49].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[49].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[49].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[49].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[4].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[4].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[4].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[4].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[5].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[5].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[5].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[5].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[6].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[6].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[6].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[6].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[7].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[7].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[7].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[7].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[8].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[8].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[8].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[8].INV\ : label is "LO:O";
  attribute BOX_TYPE of \genblk1[9].INV\ : label is "PRIMITIVE";
  attribute DONT_TOUCH of \genblk1[9].INV\ : label is std.standard.true;
  attribute XILINX_LEGACY_PRIM of \genblk1[9].INV\ : label is "LUT1_L";
  attribute XILINX_TRANSFORM_PINMAP of \genblk1[9].INV\ : label is "LO:O";
begin
  start <= \^start\;
\genblk1[0].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => \^start\,
      O => connection_1
    );
\genblk1[10].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_10,
      O => connection_11
    );
\genblk1[11].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_11,
      O => connection_12
    );
\genblk1[12].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_12,
      O => connection_13
    );
\genblk1[13].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_13,
      O => connection_14
    );
\genblk1[14].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_14,
      O => connection_15
    );
\genblk1[15].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_15,
      O => connection_16
    );
\genblk1[16].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_16,
      O => connection_17
    );
\genblk1[17].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_17,
      O => connection_18
    );
\genblk1[18].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_18,
      O => connection_19
    );
\genblk1[19].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_19,
      O => connection_20
    );
\genblk1[1].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_1,
      O => connection_2
    );
\genblk1[20].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_20,
      O => connection_21
    );
\genblk1[21].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_21,
      O => connection_22
    );
\genblk1[22].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_22,
      O => connection_23
    );
\genblk1[23].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_23,
      O => connection_24
    );
\genblk1[24].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_24,
      O => connection_25
    );
\genblk1[25].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_25,
      O => connection_26
    );
\genblk1[26].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_26,
      O => connection_27
    );
\genblk1[27].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_27,
      O => connection_28
    );
\genblk1[28].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_28,
      O => connection_29
    );
\genblk1[29].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_29,
      O => connection_30
    );
\genblk1[2].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_2,
      O => connection_3
    );
\genblk1[30].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_30,
      O => connection_31
    );
\genblk1[31].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_31,
      O => connection_32
    );
\genblk1[32].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_32,
      O => connection_33
    );
\genblk1[33].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_33,
      O => connection_34
    );
\genblk1[34].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_34,
      O => connection_35
    );
\genblk1[35].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_35,
      O => connection_36
    );
\genblk1[36].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_36,
      O => connection_37
    );
\genblk1[37].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_37,
      O => connection_38
    );
\genblk1[38].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_38,
      O => connection_39
    );
\genblk1[39].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_39,
      O => connection_40
    );
\genblk1[3].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_3,
      O => connection_4
    );
\genblk1[40].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_40,
      O => connection_41
    );
\genblk1[41].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_41,
      O => connection_42
    );
\genblk1[42].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_42,
      O => connection_43
    );
\genblk1[43].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_43,
      O => connection_44
    );
\genblk1[44].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_44,
      O => connection_45
    );
\genblk1[45].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_45,
      O => connection_46
    );
\genblk1[46].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_46,
      O => connection_47
    );
\genblk1[47].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_47,
      O => connection_48
    );
\genblk1[48].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_48,
      O => connection_49
    );
\genblk1[49].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_49,
      O => critpath
    );
\genblk1[4].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_4,
      O => connection_5
    );
\genblk1[5].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_5,
      O => connection_6
    );
\genblk1[6].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_6,
      O => connection_7
    );
\genblk1[7].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_7,
      O => connection_8
    );
\genblk1[8].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_8,
      O => connection_9
    );
\genblk1[9].INV\: unisim.vcomponents.LUT1
    generic map(
      INIT => X"1"
    )
        port map (
      I0 => connection_9,
      O => connection_10
    );
start_reg: unisim.vcomponents.FDRE
     port map (
      C => clk,
      CE => '1',
      D => test_bit,
      Q => \^start\,
      R => '0'
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity design_1_not_series_0_0 is
  port (
    clk : in STD_LOGIC;
    test_bit : in STD_LOGIC;
    start : out STD_LOGIC;
    critpath : out STD_LOGIC
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of design_1_not_series_0_0 : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of design_1_not_series_0_0 : entity is "design_1_not_series_0_0,not_series,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of design_1_not_series_0_0 : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of design_1_not_series_0_0 : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of design_1_not_series_0_0 : entity is "not_series,Vivado 2024.2";
end design_1_not_series_0_0;

architecture STRUCTURE of design_1_not_series_0_0 is
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of clk : signal is "xilinx.com:signal:clock:1.0 clk CLK";
  attribute X_INTERFACE_MODE : string;
  attribute X_INTERFACE_MODE of clk : signal is "slave";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of clk : signal is "XIL_INTERFACENAME clk, FREQ_HZ 60000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN /clk_wiz_0_clk_out1, INSERT_VIP 0";
begin
inst: entity work.design_1_not_series_0_0_not_series
     port map (
      clk => clk,
      critpath => critpath,
      start => start,
      test_bit => test_bit
    );
end STRUCTURE;
