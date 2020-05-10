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
  ## process once to initialize
  me.MainProcess(.01)
  sleep(.1) ## give server a chance to catch up
  server.ExecuteCommand("self.Deal()")
  ## process all of the cards
  for i in range(30):
    me.MainProcess(.01)
  server.ExecuteCommand("self.ChangeState( GameState.BIDDING)")
  server.ExecuteCommand("self.StartBidding()")
  server.BroadcastInfo( 'hand')
  me.MainProcess(.01)

print("start loop")
me.RequestLoop()

## if this line is commented out, then loop can be exited with ctrl-c
## can use command line to probe local class attributes
## probe remote classes with server.ExecuteCommand()
## print statements on remote will show up in that process window
me.Cleanup()

