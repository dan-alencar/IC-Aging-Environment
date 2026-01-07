import serial
import time

# Configure the serial connection
ser = serial.Serial(
    port='/dev/usbtmc0',  # Replace with your port, e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux
    baudrate=9600,        # Ensure this matches the power supply setting
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1             # Timeout in seconds for read operations
)

def send_command(command, expect_response=False):
    """
    Send a SCPI command to the power supply.
    If expect_response is True, read and return the response.
    """
    if not ser.is_open:
        ser.open()
    ser.write(f"{command}\n".encode())  # SCPI commands typically end with a newline character
    time.sleep(0.1)  # Short delay to allow the device to process the command
    if expect_response:
        response = ser.readline().decode().strip()
        return response

try:
    # Example: Measure the output voltage
    voltage = send_command('MEAS:VOLT?', expect_response=True)
    print(f"Measured Voltage: {voltage} V")

    # Example: Query the output state
    output_state = send_command('OUTP?', expect_response=True)
    print(f"Output State: {output_state}")

    # Example: Turn the output on
    #send_command('VOLT 1.2')
    #print("Output turned on.")

    # Example: Turn the output off
    #send_command('SOURce:OUTPut:STATe ON')
    #print("Output turned off.")
    
    #send_command('SYSTem:REMote')
    #print("System is now in Remote Mode")


except Exception as e:
    print(f"An error occurred: {e}")
finally:
    ser.close()

