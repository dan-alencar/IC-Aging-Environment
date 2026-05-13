# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  #Adding Page
  set Page_0 [ipgui::add_page $IPINST -name "Page 0"]
  ipgui::add_param $IPINST -name "ASK_TEMP" -parent ${Page_0}
  ipgui::add_param $IPINST -name "ASK_VCC" -parent ${Page_0}
  ipgui::add_param $IPINST -name "GET_TEMP" -parent ${Page_0}
  ipgui::add_param $IPINST -name "GET_VCC" -parent ${Page_0}


}

proc update_PARAM_VALUE.ASK_TEMP { PARAM_VALUE.ASK_TEMP } {
	# Procedure called to update ASK_TEMP when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.ASK_TEMP { PARAM_VALUE.ASK_TEMP } {
	# Procedure called to validate ASK_TEMP
	return true
}

proc update_PARAM_VALUE.ASK_VCC { PARAM_VALUE.ASK_VCC } {
	# Procedure called to update ASK_VCC when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.ASK_VCC { PARAM_VALUE.ASK_VCC } {
	# Procedure called to validate ASK_VCC
	return true
}

proc update_PARAM_VALUE.GET_TEMP { PARAM_VALUE.GET_TEMP } {
	# Procedure called to update GET_TEMP when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.GET_TEMP { PARAM_VALUE.GET_TEMP } {
	# Procedure called to validate GET_TEMP
	return true
}

proc update_PARAM_VALUE.GET_VCC { PARAM_VALUE.GET_VCC } {
	# Procedure called to update GET_VCC when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.GET_VCC { PARAM_VALUE.GET_VCC } {
	# Procedure called to validate GET_VCC
	return true
}


proc update_MODELPARAM_VALUE.ASK_TEMP { MODELPARAM_VALUE.ASK_TEMP PARAM_VALUE.ASK_TEMP } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.ASK_TEMP}] ${MODELPARAM_VALUE.ASK_TEMP}
}

proc update_MODELPARAM_VALUE.GET_TEMP { MODELPARAM_VALUE.GET_TEMP PARAM_VALUE.GET_TEMP } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.GET_TEMP}] ${MODELPARAM_VALUE.GET_TEMP}
}

proc update_MODELPARAM_VALUE.ASK_VCC { MODELPARAM_VALUE.ASK_VCC PARAM_VALUE.ASK_VCC } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.ASK_VCC}] ${MODELPARAM_VALUE.ASK_VCC}
}

proc update_MODELPARAM_VALUE.GET_VCC { MODELPARAM_VALUE.GET_VCC PARAM_VALUE.GET_VCC } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.GET_VCC}] ${MODELPARAM_VALUE.GET_VCC}
}

