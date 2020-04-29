from enum import Enum
import Pyro4

"""
Card names
"""
@Pyro4.expose
class CardName(Enum):
  UNDEFINED = -1
  PAGAT = 0
  ACE = 1 ## not pagat!
  TWO = 2
  THREE = 3
  FOUR = 4
  FIVE = 5
  SIX = 6
  SEVEN = 7
  EIGHT = 8
  NINE = 9
  TEN = 10
  ELEVEN = 11
  TWELVE = 12
  THIRTEEN = 13
  FOURTEEN = 14
  FIFTEEN = 15
  SIXTEEN = 16
  SEVENTEEN = 17
  EIGHTEEN = 18
  NINETEEN = 19
  TWENTY = 20
  MONDE = 21
  SKIS = 22
  JACK = 23
  CAVALIER = 24
  QUEEN = 25
  KING = 26

"""
Card suits
"""
@Pyro4.expose
class CardSuit(Enum):
  ## eventually these will be colored differently in curses
  UNDEFINED = -1
  TRUMP = 0
  CLUB = 1
  HEART = 2
  SPADE = 3
  DIAMOND = 4

"""
Container object for each card
"""
@Pyro4.expose
class Card:
  def __init__(self,name=CardName.UNDEFINED,suit=CardSuit.UNDEFINED):
    self.name = name
    self.suit = suit
    self.player = None
    pass
  ## need to know who played the card
  def assignPlayer(self,player):
    self.player = player
    pass
  ## clean printing
  def printCard(self):
    return ( '%8s %10s' % (self.suit.name, self.name.name) )
  ## is face card, useful when checking order
  def isFaceCard(self):
    return (self.name.value > 22)
  ## card value for counting
  def getValue(self):
    if   self.name == CardName.UNDEFINED:
      raise ValueError("Undefined card passed to getCardValue!")
    elif self.name == CardName.JACK:
      return 2.-2./3.
    elif self.name == CardName.CAVALIER:
      return 3.-2./3.
    elif self.name == CardName.QUEEN:
      return 4.-2./3.
    elif self.name == CardName.KING  or\
         self.name == CardName.PAGAT or\
         self.name == CardName.MONDE or\
         self.name == CardName.SKIS:
      return 5.-2./3.
    else:
      return 1./3.

"""
Pile is a group of more than one cards
Could be talon, hand, trick, etc...
"""
@Pyro4.expose
class Pile:
  def __init__(self):
    self.pile = list()
    pass

  def addCard(self,card):
    self.pile.append(card)
    pass
  def addCards(self,cards):
    for card in cards:
      self.addCard(card)
    pass

  def pilelen(self):
    return len(self.pile)

  ## assign player to all cards in pile
  def assignPlayer(self,player):
    for card in self.pile:
      card.assignPlayer(player)
    pass

  ## movement of cards
  def takeCard(self,i=None):
    if i is None:
      return self.pile.pop()
    return self.pile.pop(i)
  def putCard(self,card,i=None):
    if i is None:
      self.putCard(card,len(self.pile)) ## append
    else:
      self.pile.insert(i,card)
    pass

  ## flatten suits and names into separate lists
  def getFlat(self):
    suitList = list()
    nameList = list()
    for card in self.pile:
      suitList.append(card.suit)
      nameList.append(card.name)
    return (suitList,nameList)

  ## object manipulation
  def copyPile(self):
    newPile = Pile()
    for card in self.pile:
      newPile.addCard(card)
    return newPile
  def emptyPile(self):
    self.pile = list()
    pass

  ## generic: ordered by suit, then by name
  def orderPile(self):
    newPile = Pile()
    for name in CardName: ## slowsort
      for i in range(len(self.pile)-1,-1,-1): ## count backward through pile
        if self.pile[i].name == name:
          newPile.putCard(self.takeCard(i))
    self.pile = list(newPile.pile) ## copy
    newPile.emptyPile() ## empty
    for suit in CardSuit:
      for i in range(len(self.pile)-1,-1,-1):
        if self.pile[i].suit == suit:
          newPile.putCard(self.takeCard(i))
    self.pile = list(newPile.pile)
    pass

  ## printing
  def printPile(self):
    string = ''
    for card in self.pile:
      string += card.printCard()
      string += '\n\r'
    return string

  def printCard(self,i):
    return self.pile[i].printCard()
    pass

  ## get value of all cards in pile
  def getValue(self):
    value = 0.
    for card in self.pile:
      value += card.getValue()
    return value
