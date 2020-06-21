from enum import Enum
from random import shuffle
import Pyro4

from communication.menu import Menu
from gameplay.player import Player
from gameplay.cards import CardName,CardSuit,Card
from gameplay.bidding import Bidding
from gameplay.contracts import Contract

## enumerated class of game states
class GameState(Enum):
  HANGGAME    = -2 ## player exits prematurely, place hold on game
  NOGAME      = -1 ## no game in progress
  INITIALIZE  =  0 ## assign players, do data initialization
  ROUNDSTART  =  1 ## call for skis round, manipulations of game
  BIDDING     =  2 ## do bidding, call king, talon assignment
  ROUNDFINISH =  3 ## assign scores, redo hand, clean up

class GameControl:
  def __init__(self,server):
    self._gameState = GameState.NOGAME
    self._server = server  ## save server pointer for communication
    self._playerReady = [] ## when players need to confirm ready
    self._playerNames = [] ## player names (in seat order)
    self._playerHooks = {} ## Player() class instances
    self.BuildDeck() ## build reference deck
    self._bidding = Bidding(self._server) ## control class object
    self._contract = Contract(self._server) ## control class object

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

  ## change GameState
  def ChangeState(self, state, verbose=True):
    if not( isinstance( state, GameState)):
      self._server.BroadcastMessage(
        "ChangeState called with undefined state: \"{0}\"".format( state))
      raise TypeError("undefined state")
    self._gameState = state
    if verbose:
      self._server.BroadcastMessage("Game entered state {0}".format( state))

  ## getter function for GameState
  def State(self):
    return self._gameState

  ## ping the client telling them to request Menu
  def BuildMenu(self, name, tag):
    self._server.BuildMenu( name, tag)

  ## return the data to build a Menu instance
  def GetMenu(self, name, tag):
    if tag in ['bidding','kings','announcement']:
      return self._bidding.GetMenu( name, tag)
    if tag == 'talon' or tag[:4] == 'pile':
      return self._contract.GetMenu( name, tag)
    if tag == 'hand':
      return self._playerHooks[ name].GetMenu( tag)

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
    elif tag in ['bidding','kings','announcement']:
      return self._bidding.MenuMask( name, tag)
    elif tag == 'talon' or tag[:4] == 'pile':
      return self._contract.MenuMask( name, tag)
    elif tag == 'hand':
      return self._playerHooks[ name].MenuMask( tag)
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
          self._server.BroadcastMenu( 'hand')
          self.ChangeState( GameState.BIDDING)
          self.StartBidding()
    elif tag in ['bidding','kings','announcement']:
      self._bidding.ProcessMenuEntry( name, tag, req)
    elif tag == 'talon' or tag[:4] == 'pile':
      self._contract.ProcessMenuEntry( name, tag, req)
    elif tag == 'hand' and self.State() == GameState.BIDDING:
      self._contract.ProcessMenuEntry( name, tag, req)

  ## send score to every player
  def BroadcastScore(self):
    msg = "   -- Scores:"
    for name in self._playerNames:
      score = self._playerHooks[ name].GetScore()
      msg = msg + "\n> {0:16s}: {1:>4d}".format(name,score)
    self._server.BroadcastMessage(msg)

  def StartGame(self):
    ## do initialization
    self.ChangeState( GameState.INITIALIZE)

  ## add a player to the game
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

  ## getter function for the players in this game
  def Players(self):
    return self._playerNames

  ## deal the cards and assign to players
  def Deal(self):
    shuffle( self._deck)
    Nplayer = len( self._playerNames)
    ## first ones always go to Blathers
    for i in range( 6):
      card = self._deck[i]
      self._bidding.AddToTalon( card)
    ## add cards to player hands
    for i in range( 6, len( self._deck)):
      card = self._deck[i]
      name = self._playerNames[i%Nplayer]
      self._playerHooks[ name].AddToHand( card)

  def SetContract(self, contract, talon):
    self._contract.SetContract( contract, talon)

  def CleanupRound(self):
    pass

  def Cleanup(self):
    self._playerReady = []
    self._playerNames = []
    self._playerHooks = {}

  def EndGame(self):
    self._server.BroadcastMessage("ending game")
    self.BroadcastScore()
    self.Cleanup()
    self.ChangeState( GameState.NOGAME)

  @Pyro4.oneway
  def StartBidding(self):
    self._bidding.StartBidding()

  ## only to be used for testing purposes!
  def ExecuteCommand(self, cmd):
    exec(cmd)

