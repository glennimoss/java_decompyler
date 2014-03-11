grammar signature;

options {
  language=Python;
  backtrack=true;
  //output=AST;
}

FieldDescriptor
  : FieldType
  ;

FieldType
  : BaseType
  | ObjectType
  | ArrayType
  ;

BaseType
  : 'B'
  | 'C'
  | 'D'
  | 'F'
  | 'I'
  | 'J'
  | 'S'
  | 'Z'
  ;

ObjectType
  //: 'L' ClassName ';'
  : 'L' PackageSpecifier ';'
  ;

ArrayType
  : '[' ComponentType
  ;

ComponentType
  : FieldType
  ;


MethodDescriptor
  : '(' ParameterDescriptor* ')' ReturnDescriptor
  ;

ParameterDescriptor
  : FieldType
  ;


ReturnDescriptor
  : FieldType
  | VoidDescriptor
  ;

VoidDescriptor
  : 'V'
  ;

ClassSignature
  : FormalTypeParameters? SuperclassSignature SuperinterfaceSignature*
  ;

FormalTypeParameters
  : '<' FormalTypeParameter+ '>'
  ;

FormalTypeParameter
  : ID ClassBound InterfaceBound*
  ;

ClassBound
  : ':' FieldTypeSignature?
  ;

InterfaceBound
  : ':' FieldTypeSignature
  ;

SuperclassSignature
  : ClassTypeSignature
  ;

SuperinterfaceSignature
  : ClassTypeSignature
  ;

FieldTypeSignature
  : ClassTypeSignature
  | ArrayTypeSignature
  | TypeVariableSignature
  ;

ClassTypeSignature
  : 'L' PackageSpecifier? SimpleClassTypeSignature ClassTypeSignatureSuffix* ';'
  ;

PackageSpecifier
  : ID '/' PackageSpecifier*
  ;

SimpleClassTypeSignature
  : ID TypeArguments?
  ;

ClassTypeSignatureSuffix
  : '.' SimpleClassTypeSignature
  ;

TypeVariableSignature
  : 'T' ID ';'
  ;

TypeArguments
  : '<' TypeArgument+ '>'
  ;

TypeArgument
  : WildcardIndicator? FieldTypeSignature
  | '*'
  ;

WildcardIndicator
  : '+'
  | '-'
  ;

ArrayTypeSignature
  : '[' TypeSignature
  ;

TypeSignature
  : FieldTypeSignature
  | BaseType
  ;

MethodTypeSignature
  : FormalTypeParameters? '(' TypeSignature* ')' ReturnType ThrowsSignature*
  ;

ReturnType
  : TypeSignature
  | VoidDescriptor
  ;

ThrowsSignature
  : '^' ClassTypeSignature
  | '^' TypeVariableSignature
  ;

ID
  : ~('.' | ';' | '[' | '/' | '<' | '>' | ':')+
  ;

