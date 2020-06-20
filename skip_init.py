import argparse
import sys
from time import sleep

import Pyro4

from communication.gameclient import GameClient
from communication.gameserver import GameState

server = Pyro4.Proxy("PYRONAME:GameServer")

## parse command line input
parser = argparse.ArgumentParser(prog='skip_init.py',
  description='fast forward to specific phase of gameplay')
parser.add_argument('input_file', help='slot reserved for skip_init.py', nargs='?')
parser.add_argument('--bid', help='designate a player bid; last player always gets bid',
  action='store')
parser.add_argument('--king', help='designate a called king', action='store')
args = parser.parse_args(sys.argv)
print(args)

## validity checks
king_suits = ['heart','diamond','spade','club'] ## king suits that are allowed

### ensure that arguments make sense together
if not( args.king is None) and not( args.king in king_suits):
  raise ValueError("invalid called king")

me = GameClient()
_sleepTime = .1

## do the fast-forward
if len( server.GetPlayers()) == 2:

  print("fast-forward to bidding")
  server.ExecuteCommand("self.StartGame()")
  for name in server.GetPlayers():
    server.ExecuteCommand("self.AddPlayer(\"{}\")".format(name))
  ## process once to initialize
  me.MainProcess(.01)
  sleep(_sleepTime) ## give server a chance to catch up
  server.ExecuteCommand("self.Deal()")
  ## process all of the cards
  for i in range(30):
    me.MainProcess(.01)
  server.ExecuteCommand("self.ChangeState( GameState.BIDDING)")
  server.ExecuteCommand("self.StartBidding()")
  server.BroadcastMenu( 'hand')
  me.MainProcess(.01)

  ## specify bid
  if not( args.bid is None):
    print("fast-forward to kings")
    server.ExecuteCommand("self._bidding.BidderHook('active').DeactivateMenu('bidding')")
    server.ExecuteCommand("self._bidding._bidders['leading'] = self._bidding._bidders['last']")
    server.ExecuteCommand("self._bidding._bidders['active'] = self._bidding._bidders['last']")
    server.ExecuteCommand(
      "self._bidding._bidders['passed'].append(self._bidding._bidders['first'])")
    server.ExecuteCommand("self._bidding._leadingBid = '{}'".format( args.bid))
    server.ExecuteCommand("self._bidding.EndBidding()")
    sleep(_sleepTime) ## give server a chance to catch up

  ## specify called king
  if not( args.king is None):
    print("fast-forward to talon")
    server.ExecuteCommand("self._bidding.BidderHook('active').DeactivateMenu('kings')")
    server.ExecuteCommand(
      "self.ProcessMenuEntry(self._bidding._bidders['leading'], 'kings', '{}')".format( args.king))
    sleep(_sleepTime) ## give server a chance to catch up

me.RequestLoop()

## if this line is commented out, then loop can be exited with ctrl-c
## can use command line to probe local class attributes
## probe remote classes with server.ExecuteCommand()
## print statements on remote will show up in that process window
me.Cleanup()

