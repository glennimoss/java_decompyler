from collections import OrderedDict
from collections.abc import Sequence
from classfile.bytereader import ByteReader

def _ref_resolver (name, ref_type):
  def resolve_ref (self):
    idx = getattr(self, name)
    return self.constant_pool.resolve(idx, ref_type)
  return resolve_ref

def is_Constant (val):
  return isinstance(val, type) and issubclass(val, Constant)

class MetaParsed (type):
  def __prepare__ (name, bases, **kwargs):
    return OrderedDict()

  def __new__ (meta, class_name, bases, dct, uses_constant_pool=False):
    to_parse = []
    parsed_names = []

    for name, val in list(dct.items()):
      if isinstance(val, property):
        parsed_names.append(name)
        continue
      parse_method = None
      parsed_name = name
      if isinstance(val, Sequence):
        if isinstance(val, str):
          val = (val,)
        if isinstance(val, tuple) and not hasattr(ByteReader, val[0]):
          continue
        parse_method = val
        if len(val) == 2 and is_Constant(val[1]):
          parse_method = (val[0],)
          val = val[1]

      if is_Constant(val):
        if name.endswith('_index'):
          parsed_name = name[0:-6]
        else:
          parsed_name = name
          name = '_' + name
        dct[parsed_name] = property(_ref_resolver(name, val))
        uses_constant_pool = True
        if parse_method is None:
          parse_method = ('u2',)
      elif isinstance(val, MetaParsed):
        parse_method = ('parse', val)

      if parse_method is None:
        continue

      parsed_names.append(parsed_name)
      to_parse.append((name, parse_method))

    if '_parsed_names' not in dct:
      dct['_parsed_names'] = tuple(parsed_names)
    if 'parsed_names' not in dct:
      def parsed_names (cls):
        return super(myclass, cls).parsed_names() + myclass._parsed_names
      dct['parsed_names'] = classmethod(parsed_names)

    def _parse_self (self, rdr):
      for name, (parse_method, *args) in to_parse:
        args = [getattr(self, arg)
                if isinstance(arg, str) and hasattr(self, arg) else arg
                for arg in args]
        if rdr._debug:
          print("{}: {} = rdr.{}(*{}): ".format(myclass.__name__, name, parse_method, args), end='')
        val = getattr(rdr, parse_method)(*args)
        setattr(self, name, val)
    dct['_parse_self'] = _parse_self

    # TODO: this is silly
    parse_name = 'parse'
    if parse_name in dct:
      parse_name = '_parse'
    if parse_name in dct:
      parse_name += '2'
    debug_this = 'debug_parse' in dct and dct['debug_parse']
    def parse (class_, rdr, **kwargs):
      """ MetaParsed {} """
      if uses_constant_pool:
        kwargs['constant_pool'] = rdr.constant_pool
      if debug_this:
        import pdb;pdb.set_trace()
      self = super(myclass, class_).parse(rdr, **kwargs)
      myclass._parse_self(self, rdr)
      return self
    parse.__doc__ = parse.__doc__.format(class_name)
    dct[parse_name] = classmethod(parse)

    myclass = super().__new__(meta, class_name, bases, dct)
    return myclass


class Parsed (metaclass=MetaParsed):
  """ Base class eats super() chains. """
  def __init__ (self, rdr, constant_pool=None, **kwargs):
    self.constant_pool = constant_pool

  @classmethod
  def parsed_names (cls):
    return tuple()

  @classmethod
  def parse (class_, rdr, **kwargs):
    """ Parse """
    return class_(rdr, **kwargs)

  def __repr__ (self):
    return "<{}({})>".format(type(self).__name__,
                             ", ".join("{}={!r}".format(name, getattr(self, name))
                                       for name in self.parsed_names()))



class MetaTaggedParsed (MetaParsed):
  def __new__ (meta, class_name, bases, dct, **kwargs):
    # Only for top-level classes
    if not any(isinstance(base, MetaTaggedParsed) for base in bases):
      if '_class_map' not in dct:
        dct['_class_map'] = {}

      if '_read_tag' not in dct:
        def _read_tag (cls, rdr):
          return rdr.u1()
        dct['_read_tag'] = classmethod(_read_tag)

      parse_name = 'parse'
      delegate_parse = '_parse'
      if parse_name in dct:
        parse_name = '_parse'
        delegate_parse = '_parse2'
      def parse (class_, rdr, **kwargs):
        """ MetaTaggedParsed {} """
        if class_ is TopClass:
          if rdr._debug:
            print("{}._read_tag: ".format(class_.__name__), end='')
          tag = class_._read_tag(rdr)
          if rdr._debug:
            print("{}._read_tag() = {}".format(class_.__name__, tag))
          if isinstance(tag, tuple):
            tag, new_args = tag
            kwargs.update(new_args)
          try:
            SubClass = TopClass._class_map[tag]
            return SubClass.parse(rdr, **kwargs)
          except KeyError:
            raise ValueError("No subclass of {} tagged with {}".format(TopClass, tag))
        return getattr(TopClass, delegate_parse).__func__(class_, rdr, **kwargs)
      parse.__doc__ = parse.__doc__.format(class_name)
      dct[parse_name] = classmethod(parse)

    TopClass = super().__new__(meta, class_name, bases, dct, **kwargs)
    return TopClass

  def __init__ (cls, class_name, bases, dct, **kwargs):
    for base in bases:
      if hasattr(base, '_class_map'):
        if 'tag' in dct:
          base._class_map[dct['tag']] = cls
        else:
          if class_name.startswith(base.__name__):
            class_name = class_name[len(base.__name__):]
          if hasattr(base, 'tag') and hasattr(base.tag, class_name):
            base._class_map[getattr(base.tag, class_name)] = cls
          else:
            base._class_map[class_name] = cls
        break

class Constant (Parsed, metaclass=MetaTaggedParsed):
  def __repr__ (self):
    return "<{}: {} >".format(type(self).__name__, self)


__all__ = ['Parsed', 'MetaTaggedParsed']
