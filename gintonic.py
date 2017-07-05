#!/usr/bin/env python

import os
import curses
import curses.textpad as textpad


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

    def draw(self):
        self.swin.refresh()
        self.inp.refresh()

    def _handle_key(self, x):
        if x == 10:
            return 7
        return x

    def enter(self):
        curses.curs_set(1)
        curses.setsyx(2, 2)
        curses.doupdate()
        self.text.edit(self._handle_key)
        curses.curs_set(0)


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
        step = 0
        for i in range(self.offset, len(data)):
            style = 0
            if i == self.list_pos():
                style = curses.A_STANDOUT
            dat = (' ' + data[i][1] + ' ' * 100)[:self.gameswin.getmaxyx()[1] - 3] + ' '
            self.gameswin.addstr(step + 1, 1, dat, style)
            dat = (' ' + data[i][0] + ' ' * 100)[:self.syswin.getmaxyx()[1] - 3] + ' '
            self.syswin.addstr(step + 1, 1, dat, style)
            step += 1
            if step >= self.syswin.getmaxyx()[0]-2:
                break
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


def main_loop(game_menu, search_window):
    while 1:
        c = mainwindow.getch()
        if c == ord('/'):
            search_window.enter()
        if c == ord('j') or c == curses.KEY_DOWN:
            game_menu.move_down()
        if c == ord('k'):
            game_menu.move_up()
        if c == ord('\n') or c == ord('l'):
            # search_window.swin.addstr(1, 1, data[game_menu.list_pos()][1])
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
