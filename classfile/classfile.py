from classfile.attribute import Attributes
from classfile.bytereader import ByteReader
from classfile.constant import *
from classfile.descriptor import HasDescriptor
from classfile.flags import *
from formatter import Document


class Field (Parsed, HasDescriptor):
  access_flags = ('u2', FieldAccessFlags.flags)
  name_index = ConstantUtf8
  _descriptor_index = ConstantUtf8
  attributes = Attributes

  def describe (self):
    doc = Document()
    doc.append('Field name: {}'.format(self.name))
    body = doc.indent()
    body.append("Access flags: {}".format(self.access_flags))
    body.append("Descriptor: {}".format(self.descriptor))
    body.append(self.attributes.describe())
    return doc

class Method (Parsed, HasDescriptor):
  access_flags = ('u2', MethodAccessFlags.flags)
  name_index = ConstantUtf8
  _descriptor_index = ConstantUtf8
  attributes = Attributes

  def describe (self):
    doc = Document()
    doc.append('Method name: {}'.format(self.name))
    body = doc.indent()
    body.append("Access flags: {}".format(self.access_flags))
    body.append("Descriptor: {}".format(self.descriptor))
    body.append(self.attributes.describe())
    return doc


class ClassFile (Parsed):
  """ Represents a class file.

  A class file can be parsed from its bytes and this object is created.
  """

  magic = ('expect', bytes.fromhex('CAFEBABE'))

  minor_version = 'u2'
  major_version = 'u2'
  constant_pool = ConstantPool
  access_flags = ('u2', ClassAccessFlags.flags)
  _this_class_index = ConstantClass
  _super_class_index = ConstantClass

  interfaces_count = 'u2'
  interfaces = ('many', 'interfaces_count', 'pool_ref', ConstantClass)

  fields_count = 'u2'
  fields = ('many', 'fields_count', Field)

  methods_count = 'u2'
  methods = ('many', 'methods_count', Method)

  attributes = Attributes

  @classmethod
  def parse (cls, rdr):
    self = cls._parse(rdr)

    self.this_class = self._this_class.descriptor
    self.super_class = self._super_class.descriptor

    return self

  @property
  def file_name (self):
    if hasattr(self, '_file_name'):
      return self._file_name

    return "Unknown"

  @classmethod
  def from_file (class_, file):
    with open(file, 'rb') as f:
      cf = class_.from_bytes(f)
    cf._file_name = file
    return cf

  @classmethod
  def from_bytes (class_, data):
    rdr = ByteReader(data)
    return ClassFile.parse(rdr)


  def describe (self):
    doc = Document()
    doc.append('File: {}'.format(self.file_name))
    doc.append('Version: {}.{}'.format(self.major_version, self.minor_version))
    doc.append('Constants: {}'.format(len(self.constant_pool)))
    cpool = doc.indent()
    for i, const in enumerate(self.constant_pool):
      cpool.append('#{}: {!r}'.format(i, const))
    doc.append("Access flags: {}".format(self.access_flags))
    doc.append("This Class: {}".format(self.this_class))
    doc.append("Super Class: {}".format(self.super_class))
    doc.append("Interfaces: {}".format(self.interfaces_count))
    ifaces = doc.indent()
    for iface in self.interfaces:
      ifaces.append(iface)
    doc.append("Fields: {}".format(self.fields_count))
    fields = doc.indent()
    for field in self.fields:
      fields.append(field.describe())
    doc.append("Methods: {}".format(self.methods_count))
    methods = doc.indent()
    for method in self.methods:
      methods.append(method.describe())
    doc.append(self.attributes.describe())
    return doc

  def __str__ (self):
    return '\n'.join(self.describe())
