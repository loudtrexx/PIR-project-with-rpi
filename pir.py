import RPi.GPIO as GPIO
import time
import Adafruit_CharLCD as LCD
import sys
import os
import logging
import configparser
import motd
import apis

defaults = { # Define default values for when the config file does not exist
        "news": "true",
        "date": "true",
        "show_version": "true",
        "silent": "false"
        }

conf_file = "config.ini"
config = configparser.ConfigParser()
if not os.path.exists(conf_file): # If the config does not exist, create one!
    config["General"] = defaults
    with open(conf_file, "w") as f:
        config.write(f)
        
config.read(conf_file)

try:
        news = config.getboolean("General", "news")
        date = config.getboolean("General", "date")
        version = config.getboolean("General", "show_version")
        silent = config.getboolean("General", "silent")
except Exception: # Exception is a general term. I fogor what i wrote in the original non-commit lol but rewrite the values in case one of them is invalid
        config["General"] = defaults
        with open(conf_file, "w") as f:
                config.write(f)

logging.basicConfig( # Define the logging where the info about the alarms go
    filename="alarm.log",
    filemode="a",
    format="%(asctime)s - %(message)s",
    level=logging.INFO
    )
# Replace the pin numbers with the physical wirings if necessary
pin = 23
buzzer = 27
touch = 17 # Can be replaced with an actual button, i used a touch sensor
lcd = LCD.Adafruit_CharLCDBackpack(address=0x21)

GPIO.setmode(GPIO.BCM) # Use BCM layout
GPIO.setup(pin, GPIO.IN)
GPIO.setup(touch, GPIO.IN)
GPIO.setup(buzzer, GPIO.OUT)

def ir_sense():
    time.sleep(2)
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
    GPIO.output(buzzer, GPIO.LOW) # Turn the buzzer off in case it is not
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
            if date:
                motd.better_motd(time.strftime("%a %d.%m.%Y, %H:%M %Z"))
            if version:
                motd.better_motd("Suzuka alarm node v1.0")
            if news:
                motd.better_motd(apis.news())
            motd.better_motd("Hold touch to arm...")
            continue # If there's no touch we just wait


if __name__ == "__main__":
    try:
        motd.splash()
        rearm()
    except OSError:
        print("OSError: Is the switch is position A?")
