import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
import time

# o sa mai fac curat

stdscr = curses.initscr()
curses.start_color()
height, width = stdscr.getmaxyx()
middle_y = height // 2
middle_x = width // 2

curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(10, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
G_B = curses.color_pair(1)
Y_B = curses.color_pair(2)
M = curses.color_pair(10)

def startSettings(stdscr):
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)


def endSettings(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()

def CLI(stdscr):
    #loadingScreen(stdscr)
    startSettings(stdscr)
    endSettings(stdscr)

wrapper(CLI) # asa trebuie apelat pt debugging daca sunt erori