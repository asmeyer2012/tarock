from communication.menu import Menu

## wrapper class for the contracts
class Contract:
  def __init__(self, server):
    self._server = server
    self._contract = None
    self._contractSet = False

  def SetContract(self, contract):
    if contract in ['3','2','1']:
      self._contract = TeamContract( int( contract))
    else:
      self._contract = DummyContract()
    self._contractSet = True
    self._server.BroadcastMessage( "set contract to {}".format( self._contract._name))

  def CheckValid(self):
    if not( self._contractSet):
      raise ValueError("contract not set")

  def ValidPlay(self, card, hand, lead):
    self.CheckValid()
    return self._contract.ValidPlay( card, hand, lead)

  def CardValue(self, card):
    self.CheckValid()
    return self._contract.CardValue( card)

  ## return the name of the player who played the winning card
  ## trick is a dictionary; key=name, value=card
  def TrickWinner(self, trick, lead):
    self.CheckValid()
    return self._contract.TrickWinner( trick)

  def Cleanup(self):
    self._contract = None
    self._contractSet = False

  def ProcessMenuEntry(self, name, tag, req):
    self.CheckValid()
    self._contract.ProcessMenuEntry( name, tag, req)

  def SetKing(self, king):
    self.CheckValid()
    self._contract.SetKing( king)

## dummy class for proof-of-principle implementation
class DummyContract:
  def __init__(self):
    self._name = "DummyContract"

  def ValidPlay(self, card, hand, lead):
    return True

  def CardValue(self, card):
    return 0

  def TrickWinner(self, trick, lead):
    return trick.keys()[0]

  def ProcessMenuEntry(self, name, tag, req):
    pass

  def SetKing(self, king):
    raise ValueError("{} not a valid contract for calling a king".format( self._name))

## copy of DummyContract, except with kings implementation
## TODO: fix up into actual contract
class TeamContract:
  def __init__(self, num):
    self._name = "TeamContract"
    self._num = num
    self._king = None

  def ValidPlay(self, card, hand, lead):
    return True

  def CardValue(self, card):
    return 0

  def TrickWinner(self, trick, lead):
    return trick.keys()[0]

  def ProcessMenuEntry(self, name, tag, req):
    pass

  def SetKing(self, king):
    self._king = king

