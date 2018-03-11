from functools import wraps
import errno
import os
import signal
import curses
import curses.ascii
import sys
sys.path.insert(0, '../')
from communication.clientskeleton import *

class TimeoutError(Exception):
    pass

## timeout decorator
## will throw an exception if function does not successfully complete before timeout
def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator

## present the game state
## shamelessly copied from MessageWindow
class GameWindow:
  def __init__(self):
    self.ndisp = 0
    self.nlines = 14
    self.offset = 2
    self.preString = ''
    self.win = curses.newwin(self.nlines,curses.COLS,self.offset,0)
    self.lines = list()

  def addLine(self,line):
    if line == '':
      self.bottomOfDisplay()
      self.displayWindow()
      return
    ## check if line is longer than window
    ## if so, chop it and add pieces
    while line != '':
      self.lines.append(line[:curses.COLS])
      line = line[curses.COLS:]
      ## if not at the end, keep the window where it was!
      if self.ndisp > 0:
        self.ndisp += 1
    self.bottomOfDisplay()
    self.displayWindow()

  def bottomOfDisplay(self): ## go to end
    self.ndisp = 0
    self.displayWindow()

  def displayWindow(self):
    self.win.clear()
    if len(self.lines) <= self.nlines: ## when not enough lines to fill screen
      for i,line in enumerate(self.lines):
        self.win.addstr(i,0,line)
    elif self.ndisp == 0: ## when display is at most recent message
      for i,line in enumerate(self.lines[-self.nlines:]):
        self.win.addstr(i,0,line)
    else: ## when display is not at most recent message
      #for i,line in enumerate(self.lines[-self.ndisp-self.nlines:-self.ndisp]):
      for i,line in enumerate(self.lines[\
        -self.ndisp-self.nlines: max(-self.ndisp,self.nlines-len(self.lines)) ]):
        self.win.addstr(i,0,line)
    self.win.refresh()

## keep a help bar at the bottom
class HelpWindow:
  def __init__(self):
    self.ndisp = 0
    self.nlines = 1
    self.offset = 0
    self.preSting = ''
    self.win = curses.newwin(self.nlines,curses.COLS,self.offset,0)
    self.lines = list()

  def addLine(self,line):
    if line == '':
      self.bottomOfDisplay()
      self.displayWindow()
      return
    ## check if line is longer than window
    ## if so, chop it and add pieces
    while line != '':
      self.lines.append(line[:curses.COLS])
      line = line[curses.COLS:]
      ## if not at the end, keep the window where it was!
      if self.ndisp > 0:
        self.ndisp += 1
    self.bottomOfDisplay()
    self.displayWindow()

  def bottomOfDisplay(self): ## go to end
    self.ndisp = 0
    self.displayWindow()

  def displayWindow(self):
    self.win.clear()
    if len(self.lines) <= self.nlines: ## when not enough lines to fill screen
      for i,line in enumerate(self.lines):
        self.win.addstr(i,0,line)
    elif self.ndisp == 0: ## when display is at most recent message
      for i,line in enumerate(self.lines[-self.nlines:]):
        self.win.addstr(i,0,line)
    else: ## when display is not at most recent message
      #for i,line in enumerate(self.lines[-self.ndisp-self.nlines:-self.ndisp]):
      for i,line in enumerate(self.lines[\
        -self.ndisp-self.nlines: max(-self.ndisp,self.nlines-len(self.lines)) ]):
        self.win.addstr(i,0,line)
    self.win.refresh()

## handle passing messages between people
class MessageWindow:
  def __init__(self):
    self.ndisp = 0 ## count backward from end of message stream
    self.nlines = 5
    self.offset = 17
    self.preString = '> '
    self.win = curses.newwin(self.nlines,curses.COLS,self.offset,0)
    self.lines = list()

  def addLine(self,name,line):
    if line == '':
      self.bottomOfDisplay()
      self.displayWindow()
      return
    line = ('%-8s> ' % name) + line ## prepend name
    ## check if line is longer than window
    ## if so, chop it and add pieces
    while line != '':
      self.lines.append(line[:curses.COLS])
      line = line[curses.COLS:]
      ## if not at the end, keep the window where it was!
      if self.ndisp > 0:
        self.ndisp += 1
    self.bottomOfDisplay()
    self.displayWindow()

  ## self.ndisp counts number of lines from bottom
  def incrementDisplay(self): ## shift messages down
    self.ndisp = min( self.ndisp+1, len(self.lines)-self.nlines )
    self.displayWindow()
  def decrementDisplay(self): ## shift messages up
    self.ndisp = max( self.ndisp-1, 0 )
    self.displayWindow()
  def bottomOfDisplay(self): ## go to end
    self.ndisp = 0
    self.displayWindow()

  def displayWindow(self):
    self.win.clear()
    if len(self.lines) <= self.nlines: ## when not enough lines to fill screen
      for i,line in enumerate(self.lines):
        self.win.addstr(i,0,line)
    elif self.ndisp == 0: ## when display is at most recent message
      for i,line in enumerate(self.lines[-self.nlines:]):
        self.win.addstr(i,0,line)
    else: ## when display is not at most recent message
      #for i,line in enumerate(self.lines[-self.ndisp-self.nlines:-self.ndisp]):
      for i,line in enumerate(self.lines[\
        -self.ndisp-self.nlines: max(-self.ndisp,self.nlines-len(self.lines)) ]):
        self.win.addstr(i,0,line)
    self.win.refresh()

