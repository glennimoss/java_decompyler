from classfile import *
from classfile.constant import *

class ByteCode (Parsed):
  code_length = 'u4'

  @classmethod
  def parse (cls, rdr):
    self = cls._parse(rdr)

    self._byte_code = [None]*self.code_length

    rdr.start_align()
    pc = 0
    while pc < self.code_length:
      self._byte_code[pc] = Op_.parse(rdr)

      pc = rdr.aligned_offset

    return self

  def formatted (self):
    index_width = len(str(len(self._byte_code)))
    op_fmt = '{{:{}}} {{}}'.format(index_width)

    for idx, op in enumerate(self._byte_code):
      if op:
        yield op_fmt.format(idx, op)


  def __str__ (self):
    return "\n".join(self.formatted())


class Opcode (IntEnum):
  aaload = 0x32
  aastore = 0x53
  aconst_null = 0x01
  aload = 0x19
  aload_0 = 0x2a
  aload_1 = 0x2b
  aload_2 = 0x2c
  aload_3 = 0x2d
  anewarray = 0xbd
  areturn = 0xb0
  arraylength = 0xbe
  astore = 0x3a
  astore_0 = 0x4b
  astore_1 = 0x4c
  astore_2 = 0x4d
  astore_3 = 0x4e
  athrow = 0xbf
  baload = 0x33
  bastore = 0x54
  bipush = 0x10
  breakpoint = 0xca
  caload = 0x34
  castore = 0x55
  checkcast = 0xc0
  d2f = 0x90
  d2i = 0x8e
  d2l = 0x8f
  dadd = 0x63
  daload = 0x31
  dastore = 0x52
  dcmpg = 0x98
  dcmpl = 0x97
  dconst_0 = 0x0e
  dconst_1 = 0x0f
  ddiv = 0x6f
  dload = 0x18
  dload_0 = 0x26
  dload_1 = 0x27
  dload_2 = 0x28
  dload_3 = 0x29
  dmul = 0x6b
  dneg = 0x77
  drem = 0x73
  dreturn = 0xaf
  dstore = 0x39
  dstore_0 = 0x47
  dstore_1 = 0x48
  dstore_2 = 0x49
  dstore_3 = 0x4a
  dsub = 0x67
  dup = 0x59
  dup2 = 0x5c
  dup2_x1 = 0x5d
  dup2_x2 = 0x5e
  dup_x1 = 0x5a
  dup_x2 = 0x5b
  f2d = 0x8d
  f2i = 0x8b
  f2l = 0x8c
  fadd = 0x62
  faload = 0x30
  fastore = 0x51
  fcmpg = 0x96
  fcmpl = 0x95
  fconst_0 = 0x0b
  fconst_1 = 0x0c
  fconst_2 = 0x0d
  fdiv = 0x6e
  fload = 0x17
  fload_0 = 0x22
  fload_1 = 0x23
  fload_2 = 0x24
  fload_3 = 0x25
  fmul = 0x6a
  fneg = 0x76
  frem = 0x72
  freturn = 0xae
  fstore = 0x38
  fstore_0 = 0x43
  fstore_1 = 0x44
  fstore_2 = 0x45
  fstore_3 = 0x46
  fsub = 0x66
  getfield = 0xb4
  getstatic = 0xb2
  goto = 0xa7
  goto_w = 0xc8
  i2b = 0x91
  i2c = 0x92
  i2d = 0x87
  i2f = 0x86
  i2l = 0x85
  i2s = 0x93
  iadd = 0x60
  iaload = 0x2e
  iand = 0x7e
  iastore = 0x4f
  iconst_0 = 0x03
  iconst_1 = 0x04
  iconst_2 = 0x05
  iconst_3 = 0x06
  iconst_4 = 0x07
  iconst_5 = 0x08
  iconst_m1 = 0x02
  idiv = 0x6c
  if_acmpeq = 0xa5
  if_acmpne = 0xa6
  if_icmpeq = 0x9f
  if_icmpge = 0xa2
  if_icmpgt = 0xa3
  if_icmple = 0xa4
  if_icmplt = 0xa1
  if_icmpne = 0xa0
  ifeq = 0x99
  ifge = 0x9c
  ifgt = 0x9d
  ifle = 0x9e
  iflt = 0x9b
  ifne = 0x9a
  ifnonnull = 0xc7
  ifnull = 0xc6
  iinc = 0x84
  iload = 0x15
  iload_0 = 0x1a
  iload_1 = 0x1b
  iload_2 = 0x1c
  iload_3 = 0x1d
  impdep1 = 0xfe
  impdep2 = 0xff
  imul = 0x68
  ineg = 0x74
  instanceof = 0xc1
  invokedynamic = 0xba  # Note: this was introduced in Java 7
  invokeinterface = 0xb9
  invokespecial = 0xb7
  invokestatic = 0xb8
  invokevirtual = 0xb6
  ior = 0x80
  irem = 0x70
  ireturn = 0xac
  ishl = 0x78
  ishr = 0x7a
  istore = 0x36
  istore_0 = 0x3b
  istore_1 = 0x3c
  istore_2 = 0x3d
  istore_3 = 0x3e
  isub = 0x64
  iushr = 0x7c
  ixor = 0x82
  jsr = 0xa8
  jsr_w = 0xc9
  l2d = 0x8a
  l2f = 0x89
  l2i = 0x88
  ladd = 0x61
  laload = 0x2f
  land = 0x7f
  lastore = 0x50
  lcmp = 0x94
  lconst_0 = 0x09
  lconst_1 = 0x0a
  ldc = 0x12
  ldc2_w = 0x14
  ldc_w = 0x13
  ldiv = 0x6d
  lload = 0x16
  lload_0 = 0x1e
  lload_1 = 0x1f
  lload_2 = 0x20
  lload_3 = 0x21
  lmul = 0x69
  lneg = 0x75
  lookupswitch = 0xab
  lor = 0x81
  lrem = 0x71
  lreturn = 0xad
  lshl = 0x79
  lshr = 0x7b
  lstore = 0x37
  lstore_0 = 0x3f
  lstore_1 = 0x40
  lstore_2 = 0x41
  lstore_3 = 0x42
  lsub = 0x65
  lushr = 0x7d
  lxor = 0x83
  monitorenter = 0xc2
  monitorexit = 0xc3
  multianewarray = 0xc5
  new = 0xbb
  newarray = 0xbc
  nop = 0x00
  pop = 0x57
  pop2 = 0x58
  putfield = 0xb5
  putstatic = 0xb3
  ret = 0xa9
  locals()['return'] = 0xb1
  saload = 0x35
  sastore = 0x56
  sipush = 0x11
  swap = 0x5f
  tableswitch = 0xaa
  #wide = 0xc4
  wide_aload = 0xc419
  wide_astore = 0xc43a
  wide_dload = 0xc418
  wide_dstore = 0xc439
  wide_fload = 0xc417
  wide_fstore = 0xc438
  wide_iinc = 0xc484
  wide_iload = 0xc415
  wide_istore = 0xc436
  wide_lload = 0xc416
  wide_lstore = 0xc437
  wide_ret = 0xc4a9

