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

  def BuildDefaultMenu(self):
    self._menus = {} ## keep multiple menus
    self._defmenu = Menu()
    self._defmenu.AddEntry( 'quit', "Exit the program")
    self._defmenu.AddEntry( 'master', "Request master action")
    self._defmenu.AddEntry( '2p', "Start two player game", True) ## debugging purposes

  def BuildMenu(self, tag, menu):
    self._menus[ tag] = menu

  def RemoveMenu(self, tag, menu):
    del self._menus[ tag]

  def DisplayMenus(self):
    print("  ---------- ")
    self._defmenu.Display()
    for tag in sorted( self._menus.keys()):
      self._menus[ tag].Display()
    print("  ---------- ")

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
    elif verbose:
      print("invalid request \"{0}\"".format( req))
    return False

  def PrintMessage(self,msg):
    print(msg)

  def RequestLoop(self):
    ## custom requestLoop
    print('starting RequestLoop')
    quit = False
    try:
      while not( quit):
        #print(time.asctime(), "Waiting for requests...")
        self._defmenu._mask = self._server.GetDefaultMenuMask()
        self.DisplayMenus()
        ## create sets of the socket objects we will be waiting on
        pyroSockets = set(self._daemon.sockets)
        ## add stdin and sockets to list to wait for
        rs = [sys.stdin]
        rs.extend(pyroSockets)
        sleepTimeSec = 100
        ## use select to wait for inputs
        inp, _, _ = select.select(rs, [], [], sleepTimeSec)
        eventsForDaemon = []
        ## sort events
        for s in inp:
          if s is sys.stdin:
            req = sys.stdin.readline().rstrip()
            #print("received request: ",req)
            quit = self.ProcessMenuEntry( req)
          elif s in pyroSockets:
            eventsForDaemon.append(s)
        ## process daemon events
        if eventsForDaemon:
          #print("Daemon received a request")
          self._daemon.events(eventsForDaemon)
    except KeyboardInterrupt:
      print('exited RequestLoop')

if __name__=="__main__":
  me = GameClient()
  #print("Ready. Object uri =", me._uri)
  print("GameClient ready")
  me.RequestLoop()
  me.Cleanup()

