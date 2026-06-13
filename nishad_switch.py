import RPi.GPIO as GPIO
import subprocess
import time
from rpi_lcd import LCD
from signal import signal, SIGTERM, SIGHUP
import sys
import threading
import traceback
import os
from config_utils import load_config, save_config
# Constants
SWITCH_PIN = 23  # BCM GPIO pin number
LOG_FILE = "/home/hbmeter1/Hb_meter/nishad_log.txt"
SCRIPT_PATH = "/home/hbmeter1/Hb_meter/Nishad.py"

lcd = LCD()
exit_flag = threading.Event()

# Logging helper
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.ctime()}] {msg}\n")

def upload_with_rclone(local_path, remote_folder, lcd=None):
    local_path = '/home/hbmeter1/Hb_meter/'+local_path
    try:
        if lcd:
            lcd.clear()
            lcd.text("Uploading...", 1)
            lcd.text(local_path.split("/")[-1], 2)

        result = subprocess.run(
            ["rclone", "copy", local_path, remote_folder, "--ignore-existing"],
            capture_output=True, text=True, check=True
        )

        if lcd:
            lcd.clear()
            lcd.text("Upload Done", 1)
            lcd.text(local_path.split("/")[-1], 2)
            time.sleep(1)
            lcd.clear()

        print(f"✅ Uploaded {local_path} to {remote_folder}")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        if lcd:
            lcd.clear()
            lcd.text("Upload Failed", 1)
            lcd.text(local_path.split('/')[-1], 2)

        print(f"❌ Upload failed for {local_path}")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)


# Clean exit handler
def safe_exit(signum=None, frame=None):
    try:
        exit_flag.set()
        GPIO.remove_event_detect(SWITCH_PIN)
        lcd.clear()
        GPIO.cleanup()
        log("Cleaned up GPIO and LCD.")
    except Exception as e:
        log(f"Cleanup error: {e}")
    sys.exit(0)

# Display initial message
def display_ready_message(a,b):
    lcd.clear()
    lcd.text(a, 1)
    lcd.text(b, 2)

# Button press handler
def handle_button_press(channel):
    if exit_flag.is_set():
        return
    lcd.clear()
    lcd.text("Executing script...", 1)
    log("Button pressed. Running Nishad.py")

    try:
        subprocess.run(["python3", SCRIPT_PATH])
    except Exception as e:
        error_msg = f"Error: {e}"
        log(error_msg)
        lcd.text("Script error", 1)
        lcd.text(str(e)[:16], 2)  # Truncate error
        time.sleep(3)

    display_ready_message()
import subprocess
import time

def show_ip(lcd, display_time=5):
    """
    Show Raspberry Pi IP address on LCD.
    
    Parameters:
        lcd : rpi_lcd.LCD object
        display_time : int (seconds to keep IP on screen)
    """
    try:
        ip_output = subprocess.getoutput("hostname -I").strip()
        ip = ip_output.split()[0] if ip_output else "Not found"
    except Exception:
        ip = "Error"

    lcd.clear()
    lcd.text("Device Ready", 1)
    lcd.text(f"IP: {ip}", 2)
    time.sleep(display_time)
    lcd.clear()

def button_callback():
    print("Button was pushed!")
    command=f"python3 /home/hbmeter1/Hb_meter/Nishad.py"
    p=subprocess.run(command.split(" "))
    if p.returncode==0:
        print("Finished")


# Main function
def main():
    SWITCH_PIN = 23
    try:
        # log("Script starting...")
        # time.sleep(5)  # Allow system boot time

        # log(f"/dev/gpiomem exists? {os.path.exists('/dev/gpiomem')}")

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        # GPIO.setmode(GPIO.BCM)
        # GPIO.cleanup()  # Important to clear old settings
        # GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        show_ip(lcd)
        flag = True
        while True:
            print(SWITCH_PIN)
            if flag:
                display_ready_message('Press button to','take reading')
                flag = False
            if GPIO.input(SWITCH_PIN)==GPIO.LOW:
                button_callback()
                print("something")
                flag = True
                f = True
                x = time.time()
                CONFIG = load_config()
                while True:
                    if time.time()-x>15:
                        break
                    if f:
                        display_ready_message('CLICK TO UPLOAD ',CONFIG['CURRENT_VIDEO'].split("/")[-1])
                        print(CONFIG['CURRENT_VIDEO'])
                        f = False 
                    if GPIO.input(SWITCH_PIN)==GPIO.LOW:
                        print('UPLOAD  PRESSED')
                        upload_with_rclone(CONFIG['CURRENT_VIDEO'],"sandy:AIIMS_DATA/",lcd)
                        break
                if f:
                    display_ready_message('NOT','UPLOADED')

                f = True
                # break
            else:
                pass

            time.sleep(0.2)

        # display_ready_message()

        # GPIO.add_event_detect(SWITCH_PIN, GPIO.RISING, callback=handle_button_press, bouncetime=300)
        # log("GPIO event detection added.")

        while not exit_flag.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        log("KeyboardInterrupt received.")
        safe_exit()

    except RuntimeError as e:
        log(f"RuntimeError: {e}")
        lcd.clear()
        lcd.text("GPIO error", 1)
        lcd.text(str(e)[:16], 2)
        time.sleep(5)
        safe_exit()

    except Exception as e:
        log("Fatal exception:\n" + traceback.format_exc())
        lcd.clear()
        lcd.text("Fatal error", 1)
        time.sleep(5)
        safe_exit()

if __name__ == "__main__":
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)
    main()
