from dotenv import load_dotenv
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from pn532pi import Pn532, Pn532I2c, pn532
from spotipy.oauth2 import SpotifyOauthError
from gpiozero import Button, GPIOPinInUse

from lib.lcd_screen import display
from lib.rfid import readData
from lib.spotify import (
    getSongInfo,
    validateUser,
    authUser,
    getUrl,
    skipPlayback,
    togglePlayback,
)
from lib.util import checkReverse, shiftList
from lib.motor import drive_motor

import os
import sys
import time
from http.server import BaseHTTPRequestHandler
import socketserver
import threading
from multiprocessing import Process
from urllib.parse import parse_qs, urlparse

load_dotenv()

authString = ""
tagUID = ""
songInfo = {
    "song_id": "",
    "track": {"name": "", "cur": "", "end": "", "reverse": False},
    "artist": {"name": "", "cur": "", "end": "", "reverse": False},
    "album": {"name": "", "cur": "", "end": "", "reverse": False},
    "total_duration": 0,
    "current_duration": 0,
}
try:
    buttonStart = Button(7)
    buttonSkip = Button(11)
    setup_buttons = True
except GPIOPinInUse as e:
    print(e)
    print("Button Pin already in use")


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
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        # we send back a dummy favicon otherwise most browsers will send another request to get the favicon
        # this causes a race condition and our logic to grab the code collapses on itself
        self.wfile.write(
            b"<html><head><link rel='shortcut icon' href='data:image/x-icon;,' type='image/x-icon'> </head>"
        )
        self.wfile.write(bytes(f"<body><p>{message}</p>", encoding="utf-8"))
        self.wfile.write(bytes("</body></html>", encoding="utf-8"))


def setup():
    # Instantiate OLED device
    try:
        serial = i2c(port=1, address=0x3C)
        device_base = ssd1306(serial)
        device_constr = display(device_base)
    except IOError:
        sys.exit(
            "OLED display not found! Make sure the address is correct and the correct driver is selected"
        )

    # # Instantiate NFC
    try:
        PN532_I2C = Pn532I2c(1)
        nfc = Pn532(PN532_I2C)
        nfc.begin()
        time.sleep(1)
        nfc.SAMConfig()
    except IOError:
        sys.exit("NFC Reader could not be found!")

    return device_constr, nfc


