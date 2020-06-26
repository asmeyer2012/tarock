from random import shuffle
from time import sleep

from communication.menu import Menu

## wrapper class for the contracts
class Contract:
  def __init__(self, server):
    self._server = server
    self._talon = None
    self._contract = None
    self._contractSet = False
    self._leadPlayer = None
    self._activePlayer = None
    self._trick = {}

  def SetContract(self, contract, talon):
    self._talon = talon
    if contract in ['3','2','1']:
      self._contract = TeamContract( self._server, int( contract), talon)
    else:
      self._contract = DummyContract( self._server, talon)
    self._contractSet = True
    self._server.BroadcastMessage( "set contract to {}".format( self._contract._name))

  def CheckValid(self):
    if not( self._contractSet):
      raise ValueError("contract not set")

  def SetKing(self, king):
    self.CheckValid()
    self._contract.SetKing( king)

  def SetPlayers(self, playerNames):
    self._playerNames = playerNames

  def NextActivePlayer(self):
    i = self._playerNames.index( self._activePlayer)
    Nplayer = len( self._playerNames)
    self._server.ClientHook( self._activePlayer).SetToInfo( 'hand')
    self._activePlayer = self._playerNames[(i+1)%Nplayer]
    self._server.ClientHook( self._activePlayer).SetToMenu( 'hand')

  def NextLeadPlayer(self, winner):
    self._leadPlayer = winner
    self._server.ClientHook( self._activePlayer).SetToInfo( 'hand')
    if self._server.PlayerHook( self._leadPlayer).CardsInHand() == 0:
      self._server._gameControl.EndRound()
    else:
      self._activePlayer = winner
      self._server.ClientHook( self._activePlayer).SetToMenu( 'hand')

  def StartTricks(self):
    self._leadPlayer = self._server.Bidder( 'first')
    self._activePlayer = self._leadPlayer
    self._server.ClientHook( self._activePlayer).SetToMenu( 'hand')
    self._server.ClientHook( self._activePlayer).PrintMessage( "YOUR START: pick a card to play")

  def Npiles(self):
    self.CheckValid()
    return self._contract.Npiles()

  def ValidPlay(self, name, tag, req):
    playerHand = self._server.PlayerHook( name)._hand
    playedCard = playerHand[ req]
    leadCard   = self._trick.get( self._leadPlayer, None)
    return self._contract.ValidPlay( playerHand, playedCard, leadCard)

  ## return the name of the player who played the winning card
  ## trick is a dictionary; key=name, value=Card
  def TrickWinner(self):
    return self._contract.TrickWinner( self._trick, self._leadPlayer)

  def ScoreRound(self):
    cardValueSums = {}
    ## sum card values
    for name in self._playerNames:
      cardValueSums[ name] = self._server.PlayerHook( name).ScoreTricks( self._contract)
    ## sum team values
    team0 = set([ self._server.Bidder('leading') ])
    team1 = set( self._playerNames) - team0
    names = ' and '.join( list( team0))
    cardValueSums[ 'team0'] = sum([ cardValueSums[ name] for name in team0 ])
    cardValueSums[ 'team1'] = sum([ cardValueSums[ name] for name in team1 ])
    diff = cardValueSums[ 'team0'] - cardValueSums[ 'team1']
    contractValue = self._server.ContractValue() +diff
    if cardValueSums[ 'team0'] > cardValueSums[ 'team1']:
      self._server.BroadcastMessage("{} won the round with difference {}".format( names, diff))
    else:
      self._server.BroadcastMessage("{} lost the round with difference {}".format( names, diff))
      contractValue *= -1
    for name in team0:
      player = self._server.PlayerHook( name)
      player.SetScore(player.GetScore() +contractValue)
    self._server._gameControl.BroadcastScore()

  def Cleanup(self):
    self._contract = None
    self._contractSet = False
    self._leadPlayer = None
    self._activePlayer = None

  def GetMenu(self, name, tag):
    return self._contract.GetMenu( name, tag)

  def MenuMask(self, name, tag):
    return set([])

  def ProcessMenuEntry(self, name, tag, req):
    print( name, tag, req)
    if tag == 'play':
      card = self._server.PlayerHook( name)._hand[ req]
      if not( self.ValidPlay( name, tag, req)):
        self._server.ClientHook( name).PrintMessage(
          "invalid play: {}, choose another card".format( card.LongName()))
        return
      self._server.BroadcastMessage("{} played {}".format( name, card.LongName()))
      card = self._server.PlayerHook( name)._hand[ req]
      self._server.PlayerHook( name)._handMenu.MaskEntry( req)
      self._trick[ name] = card
      if set( list( self._trick.keys())) == set( self._playerNames):
        winner = self.TrickWinner()
        self._server.BroadcastMessage("{} won the trick".format( name))
        self._server.PlayerHook( winner).TakeTrick( self._trick)
        self._trick = {}
        self.NextLeadPlayer( winner)
      else:
        self.NextActivePlayer()
    elif tag == 'discard':
      self._contract.ProcessMenuEntry( name, tag, req)
    elif tag == 'talon':
      self._contract.ProcessMenuEntry( name, tag, req)

