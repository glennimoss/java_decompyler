"""Load and parse classfiles.

  >>> java_class = ClassFile.from_file('filename')
Where f is a file-like object:
  >>> java_class = ClassFile.from_bytes(f)
"""

from collections import OrderedDict
from enum import Enum, IntEnum
import struct

class ByteReader:
  def __init__ (self, data, class_file):
    self.data = data
    self.class_file = class_file

  def u1 (self):
    b = self.data.read(1)
    #print("u1:", *(hex(i) for i in b))
    #print("u1:", b)
    return int.from_bytes(b, 'big')
  def u2 (self):
    b = self.data.read(2)
    #print("u2:", *(hex(i) for i in b))
    #print("u2:", b)
    return int.from_bytes(b, 'big')
  def u4 (self):
    b = self.data.read(4)
    #print("u4:", *(hex(i) for i in b))
    #print("u4:", b)
    return int.from_bytes(b, 'big')
  def u8 (self):
    b = self.data.read(8)
    #print("u8:", *(hex(i) for i in b))
    #print("u8:", b)
    return int.from_bytes(b, 'big')

  def read (self, bytes):
    b = self.data.read(bytes)
    #print("read({}):".format(bytes), *(hex(i) for i in b))
    #print("read({}):".format(bytes), b)
    return b


class ClassFile:
  """ Represents a class file.

  A class file can be parsed from its bytes and this object is created.
  """

  magic = bytes.fromhex('CAFEBABE')

  @classmethod
  def from_file (class_, file):
    with open(file, 'rb') as f:
      return class_.from_bytes(f)

  @classmethod
  def from_bytes (class_, data):
    assert data.read(4) == class_.magic, \
        "Data does not appear to be a class file."

    self = class_()
    rdr = ByteReader(data, self)

    self.minor_version = rdr.u2()
    print('minor_version:', self.minor_version)
    self.major_version = rdr.u2()
    print('major_version:', self.major_version)
    self.constant_pool_count = rdr.u2()
    print('constant_pool_count:', self.constant_pool_count)

    self.constant_pool = [None] # Constant pool starts at 1
    while len(self.constant_pool) < self.constant_pool_count:
      const = Constant.parse(rdr)
      #print("# Constant {}:".format(len(self.constant_pool)+1), const)
      self.constant_pool.append(const)
      if const.tag in (ConstantType.Long, ConstantType.Double):
        # Longs and Doubles take up two slots
        self.constant_pool.append(None)
    for i, const in enumerate(self.constant_pool):
      if const:
        print('Constant {}:'.format(i), const)

    self.access_flags = AccessFlags.flags(rdr.u2())
    print("access_flags:", self.access_flags)
    self.this_class = rdr.u2()
    print("this_class:", self.this_class)
    self.super_class = rdr.u2()
    print("super_class:", self.super_class)
    self.interfaces_count = rdr.u2()
    print("interfaces_count:", self.interfaces_count)
    # u2
    self.interfaces = [] #[interfaces_count]
    self.fields_count = rdr.u2()
    print("fields_count:", self.fields_count)
    # field_info
    self.fields = [] #[fields_count]
    self.methods_count = rdr.u2()
    print("methods_count:", self.methods_count)
    # method_info
    self.methods = [] #[methods_count]
    self.attributes_count = rdr.u2()
    print("attributes_count:", self.attributes_count)
    # attribute_info
    self.attributes = [] #[attributes_count]

def _ref_resolver (name, ref_type):
  def resolve_ref (self):
    idx = getattr(self, name)
    try:
      ref = self.constant_pool[idx]
      assert isinstance(ref, ref_type)
      return ref
    except IndexError:
      return idx
  return resolve_ref

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

