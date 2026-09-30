-- Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2025.2.1 (lin64) Build 6403652 Thu Mar 19 13:47:00 MDT 2026
-- Date        : Thu Jun 11 11:44:27 2026
-- Host        : marceau-lesc running 64-bit Linux Mint 22.3
-- Command     : write_vhdl -force -mode funcsim
--               /home/marceau/Documents/GitHub/IC-Aging-Environment/vivado/aging_study_nexys4ddr/src/ip/clk_wiz_0/clk_wiz_0_sim_netlist.vhdl
-- Design      : clk_wiz_0
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xcau15p-ubva368-2-e
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity clk_wiz_0_clk_wiz is
  port (
    clk_en : out STD_LOGIC;
    sensor0 : out STD_LOGIC;
    clk_sys : out STD_LOGIC;
    locked : out STD_LOGIC;
    reset : in STD_LOGIC;
    clk_in1 : in STD_LOGIC;
    psclk : in STD_LOGIC;
    psen : in STD_LOGIC;
    psincdec : in STD_LOGIC;
    psdone : out STD_LOGIC
  );
end clk_wiz_0_clk_wiz;

architecture STRUCTURE of clk_wiz_0_clk_wiz is
  signal clk_in1_buf : STD_LOGIC;
  signal clkfbout : STD_LOGIC;
  signal clkfbout_buf : STD_LOGIC;
  signal clkout0 : STD_LOGIC;
  signal clkout1 : STD_LOGIC;
  signal clkout2 : STD_LOGIC;
  signal NLW_mmcm_inst_CDDCDONE_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKFBOUTB_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKFBSTOPPED_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKINSTOPPED_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKOUT0B_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKOUT1B_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKOUT2B_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKOUT3_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKOUT3B_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKOUT4_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKOUT5_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_CLKOUT6_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_DRDY_UNCONNECTED : STD_LOGIC;
  signal NLW_mmcm_inst_DO_UNCONNECTED : STD_LOGIC_VECTOR ( 15 downto 0 );
  attribute BOX_TYPE : string;
  attribute BOX_TYPE of clkfb_buf : label is "PRIMITIVE";
  attribute XILINX_LEGACY_PRIM : string;
  attribute XILINX_LEGACY_PRIM of clkfb_buf : label is "BUFG";
  attribute XILINX_TRANSFORM_PINMAP : string;
  attribute XILINX_TRANSFORM_PINMAP of clkfb_buf : label is "VCC:CE";
  attribute BOX_TYPE of clkin1_ibuf : label is "PRIMITIVE";
  attribute CAPACITANCE : string;
  attribute CAPACITANCE of clkin1_ibuf : label is "DONT_CARE";
  attribute IBUF_DELAY_VALUE : string;
  attribute IBUF_DELAY_VALUE of clkin1_ibuf : label is "0";
  attribute IFD_DELAY_VALUE : string;
  attribute IFD_DELAY_VALUE of clkin1_ibuf : label is "AUTO";
  attribute BOX_TYPE of clkout0_buf : label is "PRIMITIVE";
  attribute XILINX_LEGACY_PRIM of clkout0_buf : label is "BUFG";
  attribute XILINX_TRANSFORM_PINMAP of clkout0_buf : label is "VCC:CE";
  attribute BOX_TYPE of clkout1_buf : label is "PRIMITIVE";
  attribute XILINX_LEGACY_PRIM of clkout1_buf : label is "BUFG";
  attribute XILINX_TRANSFORM_PINMAP of clkout1_buf : label is "VCC:CE";
  attribute BOX_TYPE of clkout2_buf : label is "PRIMITIVE";
  attribute XILINX_LEGACY_PRIM of clkout2_buf : label is "BUFG";
  attribute XILINX_TRANSFORM_PINMAP of clkout2_buf : label is "VCC:CE";
  attribute BOX_TYPE of mmcm_inst : label is "PRIMITIVE";
  attribute XILINX_LEGACY_PRIM of mmcm_inst : label is "MMCME2_ADV";
  attribute XILINX_TRANSFORM_PINMAP of mmcm_inst : label is "GND:CDDCREQ";
begin
clkfb_buf: unisim.vcomponents.BUFGCE
    generic map(
      CE_TYPE => "ASYNC",
      SIM_DEVICE => "ULTRASCALE_PLUS"
    )
        port map (
      CE => '1',
      I => clkfbout,
      O => clkfbout_buf
    );
clkin1_ibuf: unisim.vcomponents.IBUF
    generic map(
      IOSTANDARD => "DEFAULT"
    )
        port map (
      I => clk_in1,
      O => clk_in1_buf
    );
clkout0_buf: unisim.vcomponents.BUFGCE
    generic map(
      CE_TYPE => "ASYNC",
      SIM_DEVICE => "ULTRASCALE_PLUS"
    )
        port map (
      CE => '1',
      I => clkout0,
      O => clk_en
    );
clkout1_buf: unisim.vcomponents.BUFGCE
    generic map(
      CE_TYPE => "ASYNC",
      SIM_DEVICE => "ULTRASCALE_PLUS"
    )
        port map (
      CE => '1',
      I => clkout1,
      O => sensor0
    );
clkout2_buf: unisim.vcomponents.BUFGCE
    generic map(
      CE_TYPE => "ASYNC",
      SIM_DEVICE => "ULTRASCALE_PLUS"
    )
        port map (
      CE => '1',
      I => clkout2,
      O => clk_sys
    );
