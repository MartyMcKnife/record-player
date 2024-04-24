from luma.oled.device import ssd1309, ssd1306
from luma.core.interface.serial import i2c
from pn532pi import Pn532, Pn532I2c, pn532
from lib.lcd_screen import display

import sys

global tag_uid
global playing

def setup():
    # Instantiate OLED device
    try:
        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial)
        device_constr = display(device) 
    except IOError:
        sys.exit("OLED display not found! Make sure the address is correct and the correct driver is selected")

    # Instantiate NFC
    try:
        PN532_I2C = Pn532I2c(1)
        nfc = Pn532(PN532_I2C)
        nfc.begin()
        nfc.SAMConfig()
    except IOError:
        sys.exit("NFC Reader could not be found!")

    return device_constr, nfc

def main(device: display, nfc: pn532):
    # Step 1: Check if we are authenticated Spotify user
    # TBD

    # Step 2: Check if there is a new NFC tag present
    success, uid = nfc.readPassiveTargetID(
            pn532.PN532_MIFARE_ISO14443A_106KBPS
        )
    if success:
        # Check to see if this is a new tag or a different one
        if uid == tag_uid:
            # Handle same track
        else:
            # Handle different track
    else:
        # No album currently select. Basically just handle life cycle upkeep
        display.no_songs()

    # Step 3: check to see if any buttons have been pushed 
    # TBD

    # Step 4: Rotate stepper if we are playing



if __name__ == "__main__":
    try:
        device, nfc = setup()
        while True:
            main(device, nfc)
    except KeyboardInterrupt:
        pass