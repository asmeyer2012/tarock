from communication.menu import Menu
from gameplay.contracts import Contract

class Bidding:
  def __init__(self, server):
    self._server = server
    self._bidders = {} ## key is bidder condition, value is name of bidder
    self._talon = {} ## dictionary to hold talon cards temporarily
    self._leadingBid = None
    self._playerNames = []
    self._contracts = {'K': 0, '3': 10, '2': 20, '1': 30,
                       'S3': 40, 'S2': 50, 'S1': 60, 'B': 70,
                       'S0': 80, 'OB': 90, 'CV': 125, 'V': 250}
    self._announcements = {
      'kontra':      None, 'rekontra':     None,
      'subkontra':   None, 'mordkontra':   None,
      'trula':       None, 'kings'     :   None,
      'king_ultimo': None, 'pagat_ultimo': None,
      'valat':       None
      }
    self.InitializeMenus()

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
    self._kingMenu = Menu()
    self._kingMenu.AddEntry( 'diamond', 'King of Diamonds')
    self._kingMenu.AddEntry( 'spade', 'King of Spades')
    self._kingMenu.AddEntry( 'heart', 'King of Hearts')
    self._kingMenu.AddEntry( 'club', 'King of Clubs')
    self._kingMenu.Deactivate()
    self._announcementMenu = Menu()
    self._announcementMenu.AddEntry( 'pass', 'No announcement')
    self._announcementMenu.AddEntry( 'kontra', 'Kontra game (x2)')
    self._announcementMenu.AddEntry( 'rekontra', 'Rekontra game (x4)')
    self._announcementMenu.AddEntry( 'subkontra', 'Subkontra game (x8)')
    self._announcementMenu.AddEntry( 'mordkontra', 'Mordkontra game (x16)')
    self._announcementMenu.AddEntry( 'trula', 'End game in possession of trula')
    self._announcementMenu.AddEntry( 'kings', 'End game in possession of all kings')
    self._announcementMenu.AddEntry( 'king_ultimo', 'Win called king on last trick')
    self._announcementMenu.AddEntry( 'pagat_ultimo', 'Win last trick with pagat')
    self._announcementMenu.AddEntry( 'valat', 'Win all tricks')
    self._announcementMenu.Deactivate()

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
        for ct,v in self._contracts.items():
          if ct == self._leadingBid:
            val = v
        #TODO: Update to allow for precendence
        out = dict((c,v) for c,v in self._contracts.items() if v <= val)
        for c in out:
          mask.add(c)
      return mask
    elif tag == 'announcement':
      mask = set(self._announcementMenu.keys())
      mask.discard('pass')
      if self._announcements['valat'] is None:
        mask.discard('valat')
        mask.discard('kontra')
        if not( self._announcements['kontra'] is None):
          mask.add('kontra')
          mask.discard('rekontra')
        if not( self._announcements['rekontra'] is None):
          mask.add('rekontra')
          mask.discard('subkontra')
        if not( self._announcements['subkontra'] is None):
          mask.add('subkontra')
          mask.discard('mordkontra')
        if not( self._announcements['mordkontra'] is None):
          mask.add('mordkontra')
        if self._announcements['trula'] is None:
          mask.discard('trula')
        if self._announcements['kings'] is None:
          mask.discard('kings')
        if self._announcements['king_ultimo'] is None:
          mask.discard('king_ultimo')
        if self._announcements['pagat_ultimo'] is None:
          mask.discard('pagat_ultimo')
      return mask
    return set([])

  def GetMenu(self, name, tag):
    if tag == 'bidding':
      return self._bidMenu
    if tag == 'kings':
      return self._kingMenu
    if tag == 'announcement':
      return self._announcementMenu

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
    self.BidderHook('active').ActivateMenu( 'bidding')

  def EndBidding(self):
    self.BidderHook('active').DeactivateMenu( 'bidding')
    self._server.BroadcastMessage(
      '{0} is Declarer with Bid {1}.'.format(self._bidders['leading'], self._leadingBid))
    self._server._gameControl.SetContract( self._leadingBid, self._talon)
    self.DeclareKing()

  ## return a hook to the client
  def BidderHook(self, tag):
    return self._server._clientHooks[ self._bidders[tag]]

  def DeclareKing(self):
    kingcontracts = ["3", "2", "1"]
    if self._leadingBid in kingcontracts:
      self._server.BroadcastMenu( 'kings')
      self._bidders['active'] = self._bidders['leading']
      self.BidderHook('active').ActivateMenu( 'kings')
    else:
      ## skip to talon
      self.HandleTalon()

  def HandleTalon(self):
    taloncontracts = ["3", "2", "1", "S3", "S2", "S1"]
    if self._leadingBid in taloncontracts:
      self._server.BroadcastMenu( 'talon')
      for i in range( self._server._gameControl._contract.Npiles()):
        self._server.BroadcastMenu( 'pile{}'.format(i))
      self._bidders['active'] = self._bidders['leading']
      self.BidderHook('active').ActivateMenu( 'talon')
    else:
      ## skip to announcements
      self.MakeAnnouncements()

  def MakeAnnouncements(self):
    self._server.BroadcastMessage("starting announcements")
    self._bidders['passed'] = []
    self._bidders['active'] = self._bidders['first']
    i = self._playerNames.index( self._bidders['first'])
    ## distribute bidding menu
    self._server.BroadcastMenu( 'announcement')
    self.BidderHook('active').ActivateMenu( 'announcement')

  def EndAnnouncements(self):
    for name in self._playerNames:
      self._server.ClientHook( name).DeactivateMenu('announcement')
    self._server.BroadcastMessage('ending announcements')
    self._server._gameControl.StartTricks()

  ## handle message forwarding to appropriate class object
  def ProcessMenuEntry(self, name, tag, req):
    if name == self._bidders['active'] and tag == 'bidding':
      if req != 'pass':
        self._leadingBid = req
        self._bidders['leading'] = name
        ## in this case, the incoming bid was the final bid
        if len(self._bidders['passed']) == len(self._playerNames)-1:
          self.EndBidding()
          return ## don't allow a NextActivePlayer call
      ## if the bid was 'pass'
      else:
        self._bidders['passed'].append( name)
        if len(self._bidders['passed']) == len(self._playerNames)-1:
          self._server.BroadcastMessage('Final Bid')
        elif len(self._bidders['passed']) == len(self._playerNames):
          self.EndBidding()
      self.NextActivePlayer( 'bidding')
    elif name == self._bidders['active'] and tag == 'kings':
      self._server._gameControl._contract.SetKing( req)
      self.BidderHook('active').DeactivateMenu( 'kings')
      self.HandleTalon()
    elif name == self._bidders['active'] and tag == 'talon':
      self._server._gameControl._contract.ProcessMenuEntry( name, tag, req)
    elif tag == 'announcement':
      if req != 'pass':
        ## TODO: change so more than one announcement can be made by same person at once
        ## need to have at least two rounds of passing to complete announcement process
        self._announcements[ req] = name
      ## if the bid was 'pass'
      else:
        self._bidders['passed'].append( name)
        if len(self._bidders['passed']) == len(self._playerNames):
          self.EndAnnouncements()
          return
      self.NextActivePlayer( 'announcement')

  def NextActivePlayer(self, tag):
    i = self._playerNames.index( self._bidders['active'])
    Nplayer = len( self._playerNames)
    self.BidderHook('active').DeactivateMenu( tag)
    for k in range(1,Nplayer+1):
      if (self._playerNames[(Nplayer+i-k)%Nplayer] not in self._bidders['passed'] ):
        self._bidders['active'] = self._playerNames[(Nplayer+i-k)%Nplayer]
        self.BidderHook('active').ActivateMenu( tag)
        return

  def SetPlayers(self,playerNames):
    self._playerNames = playerNames
    if self._bidders.get('first',None) is None:
      self._bidders['first'] = self._playerNames[0]

  def ActiveBidder(self):
    return self._bidders['active']

  ## add cards to talon when dealing
  ## just save here for now; will be handled by contract later
  def AddToTalon(self, card):
    self._talon[ card.ShortName()] = card

