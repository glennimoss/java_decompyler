class Formatter:
  def __init__ (self, content):
    self._content = content

  def _format_item (self, item):
    """ Return a formatted str. """
    return str(item)

  def __iter__ (self):
    """ Yields formatted strings. """
    for item in self._content:
      v = self._format_item(item)
      yield v

  def _self_repr (self):
    return "Formatter()"

  def __repr__ (self):
    return "<{}: {!r}>".format(self._self_repr(), self._content)

  def _debug (self):
    yield '{}:'.format(self._self_repr())
    for item in self._content._debug():
      yield '  {}'.format(item)

  def debug (self):
    for line in self._debug():
      print(line)


class PrefixFormatter (Formatter):
  def __init__ (self, prefix, content):
    super().__init__(content)
    self._prefix = prefix

  def _format_item (self, item):
    return self._prefix + str(item)

  def _self_repr (self):
    return "PrefixFormatter(prefix={!r})".format(self._prefix)

class SuffixFormatter (Formatter):
  def __init__ (self, suffix, content):
    super().__init__(content)
    self._suffix = suffix

  def _format_item (self, item):
    return str(item) + self._suffix

  def _self_repr (self):
    return "SuffixFormatter(suffix={!r})".format(self._suffix)

class SectionFormatter (Formatter):

  def __iter__ (self):
    yield from super().__iter__()
    if self._content:
      yield '' # Blank line separator


class JoinFormatter (Formatter):
  def __init__ (self, sep, content):
    super().__init__(content)
    self._sep = sep

  def __iter__ (self):
    yield self._sep.join(str(item) for item in self._content)

  def _self_repr (self):
    return "JoinFormatter(sep={!r})".format(self._sep)


class Document (Formatter, list):
  def __init__ (self, indent='  '):
    super().__init__(self)
    self._indent = indent

  def section (self, blank_separator=True):
    subdoc = Document(self._indent)
    if blank_separator:
      self.append(SectionFormatter(subdoc))
    else:
      self.append(subdoc)
    return subdoc

  def join (self, *args, sep=' '):
    subdoc = Document(self._indent)
    self.append(JoinFormatter(sep, subdoc))
    subdoc.extend(args)
    return subdoc

  def line (self, *args, sep=' ', term=';'):
    subdoc = Document(self._indent)
    self.append(SuffixFormatter(term, JoinFormatter(sep, subdoc)))
    subdoc.extend(args)
    return subdoc

  def blank_line (self):
    self.append('')

  def block (self, open=' {', close='}'):
    opener = self.line(term=open)
    body = self.indent()
    self.append(close)
    return opener, body

  def indent (self):
    subdoc = Document(self._indent)
    self.append(PrefixFormatter(self._indent, subdoc))
    return subdoc

  def _self_repr (self):
    return "Document(indent={!r})".format(self._indent)


  def __iter__ (self):
    for item in list.__iter__(self):
      if isinstance(item, Formatter):
        yield from item
      else:
        yield str(item)

  def __repr__ (self):
    return "<{}: {}>".format(self._self_repr(), list.__repr__(self._content))

  def __str__ (self):
    return "\n".join(str(item).rstrip() for item in self)

  def _debug (self):
    yield '{}: ['.format(self._self_repr())
    for item in list.__iter__(self):
      if isinstance(item, Formatter):
        for subitem in item._debug():
          yield '  {}'.format(subitem)
      else:
        yield '  {!r}'.format(item)
    yield ']'
