from abc import ABC # make mypyc compile ABC first
import typing as t
import lark
from lark import Lark, Token, v_args
from lark.visitors import Transformer
from lark.tree import Meta


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

SyntaxTerm: t.TypeAlias = t.Union[
    'LiteralSyntax',
    'LiteralBooleanSyntax',
    'TupleSyntax',
    'IdentifierSyntax',
    'LetExpressionSyntax',
    'PrintSyntax',
    'FirstSyntax',
    'SecondSyntax',
    'BinaryExpressionSyntax',
    'CallExpressionSyntax',
    'ConditionalExpressionSyntax',
    'FunctionExpressionSyntax'
]

class SyntaxLocation(t.TypedDict):
    line: int
    start: int
    end: int
    filename: str

class LiteralSyntax(t.TypedDict):
    kind: t.Literal['Int', 'Str']
    value: t.Union[int, str]
    location: SyntaxLocation

class LiteralBooleanSyntax(t.TypedDict):
    kind: t.Literal['Bool']
    value: bool
    location: SyntaxLocation

class TupleSyntax(t.TypedDict):
    kind: t.Literal['Tuple']
    first: SyntaxTerm
    second: SyntaxTerm
    location: SyntaxLocation

class IdentifierSyntax(t.TypedDict):
    kind: t.Literal['Var']
    text: str
    location: SyntaxLocation

class ParameterSyntax(t.TypedDict):
    text: str
    location: SyntaxLocation

class LetExpressionSyntax(t.TypedDict):
    kind: t.Literal['Let']
    name: ParameterSyntax
    value: SyntaxTerm
    next: SyntaxTerm
    location: SyntaxLocation

class PrintSyntax(t.TypedDict):
    kind: t.Literal['Print']
    value: SyntaxTerm
    location: SyntaxLocation

class FirstSyntax(t.TypedDict):
    kind: t.Literal['First']
    value: SyntaxTerm
    location: SyntaxLocation

class SecondSyntax(t.TypedDict):
    kind: t.Literal['Second']
    value: SyntaxTerm
    location: SyntaxLocation

BinaryOperator: t.TypeAlias = t.Literal[
    'Add',
    'Sub',
    'Mul',
    'Div',
    'Rem',
    'Eq', 'Neq',
    'Lt', 'Lte',
    'Gt', 'Gte',
    'And', 'Or'
]
class BinaryExpressionSyntax(t.TypedDict):
    kind: t.Literal['Binary']
    lhs: SyntaxTerm
    op: BinaryOperator
    rhs: SyntaxTerm
    location: SyntaxLocation

class CallExpressionSyntax(t.TypedDict):
    kind: t.Literal['Call']
    callee: SyntaxTerm
    arguments: t.List[SyntaxTerm]
    location: SyntaxLocation

class ConditionalExpressionSyntax(t.TypedDict):
    kind: t.Literal['If']
    condition: SyntaxTerm
    then: SyntaxTerm
    otherwise: SyntaxTerm
    location: SyntaxLocation

class FunctionExpressionSyntax(t.TypedDict):
    kind: t.Literal['Function']
    parameters: t.List[ParameterSyntax]
    value: SyntaxTerm
    location: SyntaxLocation

class FileSyntax(t.TypedDict):
    name: str
    expression: SyntaxTerm
    location: SyntaxLocation


