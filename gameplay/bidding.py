from communication.menu import Menu
from gameplay.contracts import TeamContract

class Bidding:
  def __init__(self, server):
    self._server = server
    self._bidders = {} ## key is bidder condition, value is name of bidder
    self._leadingBid = None
    self._playerNames = []
    self.InitializeMenus()

  def InitializeMenus(self):
    self._bidMenu = Menu()
    self._bidMenu.AddEntry( 'pass', 'No bid')
    self._bidMenu.AddEntry( '3', 'Three w/ team')
    self._bidMenu.Deactivate()
    #self._announcementMenu = Menu()
    #self._announcementMenu.AddEntry( 'pass', 'No announcement')
    #self._announcementMenu.AddEntry( 'kontra', 'Kontra game')
    #self._kingMenu = Menu()
    #self._kingMenu.AddEntry( 'diamond', 'King of Diamonds')
    #self._kingMenu.AddEntry( 'spade', 'King of Spades')
    #self._kingMenu.AddEntry( 'heart', 'King of Hearts')
    #self._kingMenu.AddEntry( 'club', 'King of Clubs')

  def MenuMask(self, name, tag):
    if tag == 'bidding':
      mask = set(['3'])
      if self._leadingBid is None:
        if self._bidders['last'] == name:
          mask.discard('3')
      elif self._leadingBid == '3':
        if self._bidders['last'] == name:
          #mask.discard('3')
          pass
      return mask
    return set([])

  def GetMenu(self, name, tag):
    if tag == 'bidding':
      return self._bidMenu

  def StartBidding(self):
    self._bidders['passed'] = []
    self._bidders['active'] = self._bidders['first']
    i = self._playerNames.index( self._bidders['first'])
    Nplayer = len( self._playerNames)
    self._bidders['last'] = self._playerNames[(Nplayer+i-1)%Nplayer]
    self._bidders['leading'] = None
    self._leadingBid = None
    ## distribute bidding menu
    self._server.BroadcastMenu( 'bidding')
    self._server._playerHooks[ self._bidders['active']].ActivateMenu( 'bidding')

  ## handle message forwarding to appropriate class object
  def ProcessMenuEntry(self, name, tag, req):
    if name == self._bidders['active'] and tag == 'bidding':
      if req != 'pass':
        self._leadingBid = req
        self._bidders['leading'] = name
      else:
        self._bidders['passed'].append( name)
      self.NextActivePlayer()

  def NextActivePlayer(self):
    i = self._playerNames.index( self._bidders['active'])
    Nplayer = len( self._playerNames)
    self._server._playerHooks[ self._bidders['active']].DeactivateMenu( 'bidding')
    self._bidders['active'] = self._playerNames[(Nplayer+i-1)%Nplayer]
    self._server._playerHooks[ self._bidders['active']].ActivateMenu( 'bidding')

  def SetPlayers(self,playerNames):
    self._playerNames = playerNames
    if self._bidders.get('first',None) is None:
      self._bidders['first'] = self._playerNames[0]

  def ActiveBidder(self):
    return self._bidders['active']

  def AnnouncementMenu(self):
    return self._announcementMenu()

  def GetContract(self, req):
    if req == '3':
      return TeamContract( 3, self._leadingBidder)
    raise ValueError("invalid contract")

