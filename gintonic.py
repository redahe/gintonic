#!/usr/bin/env python

import os
import sys
import curses
import curses.textpad as textpad
import collections
import ConfigParser
import logging
import time
import threading
import subprocess
import thumbnails_view as thumbs

LOG_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=LOG_FORMAT)


WORK_DIR = os.path.join(os.path.expanduser('~'), '.gintonic')
CONFIG_FILE = os.path.join(WORK_DIR, 'config')

SECTION = 'CONFIG'
PATH_TO_GAMES = 'path_to_games'

SYSTEM_WIDTH = 15
GAME_WIDTH = 44

PREVIEW_WIDTH = 40

exited = False

config = ConfigParser.ConfigParser()

mainwindow = curses.initscr()

data = []


def read_config():
    logging.info('Reading config: ' + CONFIG_FILE)
    config.read(CONFIG_FILE)
    global path_to_games
    path_to_games = config.get(SECTION, PATH_TO_GAMES)


def check_find(word, item):
    return word.upper() in item[0].upper() or word.upper() in item[1].upper()


class PreviewWindow(object):

    def __init__(self, mainwindow, game_menu):
        self.main = mainwindow
        self.game = game_menu
        size = mainwindow.getmaxyx()
        self.win = curses.newwin(size[0]-5, PREVIEW_WIDTH, 4, GAME_WIDTH + SYSTEM_WIDTH + 2)
        self.last_game_loaded = None

    def preview_work(self):
        while True:
            if exited:
                return
            time.sleep(0.01)
            to_load = self.game.current_game()
            if self.last_game_loaded == to_load:
                continue
            if self.main.getmaxyx()[1] < GAME_WIDTH + SYSTEM_WIDTH + 2 + 10:
                continue
            system, game = self.game.current_game()
            full_path = os.path.join(path_to_games, system, game)
            thms = thumbs.get_thumbs(full_path)
            cords = self.win.getbegyx()
            im_size_x = self.win.getmaxyx()[1] - 4
            im_size_y = int(im_size_x * (3.0 / 4) * (thumbs.cellx*1.0 / thumbs.celly))
            for i in range(2):
                if 3 + (im_size_y+1)*(i+1) > self.win.getmaxyx()[0]:
                    break
                if i < len(thms):
                    thumbs.draw_image(cords[0]+3 + (im_size_y+1)*i, cords[1]+2, im_size_y, im_size_x, thms[i])
                else:
                    thumbs.clean(cords[0]+3 + (im_size_y+1)*i, cords[1]+2, im_size_y, im_size_x)
            self.last_game_loaded == to_load

    def draw(self):
        if self.main.getmaxyx()[1] < GAME_WIDTH + SYSTEM_WIDTH + 2 + 10:
            return
        self.win.border()
        self.win.refresh()
        if thumbs.process:
            self.win.addstr(1, 2, 'Preview')
        else:
            self.win.addstr(1, 2, 'Preview isn\'t avail. See logs')
            return

    def resize(self):
        self.last_game_loaded = None
        size = self.main.getmaxyx()
        if (size[0] > 10) and (size[1] > SYSTEM_WIDTH + GAME_WIDTH + 2 + 10):
            self.win.resize(size[0]-5, min(PREVIEW_WIDTH, max(1, size[1] - SYSTEM_WIDTH - GAME_WIDTH - 4)))
            self.win.mvwin(4, SYSTEM_WIDTH + GAME_WIDTH + 2)
            self.win.clear()


class SearchWindow(object):

    def __init__(self):
        self.swin = curses.newwin(4, 59, 0, 0)
        self.inp = curses.newwin(1, 55, 2, 2)
        self.text = textpad.Textbox(self.inp, insert_mode=False)
        self.history_point = 0
        self.search_history = collections.deque(maxlen=100)

    def resize(self):
        self.swin.resize(4, 59)
        self.inp.resize(1, 55)

    def draw(self):
        self.swin.addstr(1, 20, 'Search Game')
        self.swin.border()
        self.swin.refresh()
        self.inp.refresh()

    def _handle_key(self, x):
        if x == curses.KEY_UP:
            if self.history_point < len(self.search_history):
                self.history_point += 1
                self.inp.erase()
                self.inp.addstr(0, 0, self.search_history[-self.history_point])
        if x == curses.KEY_DOWN:
            if self.history_point > 1:
                self.history_point -= 1
                self.inp.erase()
                self.inp.addstr(0, 0, self.search_history[-self.history_point])
        if x == 27:
            self.canceled = True
            return 7
        if x == 10:
            return 7
        return x

    def enter(self):
        self.history_point = 0
        curses.curs_set(1)
        curses.setsyx(2, 2)
        curses.doupdate()
        self.inp.erase()
        self.canceled = False
        res = self.text.edit(self._handle_key).strip()
        curses.curs_set(0)
        if self.canceled:
            self.inp.erase()
            self.inp.refresh()
            return ''
        elif (not(self.search_history) or self.search_history[-1] != res):
                self.search_history.append(res)
        return res


