# Physical constraints for the aging study critical-path sensor.
#
# experimental-multi-sensor branch: there is no longer a single u_sensor /
# u_adder instance pair to lock down. Each channel is
# g_sensors[i].u_channel (an rca_sensor_channel instance), with its own
# internal u_ff1/u_ff2/u_ff3/u_xor cells and its own free-running adder.
#
# NONE of the single-sensor branches' LOC/BEL/pblock constraints apply
# here -- they referenced u_sensor and u_adder/u_canary|u_sensor, none of
# which exist on this branch, and leaving them in would make Vivado error
# out on empty get_cells results. This file intentionally carries no
# per-cell placement lock yet: with NUM_SENSORS=4 independent channels,
# each needs its own pblock (co-located internally so a channel's adder
# and its own metastability sampler age together, but kept apart from the
# other channels' pblocks so one channel's placement can't drift into
# another's LUT budget). That is real synthesis-derived work -- run
# scripts/create_project.sh, implement once, then write one pblock per
# g_sensors[i].u_channel using scripts/extract_fixed_pnr_constraints.sh as
# a starting point, the same way the single-sensor branches' constraints
# were originally derived.

# --- CDC false-path: chan_alarm (FF3 / clk_en domain) -> alarm_meta (clk_sys) ---
# The per-channel 2-FF synchronizer in nexys4_aging_top.sv intentionally
# crosses this boundary for every channel. Without these constraints
# Vivado may flag spurious timing violations because the two 100 MHz
# clocks share frequency but have a dynamically varying phase.
# Verify cell names with: get_cells -hierarchical -filter {NAME =~ g_sensors*u_ff3}
for {set i 0} {$i < 4} {incr i} {
    catch {
        set_false_path \
            -from [get_cells g_sensors[$i].u_channel/u_ff3] \
            -to   [get_pins  alarm_meta_reg[$i]/D]
    }
}
