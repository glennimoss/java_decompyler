import sys
import decompyler
import classfile

classfile = classfile.ClassFile.from_file(sys.argv[1])
#print()
print(decompyler.decompyle(classfile))
