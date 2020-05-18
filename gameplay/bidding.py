from communication.menu import Menu
from gameplay.contracts import TeamContract

class Bidding:
  def __init__(self, server):
    self._server = server
    self._bidders = {} ## key is bidder condition, value is name of bidder
    self._leadingBid = None
    self._playerNames = []
    self.InitializeMenus()
    self.contracts = {'K': 0, '3': 10, '2': 20, '1': 30,
                      'S3': 40, 'S2': 50, 'S1': 60, 'B': 70,
                      'S0': 80, 'OB': 90, 'CV': 125, 'V': 250}

  def InitializeMenus(self):
    self._bidMenu = Menu()
    self._bidMenu.AddEntry( 'pass', 'No bid')
    self._bidMenu.AddEntry( 'K',  'Klop')
    self._bidMenu.AddEntry( '3',  'Three w/ partner')
    self._bidMenu.AddEntry( '2',  'Two   w/ partner')
    self._bidMenu.AddEntry( '1',  'One   w/ partner')
    self._bidMenu.AddEntry( 'S3', 'Solo Three')
    self._bidMenu.AddEntry( 'S2', 'Solo Two')
    self._bidMenu.AddEntry( 'S1', 'Solo One')
    self._bidMenu.AddEntry( 'B',  'Beggar')
    self._bidMenu.AddEntry( 'S0', 'Solo Without')
    self._bidMenu.AddEntry( 'OB', 'Open Beggar')
    self._bidMenu.AddEntry( 'CV', 'Color Valat Without')
    self._bidMenu.AddEntry( 'V',  'Valat Without')
    self._bidMenu.Deactivate()
    #self._announcementMenu = Menu()
    #self._announcementMenu.AddEntry( 'pass', 'No announcement')
    #self._announcementMenu.AddEntry( 'kontra', 'Kontra game')
    self._kingMenu = Menu()
    self._kingMenu.AddEntry( 'diamond', 'King of Diamonds')
    self._kingMenu.AddEntry( 'spade', 'King of Spades')
    self._kingMenu.AddEntry( 'heart', 'King of Hearts')
    self._kingMenu.AddEntry( 'club', 'King of Clubs')
    self._kingMenu.Deactivate()

  def MenuMask(self, name, tag):
    if tag == 'bidding':
      # Make 3 and Klop available only to final bidder after three passes
      mask = set(['K','3'])
      if self._leadingBid is None:
        if self._bidders['last'] == name:
          mask.discard('3')
          mask.discard('K')
      # Mask off any bids lower than current bid
      else:
        val = 10
        for ct,v in self.contracts.items():
          if ct == self._leadingBid:
            val = v
        #TODO: Update to allow for precendence
        out = dict((c,v) for c,v in self.contracts.items() if v <= val)
        for c in out:
          mask.add(c)
      return mask
    return set([])

  def GetMenu(self, name, tag):
    if tag == 'bidding':
      return self._bidMenu
    if tag == 'kings':
      return self._kingMenu

  def StartBidding(self):
    self._bidders['passed'] = []
    self._bidders['active'] = self._bidders['first']
    i = self._playerNames.index( self._bidders['first'])
    Nplayer = len( self._playerNames)
    self._bidders['last'] = self._playerNames[(Nplayer+i-1)%Nplayer]
    self._bidders['leading'] = None
    self._leadingBid = None
    ## distribute bidding menu
    self._server.BroadcastMenu( 'bidding')
    self._server._playerHooks[ self._bidders['active']].ActivateMenu( 'bidding')

  def EndBidding(self):
    self._server._playerHooks[ self._bidders['active']].DeactivateMenu( 'bidding')
    self._server.BroadcastMessage(
      '{0} is Declarer with Bid {1}.'.format(self._bidders['leading'], self._leadingBid))
    self.DeclareKing()

  ## handle message forwarding to appropriate class object
  def ProcessMenuEntry(self, name, tag, req):
    if name == self._bidders['active'] and tag == 'bidding':
      if req != 'pass':
        self._leadingBid = req
        self._bidders['leading'] = name
        ## in this case, the incoming bid was the final bid
        if len(self._bidders['passed']) == len(self._playerNames)-1:
          self.EndBidding()
      ## if the bid was 'pass'
      else:
        self._bidders['passed'].append( name)
        if len(self._bidders['passed']) == len(self._playerNames)-1:
          self._server.BroadcastMessage('Final Bid')
        elif len(self._bidders['passed']) == len(self._playerNames):
          self.EndBidding()
      self.NextActivePlayer()

  def NextActivePlayer(self):
    i = self._playerNames.index( self._bidders['active'])
    Nplayer = len( self._playerNames)
    self._server._playerHooks[ self._bidders['active']].DeactivateMenu( 'bidding')
    for k in range(1,Nplayer+1):
      if (self._playerNames[(Nplayer+i-k)%Nplayer] not in self._bidders['passed'] ):
        self._bidders['active'] = self._playerNames[(Nplayer+i-k)%Nplayer]
        self._server._playerHooks[ self._bidders['active']].ActivateMenu( 'bidding')
        return

  def DeclareKing(self):
    kingcontracts = ["3", "2", "1"]
    if self._leadingBid in kingcontracts:
      self._server.BroadcastMenu( 'kings')
      self._bidders['active'] = self._bidders['leading']
      self._server._playerHooks[ self._bidders['active']].ActivateMenu( 'kings')

  def SetPlayers(self,playerNames):
    self._playerNames = playerNames
    if self._bidders.get('first',None) is None:
      self._bidders['first'] = self._playerNames[0]

  def ActiveBidder(self):
    return self._bidders['active']

  def AnnouncementMenu(self):
    return self._announcementMenu()

  def StartAnnouncements(self):
    return

  def GetContract(self, req):
    if req == '3':
      return TeamContract( 3, self._leadingBidder)
    raise ValueError("invalid contract")

