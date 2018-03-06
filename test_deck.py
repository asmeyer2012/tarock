from cards import *
from deck_slovenian import *
from contract_slovenian import *

deck = slovenianDeck()
contract = slovenianGeneric()
pile = Pile()
pile.addCards( deck.getShuffled() )

### test card point values + ordering: OK!
#pile.orderPile()
#for card in pile.pile:
#  value = contract.getCardValue(card)
#  print card.printCard()+' : '+str(value)

### test card rankings, generic: OK!
#for i in range(8):
#  trick = Pile()
#  for j in range(4):
#    trick.putCard( pile.takeCard() )
#  topidx = contract.rankPile(trick)
#  trick.printPile()
#  print "top card: "+str(topidx)
#  print

### test card rankings, target non-trump: OK!
#for i in range(4):
#  trick = Pile()
#  for j in range(8):
#    card = pile.takeCard()
#    print card.printCard()
#    if card.suit != CardSuit.TRUMP:
#      print "added to trick"
#      trick.putCard( card )
#  print "trick complete"
#  topidx = contract.rankPile(trick)
#  trick.printPile()
#  print "top card: "+str(topidx)
#  print

