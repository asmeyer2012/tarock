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
    self.get_server()
    print("registering with GameServer")
    self._registered = self.srv.register_player( self._name, self._uri)
    if not( self._registered):
      print("unsuccessful registration")
      sys.exit(1)
  def get_server(self):
    self.srv = Pyro4.Proxy("PYRONAME:GameServer")
    try:
      if self.srv.check_connection():
        print("GameServer connection successful")
    except:
      print("GameServer connection unsuccessful")
      sys.exit(1)
  def check_connection(self):
    return True
  def RequestLoop(self):
    print('starting requestLoop')
    self._daemon.requestLoop()
    print('exited requestLoop')
  def cleanup(self):
    self.srv.unregister_player( self._name)
    self._daemon.unregister( self)
    self._daemon.shutdown()
    self._daemon.close()
    print('daemon closed')

if __name__=="__main__":
  name="me"
  me = GameClient(name)
  print("Ready. Object uri =", me._uri)
  me.RequestLoop()
  me.cleanup()