class PrimitiveArrayType (IntEnum):
  T_BOOLEAN = 4
  T_CHAR = 5
  T_FLOAT = 6
  T_DOUBLE = 7
  T_BYTE = 8
  T_SHORT = 9
  T_INT = 10
  T_LONG = 11

  def __str__ (self):
    return self.name


_WIDE_OP = 0xc4
class Op_ (Parsed, metaclass=MetaTaggedParsed):
  tag = Opcode

  @classmethod
  def _read_tag (cls, rdr):
    opcode = rdr.u1()
    if opcode == _WIDE_OP:
      return opcode << 8 + rdr.u1()
    return opcode

  @classmethod
  def parse (cls, rdr, **kwargs):
    offset = rdr.aligned_offset
    self = cls._parse(rdr, **kwargs)
    self._offset = offset

    return self

  def __str__ (self):
    parts = [self.__class__.__name__[3:]]
    for name in self.parsed_names():
      val = getattr(self, name)
      if name.endswith('_offset'):
        # Make jump offsets print absolute indexes.
        val += self._offset
      parts.append(str(val))
    return " ".join(parts)

class Op_aload (Op_):
  local_var_index = 'u1'

class Op_anewarray (Op_):

  type_index = Constant

class Op_astore (Op_):

  local_var_index = 'u1'

class Op_bipush (Op_):
  value = 'i1'

class Op_checkcast (Op_):
  type_index = Constant

class Op_dload (Op_):
  local_var_index = 'u1'

class Op_dstore (Op_):
  local_var_index = 'u1'

class Op_fload (Op_):
  local_var_index = 'u1'

class Op_fstore (Op_):
  local_var_index = 'u1'

class Op_getfield (Op_):
  field_ref_index = ConstantFieldref
class Op_getstatic (Op_):
  field_ref_index = ConstantFieldref
class Op_goto (Op_):
  branch_offset = 'i2'
