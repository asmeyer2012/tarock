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

  def CheckConnection(self):
    return True

  @Pyro4.oneway
  def BroadcastMessage(self,msg):
    for name in self._playerHooks:
      self._playerHooks[ name].PrintMessage( msg)

  @Pyro4.oneway
  def Ping(self):
    self.BroadcastMessage("GameServer ping")

  @Pyro4.oneway
  def ProcessMenuEntry(self, name, tag, req):
    self.BroadcastMessage("{0}: {1}/{2}".format( name, tag, req))
    if (tag,req) == ('default','2p'):
      self.StartGame()

  ## build the mask for the default menu
  def GetDefaultMenuMask(self):
    mask = set(['2p'])
    if len( self._playerHooks.keys()) > 1 and self._gameControl.State() == GameState.NOGAME:
      mask.remove('2p')
    return mask

  ## no communication with new player here! will cause process hang
  def RegisterPlayer(self, name, uri):
    if name in self._playerHooks.keys():
      return False
    self.BroadcastMessage( "{0} has joined the room".format( name))
    self._playerUris[ name] = uri
    self._playerHooks[ name] = Pyro4.Proxy( uri)
    return True

  @Pyro4.oneway
  def UnregisterPlayer(self, name):
    del self._playerHooks[ name]
    del self._playerUris[ name]
    self.BroadcastMessage( "{0} has left the room".format( name))

  def GetPlayers(self):
    return list( self._playerHooks.keys())

  @Pyro4.oneway
  def StartGame(self):
    self.BroadcastMessage("starting game")
    self._gameControl.StartGame()
    self.EndGame()

  @Pyro4.oneway
  def EndGame(self):
    self.BroadcastMessage("ending game")
    self._gameControl.EndGame()

## can be started directly from running this script,
##   but handled cleanly starting from communication/server_threads.py
if __name__=="__main__":
  Pyro4.Daemon.serveSimple( { GameServer: "GameServer" }, ns = True)

