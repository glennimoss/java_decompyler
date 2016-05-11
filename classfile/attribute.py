from classfile import *
from classfile.bytecode import ByteCode
from classfile.descriptor import HasDescriptor
from classfile.flags import *
from classfile.frames import *
from classfile.bytereader import ByteReader
from enum import Enum
import io
from collections import defaultdict
from formatter import Document

import logging

class Attribute (Parsed, metaclass=MetaTaggedParsed):
  _class_map = defaultdict(lambda: AttributeStub)
  attribute_length = 'u4'

  @classmethod
  def _read_tag (cls, rdr):
    return rdr.pool_ref(ConstantUtf8).string

  def describe (self):
    return repr(self)

class Attributes (Parsed):
  attributes_count = 'u2'

  def __init__ (self, rdr):
    super().__init__(rdr)

    self.attributes = []
    self._attr_map = {}

  @classmethod
  def parse (cls, rdr):
    self = cls._parse(rdr)

    for _ in range(self.attributes_count):
      begin = rdr.offset
      attr = Attribute.parse(rdr)
      end = rdr.offset
      parsed = end - begin - 6; # pool_ref (2) + attribute_lenth (4) = 6

      if parsed != attr.attribute_length:
        raise ValueError("Attribute {!r} expected to parse {} bytes, but parsed {}"
                         .format(attr, attr.attribute_length, parsed))

      self.attributes.append(attr)
      self._attr_map[type(attr).__name__[9:]] = attr

    return self

  def describe (self):
    doc = Document()
    doc.append("Attributes: {}".format(len(self)))
    body = doc.indent()
    for attr in self:
      body.append(attr.describe())
    return doc

  def __getitem__ (self, key):
    print("Attribute.__getitem__(key={})".format(key))
    return self._attr_map[key]

  def __len__ (self):
    return len(self.attributes)

  def __iter__ (self):
    return iter(self.attributes)

  def __contains__ (self, item):
    return item in self._attr_map or item in self.attributes

  def __getattr__ (self, name):
    if name in self._attr_map:
      return self._attr_map[name]
    if name in self.attributes:
      return self.attributes[name]
    raise AttributeError("No attribute named '{}'".format(name))


class AttributeStub (Attribute):
  """ Reads all the attribute data if we don't know what else to do with it. """
  info = ('read', 'attribute_length')


class AttributeConstantValue (Attribute):
  constantvalue_index = Constant

  def __str__ (self):
    return str(self.constantvalue)


class ExceptionHandler (Parsed):
  start_pc = 'u2'
  end_pc = 'u2'
  handler_pc = 'u2'
  catch_type = ConstantClass

class AttributeCode (Attribute):
  max_stack = 'u2'
  max_locals = 'u2'
  byte_code = ByteCode
  exception_table_length = 'u2'
  exception_table = ('many', 'exception_table_length', ExceptionHandler)
  attributes = Attributes

  def describe (self):
    doc = Document()
    doc.append("AttributeCode:")
    body = doc.indent()
    body.append("Max stack: {}".format(self.max_stack))
    body.append("Max locals: {}".format(self.max_locals))
    body.append("Byte code:")
    bytecode = body.indent()
    bytecode.extend(self.byte_code.formatted())
    body.append("Exception table: {}".format(len(self.exception_table)))
    extab = body.indent()
    for exhand in self.exception_table:
      extab.append(repr(exhand))
    body.append(self.attributes.describe())
    return doc



class AttributeStackMapTable (Attribute):
  number_of_entries = 'u2'
  entries = ('many', 'number_of_entries', StackMapFrame)

  def describe (self):
    doc = Document()
    doc.append("AttributeStackMapTable: {} frames".format(len(self.entries)))
    body = doc.indent()
    for entry in self.entries:
      body.append(repr(entry))
    return doc


class AttributeExceptions (Attribute, uses_constant_pool=True):
  number_of_exceptions = 'u2'
  exception_index_table = ('many', 'number_of_exceptions', 'u2')

  _exception_table = None

  @property
  def exception_table (self):
    if not self._exception_table:
      self._exception_table = []
      for exception_index in self.exception_index_table:
        const = self.constant_pool[exception_index]
        assert isinstance(const, ConstantClass), (
          "Exception table entries must be ConstantClass")
        self._exception_table.append(const)

    return self._exception_table

class InnerClass (Parsed):
  inner_class_info_index = ConstantClass
  outer_class_info_index = ConstantClass
  inner_name_index = ConstantUtf8
  inner_class_access_flags = ('u2', ClassAccessFlags.flags)

