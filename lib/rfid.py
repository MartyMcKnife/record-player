from pn532pi import Pn532, Pn532I2c, pn532
import time


def readData(nfc: Pn532, uid: str) -> str:
    # Check if our NFC tag is the type we expect
    if len(uid) == 7:
        # User data is stored between pages 4 and 215 in 4x2 bit chunks
        # We want everything from the last bit of page 5 onwards
        hexArray = []

        run = True

        for page in range(5, 216):
            if run:
                success, raw = nfc.mifareultralight_ReadPage(page)
                if success:
                    # loop through our page chunk
                    for item in raw:
                        # once we start reading '0' bits that means we have read all the available data on the rfid tag
                        if item == 0:
                            run = False
                            break
                        else:
                            hexArray.append(item)
                # tiny break to reset i2c device
                time.sleep(0.0000001)
            else:
                break
        # delete our last element in the array as they are a fake 'empty' bit
        del hexArray[-1:]
        # delete first 5 elements as the are meaningless data type points
        del hexArray[:5]

        # Decode our full array and return it as a string
        return "".join(chr(i) for i in hexArray)


# test code to make sure reader is working
if __name__ == "__main__":
    PN532_I2C = Pn532I2c(1)
    nfc = Pn532(PN532_I2C)
    nfc.begin()
    time.sleep(1)
    nfc.SAMConfig()
    time.sleep(1)
    nfc.setPassiveActivationRetries(0x9A)
    while True:
        print("waiting for card...")
        try:
            time.sleep(0.1)
            success, uid = nfc.readPassiveTargetID(
                pn532.PN532_MIFARE_ISO14443A_106KBPS
            )
        except OSError:
            print("retrying after 1 sec")
            time.sleep(1)

        if success:
            print(readData(nfc, uid))
