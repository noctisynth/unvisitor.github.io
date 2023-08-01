from PIL import ImageGrab
import random
import string
import io, base64

def screenshot():
    from PIL import ImageGrab
    name = ''.join(random.sample(string.ascii_letters + string.digits, 8)) + '.png'
    shot = ImageGrab.grab()
    shotfile = io.BytesIO()
    shot.save(shotfile, format='PNG')
    return [name, shotfile.getvalue()]

if __name__=="__main__":
    screenshot()
