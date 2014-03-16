from enum import IntEnum
from classfile import *
from classfile.descriptor import *

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

class ConstantNameAndType (Constant):
  tag = ConstantType.NameAndType

  name_index = ConstantUtf8
  descriptor_index = ConstantUtf8

  def __str__ (self):
    return "{}: {}".format(self.name, Descriptor.parse(self.descriptor))

class ConstantClass (Constant):
  tag = ConstantType.Class

  name_index = ConstantUtf8

  def __str__ (self):
    return bin_class(self.name)


class ConstantRef (Constant):
  cls_index = ConstantClass
  name_and_type_index = ConstantNameAndType

class ConstantFieldref (ConstantRef):
  tag = ConstantType.Fieldref

  def __str__ (self):
    try:
      return "{}.{}: {}".format(
        bin_class(self.cls.name), self.name_and_type.name,
        Descriptor.parse(self.name_and_type.descriptor))
    except:
      return "Fieldref: pending..."

class ConstantMethodref (ConstantRef):
  tag = ConstantType.Methodref

  def __str__ (self):
    try:
      return "{}.{}: {}".format(bin_class(self.cls.name),
                                           self.name_and_type.name,
                                           Descriptor.parse(
                                             self.name_and_type.descriptor))
    except:
      return "Methodref: pending..."

class ConstantInterfaceMethodref (ConstantRef):
  tag = ConstantType.InterfaceMethodref

  def __str__ (self):
    try:
      return "{}.{}: {}".format(
        bin_class(self.cls.name), self.name_and_type.name,
        Descriptor.parse(self.name_and_type.descriptor))
    except:
      return "InterfaceMethodRef: pending..."


class ConstantString (Constant):
  tag = ConstantType.String

  string_index = ConstantUtf8

  def __str__ (self):
    return str(self.string)

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
  #high_bytes = 'u4'
  #low_bytes = 'u4'

  bytes = ('read', 8)

class ConstantLong (Constant64Bits):
  tag = ConstantType.Long

  @property
  def value (self):
    return int.from_bytes(self.bytes, 'big')

  def __str__ (self):
    return str(self.value)


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


