import os
import sys
import logging
from subprocess import Popen, PIPE

cellx = 0
celly = 0
process = None

W3M_BIN = '/usr/lib/w3m/w3mimgdisplay'

LOG_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=LOG_FORMAT)


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


def draw_image(startx, starty, sizex, sizey, path):
    if not process:
        return
    inpline = "0;1;{};{};{};{};;;;;{}\n4;\n3;\n".format(
        startx*cellx, starty*celly, sizex*cellx, sizey*celly, path)
    process.stdin.write(inpline)
    process.stdin.flush()
    process.stdout.readline()
