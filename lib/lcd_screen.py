from luma.core.render import canvas
from luma.oled.device import ssd1309
from luma.emulator import device as d
from PIL import Image, ImageFont, ImageDraw
from luma.core.virtual import viewport

import time
import segno
import io
import os
import textwrap

ImageDraw.ImageDraw.font = ImageFont.truetype(
    os.path.dirname(__file__) + "/fonts/NotoSans-Medium.ttf"
)


class display:
    def __init__(self, device: ssd1309, px=8, py=4):
        self.device = device
        self.px = px
        self.py = py

    def draw_text(self, text: str, gap: int = 25):
        with canvas(self.device) as draw:
            # break up our text into lines based on the width of the device
            para = textwrap.wrap(text, width=self.device.width / 6)

            # loop through every line
            for i, line in enumerate(para):
                # get our bounding box of our text to offset correctly
                _, _, w, h = draw.textbbox((0, 0), line)
                # draw our text!
                draw.text(
                    (
                        # center horizontally
                        (self.device.width - w) / 2,
                        # center vertically
                        # we add a gap to each subsequent element so our text doesn't overlap massively
                        (self.device.height - h + (gap * (i - 1))) / 2,
                    ),
                    line,
                )

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
        self.device.display(screen)

    def no_songs(self):
        with canvas(self.device) as draw:
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
            line1Length = draw.textlength(songName)
            # if (line1Length > (int(device.width) - self.px)):


if __name__ == "__main__":
    device = d.pygame()
    display(device).draw_qrcode("https://www.google.com")
    time.sleep(10)
