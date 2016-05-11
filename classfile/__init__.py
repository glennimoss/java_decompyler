"""Load and parse classfiles.

  >>> java_class = ClassFile.from_file('filename')
Where f is a file-like object:
  >>> java_class = ClassFile.from_bytes(f)
"""

from classfile.classfile import *
