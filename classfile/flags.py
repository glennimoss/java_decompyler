from enum import IntEnum

@classmethod
def _find_flags (class_, bits):
  flags = set()

  for flag in class_:
    if flag & bits:
      flags.add(flag)

  return flags

class ClassAccessFlags (IntEnum):
  """Class access flag constants.

  ACC_PUBLIC: Declared public; may be accessed from outside its package.
  ACC_PRIVATE: Marked private in source. Inner class only.
  ACC_PROTECTED: Marked protected in source. Inner class only.
  ACC_STATIC: Marked or implicitly static in source. Inner class only.
  ACC_FINAL: Declared final; no subclasses allowed.
  ACC_SUPER: Treat superclass methods specially when invoked by the
             invokespecial instruction.
  ACC_INTERFACE: Is an interface, not a class.
  ACC_ABSTRACT: Declared abstract; must not be instantiated.
  ACC_SYNTHETIC: Declared synthetic; not present in the source code.
  ACC_ANNOTATION: Declared as an annotation type.
  ACC_ENUM: Declared as an enum type.
  """

  ACC_PUBLIC     = 0x0001
  ACC_PRIVATE    = 0x0002
  ACC_PROTECTED  = 0x0004
  ACC_STATIC     = 0x0008
  ACC_FINAL      = 0x0010
  ACC_SUPER      = 0x0020
  ACC_INTERFACE  = 0x0200
  ACC_ABSTRACT   = 0x0400
  ACC_SYNTHETIC  = 0x1000
  ACC_ANNOTATION = 0x2000
  ACC_ENUM       = 0x4000

  flags = _find_flags

class FieldAccessFlags (IntEnum):
  """Field access flag constants.

  ACC_PUBLIC: Declared public; may be accessed from outside its package.
  ACC_PRIVATE: Declared private; usable only within the defining class.
  ACC_PROTECTED: Declared protected; may be accessed within subclasses.
  ACC_STATIC: Declared static.
  ACC_FINAL: Declared final; never directly assigned to after object
             construction (JLS §17.5).
  ACC_VOLATILE: Declared volatile; cannot be cached.
  ACC_TRANSIENT: Declared transient; not written or read by a persistent object
                 manager.
  ACC_SYNTHETIC: Declared synthetic; not present in the source code.
  ACC_ENUM: Declared as an element of an enum.
  """

  ACC_PUBLIC    = 0x0001
  ACC_PRIVATE   = 0x0002
  ACC_PROTECTED = 0x0004
  ACC_STATIC    = 0x0008
  ACC_FINAL     = 0x0010
  ACC_VOLATILE  = 0x0040
  ACC_TRANSIENT = 0x0080
  ACC_SYNTHETIC = 0x1000
  ACC_ENUM      = 0x4000

  flags = _find_flags

class MethodAccessFlags (IntEnum):
  """Method access flag constants.

  ACC_PUBLIC: Declared public; may be accessed from outside its package.
  ACC_PRIVATE: Declared private; accessible only within the defining class.
  ACC_PROTECTED: Declared protected; may be accessed within subclasses.
  ACC_STATIC: Declared static.
  ACC_FINAL: Declared final; must not be overridden (§5.4.5).
  ACC_SYNCHRONIZED: Declared synchronized; invocation is wrapped by a monitor
                    use.
  ACC_BRIDGE: A bridge method, generated by the compiler.
  ACC_VARARGS: Declared with variable number of arguments.
  ACC_NATIVE: Declared native; implemented in a language other than Java.
  ACC_ABSTRACT: Declared abstract; no implementation is provided.
  ACC_STRICT: Declared strictfp; floating-point mode is FP-strict.
  ACC_SYNTHETIC: Declared synthetic; not present in the source code.
  """

  ACC_PUBLIC       = 0x0001
  ACC_PRIVATE      = 0x0002
  ACC_PROTECTED    = 0x0004
  ACC_STATIC       = 0x0008
  ACC_FINAL        = 0x0010
  ACC_SYNCHRONIZED = 0x0020
  ACC_BRIDGE       = 0x0040
  ACC_VARARGS      = 0x0080
  ACC_NATIVE       = 0x0100
  ACC_ABSTRACT     = 0x0400
  ACC_STRICT       = 0x0800
  ACC_SYNTHETIC    = 0x1000

  flags = _find_flags

