import qrcode
from PIL import Image,ImageDraw,ImageFont
from OLED_2in42 import OLED_2in42

def draw_qrcode(link: str, disp: OLED_2in42):
    disp.clear()
    image1 = Image.new("1", (disp.OLED_WIDTH, disp.OLED_HEIGHT), "WHITE")
    
    
    disp.showImage(disp.getBuffer(image1))
    
    qrcode.make(link)