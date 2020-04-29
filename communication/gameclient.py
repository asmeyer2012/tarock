import sys
import Pyro4
import Pyro4.util
from gameserver import GameServer

sys.excepthook = Pyro4.util.excepthook

class GameClient:
  def __init__(self,name):
    self._name = name
    self._registered = False
    self.get_server()
    self.register()
  def get_server(self):
    self.srv = Pyro4.Proxy("PYRONAME:game.server")
    try:
      if self.srv.check_connection():
        print("gameserver connection successful")
    except:
      print("gameserver connection unsuccessful")
      sys.exit(1)
  def register(self):
    self._registered = self.srv.register_player(self._name)
    if not(self._registered): 
      raise ValueError("player exists")
  def __del__(self):
    if self._registered:
      self.srv.unregister_player(self._name)

name="me"
me = GameClient(name)

