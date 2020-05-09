from communication.gameclient import GameClient
from communication.gameserver import GameState
from time import sleep

import Pyro4

me = GameClient()
server = Pyro4.Proxy("PYRONAME:GameServer")

## do the fast-forward
if len( server.GetPlayers()) == 2:
  print("fast-forward to bidding")
  server.ExecuteCommand("self.StartGame()")
  for name in server.GetPlayers():
    server.ExecuteCommand("self.AddPlayer(\"{}\")".format(name))
  ## process once to give server a chance to initialize
  me.MainProcess(.1)
  server.ExecuteCommand("self.Deal()")
  ## process all of the cards
  for i in range(30):
    me.MainProcess(.01)
  server.ExecuteCommand("self.ChangeState( GameState.BIDDING)")
  server.ExecuteCommand("self.StartBidding()")
  server.BroadcastInfo( 'hand')

print("start loop")
me.RequestLoop()
me.Cleanup()

