
class Player:
  def __init__(self,name):
    self.name = name
    self.hand = Pile()
    self.winnings = Pile()
    self.points = 0
    self.radli = 0
    pass
  def takeTrick(self,trick):
    for i in range(len(trick)):
      self.winnings.addCard(trick.removeCard())
    pass

