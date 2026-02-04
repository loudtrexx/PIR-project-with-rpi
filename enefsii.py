import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import Adafruit_CharLCD as LCD
import sys

reader = SimpleMFRC522()
lcd = LCD.Adafruit_CharLCDBackpack(address=0x21)

def register_tag(filename="tags.txt"):
    tag_id = read_tag()
    try:
        print("Register an NFC tag")
        with open(filename, "r") as f:
            ids = [line.strip() for line in f if line.strip()]
            
        if tag_id in ids:
            ptint("Already exists!")
        else:
            with open(filename, "a") as f:
                f.write(tag_id + "\n")
            print("Registered!")
    except FileNotFoundError:
        open(filename, "w").close()
    
    finally:
        GPIO.cleanup()
def read_tag():
    try:
        print("Read an nfc tag")
        id, text = reader.read()
        print(f"This is your id: {id}")
        return str(id).strip()
    finally:
        GPIO.cleanup()
def remove_tag(tag, filename="tags.txt"):
    try:
        with open(filename, "r") as f:
            ids = [line.strip() for line in f if line.strip()]
            
        new_ids = [i for i in ids if i != tag]
        
        with open(filename, "w") as f:
            for i in new_ids:
                f.write(i = "\n")
        
        if len(new_ids) < len(ids):
            print("Removed!")
        else:
            print("N/a matching ids")
        
    finally:
        GPIO.cleanup()

def authorized(tag, filename="tags.txt"):
    with open(filename, "r") as f:
        allowed = [line.strip() for line in f.readlines()]
    return tag in allowed

def real_check():
    while True:
        tag_id = read_tag()
        
        if authorized(tag_id):
            lcd.clear()
            lcd.set_backlight(0)
            lcd.message("Access allowed")
            time.sleep(1)
            break
        else:
            lcd.clear()
            lcd.set_backlight(0)
            lcd.message("Access denied")
            time.sleep(1)
            lcd.clear()
 
if __name__ == "__main__":
    try:
        register_tag()
        #remove_tag(read_tag())
        #read_tag()
        #real_check()
    except KeyboardInterrupt:
        sys.exit()
        