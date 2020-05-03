from communication.menu import Menu

class TeamContract:
  def __init__(self, num, name):
    self._num = num
    self._talon = []

  def ValidPlay(self, card, hand, lead):
    return True

  def CardValid(self, card):
    return 2/3.