class GameMenu(object):

    def __init__(self, mainwindow):
        self.main = mainwindow
        size = mainwindow.getmaxyx()
        self.syswin = curses.newwin(size[0]-5, SYSTEM_WIDTH, 4, 0)
        self.gameswin = curses.newwin(size[0]-5, GAME_WIDTH, 4, SYSTEM_WIDTH)
        self.offset = 0
        self.pos = 0
        self.search_pos = 0

    def resize(self):
        size = self.main.getmaxyx()
        if (size[0] > 10) and (size[1] > 20):
            self.syswin.resize(size[0]-5, min(SYSTEM_WIDTH, size[1]))
            self.gameswin.resize(size[0]-5, min(GAME_WIDTH, max(0, size[1] - SYSTEM_WIDTH)))
            self.syswin.mvwin(4, 0)
            self.gameswin.mvwin(4, 15)

    def list_pos(self):
        return self.offset + self.pos

    def current_game(self):
        if data:
            return data[self.list_pos()]

    def draw(self):
        pos = self.offset
        for i in range(self.syswin.getmaxyx()[0]-2):
            style = 0
            if pos == self.list_pos():
                style = curses.A_STANDOUT
            if pos < len(data):
                dat = (' ' + data[pos][1] + ' ' * 100)[:self.gameswin.getmaxyx()[1] - 3] + ' '
                self.gameswin.addstr(i + 1, 1, dat, style)
                dat = (' ' + data[pos][0] + ' ' * 100)[:self.syswin.getmaxyx()[1] - 3] + ' '
                self.syswin.addstr(i + 1, 1, dat, style)
            else:
                self.gameswin.addstr(i + 1, 1, (' '*100)[:self.gameswin.getmaxyx()[1] - 2])
                self.syswin.addstr(i + 1, 1, (' '*100)[:self.syswin.getmaxyx()[1] - 2])
            pos += 1
        self.main.addstr(self.main.getmaxyx()[0] - 1, 0,
                         '"q"-quit, "l"-launch, "/"- search, "n"-next, "N"-prev, "j"-down, "k"-up'[:self.main.getmaxyx()[1]-1])
        self.main.refresh()
        self.syswin.border()
        self.gameswin.border()
        self.syswin.refresh()
        self.gameswin.refresh()
        if preview_window:
            preview_window.draw()

    def move_down(self):
        if self.list_pos() < len(data) - 1:
            if self.pos < self.syswin.getmaxyx()[0]-3:
                self.pos += 1
            else:
                self.offset += 1
        self.draw()

    def move_up(self):
        if self.list_pos() > 0:
            if self.pos > 0:
                self.pos -= 1
            else:
                self.offset -= 1
        self.draw()

    def center(self, pos):
        if (pos >= 0) and (pos < len(data)):
            half = self.syswin.getmaxyx()[0] / 2
            self.offset = max(pos - half, 0)
            self.pos = pos - self.offset
        self.draw()

    def find_word(self, word):
        pos = self.list_pos()
        for i in range(pos, len(data)):
            if check_find(word, data[i]):
                return i
        for i in range(pos):
            if check_find(word, data[i]):
                return i
        return -1

    def find_next(self, word):
        pos = self.list_pos() + 1
        if pos >= len(data):
            pos = 0
        for i in range(pos, len(data)):
            if check_find(word, data[i]):
                return i
        for i in range(pos):
            if check_find(word, data[i]):
                return i
        return -1

    def find_prev(self, word):
        if len(data) == 0:
            return -1
        pos = self.list_pos() - 1
        if pos < 0:
            pos = len(data) - 1
        for i in range(pos, -1, -1):
            if check_find(word, data[i]):
                return i
        for i in range(len(data) - 1, pos, -1):
            if check_find(word, data[i]):
                return i
        return -1


game_menu = None
search_window = None
preview_window = None


def launch_game(game_tuple):
    curses.endwin()
    print('RUNNING: ' + str(game_tuple))
    system = game_tuple[0]
    game = game_tuple[1]
    full_path = os.path.join(path_to_games, system, game)
    args = config.get(SECTION, 'run_'+system).format(full_path)
    origWD = os.getcwd()
    os.chdir(os.path.dirname(CONFIG_FILE))
    try:
        subprocess.call(args, shell=True)
    except Exception as e:
        logging.exception(e)
    os.chdir(origWD)
    init_curses()
    curses.flushinp()
    search_window.draw()
    game_menu.draw()


def init_curses():
    mainwindow.keypad(1)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)


def do_resize():
    mainwindow.clear()
    game_menu.resize()
    search_window.resize()
    preview_window.resize()
    game_menu.draw()
    search_window.draw()
    preview_window.draw()


def main_loop():
    while 1:
        time.sleep(0.001)
        c = mainwindow.getch()
        if c == ord('/'):
            word = search_window.enter()
            found = game_menu.find_word(word)
            game_menu.center(found)
        if c == ord('j') or c == curses.KEY_DOWN:
            game_menu.move_down()
        if c == ord('k') or c == curses.KEY_UP:
            game_menu.move_up()
        if c == ord('n'):
            word = search_window.text.gather().strip()
            found = game_menu.find_next(word)
            game_menu.center(found)
        if c == ord('N'):
            word = search_window.text.gather().strip()
            found = game_menu.find_prev(word)
            game_menu.center(found)
        if c == ord('\n') or c == ord('l'):
            cg = game_menu.current_game()
            launch_game(cg)
        if c == ord('q'):
            return
        if c == curses.KEY_RESIZE:
            do_resize()


def main():
    global exited
    read_config()
    make_index(path_to_games)
    preview_thread = None
    try:
        thumbs.init()
        init_curses()
        global game_menu
        global search_window
        global preview_window
        search_window = SearchWindow()
        game_menu = GameMenu(mainwindow)
        preview_window = PreviewWindow(mainwindow, game_menu)
        preview_thread = threading.Thread(target=preview_window.preview_work)
        preview_thread.start()
        do_resize()
        # game_menu.draw()
        # search_window.draw()
        # preview_window.draw()
        main_loop()
    finally:
        exited = True
        if preview_thread:
            preview_thread.join()
        curses.endwin()


def make_index(path):
    global data
    systems = os.listdir(path)
    for system in systems:
        if os.path.isdir(path + os.sep + system):
            games = os.listdir(path + os.sep + system)
            for game in games:
                data.append((system, game))
    data.sort()


if __name__ == '__main__':
    main()
