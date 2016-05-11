from classfile.descriptor import ClassDescriptor, ArrayDescriptor
from classfile.flags import *
from formatter import Document

def decompyle (classfile):
  implicit = {None, 'java.lang', classfile.this_class.package}
  imports = set()
  namespace = set()
  def simplify_class (class_):
    if isinstance(class_, ArrayDescriptor):
      return ArrayDescriptor(simplify_class(class_.element_type))
    if not isinstance(class_, ClassDescriptor):
      return class_
    if class_.package not in implicit and class_ not in imports:
      if class_.class_name in namespace:
        # We can't import because of a name conflict
        return str(class_)

      imports.add(class_)
      namespace.add(class_.class_name)

    return class_.class_name

  class_def = Document()
  package_decl = class_def.section()
  import_block = class_def.section()
  decl, class_body = class_def.block()

  if classfile.this_class.package:
    package_decl.line('package', classfile.this_class.package)

  class_fields = class_body.section()
  class_methods = class_body.section()

  for flag in sorted(classfile.access_flags):
    if flag is ClassAccessFlags.ACC_PUBLIC:
      decl.append('public')
    elif flag is ClassAccessFlags.ACC_FINAL:
      decl.append('final')
    elif flag is ClassAccessFlags.ACC_ABSTRACT:
      decl.append('abstract')

  if ClassAccessFlags.ACC_INTERFACE in classfile.access_flags:
    decl.append('interface')
  elif ClassAccessFlags.ACC_ENUM in classfile.access_flags:
    decl.append('enum')
  else:
    decl.append('class')

  decl.append(classfile.this_class.class_name)

  if str(classfile.super_class) != 'java.lang.Object':
    decl.append('extends')
    decl.append(simplify_class(classfile.super_class))

  if classfile.interfaces:
    decl.append('implements')
    ifaces = decl.join(sep=', ')
    ifaces.extend(simplify_class(cls.descriptor) for cls in classfile.interfaces)

  for field in classfile.fields:
    field_line = class_fields.line()
    for flag in sorted(field.access_flags):
      if flag is FieldAccessFlags.ACC_PUBLIC:
        field_line.append('public')
      elif flag is FieldAccessFlags.ACC_PRIVATE:
        field_line.append('private')
      elif flag is FieldAccessFlags.ACC_PROTECTED:
        field_line.append('protected')
      elif flag is FieldAccessFlags.ACC_STATIC:
        field_line.append('static')
      elif flag is FieldAccessFlags.ACC_FINAL:
        field_line.append('final')
      elif flag is FieldAccessFlags.ACC_VOLATILE:
        field_line.append('volatile')
      elif flag is FieldAccessFlags.ACC_TRANSIENT:
        field_line.append('transient')
      elif flag is FieldAccessFlags.ACC_SYNTHETIC:
        # TODO: Is just skipping the right thing to do?
        #continue
        field_line.append('/* synthetic */')
    field_line.append(simplify_class(field.descriptor))
    field_line.append(field.name)
    if 'ConstantValue' in field.attributes:
      field_line.append('=');
      field_line.append(field.attributes.ConstantValue)


  for method in classfile.methods:
    method_def = class_methods.section()
    if MethodAccessFlags.ACC_ABSTRACT in method.access_flags:
      method_decl = method_def.line()
      method_body = None
    else:
      method_decl, method_body = method_def.block()

    for flag in sorted(method.access_flags):
      if flag is MethodAccessFlags.ACC_PUBLIC:
        method_decl.append('public')
      elif flag is MethodAccessFlags.ACC_PRIVATE:
        method_decl.append('private')
      elif flag is MethodAccessFlags.ACC_PROTECTED:
        method_decl.append('protected')
      elif flag is MethodAccessFlags.ACC_STATIC:
        method_decl.append('static')
      elif flag is MethodAccessFlags.ACC_FINAL:
        method_decl.append('final')
      elif flag is MethodAccessFlags.ACC_SYNCHRONIZED:
        method_decl.append('synchronized')
      elif flag is MethodAccessFlags.ACC_NATIVE:
        method_decl.append('native')
      elif flag is MethodAccessFlags.ACC_ABSTRACT:
        method_decl.append('abstract')
      elif flag is MethodAccessFlags.ACC_SYNTHETIC:
        # TODO: Is just skipping the right thing to do?
        #continue
        method_decl.append('/* synthetic */')
    if method.name.string == '<init>':
      method_decl.append(classfile.this_class.class_name)
    else:
      method_decl.append(simplify_class(method.descriptor.return_type))
      method_decl.append(method.name)

    argdef = method_decl.join(sep='')
    argdef.append('(')
    arglist = argdef.join(sep=', ')
    argdef.append(')')

    for i, arg_type in enumerate(method.descriptor.arg_types):
      arglist.join(simplify_class(arg_type), 'arg{}'.format(i))

    if method_body is not None:
      method_body.extend(method.attributes.Code.byte_code.formatted())

  # Imports should all have been collected...
  for class_ in sorted(imports):
    import_block.line('import', class_)

  return str(class_def)
