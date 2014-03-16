"""Load and parse classfiles.

  >>> java_class = ClassFile.from_file('filename')
Where f is a file-like object:
  >>> java_class = ClassFile.from_bytes(f)
"""

from collections import OrderedDict
from enum import Enum, IntEnum
import struct
import io

def unsigned (n):
  def uN (self, callback=None):
    b = self.data.read(n)
    #print("u1:", *(hex(i) for i in b))
    #print("u1:", b)
    u = int.from_bytes(b, 'big')
    if callback:
      return callback(u)
    return u
  return uN

class ByteReader:
  def __init__ (self, data, class_file):
    self.data = data
    self.class_file = class_file
    self.sub_readers = {}

  u1 = unsigned(1)
  u2 = unsigned(2)
  u3 = unsigned(3)
  u4 = unsigned(4)
  u8 = unsigned(8)

  def read (self, bytes):
    b = self.data.read(bytes)
    #print("read({}):".format(bytes), *(hex(i) for i in b))
    #print("read({}):".format(bytes), b)
    return b

  def many (self, how_many, ParseClass):
    items = []
    for i in range(how_many):
      items.append(ParseClass.parse(self))
    return items


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
      const = Constant(rdr)
      #print("# Constant {}:".format(len(self.constant_pool)+1), const)
      self.constant_pool.append(const)
      if const.tag in (ConstantType.Long, ConstantType.Double):
        # Longs and Doubles take up two slots
        self.constant_pool.append(None)
    for i, const in enumerate(self.constant_pool):
      if const:
        print('Constant {}:'.format(i), const)

    self.access_flags = ClassAccessFlags.flags(rdr.u2())
    print("access_flags:", self.access_flags)
    self.this_class = self.constant_pool[rdr.u2()]
    print("this_class:", self.this_class)
    self.super_class = self.constant_pool[rdr.u2()]
    print("super_class:", self.super_class)

    self.interfaces_count = rdr.u2()
    print("interfaces_count:", self.interfaces_count)
    self.interfaces = []
    for i in range(self.interfaces_count):
      interface = self.constant_pool[rdr.u2()]
      assert isinstance(interface, ConstantClass), (
        "Interface must reference a ConstantClass item in the constant pool")
      self.interfaces.append(interface)
    print("interfaces:", ", ".join(_bin_class(i.name) for i in self.interfaces))

    self.fields_count = rdr.u2()
    print("fields_count:", self.fields_count)
    self.fields = []
    for i in range(self.fields_count):
      self.fields.append(Field.parse(rdr))
    print("fields:", ", ".join(str(f) for f in self.fields))

    self.methods_count = rdr.u2()
    print("methods_count:", self.methods_count)
    self.methods = []
    for i in range(self.methods_count):
      self.methods.append(Method.parse(rdr))
    print("methods:", ", ".join(str(m) for m in self.methods))

    self.attributes_count = rdr.u2()
    print("attributes_count:", self.attributes_count)
    self.attributes = []
    for i in range(self.attributes_count):
      self.attributes.append(Attribute.parse(rdr))
    print("attributes:", ", ".join(str(a) for a in self.attributes))

def _ref_resolver (name, ref_type):
  def resolve_ref (self):
    idx = getattr(self, name)
    try:
      ref = self.constant_pool[idx]
      #assert isinstance(ref, ref_type)
      assert issubclass(ref_type, type(ref))
      return ref
    except IndexError:
      return idx
    except TypeError:
      import pdb;pdb.set_trace()
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

# Bootstrap creation of Constant class
Constant = type(None)
class Parsed (type):
  _class_map = {}

  def __prepare__ (name, bases, **kwargs):
    return OrderedDict()

  def __new__ (meta, class_name, bases, dct):
    to_parse = []

    for name, val in list(dct.items()):
      parse_method = ('u2',)
      if isinstance(val, type) and issubclass(val, Constant):
        if name.endswith('_index'):
          root_name = name[0:-6]
        else:
          root_name = name
          name = '_' + name
        dct[root_name] = property(_ref_resolver(name, val))

      elif isinstance(val, (str, tuple, list)):
        if isinstance(val, str):
          val = (val,)
        if isinstance(val, tuple) and not hasattr(ByteReader, val[0]):
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
        self = class_(rdr)
      for name, (parse_method, *args) in to_parse:
        args = [getattr(self, arg)
                if isinstance(arg, str) and hasattr(self, arg) else arg
                for arg in args]
        val = getattr(rdr, parse_method)(*args)
        #print("{}:".format(name), val)
        setattr(self, name, val)
      return self
    dct['_parse' if 'parse' in dct else 'parse'] = classmethod(parse)

    def __init__ (self, rdr):
      self.constant_pool = rdr.class_file.constant_pool
    dct['__init__'] = __init__

    myclass = super().__new__(meta, class_name, bases, dct)
    return myclass

  def __init__ (cls, class_name, bases, dct):
    if 'tag' in dct:
      Constant._class_map[dct['tag']] = cls

    super().__init__(class_name, bases, dct)

