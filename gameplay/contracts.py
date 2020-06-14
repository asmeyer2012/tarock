from random import shuffle

from communication.menu import Menu

## wrapper class for the contracts
class Contract:
  def __init__(self, server):
    self._server = server
    self._talon = None
    self._contract = None
    self._contractSet = False

  def SetContract(self, contract, talon):
    self._talon = talon
    if contract in ['3','2','1']:
      self._contract = TeamContract( int( contract), talon)
    else:
      self._contract = DummyContract( talon)
    self._contractSet = True
    self._server.BroadcastMessage( "set contract to {}".format( self._contract._name))

  def CheckValid(self):
    if not( self._contractSet):
      raise ValueError("contract not set")

  def Npiles(self):
    self.CheckValid()
    return self._contract.Npiles()

  def ValidPlay(self, card, hand, lead):
    self.CheckValid()
    return self._contract.ValidPlay( card, hand, lead)

  def CardValue(self, card):
    self.CheckValid()
    return self._contract.CardValue( card)

  ## return the name of the player who played the winning card
  ## trick is a dictionary; key=name, value=card
  def TrickWinner(self, trick, lead):
    self.CheckValid()
    return self._contract.TrickWinner( trick)

  def Cleanup(self):
    self._contract = None
    self._contractSet = False

  def GetMenu(self, name, tag):
    return self._contract.GetMenu( name, tag)

  def MenuMask(self, name, tag):
    return set([])

  def ProcessMenuEntry(self, name, tag, req):
    self.CheckValid()
    self._contract.ProcessMenuEntry( name, tag, req)

  def SetKing(self, king):
    self.CheckValid()
    self._contract.SetKing( king)

## dummy class for proof-of-principle implementation
class DummyContract:
  def __init__(self, talon):
    self._name = "DummyContract"
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

  def ValidPlay(self, card, hand, lead):
    return True

  def CardValue(self, card):
    return 0

  def TrickWinner(self, trick, lead):
    return trick.keys()[0]

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

  def SetKing(self, king):
    raise ValueError("{} not a valid contract for calling a king".format( self._name))

## copy of DummyContract, except with kings implementation
## TODO: fix up into actual contract
class TeamContract:
  def __init__(self, num, talon):
    self._name = "TeamContract"
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

  def ValidPlay(self, card, hand, lead):
    return True

  def CardValue(self, card):
    return 0

  def TrickWinner(self, trick, lead):
    return trick.keys()[0]

  def GetMenu(self, name, tag):
    if tag == 'talon':
      return self._talonMenu
    elif tag[:4] == 'pile':
      n = int( tag[-1])
      return self._pileMenus[n]

  def ProcessMenuEntry(self, name, tag, req):
    raise ValueError("ProcessMenuEntry")

  def SetKing(self, king):
    self._king = king

