import typing as t
import lark
from lark import Lark, Token, v_args
from lark.visitors import Transformer
from lark.tree import Meta
from coral import ast


GRAMMAR: t.Final = r"""
file: term
 
?term: logical
    | "(" term "," term ")"               -> tuple
    | "{" term "}"
    | "let" parameter "=" term ";" term   -> let
    | "if" "(" term ")" term "else" term  -> condition
    | "fn" "(" parameters ")" "=>" term   -> fn

parameters: [parameter ("," parameter)*]
parameter: CNAME

LOGICAL_OP: "&&"
    | "||"
    | "=="
    | "!="
    | "<="
    | ">="
    | "<"
    | ">"
?logical: arithmetic
    | arithmetic LOGICAL_OP logical

ARITHMETIC_OP: "+" | "-"
?arithmetic: factor | factor ARITHMETIC_OP arithmetic

FACTOR_OP: "*" | "/" | "%" 
?factor: apply | apply FACTOR_OP factor

?apply: primary | call

?primary: "(" term ")"
    | "true"           -> true
    | "false"          -> false
    | var              -> var
    | ESCAPED_STRING   -> string
    | SIGNED_NUMBER    -> integer

call: "print" "(" term ")"    -> print        
    | "first" "(" term ")"    -> first
    | "second" "(" term ")"   -> second
    | apply "(" arguments ")" -> call

arguments: [term ("," term)*]

?var: CNAME
 
%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER
%import common.CNAME
%import common.WS
%ignore WS
"""


_OPERATOR2NAME: t.Final[t.Dict[str, ast.SyntaxBinaryOperator]] = {
    '+': 'Add',
    '-': 'Sub',
    '*': 'Mul',
    '/': 'Div',
    '%': 'Rem',
    '<': 'Lt',
    '<=': 'Lte',
    '>': 'Gt',
    '>=': 'Gte',
    '==': 'Eq',
    '!=': 'Neq',
    '&&': 'And',
    '||': 'Or'
}

@v_args(meta=True)
class _Lark2RinhaAST(Transformer[Token, ast.SyntaxTerm | ast.FileSyntax]):

    def __init__(self, filename: str, visit_tokens: bool = True) -> None:
        super().__init__(visit_tokens)
        self.filename: t.Final = filename

    def file(self, meta: Meta, children: t.List[ast.SyntaxTerm]) -> ast.FileSyntax:
        return {
            'name': self.filename,
            'expression': children[0],
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def let(self, meta: Meta, children: t.List[t.Union[ast.ParameterSyntax, ast.SyntaxTerm]]) -> ast.LetExpressionSyntax:
        name = t.cast(ast.ParameterSyntax, children[0])
        value = t.cast(ast.SyntaxTerm, children[1])
        _next = t.cast(ast.SyntaxTerm, children[2])
        return {
            'kind': 'Let',
            'name': name,
            'value': value,
            'next': _next,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def fn(self, meta: Meta, children: t.List[t.Union[t.List[ast.ParameterSyntax], ast.SyntaxTerm]]) -> ast.FunctionExpressionSyntax:
        params = t.cast(t.List[ast.ParameterSyntax], children[0])
        value = t.cast(ast.SyntaxTerm, children[1])
        return {
            'kind': 'Function',
            'parameters': params,
            'value': value,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }

    def parameters(self, meta: Meta, children: t.List[t.Optional[ast.ParameterSyntax]]) -> t.List[ast.ParameterSyntax]:
        if children is None or children[0] is None:
            return []
        return t.cast(t.List[ast.ParameterSyntax], children)

    def parameter(self, meta: Meta, children: t.List[lark.Token]) -> ast.ParameterSyntax:
        return {
            'text': children[0].value,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def print(self, meta: Meta, children: t.List[ast.SyntaxTerm]) -> ast.PrintSyntax:
        return {
            'kind': 'Print',
            'value': children[0],
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def first(self, meta: Meta, children: t.List[ast.SyntaxTerm]) -> ast.FirstSyntax:
        return {
            'kind': 'First',
            'value': children[0],
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def second(self, meta: Meta, children: t.List[ast.SyntaxTerm]) -> ast.SecondSyntax:
        return {
            'kind': 'Second',
            'value': children[0],
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def call(self, meta: Meta, children: t.List[t.Union[t.List[ast.SyntaxTerm], ast.SyntaxTerm]]) -> ast.CallExpressionSyntax:
        callee = t.cast(ast.SyntaxTerm, children[0])
        args = t.cast(t.List[ast.SyntaxTerm], children[1])
        return {
            'kind': 'Call',
            'callee': callee,
            'arguments': args,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }

    def arguments(self, meta: Meta, children: t.List[t.Optional[ast.SyntaxTerm]]) -> t.List[ast.SyntaxTerm]:
        if children is None or children[0] is None:
            return []
        return t.cast(t.List[ast.SyntaxTerm], children) 
    
    def condition(self, meta: Meta, children: t.List[ast.SyntaxTerm]) -> ast.ConditionalExpressionSyntax:
        return {
            'kind': 'If',
            'condition': children[0],
            'then': children[1],
            'otherwise': children[2],
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def logical(self, meta: Meta, children: t.List[t.Union[ast.SyntaxTerm, Token]]) -> ast.BinaryExpressionSyntax:
        return self.__parse_binary(meta, children)

    def arithmetic(self, meta: Meta, children: t.List[t.Union[ast.SyntaxTerm, Token]]) -> ast.BinaryExpressionSyntax:
        return self.__parse_binary(meta, children)
    
    def factor(self, meta: Meta, children: t.List[t.Union[ast.SyntaxTerm, Token]]) -> ast.BinaryExpressionSyntax:
        return self.__parse_binary(meta, children)
    
    def __parse_binary(self, meta: Meta, children: t.List[t.Union[ast.SyntaxTerm, Token]]) -> ast.BinaryExpressionSyntax:
        left = t.cast(ast.SyntaxTerm, children[0])
        op = t.cast(Token, children[1])
        right = t.cast(ast.SyntaxTerm, children[2])
        return {
            'kind': 'Binary',
            'lhs': left,
            'op': _OPERATOR2NAME[op.value],
            'rhs': right,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }

    def var(self, meta: Meta, children: t.List[Token]) -> ast.IdentifierSyntax:
        return {
            'kind': 'Var',
            'text': children[0].value,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def tuple(self, meta: Meta, children: t.List[ast.SyntaxTerm]) -> ast.TupleSyntax:
        return {
            'kind': 'Tuple',
            'first': children[0],
            'second': children[1],
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }

    def string(self, meta: Meta, children: t.List[Token]) -> ast.LiteralSyntax:
        return {
            'kind': 'Str',
            'value': children[0].value[1:-1],
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }

    def integer(self, meta: Meta, children: t.List[Token]) -> ast.LiteralSyntax:
        return {
            'kind': 'Int',
            'value': int(children[0].value),
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def true(self, meta: Meta, children: t.List[Token]) -> ast.LiteralBooleanSyntax:
        return {
            'kind': 'Bool',
            'value': True,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }

    def false(self, meta: Meta, children: t.List[Token]) -> ast.LiteralBooleanSyntax:
        return {
            'kind': 'Bool',
            'value': False,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }


_parser: t.Final = Lark(GRAMMAR, start='file', parser='lalr', propagate_positions=True)

def parse(src: str, *, filename: str='<main>') -> ast.FileSyntax:
    return t.cast(ast.FileSyntax, _Lark2RinhaAST(filename).transform(_parser.parse(src)))
