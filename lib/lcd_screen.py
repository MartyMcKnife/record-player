from luma.core.render import canvas
from luma.oled.device import ssd1309
from luma.emulator import device
from PIL import Image, ImageFont
from luma.core.virtual import viewport

import time
import segno
import io


class display:
    def __init__(self, device: ssd1309, px=8, py=4):
        self.device = device
        self.px = px
        self.py = py

    def draw_text(self, text: str, duration: int):
        with canvas(self.device) as draw:
            draw.text((30, 40), "Please scan QR Code to authenticate")
            time.sleep(duration)

    def draw_qrcode(self, link: str):
        # generate our qr code

        # this code keeps it in buffer, so we don't waste any file space
        qrcode = segno.make(link)
        out = io.BytesIO()
        # makes the qr code have a dark background and white pixels
        qrcode.save(out, kind="png", dark="white", light=None)
        out.seek(0)

        # let pillow grab our qrcode
        img = Image.open(out).resize((64, 64))

        # create a display for our screen
        screen = Image.new(self.device.mode, (128, 64))

        # calcualte where our qr code should sit so it is centered
        x = (screen.width - img.width) // 2
        y = (screen.height - img.height) // 2

        # put qr code on screen
        screen.paste(img, (x, y))

        # display!
        device.display(screen)

    def no_songs(self):
        with canvas(self.device) as draw:
            draw.font = ImageFont("fonts/NotoSans-Medium.tff")
            x_length = draw.textlength("No music currently playing!")
            draw.text(
                ((device.width - x_length) / 2, self.py),
                "No music currently playing!",
            )

    def draw_songInfo(
        self, songName: str, songArtist: str, songAlbum: str, totalLength: int
    ):
        start_time = 0

        # create callback function to increase time
        def increase_time(current_time: int):
            return start_time + current_time

        virtual = viewport(self.device, width=1024, height=device.height)
        with canvas(virtual) as draw:
            draw.font = ImageFont("fonts/NotoSans-Medium.tff")

            # line1Length = draw.textlength(songName)
            # if (line1Length > (int(device.width) - self.px)):


if __name__ == "__main__":
    device = device.pygame()
    display(device).draw_qrcode("https://www.google.com")
    time.sleep(10)
