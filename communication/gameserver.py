from __future__ import print_function
import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class GameServer(object):
  def __init__(self):
    self.players = []
  def register_player(self, player):
    if player in self.players:
      return False
    self.players.append( player)
    return True
  def unregister_player(self, player):
    self.players.remove( player)
  def get_players(self):
    return self.players
  def check_connection(self):
    return True

def StartServer():
  Pyro4.Daemon.serveSimple( { GameServer: "game.server" }, ns = True)

if __name__=="__main__":
  StartServer()

