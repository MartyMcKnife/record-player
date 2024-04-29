from luma.core.render import canvas
from luma.oled.device import ssd1309
from luma.emulator import device as d
from PIL import Image, ImageFont, ImageDraw

import time
import segno
import io
import os
import textwrap
import datetime

ImageDraw.ImageDraw.font = ImageFont.truetype(
    os.path.dirname(__file__) + "/fonts/NotoSans-Medium.ttf"
)


class display:
    def __init__(self, device: ssd1309, px=8, py=4):
        self.device = device
        self.px = px
        self.py = py

    def millisecond_convert(self, time: int):
        seconds = int(time / 1000) % 60
        minutes = int(time / (1000 * 60)) % 60
        dt = datetime.time(0, minutes, seconds)
        return dt.strftime("%M:%S")

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
        self,
        songName: str,
        songArtist: str,
        songAlbum: str,
        totalDuration: int,
        currentDuration: int,
        gap: int = 15,
    ):
        start_time = 0

        # create callback function to increase time
        def increase_time(current_time: int):
            return start_time + current_time

        with canvas(self.device) as draw:
            # draw each info point on our screen
            # if it is gonna be wider than our screen width with padding, we left align it so the scroll looks cleaner
            # otherwise it is middle aligned
            line1length = draw.textlength(songName)
            draw.text(
                (self.px, self.py),
                songName,
                anchor=(
                    "mm"
                    if line1length > self.device.width - (self.px * 2)
                    else "lm"
                ),
            )

            line2length = draw.textlength(songArtist)
            draw.text(
                (self.px, self.py + gap),
                songArtist,
                anchor=(
                    "mm"
                    if line2length > self.device.width - (self.px * 2)
                    else "lm"
                ),
            )

            line3length = draw.textlength(songAlbum)
            draw.text(
                (self.px, self.py + gap * 2),
                songAlbum,
                anchor=(
                    "mm"
                    if line3length > self.device.width - (self.px * 2)
                    else "lm"
                ),
            )

            # draw our progress bar
            # take off the progress time at the end
            progressText = f"{self.millisecond_convert(currentDuration)} / {self.millisecond_convert(totalDuration)}"
            progressTextPaddding = 4
            textLength = draw.textlength(progressText)
            progressLength = textLength + self.px + progressTextPaddding

            # draw rectangle outline
            draw.rectangle(
                (
                    self.px,
                    self.py + gap * 3,
                    self.device.width - progressLength,
                    self.py + gap * 3 + 10,
                ),
                outline="white",
            )
            print(currentDuration / totalDuration)
            # draw rectangle fill
            # fill is calculated as a percentage of full length, based on the current / rem duration
            draw.rectangle(
                (
                    self.px,
                    self.py + gap * 3,
                    self.px
                    + (
                        (currentDuration / totalDuration)
                        * (self.device.width - progressLength)
                    ),
                    self.py + gap * 3 + 10,
                ),
                fill="white",
            )

            draw.text(
                (
                    self.device.width
                    - textLength
                    - self.px
                    + progressTextPaddding,
                    self.py + gap * 3,
                ),
                progressText,
                anchor="lt",
            )


if __name__ == "__main__":
    device = d.pygame()
    display(device).draw_qrcode("https://www.google.com")
    time.sleep(10)
