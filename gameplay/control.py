from enum import Enum
import Pyro4

class GameState(Enum):
  UNDEFINED   = -1 ## no game in progress
  INITIALIZE  =  0 ## assign players, do data initialization
  ROUNDSTART  =  1
  ROUNDFINISH =  2

class GameControl:
  def __init__(self,server):
    self._gameState = GameState.UNDEFINED
    self._server = server ## save server pointer for communication

  def ChangeState(self, state):
    if not( isinstance( state, GameState)):
      self._server.BroadcastMessage(
        "ChangeState called with undefined state: \"{0}\"".format( state))
      raise TypeError("undefined state")
    self._gameState = state

  def StartGame(self):
    self.ChangeState( GameState.INITIALIZE)
    ## do initialization
    self.ChangeState( GameState.ROUNDSTART)

  def EndGame(self):
    self.ChangeState( GameState.UNDEFINED)

