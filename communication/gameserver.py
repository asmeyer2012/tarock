from __future__ import print_function
import Pyro4

from communication.gamecontrol import GameState,GameControl

## use this for options that should not be available normally
## -- adds option for client to throw exceptions
## -- adds option to probe GameControl using ExecuteCommand()
_debug = True

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class GameServer(object):
  def __init__(self):
    self._clientHooks = {}
    self._playerUris = {}
    self._gameControl = GameControl(self)

  ## debugging function
  def CheckConnection(self):
    return True

  ## send the same message to all players
  @Pyro4.oneway
  def BroadcastMessage(self,msg):
    for name in self._clientHooks:
      self._clientHooks[ name].PrintMessage( msg)

  ## debugging function
  @Pyro4.oneway
  def Ping(self):
    self.BroadcastMessage("GameServer ping")

  ## handle message forwarding to appropriate class object
  @Pyro4.oneway
  def ProcessMenuEntry(self, name, tag, req):
    self.BroadcastMessage("{0}: {1}/{2}".format( name, tag, req))
    self._gameControl.ProcessMenuEntry( name, tag, req)

  ## send Menu to all players
  def BroadcastMenu(self, tag):
    for name in self._clientHooks.keys():
      self.BuildMenu( name, tag)

  ## ping the client telling them to request Menu
  @Pyro4.oneway
  def BuildMenu(self, name, tag):
    self._clientHooks[ name].BuildMenu( tag)

  ## return the data to build a Menu instance
  def GetMenu(self, name, tag):
    return self._gameControl.GetMenu( name, tag)

  ## build the mask for the requested menu
  def MenuMask(self, name, tag):
    return self._gameControl.MenuMask( name, tag)

  ## add a player to the registry
  ## no communication with new player here! will cause process hang
  def RegisterPlayer(self, name, uri):
    if name in self._clientHooks.keys():
      ## if player is still active, can't take this name
      if self.CheckPlayerConnection( name):
        return False
    ## messages must occur before registering player!
    self.BroadcastMessage( "{0} has joined the room".format( name))
    if (self._gameControl.State() == GameState.HANGGAME and
        name in self._gameControl.Players()):
      self.BroadcastMessage( "resuming game at round start")
      self._gameControl.ChangeState( GameState.ROUNDSTART) ## internal BroadcastMessage
    ## complete registration of player
    self._playerUris[ name] = uri
    self._clientHooks[ name] = Pyro4.Proxy( uri)
    print( "registered player {0}".format( name))
    return True

  ## when a player leaves, remove them from the registry
  @Pyro4.oneway
  def UnregisterPlayer(self, name, verbose=True):
    del self._clientHooks[ name]
    del self._playerUris[ name]
    if verbose:
      print( "unregistered player {0}".format( name))
      self.BroadcastMessage( "{0} has left the room".format( name))
    if self._gameControl.State() == GameState.INITIALIZE:
      ## not far enough to matter, just reset
      self._gameControl.Cleanup()
      self._gameControl.ChangeState( GameState.NOGAME, verbose)
    elif self._gameControl.State() != GameState.NOGAME:
      self._gameControl.CleanupRound()
      self._gameControl.ChangeState( GameState.HANGGAME, verbose)

  ## get list of player names
  def GetPlayers(self):
    return list( self._clientHooks.keys())

  ## check if player is connected. if not, unregister them
  def CheckPlayerConnection(self, name):
    try:
      self._clientHooks[ name]._pyroBind()
      print("player \"{0}\" is still active".format( name))
      return True
    except Pyro4.errors.CommunicationError:
      self.UnregisterPlayer( name, verbose=False)
      print("unregistered unreachable player \"{0}\"".format( name))
      self.BroadcastMessage("unregistered unreachable player \"{0}\"".format( name))
      return False

  ## remove players that have disconnected prematurely
  def RecoverBrokenConnection(self):
    print( self._clientHooks)
    for name in list( self._clientHooks.keys()):
      self.CheckPlayerConnection( name)
    return True

  ## ease of data access
  def BidderHook(self, tag):
    return self._gameControl._bidding.BidderHook( tag)

  def Bidder(self, tag):
    return self._gameControl._bidding.Bidder( tag)

  def ClientHook(self, name):
    return self._clientHooks[ name]

  def PlayerHook(self, name):
    return self._gameControl._playerHooks[ name]

  def ContractValue(self):
    return self._gameControl._bidding.ContractValue()

  ## only to be used for testing purposes!
  if _debug:
    @Pyro4.oneway
    def ExecuteCommand(self, cmd):
      print("executing command: {0}".format(cmd))
      self._gameControl.ExecuteCommand( cmd)

## can be started directly from running this script,
##   but handled cleanly starting from communication/server_threads.py
if __name__=="__main__":
  Pyro4.Daemon.serveSimple( { GameServer: "GameServer" }, ns = True)

