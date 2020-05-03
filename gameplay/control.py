from enum import Enum
import Pyro4

from gameplay.player import Player

## enumerated class of game states
class GameState(Enum):
  NOGAME      = -1 ## no game in progress
  INITIALIZE  =  0 ## assign players, do data initialization
  ROUNDSTART  =  1
  ROUNDFINISH =  2

class GameControl:
  def __init__(self,server):
    self._gameState = GameState.NOGAME
    self._server = server ## save server pointer for communication
    self._playerNames = [] ## player names (in seat order)
    self._playerHooks = {} ## Player() class instances

  def ChangeState(self, state):
    if not( isinstance( state, GameState)):
      self._server.BroadcastMessage(
        "ChangeState called with undefined state: \"{0}\"".format( state))
      raise TypeError("undefined state")
    self._gameState = state
    self._server.BroadcastMessage("Game entered state {0}".format( state))

  def State(self):
    return self._gameState

  ## handle message forwarding to appropriate class object
  def ProcessMenuEntry(self, name, tag, req):
    if (tag,req) == ('default','2p'):
      self.StartGame()
    elif (tag,req) == ('default','end'):
      self.EndGame()
    elif (tag,req) == ('default','') and self.State() == GameState.INITIALIZE:
      self.AddPlayer( name)

  ## send score to every player
  def BroadcastScore(self):
    msg = "  -- Scores:\n"
    for name in self._playerNames:
      score = self._playerHooks[ name].GetScore()
      msg = msg + "> {0:16s}: {1:>4d}\n".format(name,score)
    self._server.BroadcastMessage(msg)

  def StartGame(self):
    ## do initialization
    self.ChangeState( GameState.INITIALIZE)

  def AddPlayer(self, name):
    i = len( self._playerNames)
    ## two-player test
    self._server.BroadcastMessage("player {0} in seat {1}".format( name, i))
    self._playerNames.append( name)
    self._playerHooks[ name] = Player( name, self)
    if len( self._playerNames) == 2:
      self.BroadcastScore()
      ## start round
      self.ChangeState( GameState.ROUNDSTART)

  def Cleanup(self):
    self._playerNames = []
    self._playerHooks = {}

  def EndGame(self):
    print("ending game")
    self.BroadcastScore()
    self.Cleanup()
    self.ChangeState( GameState.NOGAME)

