"""Load and parse classfiles.

  >>> java_class = ClassFile.from_file('filename')
Where f is a file-like object:
  >>> java_class = ClassFile.from_bytes(f)
"""

from collections import OrderedDict
import struct
import io

def unsigned (n):
  def uN (self, callback=None):
    b = self.data.read(n)
    #print("u{}:".format(n), *(hex(i) for i in b))
    #print("u{}:".format(n), b)
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

  def read (self, bytes, callback=None):
    b = self.data.read(bytes)
    #print("read({}):".format(bytes), *(hex(i) for i in b))
    #print("read({}):".format(bytes), b)
    if callback:
      return callback(b)
    return b

  def many (self, how_many, ParseClass, *args):
    items = []
    for i in range(how_many):
      items.append(self.parse(ParseClass, *args))
    return items

  def parse (self, ParseClass, *args):
    if isinstance(ParseClass, str) and hasattr(self, ParseClass):
      return getattr(self, ParseClass)(*args)
    return ParseClass.parse(self, *args)


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
    #print('minor_version:', self.minor_version)
    self.major_version = rdr.u2()
    #print('major_version:', self.major_version)
    self.constant_pool_count = rdr.u2()
    #print('constant_pool_count:', self.constant_pool_count)

    self.constant_pool = [None] # Constant pool starts at 1
    while len(self.constant_pool) < self.constant_pool_count:
      const = Constant(rdr)
      #print("# Constant {}:".format(len(self.constant_pool)+1), repr(const))
      self.constant_pool.append(const)
      if const.tag in (ConstantType.Long, ConstantType.Double):
        # Longs and Doubles take up two slots
        self.constant_pool.append(None)
    #for i, const in enumerate(self.constant_pool):
      #if const:
        #print('Constant {}: {}:'.format(i, const.__class__.__name__), const)

    self.access_flags = ClassAccessFlags.flags(rdr.u2())
    #print("access_flags:", self.access_flags)
    self.this_class = self.constant_pool[rdr.u2()]
    #print("this_class:", self.this_class)
    self.super_class = self.constant_pool[rdr.u2()]
    #print("super_class:", self.super_class)

    self.interfaces_count = rdr.u2()
    #print("interfaces_count:", self.interfaces_count)
    self.interfaces = []
    for i in range(self.interfaces_count):
      interface = self.constant_pool[rdr.u2()]
      assert isinstance(interface, ConstantClass), (
        "Interface must reference a ConstantClass item in the constant pool")
      self.interfaces.append(interface)
    #print("interfaces:", ", ".join(str(i) for i in self.interfaces))

    self.fields_count = rdr.u2()
    #print("fields_count:", self.fields_count)
    self.fields = []
    for i in range(self.fields_count):
      self.fields.append(Field.parse(rdr))
    #print("fields:", ", ".join(str(f) for f in self.fields))

    self.methods_count = rdr.u2()
    #print("methods_count:", self.methods_count)
    self.methods = []
    for i in range(self.methods_count):
      self.methods.append(Method.parse(rdr))
    #print("methods:", ", ".join(str(m) for m in self.methods))

    self.attributes_count = rdr.u2()
    #print("attributes_count:", self.attributes_count)
    self.attributes = []
    for i in range(self.attributes_count):
      self.attributes.append(Attribute.parse(rdr))
    #print("attributes:", ", ".join(str(a) for a in self.attributes))

    return self

def _ref_resolver (name, ref_type):
  def resolve_ref (self):
    idx = getattr(self, name)
    if idx == 0:
      # TODO: Is this the right approach?
      return None
    try:
      ref = self.constant_pool[idx]
      #assert isinstance(ref, ref_type)
      assert issubclass(ref_type, type(ref))
      return ref
    except IndexError:
      return idx
    except TypeError as e:
      import pdb;pdb.set_trace()
      print(e)
  return resolve_ref

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
      elif type(val) is Parsed:
        parse_method = ('parse', val)
      elif isinstance(val, (str, tuple, list)):
        if isinstance(val, str):
          val = (val,)
        if isinstance(val, tuple) and not hasattr(ByteReader, val[0]):
          continue
        parse_method = val
      else:
        continue

      to_parse.append((name, parse_method))

    def _parse_self (self, rdr):
      for name, (parse_method, *args) in to_parse:
        args = [getattr(self, arg)
                if isinstance(arg, str) and hasattr(self, arg) else arg
                for arg in args]
        val = getattr(rdr, parse_method)(*args)
        #print("{}:".format(name), val)
        setattr(self, name, val)
    dct['_parse_self'] = _parse_self

    def parse (class_, rdr):
      mysuper = super(myclass, class_)
      if hasattr(mysuper, 'parse'):
        self = mysuper.parse(rdr)
      else:
        self = class_(rdr)
      myclass._parse_self(self, rdr)
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

from classfile.constant import *
from classfile.flags import *
from classfile.attribute import *
from classfile.descriptor import *

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



