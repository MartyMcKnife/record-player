from luma.oled.device import ssd1309, ssd1306
from luma.core.interface.serial import i2c
from pn532pi import Pn532, Pn532I2c, pn532
from lib.lcd_screen import display
from lib.spotify import validateUser, authUser, getUrl
from luma.emulator import device
from spotipy.oauth2 import SpotifyOauthError


import sys
import time
from http.server import BaseHTTPRequestHandler
import socketserver
import threading
from urllib.parse import parse_qs, urlparse


authString = ""


# handler for our http server if user hasn't already authenticated
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # update our global auth string with whatever user provided
        code = parse_qs(urlparse(self.path).query).get("code", None)
        message = ""
        code = 200
        # if we have a code, grab it
        if code:
            global authString
            authString = self.path
            message = "successfully received auth!"
        # if not let user know
        else:
            code = 400
            message = "unable to parse auth code. please try again"
        # html framework
        self.send_response(code)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.send_header("Content-length", str(len("successfully authed!")))
        self.end_headers()
        self.wfile.write(bytes(message))


def setup():
    # Instantiate OLED device
    try:
        # serial = i2c(port=1, address=0x3C)
        # device = ssd1306(serial)
        device_base = device.pygame()
        device_constr = display(device_base)
    except IOError:
        sys.exit(
            "OLED display not found! Make sure the address is correct and the correct driver is selected"
        )

    # # Instantiate NFC
    # try:
    #     PN532_I2C = Pn532I2c(1)
    #     nfc = Pn532(PN532_I2C)
    #     nfc.begin()
    #     nfc.SAMConfig()
    # except IOError:
    #     sys.exit("NFC Reader could not be found!")
    nfc = 1

    return device_constr, nfc


def main(device: display, nfc: pn532):
    # Step 1: Check if we are authenticated Spotify user
    sp = validateUser()
    if not sp:
        url = getUrl()
        # device.draw_text("Please authenticate with Spotify!")
        # time.sleep(3)

        global authString

        # start the server for receiving the correct code

        # if the authentication fails, we restart the server
        # for some reason even if we exact cleanly, the tcp server won't register the socket as realeased
        # we tell it to shutup and still start the server
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("", 5000), handler)
        x = threading.Thread(
            target=httpd.serve_forever,
            daemon=True,
        )
        x.start()
        print("Server started. Waiting...")
        # keep qr code on the screen until our resp arrives
        while not authString:
            device.draw_qrcode(url)
        print(authString)
        # wait 1 second to let success page to send to client
        time.sleep(1)
        # cleanly exit server
        httpd.server_close()
        httpd.shutdown()
        try:
            authUser(authString)
        # in case user tries to brute force or something idk we restart the server and try again
        # probably a less resource intensive way to do this but i have spent like 3 hours doing this and im kinda sick of it
        # the reality is our user wont fuck it up (famous last words)
        # add it to the list of sean pls fix
        except SpotifyOauthError:
            print(
                "Unexpected error when authenticating, trying again in 5 seconds"
            )
            time.sleep(5)

    # # Step 2: Check if there is a new NFC tag present
    # success, uid = nfc.readPassiveTargetID(
    #     pn532.PN532_MIFARE_ISO14443A_106KBPS
    # )
    # if success:
    #     # Check to see if this is a new tag or a different one
    #     if uid == tag_uid:
    #         # Handle same tra
    #         print("new uid")
    #     # else:
    #     #     # Handle different track
    # else:
    #     # No album currently select. Basically just handle life cycle upkeep
    #     display.no_songs()

    # # Step 3: check to see if any buttons have been pushed
    # # TBD

    # # Step 4: Rotate stepper if we are playing


if __name__ == "__main__":
    try:
        device_setup, nfc = setup()
        while True:
            main(device_setup, nfc)
    except KeyboardInterrupt:
        pass