class Op_goto_w (Op_):
  branch_offset = 'i4'

class Op_if_acmpeq (Op_):
  branch_offset = 'i2'
class Op_if_acmpne (Op_):
  branch_offset = 'i2'
class Op_if_icmpeq (Op_):
  branch_offset = 'i2'
class Op_if_icmpge (Op_):
  branch_offset = 'i2'
class Op_if_icmpgt (Op_):
  branch_offset = 'i2'
class Op_if_icmple (Op_):
  branch_offset = 'i2'
class Op_if_icmplt (Op_):
  branch_offset = 'i2'
class Op_if_icmpne (Op_):
  branch_offset = 'i2'
class Op_ifeq (Op_):
  branch_offset = 'i2'
class Op_ifge (Op_):
  branch_offset = 'i2'
class Op_ifgt (Op_):
  branch_offset = 'i2'
class Op_ifle (Op_):
  branch_offset = 'i2'
class Op_iflt (Op_):
  branch_offset = 'i2'
class Op_ifne (Op_):
  branch_offset = 'i2'
class Op_ifnonnull (Op_):
  branch_offset = 'i2'
class Op_ifnull (Op_):
  branch_offset = 'i2'
class Op_iinc (Op_):
  local_var_index = 'u1'
  value = 'i1'
class Op_iload (Op_):
  local_var_index = 'u1'

class Op_instanceof (Op_):
  type_index = Constant
class Op_invokedynamic (Op_):
  call_site_index = Constant
  zero_pad = ('expect', b'\x00\x00')
class Op_invokeinterface (Op_):
  interface_method_index = Constant
  count = 'u1'
  zero_pad = ('expect', b'\x00')
class Op_invokespecial (Op_):
  method_index = ConstantMethodref
class Op_invokestatic (Op_):
  method_index = ConstantMethodref
class Op_invokevirtual (Op_):
  method_index = ConstantMethodref

class Op_istore (Op_):
  local_var_index = 'u1'

class Op_jsr (Op_):
  jump_offset = 'i2'
class Op_jsr_w (Op_):
  jump_offset = 'i4'

class Op_ldc (Op_):
  const_index = ('u1', Constant)
class Op_ldc2_w (Op_):
  const_index = Constant
class Op_ldc_w (Op_):
  const_index = Constant

class Op_lload (Op_):
  local_var_index = 'u1'

class MatchOffsetPair (Parsed):
  match = 'i4'
  offset = 'i4'
class Op_lookupswitch (Op_):
  align_pad = ('align', 4)
  default_offset = 'i4'
  npairs = 'i4'
  lookup_table = ('many', 'npairs', MatchOffsetPair)

class Op_lstore (Op_):
  local_var_index = 'u1'

class Op_multianewarray (Op_):
  type_index = Constant
  dimensions = 'u1'
class Op_new (Op_):
  type_index = Constant
class Op_newarray (Op_):
  atype = ('u1', PrimitiveArrayType)

class Op_putfield (Op_):
  field_ref_index = ConstantFieldref
class Op_putstatic (Op_):
  field_ref_index = ConstantFieldref
class Op_ret (Op_):
  local_var_index = 'u1'

class Op_sipush (Op_):
  value = 'i2'

class Op_tableswitch (Op_):
  align_pad = ('align', 4)
  default_offset = 'i4'
  low_bound = 'i4'
  high_bound = 'i4'
  jump_table = ('many', 'table_size', 'i4')

  @property
  def table_size (self):
    return self.high_bound - self.low_bound + 1
class Op_wide_aload (Op_):
  local_var_index = 'u2'
class Op_wide_astore (Op_):
  local_var_index = 'u2'
class Op_wide_dload (Op_):
  local_var_index = 'u2'
class Op_wide_dstore (Op_):
  local_var_index = 'u2'
class Op_wide_fload (Op_):
  local_var_index = 'u2'
class Op_wide_fstore (Op_):
  local_var_index = 'u2'
class Op_wide_iinc (Op_):
  local_var_index = 'u2'
  value = 'i2'
class Op_wide_iload (Op_):
  local_var_index = 'u2'
class Op_wide_istore (Op_):
  local_var_index = 'u2'
class Op_wide_lload (Op_):
  local_var_index = 'u2'
class Op_wide_lstore (Op_):
  local_var_index = 'u2'
class Op_wide_ret (Op_):
  local_var_index = 'u2'

namespace = locals()
for code in Opcode:
  class_name = 'Op_{}'.format(code.name)
  if class_name not in namespace:
    exec("class {} (Op_): pass".format(class_name))