class AttributeInnerClasses (Attribute):
  number_of_classes = 'u2'
  classes = ('many', 'number_of_classes', InnerClass)


class AttributeEnclosingMethod (Attribute):
  class_index = ConstantClass
  method_index = ConstantNameAndType

class AttributeSynthetic (Attribute):
  # 0-length attribute
  pass

class AttributeSignature (Attribute):
  signature_index = ConstantUtf8

  def __repr__ (self):
    return ("<AttributeSignature(signature={})>"
            .format(self.signature))

class AttributeSourceFile (Attribute):
  sourcefile_index = ConstantUtf8

  def __repr__ (self):
    return ("<AttributeSourceFile(sourcefile={})>"
            .format(self.sourcefile))

class AttributeSourceDebugExtension (Attribute):
  debug_extension = ('read', None)

class LineNumberEntry (Parsed):
  start_pc = 'u2'
  line_number = 'u2'

class AttributeLineNumberTable (Attribute):
  line_number_table_length = 'u2'
  line_number_table = ('many', 'line_number_table_length', LineNumberEntry)

  def describe (self):
    doc = Document()
    doc.append('AttributeLineNumberTable')
    body = doc.indent()
    body.extend(self.line_number_table)
    return doc

class LocalVariableEntry (Parsed, HasDescriptor):
  start_pc = 'u2'
  length = 'u2'
  name_index = ConstantUtf8
  _descriptor_index = ConstantUtf8
  index = 'u2'

class AttributeLocalVariableTable (Attribute):
  local_variable_table_length = 'u2'
  local_variable_table = ('many', 'local_variable_table_length',
                          LocalVariableEntry)

class LocalVariableTypeEntry (Parsed):
  start_pc = 'u2'
  length = 'u2'
  name_index = ConstantUtf8
  signature_index = ConstantUtf8
  index = 'u2'

class AttributeLocalVariableTypeTable (Attribute):
  local_variable_type_table_length = 'u2'
  local_variable_type_table = ('many', 'local_variable_type_table_length',
                               LocalVariableTypeEntry)

class AttributeDeprecated (Attribute):
  # 0-length attribute
  pass

class ElementValue (Parsed):
  tag = 'u1'

  @classmethod
  def parse (class_, rdr):
    self = class_._parse(rdr)

    if tag in b"BCDFIJSZs":
      ...
    elif tag in b"e":
      ...
    elif tag in b"c":
      ...
    elif tag in b"@":
      ...
    elif tag == 91: # b'[' vim is dumb
      ...
    else:
      raise ValueError("Unknown ElementValue tag: {}".format(tag))

    return self

class ElementValueConst (ElementValue):
  const_value_index = Constant

class ElementValueEnumConst (ElementValue):
  type_name_index = ConstantUtf8
  const_name_index = ConstantUtf8

class ElementValueClass (ElementValue):
  class_info_index = ConstantUtf8

class ElementValueArray (ElementValue):
  num_values = 'u2'
  values = ('many', 'num_values', ElementValue)

class ElementValuePair (Parsed):
  element_name_index = ConstantUtf8
  value = ElementValue

class Annotation (Parsed):
  type_index = ConstantUtf8
  num_element_value_pairs = 'u2'
  element_value_pairs = ('many', 'num_element_value_pairs', ElementValuePair)

class ElementValueAnnotation (ElementValue):
  annotation = Annotation

class Annotations (Parsed):
  num_annotations = 'u2'
  annotations = ('many', 'num_annotations', Annotation)

class AttributeRuntimeVisibleAnnotations (Annotations):
  pass

class AttributeRuntimeInvisibleAnnotations (Annotations):
  pass

class ParameterAnnotations (Parsed):
  num_parameters = 'u1'
  parameter_annotations = ('many', 'num_parameters', Annotations)

class AttributeRuntimeVisibleParameterAnnotations (ParameterAnnotations):
  pass

class AttributeRuntimeInvisibleParameterAnnotations (ParameterAnnotations):
  pass

class AttributeAnnotationDefault (Attribute):
  default_value = ElementValue

class BootstrapMethods (Parsed):
  bootstrap_method_ref_index = ConstantMethodHandle
  num_bootstrap_arguments = 'u2'
  bootstrap_argument_indexes = ...

  _bootstrap_arguments = None

  @property
  def bootstrap_arguments (self):
    if not self._bootstrap_arguments:
      self._bootstrap_arguments = [self.constant_pool[idx]
                                   for idx in self.bootstrap_argument_indexes]
    return self._bootstrap_arguments

class AttributesBootstrapMethods (Attribute):
  num_bootstrap_methods = 'u2'
