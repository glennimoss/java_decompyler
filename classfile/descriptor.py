def bin_class (cls):
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
  return bin_class(''.join(chars))

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

  #return "{} ({})".format(return_type, ', '.join(args))
  args.insert(0, return_type)
  return args

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
    #if isinstance(desc, ConstantUtf8):
      #desc = str(desc)
    it = iter(desc)

    t = Descriptor._char_map[next(it)]
    if callable(t):
      t = t(it)

    return t

