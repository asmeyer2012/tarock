from enum import Enum
import Pyro4

## card names
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

## card suits
class CardSuit(Enum):
  ## eventually these will be colored differently in curses
  UNDEFINED = -1
  TRUMP = 0
  CLUB = 1
  HEART = 2
  SPADE = 3
  DIAMOND = 4

def ShortName( name):
  if not( isinstance( name, CardName)):
    raise TypeError("invalid card name: \"{0}\"".format( name))
  return {
    CardName.UNDEFINED: 'udf',
    CardName.PAGAT: 'pgt',
    CardName.ACE: '01',
    CardName.TWO: '02',
    CardName.THREE: '03',
    CardName.FOUR: '04',
    CardName.FIVE: '05',
    CardName.SIX: '06',
    CardName.SEVEN: '07',
    CardName.EIGHT: '08',
    CardName.NINE: '09',
    CardName.TEN: '10',
    CardName.ELEVEN: '11',
    CardName.TWELVE: '12',
    CardName.THIRTEEN: '13',
    CardName.FOURTEEN: '14',
    CardName.FIFTEEN: '15',
    CardName.SIXTEEN: '16',
    CardName.SEVENTEEN: '17',
    CardName.EIGHTEEN: '18',
    CardName.NINETEEN: '19',
    CardName.TWENTY: '20',
    CardName.MONDE: 'mnd',
    CardName.SKIS: 'ski',
    CardName.JACK: 'jck',
    CardName.CAVALIER: 'cav',
    CardName.QUEEN: 'que',
    CardName.KING: 'kng'
  }[name]

## card suits
def ShortSuit( suit):
  if not( isinstance( suit, CardSuit)):
    raise TypeError("invalid card suit: \"{0}\"".format( suit))
  return {
    CardSuit.UNDEFINED:  'udf',
    CardSuit.TRUMP: 'tmp',
    CardSuit.CLUB: 'clb',
    CardSuit.HEART: 'hrt',
    CardSuit.SPADE: 'spd',
    CardSuit.DIAMOND: 'dmd'
  }[suit]

## container object for card
class Card:
  def __init__(self,name=CardName.UNDEFINED,suit=CardSuit.UNDEFINED):
    self._name = name
    self._suit = suit
    pass
  def Name(self):
    return self._name
  def Suit(self):
    return self._suit
  def ShortName(self):
    return "{0:3}/{1:3}".format( ShortSuit( self._suit), ShortName( self._name))
  def LongName(self):
    return self.__str__()
  def __str__(self):
    return ( '{0:8s} {1:10s}'.format(self._suit.name, self._name.name) )
  def __repr__(self):
    return ( 'Card({0}, {1})'.format(self._suit, self._name) )


