from __future__ import print_function
import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class GameServer(object):
  def __init__(self):
    self.player_hooks = {}
    self.player_uris = {}

  def CheckConnection(self):
    return True

  @Pyro4.oneway
  def BroadcastMessage(self,msg):
    for name in self.player_hooks:
      self.player_hooks[ name].PrintMessage( msg)

  @Pyro4.oneway
  def Ping(self):
    self.BroadcastMessage("GameServer ping")

  @Pyro4.oneway
  def ProcessMenuEntry(self, name, tag, req):
    self.BroadcastMessage("{0}: {1}/{2}".format( name, tag, req))

  def RegisterPlayer(self, name, uri):
    if name in self.player_hooks.keys():
      return False
    self.BroadcastMessage( "{0} has joined the game".format( name))
    self.player_uris[ name] = uri
    self.player_hooks[ name] = Pyro4.Proxy( uri)
    return True

  @Pyro4.oneway
  def UnregisterPlayer(self, name):
    del self.player_hooks[ name]
    del self.player_uris[ name]
    self.BroadcastMessage( "{0} has left the game".format( name))

if __name__=="__main__":
  Pyro4.Daemon.serveSimple( { GameServer: "GameServer" }, ns = True)