class Constant (type):
  _class_map = {}

  def __prepare__ (name, bases, **kwargs):
    return OrderedDict()

  def __new__ (meta, class_name, bases, dct):
    to_parse = []

    for name, val in list(dct.items()):
      parse_method = ('u2',)
      if type(val) is Constant and name.endswith('_index'):
        root_name = name[0:-6]
        dct[root_name] = property(_ref_resolver(name, val))

      elif isinstance(val, (str, tuple)):
        if isinstance(val, str):
          val = (val,)
        if not hasattr(ByteReader, val[0]):
          continue
        parse_method = val
      else:
        continue

      to_parse.append((name, parse_method))

    def parse (class_, rdr):
      mysuper = super(myclass, class_)
      if hasattr(mysuper, 'parse'):
        self = mysuper.parse(rdr)
      else:
        self = class_(rdr.class_file.constant_pool)
      for name, (parse_method, *args) in to_parse:
        args = [getattr(self, arg)
                if isinstance(arg, str) and hasattr(self, arg) else arg
                for arg in args]
        val = getattr(rdr, parse_method)(*args)
        #print("{}:".format(name), val)
        setattr(self, name, val)
      return self
    dct['parse'] = classmethod(parse)

    def __init__ (self, constant_pool):
      self.constant_pool = constant_pool
    dct['__init__'] = __init__

    myclass = super().__new__(meta, class_name, bases, dct)
    return myclass

  def __init__ (cls, class_name, bases, dct):
    if hasattr(cls, 'tag'):
      Constant._class_map[getattr(cls, 'tag')] = cls

    super().__init__(class_name, bases, dct)

  @classmethod
  def parse (class_, rdr):
    tag = rdr.u1()
    ConstClass = class_._class_map[tag]
    #print("tag:", ConstClass.tag)

    const = ConstClass.parse(rdr)
    #print("constant:", *const)
    return const

class ConstantUtf8 (metaclass=Constant):
  tag = ConstantType.Utf8

  length = 'u2'
  bytes = ('read', 'length')

  @property
  def string (self):
    return self.bytes.decode()

  def __str__ (self):
    return self.string

class ConstantNameAndType (metaclass=Constant):
  tag = ConstantType.NameAndType

  name_index = ConstantUtf8
  descriptor_index = ConstantUtf8

  def __str__ (self):
    return "NameAndType {}: {}".format(self.name,
                                       Descriptor.parse(self.descriptor))

class ConstantClass (metaclass=Constant):
  tag = ConstantType.Class

  name_index = ConstantUtf8

  def __str__ (self):
    return "Class: {}".format(_class_name(iter(str(self.name))))


class ConstantRef (metaclass=Constant):
  cls_index = ConstantClass
  name_and_type_index = ConstantNameAndType

class ConstantFieldref (ConstantRef):
  tag = ConstantType.Fieldref

  def __str__ (self):
    try:
      return "Fieldref: {}.{}: {}".format(
        self.cls.name, self.name_and_type.name,
        Descriptor.parse(self.name_and_type.descriptor))
    except:
      return "Fieldref: pending..."

class ConstantMethodref (ConstantRef):
  tag = ConstantType.Methodref

  def __str__ (self):
    try:
      return "Methodref: {}.{}: {}".format(self.cls.name,
                                           self.name_and_type.name,
                                           Descriptor.parse(
                                             self.name_and_type.descriptor))
    except:
      return "Methodref: pending..."

class ConstantInterfaceMethodref (ConstantRef):
  tag = ConstantType.InterfaceMethodref

  def __str__ (self):
    try:
      return "InterfaceMethodref: {}.{}: {}".format(
        self.cls.name, self.name_and_type.name,
        Descriptor.parse(self.name_and_type.descriptor))
    except:
      return "InterfaceMethodRef: pending..."


class ConstantString (metaclass=Constant):
  tag = ConstantType.String

  string_index = ConstantUtf8

  def __str__ (self):
    return "String: {}".format(self.string)

class Constant32Bits (metaclass=Constant):
  bytes = ('read', 4)