_OPERATOR2NAME: t.Final['t.Dict[str, BinaryOperator]'] = {
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
class _Lark2RinhaAST(Transformer[Token, SyntaxTerm | FileSyntax]):

    def __init__(self, filename: str, visit_tokens: bool = True) -> None:
        super().__init__(visit_tokens)
        self.filename: t.Final = filename

    def file(self, meta: Meta, children: t.List[SyntaxTerm]) -> FileSyntax:
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
    
    def let(self, meta: Meta, children: t.List[t.Union[ParameterSyntax, SyntaxTerm]]) -> LetExpressionSyntax:
        name = t.cast(ParameterSyntax, children[0])
        value = t.cast(SyntaxTerm, children[1])
        _next = t.cast(SyntaxTerm, children[2])
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
    
    def fn(self, meta: Meta, children: t.List[t.Union[t.List[ParameterSyntax], SyntaxTerm]]) -> FunctionExpressionSyntax:
        params = t.cast(t.List[ParameterSyntax], children[0])
        value = t.cast(SyntaxTerm, children[1])
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

    def parameters(self, meta: Meta, children: t.List[t.Optional[ParameterSyntax]]) -> t.List[ParameterSyntax]:
        if children is None or children[0] is None:
            return []
        return t.cast(t.List[ParameterSyntax], children)

    def parameter(self, meta: Meta, children: t.List[lark.Token]) -> ParameterSyntax:
        return {
            'text': children[0].value,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }
    
    def print(self, meta: Meta, children: t.List[SyntaxTerm]) -> PrintSyntax:
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
    
    def first(self, meta: Meta, children: t.List[SyntaxTerm]) -> FirstSyntax:
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
    
    def second(self, meta: Meta, children: t.List[SyntaxTerm]) -> SecondSyntax:
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
    
    def call(self, meta: Meta, children: t.List[t.Union[t.List[SyntaxTerm], SyntaxTerm]]) -> CallExpressionSyntax:
        callee = t.cast(SyntaxTerm, children[0])
        args = t.cast(t.List[SyntaxTerm], children[1])
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

    def arguments(self, meta: Meta, children: t.List[t.Optional[SyntaxTerm]]) -> t.List[SyntaxTerm]:
        if children is None or children[0] is None:
            return []
        return t.cast(t.List[SyntaxTerm], children) 
    
    def condition(self, meta: Meta, children: t.List[SyntaxTerm]) -> ConditionalExpressionSyntax:
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
    
    def logical(self, meta: Meta, children: t.List[t.Union[SyntaxTerm, Token]]) -> BinaryExpressionSyntax:
        return self.__parse_binary(meta, children)

    def arithmetic(self, meta: Meta, children: t.List[t.Union[SyntaxTerm, Token]]) -> BinaryExpressionSyntax:
        return self.__parse_binary(meta, children)
    
    def factor(self, meta: Meta, children: t.List[t.Union[SyntaxTerm, Token]]) -> BinaryExpressionSyntax:
        return self.__parse_binary(meta, children)
    
    def __parse_binary(self, meta: Meta, children: t.List[t.Union[SyntaxTerm, Token]]) -> BinaryExpressionSyntax:
        left = t.cast(SyntaxTerm, children[0])
        op = t.cast(Token, children[1])
        right = t.cast(SyntaxTerm, children[2])
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

    def var(self, meta: Meta, children: t.List[Token]) -> IdentifierSyntax:
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
    
    def tuple(self, meta: Meta, children: t.List[SyntaxTerm]) -> TupleSyntax:
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

    def string(self, meta: Meta, children: t.List[Token]) -> LiteralSyntax:
        return {
            'kind': 'Str',
            'value': children[0].value,
            'location': {
                'filename': self.filename,
                'line': meta.line,
                'start': meta.column,
                'end': meta.end_column
            }
        }

    def integer(self, meta: Meta, children: t.List[Token]) -> LiteralSyntax:
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
    
    def true(self, meta: Meta, children: t.List[Token]) -> LiteralBooleanSyntax:
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

    def false(self, meta: Meta, children: t.List[Token]) -> LiteralBooleanSyntax:
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

def parse(src: str, *, filename: str='<main>') -> FileSyntax:
    return t.cast(FileSyntax, _Lark2RinhaAST(filename).transform(_parser.parse(src)))


def flatten(term: SyntaxTerm, result: t.List[SyntaxTerm]) -> None:
    """Flattens the AST into a list with topological order."""
    match term['kind']:
        case 'Int' | 'Str' | 'Bool' | 'Var':
            result.append(term)
            return
        case 'Tuple':
            term = t.cast(TupleSyntax, term)
            flatten(term['first'], result)
            flatten(term['second'], result)
            result.append(term)
            return
        case 'Binary':
            term = t.cast(BinaryExpressionSyntax, term)
            flatten(term['lhs'], result)
            flatten(term['rhs'], result)
            result.append(term)
            return
        case 'Call':
            term = t.cast(CallExpressionSyntax, term)
            for arg in reversed(term['arguments']):
                flatten(arg, result)
            flatten(term['callee'], result)
            result.append(term)
            return
        case 'Print':
            term = t.cast(PrintSyntax, term)
            flatten(term['value'], result)
            result.append(term)
            return
        case 'First':
            term = t.cast(FirstSyntax, term)
            flatten(term['value'], result)
            result.append(term)
            return
        case 'Second':
            term = t.cast(SecondSyntax, term)
            flatten(term['value'], result)
            result.append(term)
            return
        case 'If':
            term = t.cast(ConditionalExpressionSyntax, term)
            flatten(term['condition'], result)
            flatten(term['then'], result)
            flatten(term['otherwise'], result)
            result.append(term)
            return
        case 'Function':
            term = t.cast(FunctionExpressionSyntax, term)
            flatten(term['value'], result)
            result.append(term)
            return
        case 'Let':
            term = t.cast(LetExpressionSyntax, term)
            flatten(term['value'], result)
            flatten(term['next'], result)
            result.append(term)
            return
        case _:
            raise ValueError(f"unknown node kind '{term['kind']}'")
