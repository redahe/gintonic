import os
import sys
import logging
from subprocess import Popen, PIPE


W3M_BIN = '/usr/lib/w3m/w3mimgdisplay'
THUMBS_SUBFOLDER = 'thumbnails'


FILE_TYPES = ['.png', '.jpg', '.gif', '.jpeg',
              '.PNG', '.JPG', '.JPEG', '.GIF']
LOG_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=LOG_FORMAT)


cellx = 0
celly = 0
process = None


def init():
    global process
    global cellx
    global celly
    try:
        rows, columns = os.popen('stty size', 'r').read().split()
        output = Popen([W3M_BIN, "-test"], stdout=PIPE).communicate()[0].split()
        xpixels, ypixels = int(output[0]), int(output[1])
        cellx = (xpixels+2) / int(columns)
        celly = (ypixels+2) / int(rows)
        process = Popen(W3M_BIN, stdin=PIPE, stdout=PIPE)
    except Exception as e:
        logging.exception(e)
        process = None


def draw_image(starty, startx, sizey, sizex, path):
    if not process:
        return
    inpline = "0;1;{};{};{};{};;;;;{}\n4;\n3;\n".format(
        startx*cellx, starty*celly, sizex*cellx, sizey*celly, path)
    process.stdin.write(inpline)
    process.stdin.flush()
    process.stdout.readline()


def clean(starty, startx, sizey, sizex):
    if not process:
        return
    inpline = "6;{};{};{};{}\n4;\n3;\n".format(
        startx*cellx+2, starty*celly+2, sizex*cellx, sizey*celly)
    process.stdin.write(inpline)
    process.stdin.flush()
    process.stdout.readline()


def get_thumbs(game_folder):
    res = []
    subf = os.path.join(game_folder, THUMBS_SUBFOLDER)
    if os.path.exists(subf) and os.path.isdir(subf):
        files = os.listdir(subf)
        for f in files:
            for ft in FILE_TYPES:
                if f.endswith(ft):
                    res.append(os.path.join(subf, f))
                    break
    res.sort()
    return res

if __name__ == '__main__':
    init()
    th = (get_thumbs('/home/reda/games/dos/WOLF3D'))[0]
    draw_image(10, 60, 20, 50, th)
    raw_input('press enter')
    clean(10, 60, 20, 50)
    raw_input('press enter')
