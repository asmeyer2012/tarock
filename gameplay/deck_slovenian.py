from cards import *
from random import shuffle

class slovenianDeck:
  def __init__(self):
    self.deck = list()
    self.initializeDeck()
    pass
  ## add all of the cards to the deck
  def initializeDeck(self):
    for name in CardName:
      if name.value == 0 or (name.value > 1 and name.value < 23):
        self.deck.append( Card(name, CardSuit.TRUMP) )
      pass
    for name in CardName:
      if   name.value > 0 and name.value < 5:
        self.deck.append( Card(name, CardSuit.HEART) )
        self.deck.append( Card(name, CardSuit.DIAMOND) )
      elif name.value > 6 and name.value < 11:
        self.deck.append( Card(name, CardSuit.CLUB) )
        self.deck.append( Card(name, CardSuit.SPADE) )
      elif name.value > 22:
        self.deck.append( Card(name, CardSuit.CLUB) )
        self.deck.append( Card(name, CardSuit.HEART) )
        self.deck.append( Card(name, CardSuit.SPADE) )
        self.deck.append( Card(name, CardSuit.DIAMOND) )
    ## unitarity check
    if len(self.deck) != 54:
      for i,card in enumerate(self.deck):
        print card.name, card.suit
      raise ValueError("Slovenian deck has wrong number of cards!")
    pass
  def getShuffled(self):
    newDeck = list(self.deck) ## copy list
    shuffle(newDeck)
    return newDeck

