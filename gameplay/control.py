from enum import Enum
import Pyro4

from gameplay.player import Player

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

  def BroadcastScore(self):
    msg = "  -- Scores:\n"
    for name in self._playerNames:
      score = self._playerHooks[ name].GetScore()
      msg = msg + "> {0:16s}: {1:>4d}\n".format(name,score)
    self._server.BroadcastMessage(msg)

  def StartGame(self):
    ## do initialization
    self.ChangeState( GameState.INITIALIZE)
    ## two-player test
    for i,name in enumerate( self._server.GetPlayers()[:2]):
      self._server.BroadcastMessage("player {0} in seat {1}".format( name, i))
      self._playerNames.append( name)
      self._playerHooks[ name] = Player( name, self)
    self.BroadcastScore()
    ## start round
    self.ChangeState( GameState.ROUNDSTART)

  def EndGame(self):
    self.ChangeState( GameState.NOGAME)

