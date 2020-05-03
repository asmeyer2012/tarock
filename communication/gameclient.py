import socket
import select
import time
import sys

import Pyro4
import Pyro4.util

from communication.gameserver import GameServer
from communication.menu import Menu

sys.excepthook = Pyro4.util.excepthook

@Pyro4.expose
class GameClient:
  def __init__(self):
    self._daemon = Pyro4.Daemon()
    self._uri = self._daemon.register( self)
    self.BuildDefaultMenu()
    self.GetServer()
    while (True):
      self._name = input(" player name > ")
      if self._server.RegisterPlayer( self._name, self._uri):
        break
      print("unsuccessful player registration: name taken")

  ## get the GameServer and save it to client attribute
  def GetServer(self):
    self._server = Pyro4.Proxy("PYRONAME:GameServer")
    try:
      if self._server.CheckConnection():
        print("GameServer connection successful")
    except Pyro4.errors.NamingError:
      print("GameServer connection unsuccessful")
      sys.exit(1)

  def Cleanup(self):
    self._server.UnregisterPlayer( self._name)
    self._daemon.unregister( self)
    self._daemon.shutdown()
    self._daemon.close()
    print('client daemon closed')

  ## build the default menu that is always available to client
  ## masking entries is controlled by GameServer
  def BuildDefaultMenu(self):
    self._menus = {} ## keep multiple menus
    self._defmenu = Menu()
    self._defmenu.AddEntry( '', "Ready", True)
    self._defmenu.AddEntry( 'quit', "Exit the program")
    self._defmenu.AddEntry( 'master', "Request master action")
    self._defmenu.AddEntry( 'end', "End the game", True)
    self._defmenu.AddEntry( '2p', "Start two player game", True) ## debugging purposes

  ## add or alter a menu of options
  def BuildMenu(self, tag, menu):
    self._menus[ tag] = menu

  ## alter mask of default menu
  def RemaskDefaultMenu(self, mask):
    self._defmenu._mask = mask

  ## alter mask of existing menu
  def RemaskMenu(self, tag, mask):
    self._menus[ tag]._mask = mask

  def RemaskMenus(self):
    self.RemaskDefaultMenu( self._server.MenuMask( self._name))
    for tag in self._menus.keys():
      self.RemaskMenu( self._server.MenuMask( self._name, tag))

  ## get rid of a menu that is not relevant
  def RemoveMenu(self, tag, menu):
    del self._menus[ tag]

  ## display all menus for client
  def DisplayMenus(self):
    print("  ---------- ")
    self._defmenu.Display()
    for tag in sorted( self._menus.keys()):
      self._menus[ tag].Display()
    print("  ---------- ")

  ## figure out if a valid request has been entered and send it to GameServer
  def ProcessMenuEntry(self, req, verbose=True):
    if req == 'quit':
      return True
    if (req in self._defmenu._entries.keys()) and not( req in self._defmenu._mask):
      self._server.ProcessMenuEntry( self._name, 'default', req)
      return False
    valid = False
    for tag in self._menus.keys():
      if self._menus[ tag].GetSelection( req):
        valid = True
        break
    if valid:
      self._server.ProcessMenuEntry( self._name, tag, req)
    elif len( req) > 0 and verbose:
      print("invalid request \"{0}\"".format( req))
    return False

  ## print message only to this client
  def PrintMessage(self,msg):
    print(msg)

  ## idle loop where requests are handled
  def RequestLoop(self):
    ## custom requestLoop
    print('starting RequestLoop')
    quit = False
    try:
      while not( quit):
        #print(time.asctime(), "Waiting for requests...")
        self.RemaskMenus()
        self.DisplayMenus()
        ## create sets of the socket objects we will be waiting on
        pyroSockets = set(self._daemon.sockets)
        ## add stdin and sockets to list to wait for
        rs = [sys.stdin]
        rs.extend(pyroSockets)
        sleepTimeSec = 100
        ## select blocks evaluation until user enters a line or server calls client process
        inp, _, _ = select.select(rs, [], [], sleepTimeSec)
        eventsForDaemon = []
        ## sort events
        for s in inp:
          ## user input
          if s is sys.stdin:
            req = sys.stdin.readline().rstrip()
            #print("received request: ",req)
            quit = self.ProcessMenuEntry( req)
          ## server call
          elif s in pyroSockets:
            eventsForDaemon.append(s)
        ## process daemon events
        if eventsForDaemon:
          #print("Daemon received a request")
          self._daemon.events(eventsForDaemon)
    except KeyboardInterrupt:
      ## can also quit with KeyboardInterrupt
      print('exited RequestLoop')

if __name__=="__main__":
  me = GameClient()
  #print("Ready. Object uri =", me._uri)
  print("GameClient ready")
  me.RequestLoop()
  me.Cleanup()