mmcm_inst: unisim.vcomponents.MMCME4_ADV
    generic map(
      BANDWIDTH => "OPTIMIZED",
      CLKFBOUT_MULT_F => 10.000000,
      CLKFBOUT_PHASE => 0.000000,
      CLKFBOUT_USE_FINE_PS => "FALSE",
      CLKIN1_PERIOD => 10.000000,
      CLKIN2_PERIOD => 0.000000,
      CLKOUT0_DIVIDE_F => 10.000000,
      CLKOUT0_DUTY_CYCLE => 0.500000,
      CLKOUT0_PHASE => 99.000000,
      CLKOUT0_USE_FINE_PS => "FALSE",
      CLKOUT1_DIVIDE => 10,
      CLKOUT1_DUTY_CYCLE => 0.500000,
      CLKOUT1_PHASE => 0.000000,
      CLKOUT1_USE_FINE_PS => "TRUE",
      CLKOUT2_DIVIDE => 10,
      CLKOUT2_DUTY_CYCLE => 0.500000,
      CLKOUT2_PHASE => 0.000000,
      CLKOUT2_USE_FINE_PS => "FALSE",
      CLKOUT3_DIVIDE => 1,
      CLKOUT3_DUTY_CYCLE => 0.500000,
      CLKOUT3_PHASE => 0.000000,
      CLKOUT3_USE_FINE_PS => "FALSE",
      CLKOUT4_CASCADE => "FALSE",
      CLKOUT4_DIVIDE => 1,
      CLKOUT4_DUTY_CYCLE => 0.500000,
      CLKOUT4_PHASE => 0.000000,
      CLKOUT4_USE_FINE_PS => "FALSE",
      CLKOUT5_DIVIDE => 1,
      CLKOUT5_DUTY_CYCLE => 0.500000,
      CLKOUT5_PHASE => 0.000000,
      CLKOUT5_USE_FINE_PS => "FALSE",
      CLKOUT6_DIVIDE => 1,
      CLKOUT6_DUTY_CYCLE => 0.500000,
      CLKOUT6_PHASE => 0.000000,
      CLKOUT6_USE_FINE_PS => "FALSE",
      COMPENSATION => "ZHOLD",
      DIVCLK_DIVIDE => 1,
      IS_CLKINSEL_INVERTED => '0',
      IS_PSEN_INVERTED => '0',
      IS_PSINCDEC_INVERTED => '0',
      IS_PWRDWN_INVERTED => '0',
      IS_RST_INVERTED => '0',
      REF_JITTER1 => 0.010000,
      REF_JITTER2 => 0.010000,
      SS_EN => "FALSE",
      SS_MODE => "CENTER_HIGH",
      SS_MOD_PERIOD => 10000,
      STARTUP_WAIT => "FALSE"
    )
        port map (
      CDDCDONE => NLW_mmcm_inst_CDDCDONE_UNCONNECTED,
      CDDCREQ => '0',
      CLKFBIN => clkfbout_buf,
      CLKFBOUT => clkfbout,
      CLKFBOUTB => NLW_mmcm_inst_CLKFBOUTB_UNCONNECTED,
      CLKFBSTOPPED => NLW_mmcm_inst_CLKFBSTOPPED_UNCONNECTED,
      CLKIN1 => clk_in1_buf,
      CLKIN2 => '0',
      CLKINSEL => '1',
      CLKINSTOPPED => NLW_mmcm_inst_CLKINSTOPPED_UNCONNECTED,
      CLKOUT0 => clkout0,
      CLKOUT0B => NLW_mmcm_inst_CLKOUT0B_UNCONNECTED,
      CLKOUT1 => clkout1,
      CLKOUT1B => NLW_mmcm_inst_CLKOUT1B_UNCONNECTED,
      CLKOUT2 => clkout2,
      CLKOUT2B => NLW_mmcm_inst_CLKOUT2B_UNCONNECTED,
      CLKOUT3 => NLW_mmcm_inst_CLKOUT3_UNCONNECTED,
      CLKOUT3B => NLW_mmcm_inst_CLKOUT3B_UNCONNECTED,
      CLKOUT4 => NLW_mmcm_inst_CLKOUT4_UNCONNECTED,
      CLKOUT5 => NLW_mmcm_inst_CLKOUT5_UNCONNECTED,
      CLKOUT6 => NLW_mmcm_inst_CLKOUT6_UNCONNECTED,
      DADDR(6 downto 0) => B"0000000",
      DCLK => '0',
      DEN => '0',
      DI(15 downto 0) => B"0000000000000000",
      DO(15 downto 0) => NLW_mmcm_inst_DO_UNCONNECTED(15 downto 0),
      DRDY => NLW_mmcm_inst_DRDY_UNCONNECTED,
      DWE => '0',
      LOCKED => locked,
      PSCLK => psclk,
      PSDONE => psdone,
      PSEN => psen,
      PSINCDEC => psincdec,
      PWRDWN => '0',
      RST => reset
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity clk_wiz_0 is
  port (
    clk_en : out STD_LOGIC;
    sensor0 : out STD_LOGIC;
    clk_sys : out STD_LOGIC;
    reset : in STD_LOGIC;
    locked : out STD_LOGIC;
    clk_in1 : in STD_LOGIC;
    psclk : in STD_LOGIC;
    psen : in STD_LOGIC;
    psincdec : in STD_LOGIC;
    psdone : out STD_LOGIC
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of clk_wiz_0 : entity is true;
end clk_wiz_0;

architecture STRUCTURE of clk_wiz_0 is
begin
inst: entity work.clk_wiz_0_clk_wiz
     port map (
      clk_en => clk_en,
      clk_in1 => clk_in1,
      clk_sys => clk_sys,
      locked => locked,
      psclk => psclk,
      psdone => psdone,
      psen => psen,
      psincdec => psincdec,
      reset => reset,
      sensor0 => sensor0
    );
end STRUCTURE;
