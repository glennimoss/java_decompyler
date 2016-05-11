def _debug_log (start, n, b, end=None):
  print("read@0x{:04x}({}):".format(start, n), *("0x{:02x}".format(i) for i in b), end=end)

def parse_int(n, signed=False):
  def N (self, callback=None):
    """ Read and parse a {}-byte {} integer. """
    start = self.offset
    b = self.data.read(n)
    i = int.from_bytes(b, 'big', signed=signed)
    if self._debug:
      _debug_log(start, n, b, end='')
      print(' ->', i)

    if i == 1572910:
      import pdb;pdb.set_trace()
    if callback:
      return callback(i)
    return i
  N.__name__ = '{}{}'.format('ui'[signed], n)
  N.__qualname__ = 'ByteReader.' + N.__name__
  N.__doc__ = N.__doc__.format(n, ['unsigned', 'signed'][signed])
  return N

class ByteReader:
  _debug = False

  def __init__ (self, data, constant_pool=None):
    self.data = data
    self.constant_pool = constant_pool
    self._align_from = 0

  u1 = parse_int(1)
  u2 = parse_int(2)
  #u3 = parse_int(3)
  u4 = parse_int(4)
  #u8 = parse_int(8)

  i1 = parse_int(1, signed=True)
  i2 = parse_int(2, signed=True)
  i4 = parse_int(4, signed=True)

  @property
  def length (self):
    if not hasattr(self, '_length'):
      orig_pos = self.data.tell()
      self._length = self.data.seek(0, 2)
      self.data.seek(orig_pos)
    return self._length

  @property
  def offset (self):
    return self.data.tell()

  def start_align (self):
    self._align_from = self.offset

  @property
  def aligned_offset (self):
    return self.offset - self._align_from

  def read (self, n, callback=None):
    """ Read n bytes returned as a bytes object, or optionally through a callback.

    If callback is not None, then the bytes object is passed to the callback
    and returns that result.
    """
    start = self.offset
    b = self.data.read(n)
    if self._debug:
      _debug_log(start, n, b)
    if callback:
      return callback(b)
    return b

  def expect (self, expected_bytes):
    found_bytes = self.read(len(expected_bytes))
    if found_bytes != expected_bytes:
      raise ValueError("Expected to read {!r} but found {!r}".format(expected_bytes,
                                                                     found_bytes))
    return found_bytes

  def pool_ref (self, ref_type):
    idx = self.u2()
    return self.constant_pool.resolve(idx, ref_type)

  def many (self, how_many, ParseClass, *args):
    """ Repeatedly parse ParseClass items how_many times.

    Any additional arguments are passed to the ParseClass method.
    """
    if self._debug and not how_many:
      print('[]')
    items = []
    for i in range(how_many):
      if self._debug:
        print("many #{}: ".format(i), end='')
      items.append(self.parse(ParseClass, *args))
    return items

  def parse (self, ParseClass, *args):
    """ Parse a ParseClass item.

    If ParseClass is a string that is the name of a method on this class, then
    that method is called to parse. Otherwise, ParseClass.parse is called.

    Any additional arguments are passed to the parsing call.
    """
    if isinstance(ParseClass, str) and hasattr(self, ParseClass):
      return getattr(self, ParseClass)(*args)
    return ParseClass.parse(self, *args)

  def align (self, multiple):
    if self._debug:
      print("align({}): ".format(multiple), end='')
    offset = self.aligned_offset
    aligned_offset = (offset + (multiple-1))//multiple * multiple
    return self.read(aligned_offset - offset)
