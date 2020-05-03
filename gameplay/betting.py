from communication.menu import Menu
from gameplay.contracts import TeamContract

class Betting:
  def __init__(self):
    self._leadingBid = None
    self._leadingBidder = None
    self.BuildMenus()

  def BuildMenu(self):
    self._betMenu = Menu()
    self._betMenu.AddEntry( '3', 'Three w/ team')
    self._announcementMenu = Menu()
    self._announcementMenu.AddEntry( '', 'No announcement')
    self._announcementMenu.AddEntry( 'kontra', 'Kontra game')

  def BetMenu(self):
    return self._betMenu()

  def AnnouncementMenu(self):
    return self._announcementMenu()

  def GetContract(self, req):
    if req == '3':
      return TeamContract( 3, self._leadingBidder)
    raise ValueError("invalid contract")

