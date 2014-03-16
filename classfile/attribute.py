from classfile import *
from classfile.flags import *
from classfile.frames import *

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


class ExceptionHandler (metaclass=Parsed):
  start_pc = 'u2'
  end_pc = 'u2'
  handler_pc = 'u2'
  catch_type = ConstantClass

class AttributeCode (metaclass=Parsed):
  max_stack = 'u2'
  max_locals = 'u2'
  code_length = 'u4'
  code = ('read', 'code_length')
  exception_table_length = 'u2'
  exception_table = ('many', 'exception_table_length', ExceptionHandler)
  attributes_count = 'u2'
  attributes = ('many', 'attributes_count', Attribute)

class AttributeStackMapTable (metaclass=Parsed):
  number_of_entries = 'u2'
  entries = ('many', 'number_of_entries', StackMapFrame)

class AttributeExceptions (metaclass=Parsed):
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

class InnerClass (metaclass=Parsed):
  inner_class_info_index = ConstantClass
  outer_class_info_index = ConstantClass
  inner_name_index = ConstantUtf8
  inner_class_access_flags = ('u2', ClassAccessFlags.flags)

class AttributeInnerClasses (metaclass=Parsed):
  number_of_classes = 'u2'
  classes = ('many', 'number_of_classes', InnerClass)


class AttributeEnclosingMethod (metaclass=Parsed):
  class_index = ConstantClass
  method_index = ConstantNameAndType

class AttributeSynthetic (metaclass=Parsed):
  pass

class AttributeSignature (metaclass=Parsed):
  signature_index = ConstantUtf8

  def __str__ (self):
    return ("<AttributeSignature(signature={})>"
            .format(self.signature))

class AttributeSourceFile (metaclass=Parsed):
  sourcefile_index = ConstantUtf8

  def __str__ (self):
    return ("<AttributeSourceFile(sourcefile={})>"
            .format(self.sourcefile))

class AttributeSourceDebugExtension (metaclass=Parsed):
  debug_extension = ('read', None)

class LineNumberEntry (metaclass=Parsed):
  start_pc = 'u2'
  line_number = 'u2'

class AttributeLineNumberTable (metaclass=Parsed):
  line_number_table_length = 'u2'
  line_number_table = ('many', 'line_number_table_length', LineNumberEntry)

class LocalVariableEntry (metaclass=Parsed):
  start_pc = 'u2'
  length = 'u2'
  name_index = ConstantUtf8
  descriptor_index = ConstantUtf8
  index = 'u2'

class AttributeLocalVariableTable (metaclass=Parsed):
  local_variable_table_length = 'u2'
  local_variable_table = ('many', 'local_variable_table_length',
                          LocalVariableEntry)

class LocalVariableTypeEntry (metaclass=Parsed):
  start_pc = 'u2'
  length = 'u2'
  name_index = ConstantUtf8
  signature_index = ConstantUtf8
  index = 'u2'

class AttributeLocalVariableTypeTable (metaclass=Parsed):
  local_variable_type_table_length = 'u2'
  local_variable_type_table = ('many', 'local_variable_type_table_length',
                               LocalVariableTypeEntry)

class AttributeDeprecated (metaclass=Parsed):
  pass

class ElementValue (metaclass=Parsed):
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

class ElementValuePair (metaclass=Parsed):
  element_name_index = ConstantUtf8
  value = ElementValue

class Annotation (metaclass=Parsed):
  type_index = ConstantUtf8
  num_element_value_pairs = 'u2'
  element_value_pairs = ('many', 'num_element_value_pairs', ElementValuePair)

class ElementValueAnnotation (ElementValue):
  annotation = Annotation

class Annotations (metaclass=Parsed):
  num_annotations = 'u2'
  annotations = ('many', 'num_annotations', Annotation)

class AttributeRuntimeVisibleAnnotations (Annotations):
  pass

class AttributeRuntimeInvisibleAnnotations (Annotations):
  pass

class ParameterAnnotations (metaclass=Parsed):
  num_parameters = 'u1'
  parameter_annotations = ('many', 'num_parameters', Annotations)

class AttributeRuntimeVisibleParameterAnnotations (ParameterAnnotations):
  pass

class AttributeRuntimeInvisibleParameterAnnotations (ParameterAnnotations):
  pass

class AttributeAnnotationDefault (metaclass=Parsed):
  default_value = ElementValue

class BootstrapMethods (metaclass=Parsed):
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

class AttributesBootstrapMethods (metaclass=Parsed):
  num_bootstrap_methods = 'u2'

