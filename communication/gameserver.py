from __future__ import print_function
import Pyro4

from gameplay.control import GameState,GameControl

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class GameServer(object):
  def __init__(self):
    self._playerHooks = {}
    self._playerUris = {}
    self._gameControl = GameControl(self)

  ## debugging function
  def CheckConnection(self):
    return True

  ## send the same message to all players
  @Pyro4.oneway
  def BroadcastMessage(self,msg):
    for name in self._playerHooks:
      self._playerHooks[ name].PrintMessage( msg)

  ## debugging function
  @Pyro4.oneway
  def Ping(self):
    self.BroadcastMessage("GameServer ping")

  ## handle message forwarding to appropriate class object
  @Pyro4.oneway
  def ProcessMenuEntry(self, name, tag, req):
    self.BroadcastMessage("{0}: {1}/{2}".format( name, tag, req))
    self._gameControl.ProcessMenuEntry( name, tag, req)

  ## build the mask for the requested menu
  def MenuMask(self, name, tag):
    return self._gameControl.MenuMask( name, tag)

  ## add a player to the registry
  ## no communication with new player here! will cause process hang
  def RegisterPlayer(self, name, uri):
    if name in self._playerHooks.keys():
      return False
    self.BroadcastMessage( "{0} has joined the room".format( name))
    self._playerUris[ name] = uri
    self._playerHooks[ name] = Pyro4.Proxy( uri)
    return True

  ## when a player leaves, remove them from the registry
  @Pyro4.oneway
  def UnregisterPlayer(self, name):
    del self._playerHooks[ name]
    del self._playerUris[ name]
    self.BroadcastMessage( "{0} has left the room".format( name))

  ## get list of player names
  def GetPlayers(self):
    return list( self._playerHooks.keys())

## can be started directly from running this script,
##   but handled cleanly starting from communication/server_threads.py
if __name__=="__main__":
  Pyro4.Daemon.serveSimple( { GameServer: "GameServer" }, ns = True)

