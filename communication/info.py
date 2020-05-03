from enum import Enum

from communication.menu import Menu

## class for handling generic info
class Info:
  def __init__( self, tag):
    self._tag = tag
    self._entries = {}
    self._mask = set([]) ## which entries to mask

  ## display menu entries for user
  def Display( self):
    print('   {0}'.format(self._tag))
    for key in sorted( self._entries.keys()):
      if not( key in self._mask):
        line = self._entries[key]
        print('>     {0}'.format(line))

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
    self._mask.insert( key)

  ## unhide a menu entry
  def UnmaskEntry( self, key):
    self._mask.discard( key)

  ## copy into a menu and return
  def BuildMenu(self):
    menu = Menu()
    menu._entries = dict( self._entries)
    menu._mask = set( self._mask)
    return menu

