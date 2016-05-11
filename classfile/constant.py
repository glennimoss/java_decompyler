from enum import IntEnum
from classfile.descriptor import HasDescriptor, ClassDescriptor, SignatureDescriptor
import classfile.meta
from classfile.meta import *
import struct
from classfile.meta import Constant

class ConstantPool (Parsed, list):
  pool_count = 'u2'

  @classmethod
  def parse (cls, rdr):
    self = cls._parse(rdr)

    rdr.constant_pool = self

    self.append(None) # Constant pool starts at 1
    while len(self) < self.pool_count:
      const = Constant.parse(rdr)
      self.append(const)
      if const.tag in (ConstantType.Long, ConstantType.Double):
        # Longs and Doubles take up two slots
        self.append(None)

    return self

  def resolve (self, idx, ref_type):
    if idx == 0:
      # TODO: Is this the right approach?
      import pdb;pdb.set_trace()
      return None
    try:
      ref = self[idx]
      assert (isinstance(ref, ref_type),
              "constant_pool[{}] = {!r}, expected {}".format(idx, ref, ref_type))
      return ref
    except IndexError:
      return idx
    #except (TypeError, AssertionError) as e:
      ##import pdb;pdb.set_trace()
      #print(e)


class ConstantType (IntEnum):
  Class               = 0x07
  Fieldref            = 0x09
  Methodref           = 0x0a
  InterfaceMethodref  = 0x0b
  String              = 0x08
  Integer             = 0x03
  Float               = 0x04
  Long                = 0x05
  Double              = 0x06
  NameAndType         = 0x0c
  Utf8                = 0x01
  MethodHandle        = 0x0f
  MethodType          = 0x10
  InvokeDynamic       = 0x12

class ConstantUtf8 (Constant):
  tag = ConstantType.Utf8

  length = 'u2'
  bytes = ('read', 'length')

  @property
  def string (self):
    return self.bytes.decode()

  def __str__ (self):
    return self.string

  def __iter__ (self):
    return iter(self.string)

class ConstantNameAndType (Constant, HasDescriptor):
  tag = ConstantType.NameAndType

  name_index = ConstantUtf8
  _descriptor_index = ConstantUtf8

  def __str__ (self):
    try:
      if isinstance(self.descriptor, SignatureDescriptor):
        return "{} {}{}".format(self.descriptor.return_type,
                                self.name,
                                self.descriptor.arg_types)
      return "{} {}".format(self.descriptor, self.name)
    except TypeError as e:
      print("-->", e)
      return "name: #{} _descriptor: #{}".format(self.name_index, self._descriptor_index)

class ConstantClass (Constant, HasDescriptor):
  tag = ConstantType.Class

  name_index = ConstantUtf8

  def __str__ (self):
    return str(self.descriptor)

  @property
  def _descriptor (self):
    return 'L{};'.format(self.name)

class ConstantRef (Constant):
  _cls_index = ConstantClass
  name_and_type_index = ConstantNameAndType

  @property
  def cls (self):
    return self._cls.descriptor

class ConstantFieldref (ConstantRef):
  tag = ConstantType.Fieldref

  def __str__ (self):
    try:
      return "{} {}.{}".format(self.name_and_type.descriptor, self.cls,
                               self.name_and_type.name)
    except AttributeError as e:
      print("-->", e)
      return "cls: #{} name_and_type: #{}".format(self._cls_index, self.name_and_type_index)

class ConstantMethodref (ConstantRef):
  tag = ConstantType.Methodref

  def __str__ (self):
    try:
      sig = self.name_and_type.descriptor
      return "{} {}.{}{}".format(sig.return_type,
                                 self.cls,
                                 self.name_and_type.name,
                                 sig.arg_types
                                )
    except AttributeError as e:
      print("-->", e)
      return "cls: #{} name_and_type: #{}".format(self._cls_index, self.name_and_type_index)

class ConstantInterfaceMethodref (ConstantMethodref):
  tag = ConstantType.InterfaceMethodref


class ConstantString (Constant):
  tag = ConstantType.String

  value_index = ConstantUtf8

  def __str__ (self):
    try:
      return '"{}"'.format(
        self.value.string
        .replace('\\', r'\\')
        .replace('"', r'\"')
      )
    except AttributeError as e:
      print("-->", e)
      return "value: #{}".format(self.value_index)

class Constant32Bits (Constant):
  bytes = ('read', 4)

class ConstantInteger (Constant32Bits):
  tag = ConstantType.Integer

  @property
  def value (self):
    return int.from_bytes(self.bytes, 'big')

  def __str__ (self):
    return str(self.value)

class ConstantFloat (Constant32Bits):
  tag = ConstantType.Float

  @property
  def value (self):
    return struct.unpack('>f', self.bytes)[0]

  def __str__ (self):
    return str(self.value)

class Constant64Bits (Constant):
  bytes = ('read', 8)

class ConstantLong (Constant64Bits):
  tag = ConstantType.Long

  @property
  def value (self):
    return int.from_bytes(self.bytes, 'big')

  def __str__ (self):
    return "{}L".format(self.value)


class ConstantDouble (Constant64Bits):
  tag = ConstantType.Double

  @property
  def value (self):
    return struct.unpack('>d', self.bytes)[0]

  def __str__ (self):
    return str(self.value)

#NO idea what to do with these
class ConstantMethodHandle (Constant):
  REF_getField          =  1  #  getfield         C.f:T
  REF_getStatic         =  2  #  getstatic        C.f:T
  REF_putField          =  3  #  putfield         C.f:T
  REF_putStatic         =  4  #  putstatic        C.f:T
  REF_invokeVirtual     =  5  #  invokevirtual    C.m:(A*)T
  REF_invokeStatic      =  6  #  invokestatic     C.m:(A*)T
  REF_invokeSpecial     =  7  #  invokespecial    C.m:(A*)T
  REF_newInvokeSpecial  =  8  #  new C; dup; invokespecial  C.<init>:(A*)void
  REF_invokeInterface   =  9  #  invokeinterface  C.m:(A*)T

  tag = ConstantType.MethodHandle

  reference_kind = 'u1'
  # 1,2,3,4
  reference_index = ConstantFieldref
  # 5,6,7,8
  reference_index = ConstantMethodref
  # 9
  reference_index = ConstantInterfaceMethodref

  # 5,6,7,9 -> ref name != <init> or <clinit>
  # 8 -> ref name == <init>

class ConstantMethodType (Constant):
  tag = ConstantType.MethodType

  descriptor_index = ConstantUtf8

class ConstantInvokeDynamic (Constant):
  tag = ConstantType.InvokeDynamic

  #bootstrap_method_attr_index = Bootsrap_ref #??
  name_and_type_index = ConstantNameAndType
