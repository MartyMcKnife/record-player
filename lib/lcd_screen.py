from luma.core.render import canvas
from luma.oled.device import ssd1309, ssd1306
from luma.core.interface.serial import i2c
from PIL import Image

import time
import segno
import io


class display:
    def __init__(self, device: ssd1309, px=8, py=8):
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
        qrcode.save(out, kind="png", scale=4, dark="white", light=None)
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


if __name__ == "__main__":
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial)
    display(device).draw_qrcode("https://www.google.com")
