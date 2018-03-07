import curses
import os
import sys

from interface.interface import *
#from communication.xxx import *

playerName = 'aaron'
if len(sys.argv) > 1:
  playerName = sys.argv[1]

## initialize pyro4 name server
pass

## initialize curses for interface
stdscr = curses.initscr()
cmdWin = CommandWindow(playerName)
curses.wrapper(cmdWin.idleLoop)

