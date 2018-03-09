from cards import *

"""
Rules for the klop contract
"""
class klop:
  def __init__(self):
    self.talon = Pile()
    pass
  ## 
  def getCardValue(self,card):
    if   card.name == CardName.UNDEFINED:
      raise ValueError("Undefined card passed to getCardValue!")
    elif card.name == CardName.JACK:
      return 2.-2./3.
    elif card.name == CardName.CAVALIER:
      return 3.-2./3.
    elif card.name == CardName.QUEEN:
      return 4.-2./3.
    elif card.name == CardName.KING  or\
         card.name == CardName.PAGAT or\
         card.name == CardName.MONDE or\
         card.name == CardName.SKIS:
      return 5.-2./3.
    else:
      return 1./3.
  ## find top card in pile, return its index from original pile
  ## pretty inefficient, but probably okay
  def rankPile(self,pile):
    suitList,nameList = pile.getFlat()
    if CardName.PAGAT in nameList and\
       CardName.MONDE in nameList and\
       CardName.SKIS  in nameList:
      return nameList.index( CardName.PAGAT ) ## emperor trick
    #
    newPile = pile.copyPile()
    newPile.orderPile()
    if CardSuit.TRUMP in suitList:
      topCard = newPile.pile[0]
      return pile.pile.index( topCard ) ## trump card, already ordered
    else:
      leadSuit = pile.pile[0].suit
      suitList,nameList = newPile.getFlat()
      if leadSuit.name == CardSuit.HEART or\
         leadSuit.name == CardSuit.DIAMOND:
        ## check for reverse ordering of red suits
        topCard = newPile.pile[ suitList.index(leadSuit) ]
        if topCard.name.value > 22: ## face card, already ordered
          return pile.pile.index( topCard )
        else: ## find the cards of leading suit and return the last
          suitList.reverse()
          topCard = newPile.pile[ len(suitList) - 1 - suitList.index(leadSuit) ]
          return pile.pile.index( topCard )
      else:
        topCard = newPile.pile[ suitList.index(leadSuit) ]
        return pile.pile.index( topCard ) ## black card, already ordered
    pass

  ## determine whether card would be the highest-ranking card if it is played to pile
  def beatTrick(self,pile,card):
    trick = pile.CopyPile()
    trick.addCard(card)
    topidx = trick.rankPile()
    if topidx == len(pile):
      return True
    else:
      return False

  def legalLead(self, hand, card):
    # only illegal lead card is Pagat, unless it's your last card
    if (card.name.value == 0 and len(hand) > 1):
      return False
    else:
      return True

  def legalFollow(self, hand, card, trick):
    # first check whether the Pagat was played illegally
    if card.name.value == 0:
      if sum(c.suit == CardSuit.TRUMP for c in hand) > 1:
        return False

    # FOLLOWED SUIT
    if card.suit == trick[0].suit: #followed suit
      if trick[0].suit == TRUMP:   #followed trump with trump
        if beatTrick(trick, card): #you beat the top card
          return True
        else:
          for c in hand:
            if beatTrick(trick, c):
              return False         #you could have beaten the top card
            else:
              return True          #you couldn't beat the top card
      else:                         #followed a natural suit
        suitList,nameList = trick.getFlat()
        if CardSuit.TRUMP in suitList: #trick has already been trumped
          return True
        else:                          #you need to beat if possible
          if beatTrick(trick, card):
            return True                #you beat the top card
          else:
            for c in hand:
              if c.suit == trick[0].suit:
                if beatTrick(trick, c):
                  return False        # you could beat the top card
            return False              # if you get here, you couldn't win

    # SHOULD HAVE FOLLOWED SUIT
    else:
      suitList,nameList = hand.getFlat()
      if trick[0].suit in suitList:
        return False

    # TRUMPED
      elif card.suit == CardSuit.TRUMP:
        tsuitList, tnameList = trick.getFlat()
        if CardSuit.TRUMP in tsuitList:
          if beatTrick(trick, card):   #you beat the top card
            return True
          else:
            for c in hand:
              if beatTrick(trick, c):
                return False #you could have beaten the top card
              else:
                return True #you couldn't beat the top card
        else:             #yours is the first trump
          return True

    # SHOULD HAVE TRUMPED
      elif CardSuit.TRUMP in suitList:
        return False

    # COULD NOT TRUMP
      else:
        return True

