grammar signature;

options {
  language=Python;
  backtrack=true;
  output=AST;
}

tokens { ID; CLASS; }

fieldDescriptor
  : fieldType^
  ;

fieldType
  : baseType
  | objectType
  | arrayType
  ;

baseType
  : 'B'
  | 'C'
  | 'D'
  | 'F'
  | 'I'
  | 'J'
  | 'S'
  | 'Z'
  ;

objectType
  : 'L'^ className ';'!
  ;

className
  : packageSpecifier? id
  -> ^(CLASS packageSpecifier? id)
  ;

arrayType
  : '['^ componentType
  ;

componentType
  : fieldType
  ;


methodDescriptor
  : '('^ parameterDescriptor* ')' returnDescriptor
  ;

parameterDescriptor
  : fieldType
  ;


returnDescriptor
  : fieldType
  | voidDescriptor
  ;

voidDescriptor
  : 'V'
  ;

classSignature
  : formalTypeParameters? superclassSignature superinterfaceSignature*
  ;

formalTypeParameters
  : '<' formalTypeParameter+ '>'
  ;

formalTypeParameter
  : id classBound interfaceBound*
  ;

classBound
  : ':' fieldTypeSignature?
  ;

interfaceBound
  : ':' fieldTypeSignature
  ;

superclassSignature
  : classTypeSignature
  ;

superinterfaceSignature
  : classTypeSignature
  ;

fieldTypeSignature
  : classTypeSignature
  | arrayTypeSignature
  | typeVariableSignature
  ;

classTypeSignature
  : 'L' packageSpecifier? simpleClassTypeSignature classTypeSignatureSuffix* ';'
  ;

packageSpecifier
  : id '/' packageSpecifier*
  ;

simpleClassTypeSignature
  : id typeArguments?
  ;

classTypeSignatureSuffix
  : '.' simpleClassTypeSignature
  ;

typeVariableSignature
  : 'T' id ';'
  ;

typeArguments
  : '<' typeArgument+ '>'
  ;

typeArgument
  : wildcardIndicator? fieldTypeSignature
  | '*'
  ;

wildcardIndicator
  : '+'
  | '-'
  ;

arrayTypeSignature
  : '[' typeSignature
  ;

typeSignature
  : fieldTypeSignature
  | baseType
  ;

methodTypeSignature
  : formalTypeParameters? '(' typeSignature* ')' returnType throwsSignature*
  ;

returnType
  : typeSignature
  | voidDescriptor
  ;

throwsSignature
  : '^' classTypeSignature
  | '^' typeVariableSignature
  ;

id_chars
  : ~('.' | ';' | '[' | '/' | '<' | '>' | ':')+
  ;

id
  : id_chars
  -> ^(ID id_chars)
  ;


ELSE
  : ~('.' | ';' | '[' | '/' | '<' | '>' | ':')
  ;

