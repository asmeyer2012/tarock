from enum import Enum
import Pyro4

from communication.menu import Menu
from gameplay.player import Player

## enumerated class of game states
class GameState(Enum):
  NOGAME      = -1 ## no game in progress
  INITIALIZE  =  0 ## assign players, do data initialization
  ROUNDSTART  =  1
  BETTING     =  2
  ROUNDFINISH =  3

class GameControl:
  def __init__(self,server):
    self._gameState = GameState.NOGAME
    self._server = server ## save server pointer for communication
    self._playerReady = [] ## when players need to confirm ready
    self._playerNames = [] ## player names (in seat order)
    self._playerHooks = {} ## Player() class instances
    #self._menu = Menu()

  def ChangeState(self, state):
    if not( isinstance( state, GameState)):
      self._server.BroadcastMessage(
        "ChangeState called with undefined state: \"{0}\"".format( state))
      raise TypeError("undefined state")
    self._gameState = state
    self._server.BroadcastMessage("Game entered state {0}".format( state))

  def State(self):
    return self._gameState

  #def BuildMenu(self):
  #  self._menu = Menu()
  #  self._menu.AddEntry( '', "Ready", True)
  #  self._menu.AddEntry( 'end', "End the game")
  #  self._menu.AddEntry( '2p', "Start two player game", True) ## debugging purposes

  ## build the mask for the requested menu
  def MenuMask(self, name, tag):
    if tag == 'default':
      mask = set(['2p','','end'])
      if len( self._server.GetPlayers()) > 1 and self.State() == GameState.NOGAME:
        mask.discard('2p')
      if self.State() in [ GameState.INITIALIZE, GameState.ROUNDSTART ]:
        if not( name in self._playerReady):
          mask.discard('')
        mask.discard('end')
      return mask
    else:
      return set([])

  ## handle message forwarding to appropriate class object
  def ProcessMenuEntry(self, name, tag, req):
    if (tag,req) == ('default','2p'):
      self.StartGame()
    elif (tag,req) == ('default','end'):
      self.EndGame()
    elif (tag,req) == ('default','') and self.State() == GameState.INITIALIZE:
      self.AddPlayer( name)
    elif (tag,req) == ('default','') and self.State() == GameState.ROUNDSTART:
      if name in self._playerNames:
        self._playerReady.append( name)
        self._server.BroadcastMessage("{0} ready".format( name))
        if set( self._playerReady) == set( self._playerNames):
          self._playerReady = []
          #self.ChangeState( GameState.BETTING)

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
    if not( name in self._playerNames):
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
    self._server.BroadcastMessage("ending game")
    self.BroadcastScore()
    self.Cleanup()
    self.ChangeState( GameState.NOGAME)

