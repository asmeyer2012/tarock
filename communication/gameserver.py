from __future__ import print_function
import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class GameServer(object):
  def __init__(self):
    self.player_hooks = {}
    self.player_uris = {}
  def register_player(self, name, uri):
    if name in self.player_hooks.keys():
      return False
    print("saving uri")
    self.player_uris[ name] = uri
    print("creating hook")
    self.player_hooks[ name] = Pyro4.Proxy( uri)
    print(self.player_hooks[ name])
    #print("checking hook")
    #if self.player_hooks[ name].check_connection():
    #  print("player connection successful")
    return True
  def unregister_player(self, name):
    del self.player_hooks[ name]
    del self.player_uris[ name]
  def get_players(self):
    return self.player_hooks.keys()
  def check_connection(self):
    return True

if __name__=="__main__":
  Pyro4.Daemon.serveSimple( { GameServer: "GameServer" }, ns = True)

