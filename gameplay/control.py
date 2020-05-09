from enum import Enum
from random import shuffle
import Pyro4

from communication.menu import Menu
from gameplay.player import Player
from gameplay.cards import CardName,CardSuit,Card
from gameplay.bidding import Bidding

## enumerated class of game states
class GameState(Enum):
  NOGAME      = -1 ## no game in progress
  INITIALIZE  =  0 ## assign players, do data initialization
  ROUNDSTART  =  1
  BIDDING     =  2
  ROUNDFINISH =  3

class GameControl:
  def __init__(self,server):
    self._gameState = GameState.NOGAME
    self._server = server  ## save server pointer for communication
    self._playerReady = [] ## when players need to confirm ready
    self._playerNames = [] ## player names (in seat order)
    self._playerHooks = {} ## Player() class instances
    self.BuildDeck() ## build reference deck
    #self._menu = Menu()    ## 'master' menu
    self._bidding = Bidding(self._server) ## control class object

  def BuildDeck(self):
    self._deck = []
    for name in CardName:
      if name.value == 0 or (name.value > 1 and name.value < 23):
        self._deck.append( Card(name, CardSuit.TRUMP) )
      pass
    for name in CardName:
      if   name.value > 0 and name.value < 5:
        self._deck.append( Card(name, CardSuit.HEART) )
        self._deck.append( Card(name, CardSuit.DIAMOND) )
      elif name.value > 6 and name.value < 11:
        self._deck.append( Card(name, CardSuit.CLUB) )
        self._deck.append( Card(name, CardSuit.SPADE) )
      elif name.value > 22:
        self._deck.append( Card(name, CardSuit.CLUB) )
        self._deck.append( Card(name, CardSuit.HEART) )
        self._deck.append( Card(name, CardSuit.SPADE) )
        self._deck.append( Card(name, CardSuit.DIAMOND) )
    ## unitarity check
    if len(self._deck) != 54:
      for i,card in enumerate(self._deck):
        print(card)
      raise ValueError("deck has wrong number of cards")

  def ChangeState(self, state):
    if not( isinstance( state, GameState)):
      self._server.BroadcastMessage(
        "ChangeState called with undefined state: \"{0}\"".format( state))
      raise TypeError("undefined state")
    self._gameState = state
    self._server.BroadcastMessage("Game entered state {0}".format( state))

  def State(self):
    return self._gameState

  ## ping the client telling them to request Menu
  def BuildMenu(self, name, tag):
    self._server.BuildMenu( name, tag)

  def BuildInfo(self, name, tag):
    self._server.BuildInfo( name, tag)

  ## return the data to build a Menu instance
  def GetMenu(self, name, tag):
    if tag == 'bidding':
      return self._bidding.GetMenu( name, tag)

  def GetInfo(self, name, tag):
    if tag == 'hand':
      return self._playerHooks[ name].GetInfo( tag)

  ## build the mask for the requested menu
  def MenuMask(self, name, tag):
    if tag == 'default':
      mask = set(['2p','','end','master'])
      if len( self._server.GetPlayers()) > 1 and self.State() == GameState.NOGAME:
        mask.discard('2p')
      if self.State() in [ GameState.INITIALIZE, GameState.ROUNDSTART ]:
        if not( name in self._playerReady):
          mask.discard('')
        mask.discard('end')
      return mask
    elif tag == 'bidding':
      return self._bidding.MenuMask( name, tag)
    else:
      return set([])

  ## build the mask for the requested menu
  def InfoMask(self, name, tag):
    if tag == 'hand':
      return self._playerHooks[ name].InfoMask( tag)
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
          self.Deal()
          self._server.BroadcastInfo( 'hand')
          self.ChangeState( GameState.BIDDING)
          self._bidding.StartBidding()
    elif tag == 'bidding':
      self._bidding.ProcessMenuEntry( name, tag, req)

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
      self._bidding.SetPlayers( self._playerNames)
      ## start round
      self.ChangeState( GameState.ROUNDSTART)

  def Deal(self):
    shuffle( self._deck)
    Nplayer = len( self._playerNames)
    for i in range( len( self._deck)):
      card = self._deck[i]
      name = self._playerNames[i%Nplayer]
      self._playerHooks[ name].AddToHand( card)

  def Cleanup(self):
    self._playerNames = []
    self._playerHooks = {}

  def EndGame(self):
    self._server.BroadcastMessage("ending game")
    self.BroadcastScore()
    self.Cleanup()
    self.ChangeState( GameState.NOGAME)

