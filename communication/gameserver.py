from __future__ import print_function
import Pyro4

from communication.gamecontrol import GameState,GameControl

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

  ## send Menu to all players
  def BroadcastMenu(self, tag):
    for name in self._playerHooks.keys():
      self.BuildMenu( name, tag)

  def BroadcastInfo(self, tag):
    for name in self._playerHooks.keys():
      self.BuildInfo( name, tag)

  ## ping the client telling them to request Menu
  @Pyro4.oneway
  def BuildMenu(self, name, tag):
    self._playerHooks[ name].BuildMenu( tag)

  @Pyro4.oneway
  def BuildInfo(self, name, tag):
    self._playerHooks[ name].BuildInfo( tag)

  ## return the data to build a Menu instance
  def GetMenu(self, name, tag):
    return self._gameControl.GetMenu( name, tag)

  def GetInfo(self, name, tag):
    return self._gameControl.GetInfo( name, tag)

  ## build the mask for the requested menu
  def MenuMask(self, name, tag):
    return self._gameControl.MenuMask( name, tag)

  def InfoMask(self, name, tag):
    return self._gameControl.InfoMask( name, tag)

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