def main(device: display, nfc: pn532):
    # Step 1: Check if we are authenticated Spotify user. If not authenticate
    sp = validateUser()
    # oauth logic for spotify
    if not sp:
        device.draw_text("Please scan the QR code to login with Spotify!")
        time.sleep(3)

        global authString

        url = getUrl()
        print(url)

        # start the server for receiving the correct code

        # if the authentication fails, we restart the server
        # for some reason even if we exact cleanly, the tcp server won't register the socket as realeased
        # we tell it to shutup and still start the server
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("", 8080), handler)
        x = threading.Thread(
            target=httpd.serve_forever,
            daemon=True,
        )
        x.start()
        print("Server started. Waiting...")
        # keep qr code on the screen until our resp arrives
        while not authString:
            device.draw_qrcode(url)
        # wait 1 second to let success page to send to client
        time.sleep(1)
        # cleanly exit server
        httpd.server_close()
        httpd.shutdown()
        try:
            sp = authUser(authString)
        # in case user tries to brute force or something idk we restart the server and try again
        # probably a less resource intensive way to do this but i have spent like 3 hours doing this and im kinda sick of it
        # the reality is our user wont fuck it up (famous last words)
        # add it to the list of sean pls fix
        except SpotifyOauthError as e:
            device.draw_text(
                "Unexpected error when authenticating, trying again in 5 seconds",
            )
            authString = ""
            print(e)
            time.sleep(5)
    # # Step 2: Check if there is a new NFC tag present
    success, uid = nfc.readPassiveTargetID(
        pn532.PN532_MIFARE_ISO14443A_106KBPS
    )
    # check both we have an NFC tag and a spotify instance
    motorProcess = None
    if success and sp:
        global songInfo
        global tagUID
        motorProcess = None

        # Check to see if this is a new tag or a different one
        if uid == tagUID:
            # Handle same track
            track_data = songInfo["track"]
            artist_data = songInfo["artist"]
            album_data = songInfo["album"]

            track_data["reverse"] = checkReverse(track_data)
            artist_data["reverse"] = checkReverse(artist_data)
            album_data["reverse"] = checkReverse(album_data)
            print(songInfo)
            device.draw_songInfo(
                track_data["cur"],
                artist_data["cur"],
                album_data["cur"],
                songInfo["total_duration"],
                songInfo["current_duration"],
            )

            # wait half a second before refreshing our spotify status
            # we do this at the end so as not to waste the request made when the record is initially placed
            time.sleep(0.5)
            # update song info
            newSongInfo = getSongInfo(
                sp,
                cur_id=songInfo["song_id"],
                ends={
                    "track": songInfo["track"]["end"],
                    "artist": songInfo["artist"]["end"],
                    "album": songInfo["album"]["end"],
                },
                device=device,
            )
            # check if track is different
            # if it is shift our text
            # otherwise just update the object
            if newSongInfo["song_id"] == songInfo["song_id"]:
                songInfo["track"]["cur"] = shiftList(track_data)
                songInfo["artist"]["cur"] = shiftList(artist_data)
                songInfo["album"]["cur"] = shiftList(album_data)
                songInfo["current_duration"] = newSongInfo["current_duration"]
                songInfo["total_duration"] = newSongInfo["total_duration"]

            else:
                songInfo = newSongInfo

        else:
            # Handle different track
            device_id = os.getenv("DEVICE_ID")
            # get our uri
            uri = readData(nfc, uid)
            # transfer playing to our device
            sp.transfer_playback(device_id, force_play=False)
            # start playback and update currently playing uri
            # we use context uri as we want to play the album not just an individual track
            sp.start_playback(device_id, context_uri=uri)
            # create a new motorprocess
            # this will be used to ensure that driving the motor doesn't block the loop
            motorProcess = Process(target=drive_motor)
            motorProcess.start()
            # tiny delay to ensure current playback will be correct
            time.sleep(1)
            songDetails = getSongInfo(sp, device=device)
            songInfo = songDetails
            tagUID = uid
    else:
        # No album currently select. Basically just handle life cycle upkeep
        device.no_songs()
        # only pause playback if we were already playing a song
        if songInfo["song_id"]:
            sp.pause_playback()
        # clear the songInfo object so nothing else that uses it for checking stuffs up
        songInfo = {
            "song_id": "",
            "track": {"name": "", "cur": "", "end": "", "reverse": False},
            "artist": {"name": "", "cur": "", "end": "", "reverse": False},
            "album": {"name": "", "cur": "", "end": "", "reverse": False},
            "total_duration": 0,
            "current_duration": 0,
        }

        # if we are driving the motor, kill it
        if motorProcess:
            motorProcess.join()
            motorProcess.kill()

    # Step 3: check to see if any buttons have been pushed. If they have, handle corresponding
    global setup_buttons
    if sp and setup_buttons:
        buttonStart.when_deactivated = togglePlayback(
            sp=sp, songInfo=songInfo
        )
        buttonSkip.when_deactivated = skipPlayback(sp=sp)
        setup_buttons = True


if __name__ == "__main__":
    device_setup, nfc = setup()
    consec_errors = 0
    while True:
        # try:
        main(device_setup, nfc)
        # reset our consecutive errors if we run through the main loop aok
        consec_errors = 0
    # if something stuffs up in the loop, try and recover from it
    # except Exception as e:
    #     device_setup.draw_text(
    #         "Something went wrong, seeing if we can restart"
    #     )
    #     consec_errors += 1
    #     print(e)
    #     # we've crashed too many times. give up :(
    #     if consec_errors > 3:
    #         while True:
    #             device_setup.draw_text(
    #                 "Please check log and restart device"
    #             )
    #     time.sleep(2)
