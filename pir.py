import RPi.GPIO as GPIO
import time
import Adafruit_CharLCD as LCD
import sys
import os
import logging
import configparser
import motd
import apis

defaults = { # Default choices (Recommended)
        "news": "false",
        "date": "true",
        "show_version": "false",
        "silent": "false"
        }

conf_file = "config.ini"
config = configparser.ConfigParser()

if not os.path.exists(conf_file): # If the config file is  not there we make it
    config["General"] = defaults
    with open(conf_file, "w") as f:
        config.write(f)
        
config.read(conf_file)

try: # Try to define the booleans to the variables
    news = config.getboolean("General", "news")
    date = config.getboolean("General", "date")
    version = config.getboolean("General", "show_version")
    silent = config.getboolean("General", "silent")
except ValueError: # If it fails we just reset the settings
    config["General"] = defaults
    with open(conf_file, "w") as f:
        config.write(f)
    news = config.getboolean("General", "news")
    date = config.getboolean("General", "date")
    version = config.getboolean("General", "show_version")
    silent = config.getboolean("General", "silent")

logging.basicConfig( # Define the log and message format
    filename="alarm.log",
    filemode="a",
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
    )

pin = 23 # PIR
buzzer = 27 # Vibration
touch = 17 # Touch sensor
lcd = LCD.Adafruit_CharLCDBackpack(address=0x21) # Define the on board lcd

GPIO.setmode(GPIO.BCM) # Use BCM layout
GPIO.setup(pin, GPIO.IN)
GPIO.setup(touch, GPIO.IN)
GPIO.setup(buzzer, GPIO.OUT)

def ir_sense():
    time.sleep(2) # Quick init break
    status = True
    try:
        while status:
            if GPIO.input(pin):
                lcd.clear()
                lcd.set_backlight(0)
                lcd.message("Detected!") # Show message on the lcd and log it
                logging.info("Detected movement")
                if silent == False:
                    GPIO.output(buzzer, GPIO.HIGH) # enable the buzzer if we're not silent
                time.sleep(5) # 5 seems good enough for the pir sensor to not detect movement twice in quick succession 
                lcd.clear()
                lcd.set_backlight(1) # Clear and turn off the backlight when the alarm is over
            else:
                if GPIO.input(touch):
                    status = False # Set the loop status to false so it should end without causing the program to end
                    logging.info("Alarm disarmed")
                    rearm()
                else:
                    GPIO.output(buzzer, GPIO.LOW) # Turn the buzzer off in case there's no movement nor touch
                    time.sleep(.1)
    except KeyboardInterrupt:
        sys.exit() # Debugging purposses
    finally:
        rearm() # If the built in touch input doesn't break it at least we get back somehow

def rearm():
    GPIO.output(buzzer, GPIO.LOW) # Turn off the buzzer in case when disarming it gets left on
    lcd.set_backlight(0)
    lcd.message("Hold to Arm") # Display rearm message on the built in lcd 
    time.sleep(2) # Somehow crucial i have no idea why
    while True:
        if GPIO.input(touch): # If the touch sensor is touched we rearm the alarm
            lcd.clear()
            lcd.message("Arming...")
            time.sleep(3)
            logging.info("Alarm armed")
            lcd.clear()
            lcd.set_backlight(1)
            ir_sense()
        else:
            if date: # Take date from the device in the specified format
                motd.better_motd(time.strftime("%a %d.%m.%Y, %H:%M %Z"))
            if version: # Show version of the software
                motd.better_motd("Suzuka alarm node v1.0 RC v1.3.2")
            if news: # Display google news feed
                motd.better_motd(apis.news())
            motd.better_motd("Hold touch to arm...")
            continue # If there's no touch we just wait


if __name__ == "__main__":
    try:
        motd.splash()
    #ir_sense() # [DEBUG] Begin with the alarm already armed
        rearm()
    except OSError:
        print("OSError: Is the switch is position A?")