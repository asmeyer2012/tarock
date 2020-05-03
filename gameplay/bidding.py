from communication.menu import Menu
from gameplay.contracts import TeamContract

class Bidding:
  def __init__(self):
    self._leadingBid = None
    self._leadingBidder = None
    self.BuildMenus()

  def BuildMenus(self):
    self._bidMenu = Menu()
    self._bidMenu.AddEntry( 'pass', 'No bid')
    self._bidMenu.AddEntry( '3', 'Three w/ team')
    self._announcementMenu = Menu()
    self._announcementMenu.AddEntry( 'pass', 'No announcement')
    self._announcementMenu.AddEntry( 'kontra', 'Kontra game')
    self._kingMenu = Menu()
    self._kingMenu.AddEntry( 'diamond', 'King of Diamonds')
    self._kingMenu.AddEntry( 'spade', 'King of Spades')
    self._kingMenu.AddEntry( 'heart', 'King of Hearts')
    self._kingMenu.AddEntry( 'club', 'King of Clubs')

  def BidMenu(self):
    return self._betMenu()

  def AnnouncementMenu(self):
    return self._announcementMenu()

  def GetContract(self, req):
    if req == '3':
      return TeamContract( 3, self._leadingBidder)
    raise ValueError("invalid contract")

