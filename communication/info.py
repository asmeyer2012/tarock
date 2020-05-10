from enum import Enum

from communication.menu import Menu

import Pyro4
from Pyro4.util import SerializerBase

Pyro4.config.SERIALIZER = "serpent"

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

## need to define functions to serialize so Menu can be passed with Pyro
def SerializeInfoToDict(info):
  out = {}
  out["__class__"] = "Info"
  out["_tag"] = info._tag
  for key in info._entries.keys():
    out["_entries.{0}".format( key)] = info._entries[ key]
    if key in info._mask:
      out["_mask.{0}".format( key)] = True
    else:
      out["_mask.{0}".format( key)] = False
  return out

## need to define functions to serialize so Menu can be passed with Pyro
def DeserializeInfoDict(classname, mdict):
  info = Info(mdict["_tag"])
  for key in mdict.keys():
    if key[:8] == '_entries':
      xkey = key[9:]
      info._entries[ xkey] = mdict[ key]
      if mdict[ "_mask.{0}".format( xkey)]:
        info._mask.add( xkey)
  return info

SerializerBase.register_class_to_dict(Info, SerializeInfoToDict)
SerializerBase.register_dict_to_class("Info", DeserializeInfoDict)

