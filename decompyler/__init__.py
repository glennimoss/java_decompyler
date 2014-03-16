from classfile.flags import *

def decompyle (classfile):
  lines = ['\n']

  line = [' ']
  for flag in sorted(classfile.access_flags):
    if flag is ClassAccessFlags.ACC_PUBLIC:
      line.append('public')
    elif flag is ClassAccessFlags.ACC_FINAL:
      line.append('final')
    elif flag is ClassAccessFlags.ACC_ABSTRACT:
      line.append('abstract')

  if ClassAccessFlags.ACC_INTERFACE in classfile.access_flags:
    line.append('interface')
  elif ClassAccessFlags.ACC_ENUM in classfile.access_flags:
    line.append('enum')
  else:
    line.append('class')

  line.append(classfile.this_class)

  if str(classfile.super_class) != 'java.lang.Object':
    line.append('extends')
    line.append(classfile.super_class)

  if classfile.interfaces:
    line.append('implements')
    line.append([', '] + classfile.interfaces)

  line.append('{')
  lines.append(line)

  for field in classfile.fields:
    line = [' ', ' ']
    for flag in sorted(field.access_flags):
      if flag is FieldAccessFlags.ACC_PUBLIC:
        line.append('public')
      elif flag is FieldAccessFlags.ACC_PRIVATE:
        line.append('private')
      elif flag is FieldAccessFlags.ACC_PROTECTED:
        line.append('protected')
      elif flag is FieldAccessFlags.ACC_STATIC:
        line.append('static')
      elif flag is FieldAccessFlags.ACC_FINAL:
        line.append('final')
      elif flag is FieldAccessFlags.ACC_VOLATILE:
        line.append('volatile')
      elif flag is FieldAccessFlags.ACC_TRANSIENT:
        line.append('transient')
      elif flag is FieldAccessFlags.ACC_SYNTHETIC:
        # TODO: Is just skipping the right thing to do?
        continue
    line.append(field.descriptor)
    line.append(['', field.name, ';'])

    lines.append(line)

  lines.append('')

  for method in classfile.methods:
    method_lines = ['\n  ']
    line = [' ', ' ']
    for flag in sorted(method.access_flags):
      if flag is MethodAccessFlags.ACC_PUBLIC:
        line.append('public')
      elif flag is MethodAccessFlags.ACC_PRIVATE:
        line.append('private')
      elif flag is MethodAccessFlags.ACC_PROTECTED:
        line.append('protected')
      elif flag is MethodAccessFlags.ACC_STATIC:
        line.append('static')
      elif flag is MethodAccessFlags.ACC_FINAL:
        line.append('final')
      elif flag is MethodAccessFlags.ACC_SYNCHRONIZED:
        line.append('synchronized')
      elif flag is MethodAccessFlags.ACC_NATIVE:
        line.append('native')
      elif flag is MethodAccessFlags.ACC_ABSTRACT:
        line.append('abstract')
      elif flag is MethodAccessFlags.ACC_SYNTHETIC:
        # TODO: Is just skipping the right thing to do?
        continue
    ret_type, *arg_types = method.descriptor
    if method.name.string == '<init>':
      line.append(classfile.this_class)
    else:
      line.append(ret_type)
      line.append(method.name)

    args = [', ']
    for i, arg_type in enumerate(arg_types):
      arg = [' ', arg_type, 'arg{}'.format(i)]
      args.append(arg)

    rest = ['', '(', args, ')']
    if MethodAccessFlags.ACC_ABSTRACT in method.access_flags:
      rest.append(';')
    else:
      rest.append(' {')
    line.append(rest)
    method_lines.append(line)

    # Code...
    body_lines = ['\n    ']
    body_lines.append('    // Code...')

    method_lines.append(body_lines)

    method_lines.append('}')
    lines.append(method_lines)

  lines.append('}')

  return format(lines)



def format (item):
  if type(item) is list:
    return item[0].join(format(e) for e in item[1:])
  return str(item)