## either get the key when pressed, or timeout the call after 1 second
## put in loop and keep calling, but use the timeout to check for updates from abroad
@timeout(1)
def timeoutGetKey(stdscr):
  return stdscr.getkey()

## control all the other windows and handle input
class CommandWindow:
  def __init__(self,name):
    #self.msgWin = None
    self.gmWin  = GameWindow()
    self.msgWin = MessageWindow()
    self.helpWin = HelpWindow()
    self.name = name
    self.offset = 22
    self.win = curses.newwin(1,curses.COLS,self.offset,0)
    self.client = GameCommands()
    pass

  def getNextKey(self,stdscr):
    try:
      return timeoutGetKey(stdscr)
    except KeyboardInterrupt:
      raise ## fast quit with ctrl-C
    except:
      return ## catch timeout
  def returnCursor(self,stdscr):
    stdscr.move(self.offset,0)

  ## handle idle operations, waiting for some specific command
  def idleLoop(self,stdscr): ## pass in standard cursor
    self.helpWin.addLine("Commands:      r - register   l - leave   d - deal   s - show hand")
    while True:
      self.returnCursor(stdscr)
      nextKey = self.getNextKey(stdscr)
      if   nextKey is None:
        continue
      elif nextKey == 'KEY_UP': ## move messages up to display later messages
        self.msgWin.incrementDisplay()
        pass
      elif nextKey == 'KEY_DOWN': ## move messages down to display earlier messages
        self.msgWin.decrementDisplay()
        pass
      elif nextKey == '\n': ## start writing a message
        if self.msgWin is None:
          raise ValueError("message window not set!")
        self.messageLoop(stdscr)
      elif nextKey == 'r': ## register command
        self.gmWin.addLine(self.client.register(self.name))
        self.gmWin.addLine(self.client.printPlayers())
      elif nextKey == 'l': ## leave command
        self.client.leave()
        print "Goodbye"
        break
      elif nextKey == 'd': ## deal
        self.gmWin.addLine(self.client.deal())
      elif nextKey == 's': ## show hand
        cards = self.client.handlen()
        for i in range(cards):
          self.gmWin.addLine(self.client.printCard(i))
      ## how do I escape?

  ## in message mode, get a message
  def messageLoop(self,stdscr):
    line = ''
    lineend = ''
    curses.echo()
    stdscr.addstr(self.msgWin.preString)
    while True:
      nextKey = self.getNextKey(stdscr)
      if   nextKey is None:
        continue
      elif nextKey == '\n': ## display current text in message window and exit message mode
        self.msgWin.addLine(self.name,line+lineend)
        for i in range(curses.LINES-1,self.offset-1,-1):
          stdscr.move(i,0)
          stdscr.deleteln()
        break
      elif nextKey == 'KEY_BACKSPACE': ## delete previous character
        ## because of echo, backspace also moves cursor
        y,x = stdscr.getyx()
        if x > len(self.msgWin.preString)-1:
         stdscr.delch(y,x)
         line = line[:-1]
        else:
         stdscr.move(y,x+1) ## undo backspace move
         pass
      elif nextKey == 'KEY_UP': ## move messages up to display later messages
        self.msgWin.incrementDisplay()
        pass
      elif nextKey == 'KEY_DOWN': ## move messages down to display earlier messages
        self.msgWin.decrementDisplay()
        pass
      elif nextKey == 'KEY_RIGHT': ## move cursor to right
        if lineend == '':
          continue
        line = line + lineend[0]
        lineend = lineend[1:]
        y,x = stdscr.getyx()
        if x < curses.COLS:
          stdscr.move(y,x+1) 
      elif nextKey == 'KEY_LEFT': ## move cursor to left
        if line == '':
          continue
        lineend = line[-1] + lineend
        line = line[:-1]
        y,x = stdscr.getyx()
        if x > len(self.msgWin.preString)-1:
          stdscr.move(y,x-1) 
      elif len(nextKey) > 1: ## special keys mostly
        pass
      else: ## pleb typing
        line = line + str(nextKey)
        y,x = stdscr.getyx()
        stdscr.addstr(y,x,lineend)
        stdscr.move(y,x)
    curses.noecho()

