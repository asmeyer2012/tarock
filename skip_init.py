import argparse
import sys
from time import sleep

import Pyro4

from communication.gameclient import GameClient
from communication.gameserver import GameState

server = Pyro4.Proxy("PYRONAME:GameServer")

## parse command line input
parser = argparse.ArgumentParser(prog='skip_init',
  description='skip steps to get to specific part of game')
parser.add_argument('infile', nargs='?')
parser.add_argument('--bid', help='designate a player bid', action='store')
#parser.add_argument('--king', help='designate a called king', action='store')
args = parser.parse_args(sys.argv)
print(args)

### validity checks
#king_contracts = ['3','2','1'] ## contracts that allow a called king
#king_suits = ['heart','diamond','spade','club'] ## king suits that are allowed

### ensure that arguments make sense together
#if args.bidding and not( args.bid is None):
#  raise ValueError("cannot both start at bidding phase and specify bid")

me = GameClient()

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
  server.BroadcastMenu( 'hand')
  me.MainProcess(.01)

  if not( args.bid is None):
    print("fast-forward to kings")
    server.ExecuteCommand("self._bidding.BidderHook('active').DeactivateMenu('bidding')")
    server.ExecuteCommand("self._bidding._bidders['leading'] = self._bidding._bidders['last']")
    server.ExecuteCommand("self._bidding._bidders['active'] = self._bidding._bidders['last']")
    server.ExecuteCommand(
      "self._bidding._bidders['passed'].append(self._bidding._bidders['first'])")
    server.ExecuteCommand("self._bidding._leadingBid = '{}'".format( args.bid))
    server.ExecuteCommand("self._bidding.EndBidding()")

me.RequestLoop()

## if this line is commented out, then loop can be exited with ctrl-c
## can use command line to probe local class attributes
## probe remote classes with server.ExecuteCommand()
## print statements on remote will show up in that process window
me.Cleanup()

