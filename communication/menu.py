from enum import Enum

import Pyro4
from Pyro4.util import SerializerBase

Pyro4.config.SERIALIZER = "serpent"

## class for handling menu entries
class Menu:
  def __init__( self, active=True):
    self._entries = {}
    self._mask = set([]) ## which entries to mask
    self._active = active

  ## display menu entries for user
  def Display( self):
    if self._active:
      for key in sorted( self._entries.keys()):
        if not( key in self._mask):
          line = self._entries[key]
          print('> {0:10s}: {1}'.format(key,line))

  ## solicit user for input
  def GetSelection( self, req, verbose=False):
    if self._active:
      if req in self._entries.keys():
        return not(req in self._mask)
      if verbose:
        print("invalid request \"{0}\"".format( req))
    return False

  def IsActive( self):
    return self._active

  def Activate( self):
    self._active = True

  def Deactivate( self):
    self._active = False

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

## need to define functions to serialize so Menu can be passed with Pyro
def SerializeMenuToDict(menu):
  out = {}
  out["__class__"] = "Menu"
  out["_active"] = menu._active
  for key in menu._entries.keys():
    out["_entries.{0}".format( key)] = menu._entries[ key]
    if key in menu._mask:
      out["_mask.{0}".format( key)] = True
    else:
      out["_mask.{0}".format( key)] = False
  return out

## need to define functions to serialize so Menu can be passed with Pyro
def DeserializeMenuDict(classname, mdict):
  menu = Menu()
  menu._active = mdict["_active"]
  for key in mdict.keys():
    if key[:8] == '_entries':
      xkey = key[9:]
      menu._entries[ xkey] = mdict[ key]
      if mdict[ "_mask.{0}".format( xkey)]:
        menu._mask.add( xkey)
  return menu

SerializerBase.register_class_to_dict(Menu, SerializeMenuToDict)
SerializerBase.register_dict_to_class("Menu", DeserializeMenuDict)

