import socket
import select
import time
import sys

import Pyro4
import Pyro4.util

from gameserver import GameServer

sys.excepthook = Pyro4.util.excepthook

@Pyro4.expose
class GameClient:
  def __init__(self,name):
    self._name = name
    self._registered = False ## registered with gameserver
    print("creating Daemon")
    self._daemon = Pyro4.Daemon()
    print("registering Daemon")
    self._uri = self._daemon.register( self)
    print("getting GameServer")
    self.GetServer()
    print("registering with GameServer")
    self._registered = self.srv.RegisterPlayer( self._name, self._uri)
    if not( self._registered):
      print("unsuccessful registration")
      sys.exit(1)
  def GetServer(self):
    self.srv = Pyro4.Proxy("PYRONAME:GameServer")
    try:
      if self.srv.CheckConnection():
        print("GameServer connection successful")
    except Pyro4.errors.NamingError:
      print("GameServer connection unsuccessful")
      sys.exit(1)
  def PrintBroadcastMessage(self,msg):
    print(msg)
  def RequestLoop(self):
    print('starting RequestLoop')
    ## custom requestLoop
    try:
      while True:
        print(time.asctime(), "Waiting for requests...")
        ## create sets of the socket objects we will be waiting on
        pyroSockets = set(self._daemon.sockets)
        ## add stdin and sockets to list to wait for
        rs = [sys.stdin]
        rs.extend(pyroSockets)
        sleepTimeSec = 10
        ## use select to wait for inputs
        inp, _, _ = select.select(rs, [], [], sleepTimeSec)
        eventsForDaemon = []
        ## sort events
        for s in inp:
          if s is sys.stdin:
            val = sys.stdin.readline().rstrip()
            print("received keyboard input: ",val)
          elif s in pyroSockets:
            eventsForDaemon.append(s)
        ## process daemon events
        if eventsForDaemon:
          print("Daemon received a request")
          self._daemon.events(eventsForDaemon)
    except KeyboardInterrupt:
      print('exited RequestLoop')
  def Cleanup(self):
    self.srv.UnregisterPlayer( self._name)
    self._daemon.unregister( self)
    self._daemon.shutdown()
    self._daemon.close()
    print('daemon closed')

if __name__=="__main__":
  name="me"
  me = GameClient(name)
  print("Ready. Object uri =", me._uri)
  me.RequestLoop()
  me.Cleanup()

