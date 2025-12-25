# ------------------------------------------------------------------
# 0. Open the Project (Automatic Detection)
# ------------------------------------------------------------------
# Find any .xpr file in the current directory
set project_file [glob -nocomplain *.xpr]

if { $project_file eq "" } {
    puts "ERROR: No Vivado project file (.xpr) found in this directory!"
    exit 1
}

# Open the found project
puts "Opening project: $project_file"
open_project $project_file

# ------------------------------------------------------------------
# Handle optional 'jobs' argument (Default = 12)
# ------------------------------------------------------------------
if { $argc > 0 } {
    set num_jobs [lindex $argv 0]
} else {
    set num_jobs 12
}

puts "------------------------------------------------"
puts "  Starting build with $num_jobs parallel jobs..."
puts "------------------------------------------------"

# 1. Reset previous runs to ensure fresh build
reset_run synth_1
reset_run impl_1

# 2. Launch Implementation targeting Bitstream generation 
launch_runs impl_1 -to_step write_bitstream -jobs $num_jobs

# 3. Wait for it to finish so you know when it's done
wait_on_run impl_1

puts "------------------------------------------------"
puts "  DONE: Bitstream generation complete.          "
puts "------------------------------------------------"
