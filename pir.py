import RPi.GPIO as GPIO
import time
import Adafruit_CharLCD as LCD
import sys
import logging
import motd
import apis

logging.basicConfig(
    filename="alarm.log",
    filemode="a",
    format="%(asctime)s - %(message)s",
    level=logging.INFO
    )

pin = 23
buzzer = 27
touch = 17
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
                lcd.message("Detected!")
                logging.info("Detected movement")
               
                GPIO.output(buzzer, GPIO.HIGH) # Draw text on the lcd and enable the buzzer
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
            motd.better_motd(time.strftime("%a %d.%m.%Y, %H:%M %Z"))
            motd.better_motd("Suzuka alarm node version 1.5")
            motd.better_motd(apis.news())
            motd.better_motd("Hold to arm...")
            continue # If there's no touch we just wait


if __name__ == "__main__":
    motd.splash()
    #ir_sense() # Begin with the alarm already armed
    rearm()