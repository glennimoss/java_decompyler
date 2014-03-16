from classfile import *
from enum import IntEnum

class VerificationType (IntEnum):
  Top = 0
  Integer = 1
  Float = 2
  Double = 3
  Long = 4
  Null = 5
  UninitializedThis = 6
  Object = 7
  Uninitialized = 8


class StackMapFrame (metaclass=Parsed):
  frame_type = 'u1'

  @classmethod
  def parse (class_, rdr):
    self = class_._parse(rdr)

    if self.frame_type < 64:
      self.__class__ = SameFrame
    elif self.frame_type < 128:
      self.__class__ = SameLocals1StackItemFrame
    elif self.frame_type < 247:
      raise ValueError('No such frame_type: {}'.format(self.frame_type))
    elif self.frame_type == 247:
      self.__class__ = SameLocals1StackItemFrameExtended
    elif self.frame_type < 251:
      self.__class__ = ChopFrame
    elif self.frame_type == 251:
      self.__class__ = SameFrameExtended
    elif self.frame_type < 255:
      self.__class__ = AppendFrame
    elif self.frame_type == 255:
      self.__class__ = FullFrame
    else:
      raise ValueError('No such frame_type: {}'.format(self.frame_type))

    self._parse_self()

    return self

class SameFrame (StackMapFrame):
  @property
  def offset_delta (self):
    return self.frame_type

class SameLocals1StackItemFrame (StackMapFrame):
  stack = ('u1', VerificationType)

  @property
  def offset_delta (self):
    return self.frame_type - 64

class SameLocals1StackItemFrameExtended:
  offset_delta = 'u2'
  stack = ('u1', VerificationType)

class ChopFrame:
  offset_delta = 'u2'

  @property
  def num_chopped (self):
    return 251 - self.frame_type

class SameFrameExtended (StackMapFrame):
  offset_delta = 'u2'

class AppendFrame (StackMapFrame):
  offset_delta = 'u2'
  locals = ('read', 'number_of_locals',
            lambda bytes: [VerificationType(b) for b in bytes])

  @property
  def number_of_locals (self):
    return frame_type - 251

class FullFrame (StackMapFrame):
  offset_delta = 'u2'
  number_of_locals = 'u2'
  locals = ('read', 'number_of_locals',
            lambda bytes: [VerificationType(b) for b in bytes])
