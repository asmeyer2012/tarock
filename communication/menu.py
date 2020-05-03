from enum import Enum

## class for handling menu entries
class Menu:
  def __init__( self):
    self._entries = {}
    self._mask = set([]) ## which entries to mask

  ## display menu entries for user
  def Display( self):
    for key in sorted( self._entries.keys()):
      if not( key in self._mask):
        line = self._entries[key]
        print('> {0:10s}: {1}'.format(key,line))

  ## solicit user for input
  def GetSelection( self, req, verbose=False):
    if req in self._entries.keys():
      return not(req in self._mask)
    if verbose:
      print("invalid request \"{0}\"".format( req))
    return False

  ## add an entry to the menu
  def AddEntry( self, key, entry, masked=False):
    self._entries[ key] = entry
    if masked:
      self.MaskEntry( key)

  ## remove a menu entry
  def RemoveEntry( self, key):
    del self._entries[ key]

  ## hide a menu entry
  def MaskEntry( self, key):
    self._mask.add( key)

  ## unhide a menu entry
  def UnmaskEntry( self, key):
    self._mask.discard( key)

