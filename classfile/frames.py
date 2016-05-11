#from classfile import *
from classfile.constant import *
from classfile.meta import *
from enum import IntEnum

class VerificationType (IntEnum):
  TopVariableInfo = 0
  IntegerVariableInfo = 1
  FloatVariableInfo = 2
  DoubleVariableInfo = 3
  LongVariableInfo = 4
  NullVariableInfo = 5
  UninitializedThisVariableInfo = 6
  ObjectVariableInfo = 7
  UninitializedVariableInfo = 8
class VerificationTypeInfo (Parsed, metaclass=MetaTaggedParsed):
  tag = VerificationType

class TopVariableInfo (VerificationTypeInfo):
  pass

class IntegerVariableInfo (VerificationTypeInfo):
  pass

class FloatVariableInfo (VerificationTypeInfo):
  pass

class LongVariableInfo (VerificationTypeInfo):
  pass

class DoubleVariableInfo (VerificationTypeInfo):
  pass

class NullVariableInfo (VerificationTypeInfo):
  pass

class UninitializedThisVariableInfo (VerificationTypeInfo):
  pass

class ObjectVariableInfo (VerificationTypeInfo):
  cpool_index = ConstantClass

  @property
  def descriptor (self):
    return self.cpool.descriptor

class UninitializedVariableInfo (VerificationTypeInfo):
  offset = 'u2'

class StackMapFrame (Parsed, metaclass=MetaTaggedParsed):
  def __init__ (self, rdr, frame_type=None, **kwargs):
    super().__init__(rdr, **kwargs)
    self.frame_type = frame_type

  @classmethod
  def _read_tag (cls, rdr):
    frame_type = rdr.u1()

    if frame_type < 64:
      tag = 'SameFrame'
    elif frame_type < 128:
      tag = 'SameLocals1StackItemFrame'
    elif frame_type < 247:
      raise ValueError('Reserved for future use frame_type: {}'.format(frame_type))
    elif frame_type == 247:
      tag = 'SameLocals1StackItemFrameExtended'
    elif frame_type < 251:
      tag = 'ChopFrame'
    elif frame_type == 251:
      tag = 'SameFrameExtended'
    elif frame_type < 255:
      tag = 'AppendFrame'
    elif frame_type == 255:
      tag = 'FullFrame'
    else:
      raise ValueError('No such frame_type: {}'.format(frame_type))

    return (tag, {'frame_type': frame_type})

class SameFrame (StackMapFrame):
  @property
  def offset_delta (self):
    return self.frame_type

class SameLocals1StackItemFrame (StackMapFrame):
  stack = ('u1', VerificationTypeInfo)

  @property
  def offset_delta (self):
    return self.frame_type - 64

class SameLocals1StackItemFrameExtended (StackMapFrame):
  offset_delta = 'u2'
  stack = ('u1', VerificationTypeInfo)

class ChopFrame (StackMapFrame):
  offset_delta = 'u2'

  @property
  def num_chopped (self):
    return 251 - self.frame_type

class SameFrameExtended (StackMapFrame):
  offset_delta = 'u2'

class AppendFrame (StackMapFrame):
  offset_delta = 'u2'
  locals = ('many', 'number_of_locals', VerificationTypeInfo)

  @property
  def number_of_locals (self):
    return self.frame_type - 251

class FullFrame (StackMapFrame):
  offset_delta = 'u2'
  number_of_locals = 'u2'
  locals = ('many', 'number_of_locals', VerificationTypeInfo)
  number_of_stack_items = 'u2'
  stack = ('many', 'number_of_stack_items', VerificationTypeInfo)
