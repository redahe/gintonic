#!/usr/bin/env python

import os
import curses
import curses.textpad as textpad
import collections


mainwindow = curses.initscr()

data = [('NES', 'sobaka'), ('NES', 'glaza'), ('MegaDrive', 'konskiy look'),
        ('MegaDrive', 'changeme'), ('MegaDrive', 'brbasasasasasasasas'),
        ('PSX', 'shamanskiy buben ahahahahahahahhaahahhahaahahhaahhahaahahhahahahaahhaahhahahahahaha')] * 10

for i in range(len(data)):
    data[i] = (data[i][0], '_'+str(i)+'_'+data[i][1])


class SearchWindow(object):

    def __init__(self):
        self.swin = curses.newwin(4, 59, 0, 0)
        self.swin.addstr(1, 20, 'Search Game')
        self.swin.border()
        self.inp = curses.newwin(1, 55, 2, 2)
        self.text = textpad.Textbox(self.inp, insert_mode=False)
        self.history_point = 0
        self.search_history = collections.deque(maxlen=100)

    def draw(self):
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
        if x == 10:
            return 7
        return x

    def enter(self):
        self.history_point = 0
        curses.curs_set(1)
        curses.setsyx(2, 2)
        curses.doupdate()
        self.inp.erase()
        res = self.text.edit(self._handle_key).strip()
        if not(self.search_history) or self.search_history[-1] != res:
            self.search_history.append(res)
        curses.curs_set(0)
        return res


class GameMenu(object):

    def __init__(self, mainwindow):
        self.main = mainwindow
        size = mainwindow.getmaxyx()
        self.syswin = curses.newwin(size[0]-5, 15, 4, 0)
        self.syswin.border()
        self.gameswin = curses.newwin(size[0]-5, 44, 4, 15)
        self.gameswin.border()
        self.offset = 0
        self.pos = 0

    def list_pos(self):
        return self.offset + self.pos

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
        self.syswin.refresh()
        self.gameswin.refresh()

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
            if (word in data[i][0]) or (word in data[i][1]):
                return i
        for i in range(pos):
            if (word in data[i][0]) or (word in data[i][1]):
                return i
        return -1

    def find_next(self, word):
        pos = self.list_pos() + 1
        if pos >= len(data):
            pos = 0
        for i in range(pos, len(data)):
            if (word in data[i][0]) or (word in data[i][1]):
                return i
        for i in range(pos):
            if (word in data[i][0]) or (word in data[i][1]):
                return i
        return -1

    def find_prev(self, word):
        if len(data) == 0:
            return -1
        pos = self.list_pos() - 1
        if pos < 0:
            pos = len(data) - 1
        for i in range(pos, -1, -1):
            if (word in data[i][0]) or (word in data[i][1]):
                return i
        for i in range(len(data) - 1, pos, -1):
            if (word in data[i][0]) or (word in data[i][1]):
                return i
        return -1


def main_loop(game_menu, search_window):
    while 1:
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
            search_window.draw()
        if c == ord('q') or c == 27:
            return


def main():
    try:
        mainwindow.keypad(1)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        mainwindow.addstr(mainwindow.getmaxyx()[0] - 1, 1,
                          '"l" - launch, "/"  - search, "n" - next, "N" - prev, "j" - down, "k" - up, q - quit')
        mainwindow.refresh()
        sw = SearchWindow()
        gm = GameMenu(mainwindow)
        gm.draw()
        sw.draw()
        main_loop(gm, sw)
    finally:
        # curses.nocbreak()
        # mainwindow.keypad(0)
        # curses.echo()
        curses.endwin()


def make_index(path):
    index = {}
    systems = os.listdir(path)
    for system in systems:
        games = os.listdir(path + os.sep + system)
        index[system] = games
    return index


if __name__ == '__main__':
    main()
