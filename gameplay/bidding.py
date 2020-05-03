from communication.menu import Menu
from gameplay.contracts import TeamContract

class Bidding:
  def __init__(self, server):
    self._server = server
    self._bidders = {} ## key is bidder condition, value is name of bidder
    self._leadingBid = None
    self._playerNames = []
    self.BuildMenus()

  def BuildMenus(self):
    self._bidMenu = Menu()
    self._bidMenu.AddEntry( 'pass', 'No bid')
    self._bidMenu.AddEntry( '3', 'Three w/ team')
    #self._announcementMenu = Menu()
    #self._announcementMenu.AddEntry( 'pass', 'No announcement')
    #self._announcementMenu.AddEntry( 'kontra', 'Kontra game')
    #self._kingMenu = Menu()
    #self._kingMenu.AddEntry( 'diamond', 'King of Diamonds')
    #self._kingMenu.AddEntry( 'spade', 'King of Spades')
    #self._kingMenu.AddEntry( 'heart', 'King of Hearts')
    #self._kingMenu.AddEntry( 'club', 'King of Clubs')

  def StartBidding(self):
    self._bidders['active'] = self._bidders['first']
    i = self._playerNames.index( self._bidders['first'])
    Nplayer = len( self._playerNames)
    self._bidders['last'] = self._playerNames[(Nplayer+i-1)%Nplayer]
    self._bidders['leading'] = None
    self._leadingBid = None

  def SetPlayers(self,playerNames):
    self._playerNames = playerNames
    if self._bidders.get('first',None) is None:
      self._bidders['first'] = self._playerNames[0]

  def ActiveBidder(self):
    return self._bidders['active']

  def BidMenu(self):
    return self._bidMenu()

  def AnnouncementMenu(self):
    return self._announcementMenu()

  def GetContract(self, req):
    if req == '3':
      return TeamContract( 3, self._leadingBidder)
    raise ValueError("invalid contract")

