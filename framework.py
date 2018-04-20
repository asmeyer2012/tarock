import curses
import os
import sys

from interface.interface import *
from communication.clientskeleton import *

playerName = 'aaron'
if len(sys.argv) > 1:
  playerName = sys.argv[1]

## initialize pyro4 name server
pass

## initialize curses for interface
stdscr = curses.initscr()
gc = GameCommands(playerName)
curses.wrapper(gc.interface.idleLoop)

