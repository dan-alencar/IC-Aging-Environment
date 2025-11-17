""" import subprocess
import time

USB_DEVICE_ID = "1-1"

def reset_usb(device_id):
    try:
        print(f"Unbinding USB device {device_id}...")
        #subprocess.run(["sudo", "tee", "/sys/bus/usb/drivers/usb/unbind"],
        #               input=device_id.encode(), check=True)
        time.sleep(1)

        print(f"Binding USB device {device_id} again...")
        subprocess.run(["sudo", "tee", "/sys/bus/usb/drivers/usb/bind"],
                       input=device_id.encode(), check=True)

        print(f"USB device {device_id} has been reset.")
    except Exception as e:
        print(f"Error resetting device {device_id}: {e}")

if __name__ == "__main__":
    reset_usb(USB_DEVICE_ID) """