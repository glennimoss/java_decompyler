def _class_name (it):
  chars = []
  try:
    c = next(it)
    while c != ';':
      if c == '/':
        chars.append('.')
      else:
        chars.append(c)
      c = next(it)
  except StopIteration:
    pass
  return ClassDescriptor(''.join(chars))

def _array (it):
  return ArrayDescriptor(parse_descriptor(it))

def _args (it):
  args = []

  try:
    while True:
      args.append(parse_descriptor(it))
  except StopIteration:
    pass

  return_type = parse_descriptor(it)

  return SignatureDescriptor(return_type, args)

def _end_args (it):
  raise StopIteration()

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
def parse_descriptor (desc):
  it = iter(desc)

  t = _char_map[next(it)]
  if callable(t):
    t = t(it)
  else:
    t = SimpleTypeDescriptor(t)

  return t

class TypeDescriptor:
  pass

class SimpleTypeDescriptor (TypeDescriptor, str):
  def __repr__ (self):
    return "<{}: {} >".format(self.__class__.__name__, self)


class ArrayDescriptor (SimpleTypeDescriptor):
  def __new__ (class_, element_type):
    if not isinstance(element_type, TypeDescriptor):
      element_type = SimpleTypeDescriptor(element_type)
    self = super().__new__(class_, '{}[]'.format(element_type))
    self.element_type = element_type
    return self

class ClassDescriptor (SimpleTypeDescriptor):
  def __init__ (self, _):
    try:
      self.package = self.rsplit('.', 1)[-2]
    except IndexError:
      self.package = None
    self.class_name = self.rsplit('.', 1)[-1]

class ArgumentsDescriptor (TypeDescriptor, list):
  pass

class SignatureDescriptor (TypeDescriptor):
  def __init__ (self, return_type, arg_types):
    if not isinstance(arg_types, ArgumentsDescriptor):
      arg_types = ArgumentsDescriptor(arg_types)
    self.return_type = return_type
    self.arg_types = arg_types

  def __str__ (self):
    return "{} ({})".format(self.return_type, self.arg_types)

class HasDescriptor:
  @property
  def descriptor (self):
    if not hasattr(self, '_parsed_descriptor'):
      self._parsed_descriptor = parse_descriptor(self._descriptor)
    return self._parsed_descriptor