class ConstantInteger (Constant32Bits):
  tag = ConstantType.Integer

  @property
  def value (self):
    return int.from_bytes(self.bytes, 'big')

  def __str__ (self):
    return "Int: {}".format(self.value)

class ConstantFloat (Constant32Bits):
  tag = ConstantType.Float

  @property
  def value (self):
    return struct.unpack('>f', self.bytes)[0]

  def __str__ (self):
    return "Float: {}".format(self.value)

class Constant64Bits (metaclass=Constant):
  #high_bytes = 'u4'
  #low_bytes = 'u4'

  bytes = ('read', 8)

class ConstantLong (Constant64Bits):
  tag = ConstantType.Long

  @property
  def value (self):
    return int.from_bytes(self.bytes, 'big')

  def __str__ (self):
    return "Long: {}".format(self.value)


class ConstantDouble (Constant64Bits):
  tag = ConstantType.Double

  @property
  def value (self):
    return struct.unpack('>d', self.bytes)[0]

  def __str__ (self):
    return "Double: {}".format(self.value)

class ConstantMethodHandle (metaclass=Constant):
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

class ConstantMethodType (metaclass=Constant):
  tag = ConstantType.MethodType

  descriptor_index = ConstantUtf8

class ConstantInvokeDynamic (metaclass=Constant):
  tag = ConstantType.InvokeDynamic

  #bootstrap_method_attr_index = Bootsrap_ref #??
  name_and_type_index = ConstantNameAndType


class AccessFlags (IntEnum):
  """Access flag constants.

  ACC_PUBLIC: Declared public; may be accessed from outside its package.
  ACC_FINAL: Declared final; no subclasses allowed.
  ACC_SUPER: Treat superclass methods specially when invoked by the
             invokespecial instruction.
  ACC_INTERFACE: Is an interface, not a class.
  ACC_ABSTRACT: Declared abstract; must not be instantiated.
  ACC_SYNTHETIC: Declared synthetic; not present in the source code.
  ACC_ANNOTATION: Declared as an annotation type.
  ACC_ENUM: Declared as an enum type.
  """

  ACC_PUBLIC     = 0x0001
  ACC_FINAL      = 0x0010
  ACC_SUPER      = 0x0020
  ACC_INTERFACE  = 0x0200
  ACC_ABSTRACT   = 0x0400
  ACC_SYNTHETIC  = 0x1000
  ACC_ANNOTATION = 0x2000
  ACC_ENUM       = 0x4000

  @staticmethod
  def flags (flags_set):
    flags = set()

    for flag in AccessFlags:
      if flag & flags_set:
        flags.add(flag)

    return flags

def _class_name (it):
  chars = []
  try:
    c = next(it)
    while c != ';':
      if c == '/':
        c = '.'
      chars.append(c)
      c = next(it)
  except StopIteration:
    pass
  return ''.join(chars)

def _array (it):
  return Descriptor.parse(it) + '[]'

def _args (it):
  args = []

  try:
    while True:
      args.append(Descriptor.parse(it))
  except StopIteration:
    pass

  return_type = Descriptor.parse(it)

  return "{} ({})".format(return_type, ', '.join(args))

def _end_args (it):
  raise StopIteration()


class Descriptor:
  _char_map = {
    'B': 'byte',
    'C': 'char',
    'D': 'double',
    'F': 'float',
    'I': 'int',
    'J': 'long',
    'L': _class_name,
    'S': 'short',
    'V': 'void',
    'Z': 'boolean',
    '[': _array,
    '(': _args,
    ')': _end_args,
  }

  @classmethod
  def parse (class_, desc):
    if isinstance(desc, ConstantUtf8):
      desc = str(desc)
    it = iter(desc)

    t = Descriptor._char_map[next(it)]
    if callable(t):
      t = t(it)

    return t





class Opcode:
  code = 0


if __name__ == '__main__':
  import sys
  classfile = ClassFile.from_file(sys.argv[1])
