
class Player:
  def __init__(self,name,server):
    self._name = name
    self._server = server
    self._score = 0
    #self._radliRemaining = 0
    #self._radliFinished = 0

  def SetScore(self,score):
    self._score = score

  def GetScore(self):
    return self._score

  #def AddRadli(self):
  #  self._radliRemaining += 1

  #def FinishRadli(self):
  #  self._radliFinished += 1
  #  self._radliRemaining -= 1