class Constant (metaclass=Parsed):
  def __new__ (class_, rdr):
    if class_ is not Constant:
      return super(Constant, class_).__new__(class_)
    tag = rdr.u1()
    ConstClass = class_._class_map[tag]
    #print("tag:", ConstClass.tag)

    const = ConstClass.parse(rdr)
    #print("constant:", *const)
    return const
# Remove parse method from base class
delattr(Constant, 'parse')

class ConstantUtf8 (Constant):
  tag = ConstantType.Utf8

  length = 'u2'
  bytes = ('read', 'length')

  @property
  def string (self):
    return self.bytes.decode()

  def __str__ (self):
    return self.string

class ConstantNameAndType (Constant):
  tag = ConstantType.NameAndType

  name_index = ConstantUtf8
  descriptor_index = ConstantUtf8

  def __str__ (self):
    return "NameAndType {}: {}".format(self.name,
                                       Descriptor.parse(self.descriptor))

class ConstantClass (Constant):
  tag = ConstantType.Class

  name_index = ConstantUtf8

  def __str__ (self):
    return "Class: {}".format(_bin_class(self.name))


class ConstantRef (Constant):
  cls_index = ConstantClass
  name_and_type_index = ConstantNameAndType

class ConstantFieldref (ConstantRef):
  tag = ConstantType.Fieldref

  def __str__ (self):
    try:
      return "Fieldref: {}.{}: {}".format(
        _bin_class(self.cls.name), self.name_and_type.name,
        Descriptor.parse(self.name_and_type.descriptor))
    except:
      return "Fieldref: pending..."

class ConstantMethodref (ConstantRef):
  tag = ConstantType.Methodref

  def __str__ (self):
    try:
      return "Methodref: {}.{}: {}".format(_bin_class(self.cls.name),
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
        _bin_class(self.cls.name), self.name_and_type.name,
        Descriptor.parse(self.name_and_type.descriptor))
    except:
      return "InterfaceMethodRef: pending..."


class ConstantString (Constant):
  tag = ConstantType.String

  string_index = ConstantUtf8

  def __str__ (self):
    return "String: {}".format(self.string)

class Constant32Bits (Constant):
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
    return "Long: {}".format(self.value)


class ConstantDouble (Constant64Bits):
  tag = ConstantType.Double

  @property
  def value (self):
    return struct.unpack('>d', self.bytes)[0]

  def __str__ (self):
    return "Double: {}".format(self.value)

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


@classmethod
def _find_flags (class_, bits):
  flags = set()

  for flag in class_:
    if flag & bits:
      flags.add(flag)

  return flags