## dummy class for proof-of-principle implementation
class DummyContract:
  def __init__(self, server, talon):
    self._name = "DummyContract"
    self._server = server
    self._talon = talon
    self._pileMenus = []
    self.DistributeTalon()

  ## written for TeamContract, then copied here
  def DistributeTalon(self):
    cards = list( self._talon.values())
    shuffle( cards)
    Npile = self.Npiles()
    ## create a pile menu to choose which cards to pick up
    self._talonMenu = Menu()
    self._talonMenu.Deactivate()
    for i in range( Npile):
      tag = 'pile{}'.format( i)
      desc = '' ## description of cards in pile
      ## create a menu for each pile of cards
      menu = Menu(info=True)
      ## distribute cards to the piles
      ## build the description for the pile menu
      for card in cards[ i*self._num: (i+1)*self._num]:
        menu.AddEntry( card.ShortName(), card.LongName()) ## entry for each card
        desc = desc +('/' if (len( desc) > 0) else '') +'{}'.format( card.LongName())
      self._talonMenu.AddEntry( tag, desc) ## entry for picking piles
      self._pileMenus.append( menu)

  def Npiles(self):
    return 1

  def ValidPlay(self, hand, play, lead):
    return True

  def CardValue(self, card):
    return 0

  def TrickWinner(self, trick, leadPlayer):
    return list( trick.keys())[0]

  def GetMenu(self, name, tag):
    if tag == 'talon':
      return self._talonMenu
    elif tag[:4] == 'pile':
      return self._pileMenus[0]

  def ProcessMenuEntry(self, name, tag, req):
    if tag == 'talon' and req[:4] == 'pile':
      n = int( req[-1])
      self._server._gameControl._bidders['active'].DeactivateMenu('talon')
      self._server.BroadcastMessage("{} picked {}".format( name, req))
    raise ValueError("ProcessMenuEntry")

  def SetKing(self, king):
    raise ValueError("{} not a valid contract for calling a king".format( self._name))

## copy of DummyContract, except with kings implementation
## TODO: fix up into actual contract
class TeamContract:
  def __init__(self, server, num, talon):
    self._name = "TeamContract"
    self._server = server
    self._num = num
    self._king = None
    self._talon = talon
    self._talonMenu = None
    self._pileMenus = []
    self.DistributeTalon()

  def DistributeTalon(self):
    cards = list( self._talon.values())
    shuffle( cards)
    Npile = len( cards) //self._num
    ## create a pile menu to choose which cards to pick up
    self._talonMenu = Menu()
    self._talonMenu.Deactivate()
    for i in range( Npile):
      tag = 'pile{}'.format( i)
      desc = '' ## description of cards in pile
      ## create a menu for each pile of cards
      menu = Menu(info=True)
      #menu.Deactivate() ## menus broadcast right before display
      ## distribute cards to the piles
      ## build the description for the pile menu
      for card in cards[ i*self._num: (i+1)*self._num]:
        menu.AddEntry( card.ShortName(), card.LongName()) ## entry for each card
        desc = desc +('/' if (len( desc) > 0) else '') +'{}'.format( card.LongName())
      self._talonMenu.AddEntry( tag, desc) ## entry for picking piles
      self._pileMenus.append( menu)

  def Npiles(self):
    return len( self._pileMenus)

  def ValidPlay(self, hand, play, lead):
    return True

  def CardValue(self, card):
    return 0

  def TrickWinner(self, trick, leadPlayer):
    return list( trick.keys())[0]

  def GetMenu(self, name, tag):
    if tag == 'talon':
      return self._talonMenu
    elif tag[:4] == 'pile':
      n = int( tag[-1])
      return self._pileMenus[n]

  def ProcessMenuEntry(self, name, tag, req):
    if tag == 'talon' and req[:4] == 'pile':
      n = int( req[-1])
      self._server.BidderHook('leading').DeactivateMenu('talon')
      self._server.BroadcastMessage("{} picked {}".format( name, req))
      for shortName,longName in self._pileMenus[ n].items():
        card = self._talon[ shortName]
        self._server.BroadcastMessage("{} picked up {}".format( name, longName))
        self._server.PlayerHook( name).AddToHand( card, fromTalon=True)
      ## refresh the menu
      self._server.PlayerHook( name).HandToMenu()
      self._server.ClientHook( name).PrintMessage(
        "YOUR TURN: choose {} cards to lay down".format( self._num))
    elif tag == 'discard':
      Ndiscard = self._server.PlayerHook( name).DiscardFromHand( req)
      if Ndiscard == self._num:
        ## go to announcements
        self._server.PlayerHook( name).HandToInfo()
        self._server._gameControl._bidding.MakeAnnouncements()
      else:
        self._server.ClientHook( name).PrintMessage(
          "YOUR TURN: choose {} cards to lay down".format( self._num -Ndiscard))

  def SetKing(self, king):
    self._king = king

