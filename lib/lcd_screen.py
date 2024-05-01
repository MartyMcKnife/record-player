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
    def __init__(self, device: ssd1309, px=8, py=8):
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

    def get_text_overflow(self, text: str):
        with canvas(self.device) as draw:
            textLength = draw.textlength(text)
            # get the pixel width that overflows
            textOverflowWidth = textLength - (self.device.width - (self.px * 2))
            # if we don't overflow, don't return any overflowed text
            if textOverflowWidth <= 0:
                return ""
            # reverse the list to get the text that overflows
            splitTextRev = list(text)[::-1]

            charlist = []
            i = 0
            # loop through every character (and its predecessor) and check to see if it is the length of the overflow
            while draw.textlength("".join(charlist)) < textOverflowWidth:
                charlist.append(splitTextRev[i])
                i += 1
            # return the chopped off text
            return "".join(charlist)[::-1]

    def draw_song_text(self, draw, text: str, number: int, gap: int):
        # if it is gonna be wider than our screen width with padding, we left align it so the scroll looks cleaner
        # otherwise it is middle aligned
        textLength = draw.textlength(text)
        if textLength > self.device.width - (self.px * 2):
            draw.text((self.px, self.py + (gap * (number - 1))), text, anchor="lm")
            # if we are overflowing, we want there to still be some padding on the right left so it looks clean
            # draw a black rectangle over the top to make this work
            # we make this rectangle span the full height because I am lazy and this it is more efficient than dynamically finding the text height
            draw.rectangle(
                (
                    self.device.width - self.py,
                    0,
                    self.device.width,
                    self.device.height,
                ),
                fill="black",
            )
        else:
            draw.text(
                (
                    (self.device.width - self.px / 2) / 2,
                    self.py + (gap * (number - 1)),
                ),
                text,
                anchor="mm",
            )

    def draw_songInfo(
        self,
        songName: str,
        songArtist: str,
        songAlbum: str,
        totalDuration: int,
        currentDuration: int,
        gap: int = 14,
    ):

        with canvas(self.device) as draw:
            # draw each info point on our screen

            self.draw_song_text(draw, songName, 1, gap)
            self.draw_song_text(draw, songArtist, 2, gap)
            self.draw_song_text(draw, songAlbum, 3, gap)

            # draw our progress bar
            # calculate the needed space for the progress time at the end
            progressText = f"{self.millisecond_convert(currentDuration)} / {self.millisecond_convert(totalDuration)}"
            progressTextPaddding = 2
            textLength = draw.textlength(progressText, font_size=8)
            progressLength = textLength + self.px + progressTextPaddding

            # draw rectangle outline
            draw.rectangle(
                (
                    self.px,
                    self.py + (gap * 3),
                    self.device.width - progressLength,
                    self.py + (gap * 3) + 5,
                ),
                outline="white",
            )
            # draw rectangle fill
            # fill is calculated as a percentage of full length, based on the current / rem duration
            draw.rectangle(
                (
                    self.px,
                    self.py + (gap * 3),
                    (
                        (currentDuration / totalDuration)
                        * (self.device.width - progressLength)
                    ),
                    self.py + (gap * 3) + 5,
                ),
                fill="white",
            )

            draw.text(
                (
                    self.device.width - textLength - self.px + progressTextPaddding,
                    self.py + (gap * 3),
                ),
                progressText,
                font_size=8,
                anchor="lt",
            )


if __name__ == "__main__":
    device = d.pygame()
    print(
        display(device).draw_song_text(
            text="This is a really really really long string", number=1, gap=0
        )
    )
    time.sleep(10)