class ClassAccessFlags (IntEnum):
  """Class access flag constants.

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

  flags = _find_flags

class FieldAccessFlags (IntEnum):
  """Field access flag constants.

  ACC_PUBLIC: Declared public; may be accessed from outside its package.
  ACC_PRIVATE: Declared private; usable only within the defining class.
  ACC_PROTECTED: Declared protected; may be accessed within subclasses.
  ACC_STATIC: Declared static.
  ACC_FINAL: Declared final; never directly assigned to after object
             construction (JLS §17.5).
  ACC_VOLATILE: Declared volatile; cannot be cached.
  ACC_TRANSIENT: Declared transient; not written or read by a persistent object
                 manager.
  ACC_SYNTHETIC: Declared synthetic; not present in the source code.
  ACC_ENUM: Declared as an element of an enum.
  """

  ACC_PUBLIC    = 0x0001
  ACC_PRIVATE   = 0x0002
  ACC_PROTECTED = 0x0004
  ACC_STATIC    = 0x0008
  ACC_FINAL     = 0x0010
  ACC_VOLATILE  = 0x0040
  ACC_TRANSIENT = 0x0080
  ACC_SYNTHETIC = 0x1000
  ACC_ENUM      = 0x4000

  flags = _find_flags

class MethodAccessFlags (IntEnum):
  """Method access flag constants.

  ACC_PUBLIC: Declared public; may be accessed from outside its package.
  ACC_PRIVATE: Declared private; accessible only within the defining class.
  ACC_PROTECTED: Declared protected; may be accessed within subclasses.
  ACC_STATIC: Declared static.
  ACC_FINAL: Declared final; must not be overridden (§5.4.5).
  ACC_SYNCHRONIZED: Declared synchronized; invocation is wrapped by a monitor
                    use.
  ACC_BRIDGE: A bridge method, generated by the compiler.
  ACC_VARARGS: Declared with variable number of arguments.
  ACC_NATIVE: Declared native; implemented in a language other than Java.
  ACC_ABSTRACT: Declared abstract; no implementation is provided.
  ACC_STRICT: Declared strictfp; floating-point mode is FP-strict.
  ACC_SYNTHETIC: Declared synthetic; not present in the source code.
  """

  ACC_PUBLIC       = 0x0001
  ACC_PRIVATE      = 0x0002
  ACC_PROTECTED    = 0x0004
  ACC_STATIC       = 0x0008
  ACC_FINAL        = 0x0010
  ACC_SYNCHRONIZED = 0x0020
  ACC_BRIDGE       = 0x0040
  ACC_VARARGS      = 0x0080
  ACC_NATIVE       = 0x0100
  ACC_ABSTRACT     = 0x0400
  ACC_STRICT       = 0x0800
  ACC_SYNTHETIC    = 0x1000

  flags = _find_flags

def _bin_class (cls):
  return str(cls).replace('/', '.')

def _class_name (it):
  chars = []
  try:
    c = next(it)
    while c != ';':
      chars.append(c)
      c = next(it)
  except StopIteration:
    pass
  return _bin_class(''.join(chars))

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

class Attribute (metaclass=Parsed):
  attribute_name_index = ConstantUtf8
  attribute_length = 'u4'
  info = ('read', 'attribute_length')

  @classmethod
  def parse (class_, rdr):
    self = class_._parse(rdr)
    try:
      AttrClass = globals()['Attribute' + self.attribute_name.string]

      sub_reader = ByteReader(io.BytesIO(self.info), rdr.class_file)
      return AttrClass.parse(sub_reader)
    except:
      return self


  def __str__ (self):
    return ("<Attribute(attribute_name={}, attribute_length={}, info={})>"
            .format(self.attribute_name, self.attribute_length, self.info))

class AttributeConstantValue (metaclass=Parsed):
  constantvalue_index = ConstantUtf8

  def __str__ (self):
    return ("<AttributeConstantValue(constantvalue={})>"
            .format(self.constantvalue))


class AttributeSourceFile (metaclass=Parsed):
  sourcefile_index = ConstantUtf8

  def __str__ (self):
    return ("<AttributeSourceFile(sourcefile={})>"
            .format(self.sourcefile))

class ExceptionHandler (metaclass=Parsed):
  start_pc = 'u2'
  end_pc = 'u2'
  handler_pc = 'u2'
  catch_type = 'u2'

class AttributeCode (metaclass=Parsed):
  max_stack = 'u2'
  max_locals = 'u2'
  code_length = 'u4'
  code = ('read', 'code_length')
  exception_table_length = 'u2'
  exception_table = ('many', 'exception_table_length', ExceptionHandler)
  attributes_count = 'u2'
  attributes = ('many', 'attributes_count', Attribute)

class AttributeSignature (metaclass=Parsed):
  signature_index = ConstantUtf8

  def __str__ (self):
    return ("<AttributeSignature(signature={})>"
            .format(self.signature))

class Field (metaclass=Parsed):
  access_flags = ('u2', FieldAccessFlags.flags)
  name_index = ConstantUtf8
  _descriptor_index = ConstantUtf8
  attributes_count = 'u2'
  attributes = ('many', 'attributes_count', Attribute)

  @property
  def descriptor (self):
    return Descriptor.parse(self._descriptor)

  def __str__ (self):
    return ("<Field(access_flags={}, name={}, descriptor={}, "
            "attributes_count={}, attributes={})>".format(
              self.access_flags, self.name, self.descriptor,
              self.attributes_count,
              '[{}]'.format(', '.join(str(a) for a in self.attributes))))

class Method (metaclass=Parsed):
  access_flags = ('u2', MethodAccessFlags.flags)
  name_index = ConstantUtf8
  _descriptor_index = ConstantUtf8
  attributes_count = 'u2'
  attributes = ('many', 'attributes_count', Attribute)

  @property
  def descriptor (self):
    return Descriptor.parse(self._descriptor)

  def __str__ (self):
    return ("<Method(access_flags={}, name={}, descriptor={}, "
            "attributes_count={}, attributes={})>".format(
              self.access_flags, self.name, self.descriptor,
              self.attributes_count,
              '[{}]'.format(', '.join(str(a) for a in self.attributes))))


class Opcode:
  code = 0


if __name__ == '__main__':
  import sys
  classfile = ClassFile.from_file(sys.argv[1])
