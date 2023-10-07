import enum
import typing as t


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

SyntaxBinaryOperator: t.TypeAlias = t.Literal[
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
    op: SyntaxBinaryOperator
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


class NativeType(enum.Enum):
    ANY = enum.auto()
    """All possible types"""
    UNDEFINED = enum.auto()
    """No type"""
    BOOLEAN = enum.auto()
    INTEGER = enum.auto()
    STRING = enum.auto()
    TUPLE = enum.auto()
    FUNCTION = enum.auto()
    UNION = enum.auto()
    """Types union"""

    def __str__(self) -> str:
        return self.name.lower().capitalize()
    
    def __repr__(self) -> str:
        return f'NativeType.{self.name}'
    
class IBoundType:
    """A generic type for AST nodes which is specialized during type inference"""

    @property
    def is_static(self) -> bool:
        raise NotImplementedError
    
    @property
    def type(self) -> NativeType:
        raise NotImplementedError
    
    @property
    def generics(self) -> t.Sequence['IBoundType']:
        raise NotImplementedError

    def union(self, other: 'IBoundType') -> 'IBoundType':
        """Merges this type with the given one creating a type union.
        
        Union with ANY results in ANY.
        Union with UNDEFINED results in UNDEFINED.
        """
        raise NotImplementedError
    
    def lower(self, other: 'IBoundType') -> 'IBoundType':
        """Returns the most specialized type between this type and the given one.
        
        Any concrete type is a specialization of the abstract ANY type.
        UNDEFINED is the max specialization of any type.

        - lower(ANY, ANY)       = ANY
        - lower(ANY, UNDEFINED) = UNDEFINED
        - lower(ANY, T)         = T
        - lower(UNDEFINED, T)   = UNDEFINED
        - lower(T, U)           = U if T contains U, UNDEFINED otherwise
        """
        raise NotImplementedError

    def lowers(self, other: 'IBoundType') -> bool:
        """Returns True if this type is more specialized than the given type, False otherwise"""
        raise NotImplementedError
    
    def __eq__(self, __value: object) -> bool:
        raise NotImplementedError
    
    def __hash__(self) -> int:
        raise NotImplementedError

class BoundType(IBoundType):

    def __init__(self, type_: NativeType, generics: t.Sequence[IBoundType]) -> None:
        self._native_type: t.Final = type_
        self._generics: t.Final = generics
        self._is_static: t.Final = (
            type_  != NativeType.ANY and
            type_ != NativeType.UNDEFINED and
            all(arg.is_static for arg in generics)
        )
        self._hashseed: t.Final = (self._native_type, self._generics)

    @property
    def is_static(self) -> bool:
        return self._is_static
    
    @property
    def type(self) -> NativeType:
        return self._native_type
    
    @property
    def generics(self) -> t.Sequence[IBoundType]:
        return self._generics
    
    def union(self, other: IBoundType) -> IBoundType:
        if self._native_type == NativeType.ANY or self._native_type == NativeType.UNDEFINED:
            return self
        if other.type == NativeType.ANY or other.type == NativeType.UNDEFINED:
            return other
        if other.type == NativeType.UNION or other.type == NativeType.FUNCTION:
            return other.union(self)
        if self._native_type != other.type:
            return BoundTypeUnion({self._native_type: self, other.type: other})
        other = t.cast(BoundType, other)
        other_generics = other.generics
        if len(self._generics) != len(other_generics):
            raise TypeError(f"can't union '{self}' with {other} because they have different number of generics")
        if len(self._generics) == 0:
            return self # self == other
        return BoundType(
            self._native_type,
            tuple(myg.union(other_generics[i]) for i, myg in enumerate(self._generics))
        )
    
    def lower(self, other: IBoundType) -> IBoundType:
        if self._native_type == NativeType.UNDEFINED:
            return self
        if other.type == NativeType.UNDEFINED:
            return other
        if self._native_type == NativeType.ANY:
            return other
        if other.type == NativeType.ANY:
            return self
        if other.type != self._native_type:
            return BoundType(NativeType.UNDEFINED, ())
        other = t.cast(BoundType, other)
        if len(self._generics) != len(other.generics):
            raise TypeError(f"can't intersect '{self}' and '{other}' because they have different number of generics")
        if len(self._generics) == 0:
            return self # self == other
        other_generics = other.generics
        return BoundType(
            self._native_type,
            tuple(myg.lower(other_generics[i]) for i, myg in enumerate(self._generics))
        )
    
    def lowers(self, other: IBoundType) -> bool:
        lower = self.lower(other)
        return (
            lower.type != NativeType.ANY and
            all(generic.type != NativeType.ANY for generic in lower.generics)
        )
    
    def __eq__(self, o: object) -> bool:
        return type(o) is BoundType and self._native_type == o._native_type and self._generics == o._generics
    
    def __hash__(self) -> int:
        return hash(self._hashseed)
    
    def __str__(self) -> str:
        if len(self._generics) > 0:
            return f"{self._native_type}<{', '.join(str(arg) for arg in self._generics)}>"
        else:
            return str(self._native_type)
        
    def __repr__(self) -> str:
        return f'{type(self).__name__}(type_={repr(self._native_type)}, generics={repr(self._generics)})'

class BoundTypeUnion(IBoundType):

    def __init__(self, members: t.Dict[NativeType, IBoundType]) -> None:
        self._members: t.Final = members
        self._hashseed: t.Final = tuple(member for member in members.values())

    @property
    def is_static(self) -> bool:
        return False

    @property
    def type(self) -> NativeType:
        return NativeType.UNION
    
    @property
    def generics(self) -> t.Sequence[IBoundType]:
        return ()
    
    @property
    def members(self) -> t.Dict[NativeType, IBoundType]:
        return self._members
    
    @classmethod
    def for_members(cls, *members: IBoundType) -> 'BoundTypeUnion':
        return BoundTypeUnion({member.type: member for member in members})

    def union(self, other: IBoundType) -> IBoundType:
        if other.type == NativeType.ANY or other.type == NativeType.UNDEFINED:
            return other
        if other.type == NativeType.UNION:
            other = t.cast(BoundTypeUnion, other)
            other_members = other.members
            union: t.List[IBoundType] = []
            for my_member in self._members.values():
                other_member = other_members.get(my_member.type, None)
                if other_member is None:
                    union.append(my_member)
                else:
                    union.append(my_member.union(other_member))
            return BoundTypeUnion({member.type: member for member in union})
        else:
            my_member2 = self._members.get(other.type, None)
            if my_member2 is None:
                return self # the union result is ourself
            union2 = self._members.copy()
            union2[my_member2.type] = my_member2.union(other)
            return BoundTypeUnion(union2)
    
    def lower(self, other: IBoundType) -> IBoundType:
        if other.type == NativeType.ANY:
            return self
        if other.type == NativeType.UNDEFINED:
            return other
        if other.type == NativeType.UNION:
            other = t.cast(BoundTypeUnion, other)
            intersection: t.List[IBoundType] = []
            other_members = other.members
            for my_member in self._members.values():
                other_member = other_members.get(my_member.type, None)
                if other_member is None:
                    continue
                intersection.append(my_member.lower(other_member))
            if len(intersection) == 0:
                return BoundType(NativeType.UNDEFINED, ())
            return BoundTypeUnion({member.type: member for member in intersection})
        else:
            my_member2 = self._members.get(other.type, None)
            if my_member2 is None:
                return BoundType(NativeType.UNDEFINED, ())
            return my_member2.lower(other)

    def lowers(self, other: IBoundType) -> bool:
        lower = self.lower(other)
        return lower.type != NativeType.ANY

    def __eq__(self, o: object) -> bool:
        return isinstance(o, BoundTypeUnion) and self._members == o.members

    def __hash__(self) -> int:
        return hash(self._hashseed)

    def __str__(self) -> str:
        return ' | '.join(str(mem) for mem in self._members)
    
    def __repr__(self) -> str:
        return f'{type(self).__name__}(members={repr(self._members)})'

class BoundFunctionType(IBoundType):

    def __init__(self, params: t.Sequence[IBoundType], return_type: IBoundType) -> None:
        super().__init__()
        self._params: t.Final = params
        self._return_type: t.Final = return_type
        self._is_static: t.Final = return_type.is_static and all(param.is_static for param in params)
        self._hashseed: t.Final = (params, return_type)

    @property
    def type(self) -> NativeType:
        return NativeType.FUNCTION

    @property
    def is_static(self) -> bool:
        return self._is_static

    @property
    def params(self) -> t.Sequence[IBoundType]:
        return self._params

    @property
    def return_type(self) -> IBoundType:
        return self._return_type

    @property
    def generics(self) -> t.Sequence[IBoundType]:
        return (self._return_type,)

    def union(self, other: IBoundType) -> IBoundType:
        if other.type == NativeType.ANY or other.type == NativeType.UNDEFINED:
            return other
        if other.type == NativeType.UNION:
            return other.union(self)
        if other.type != NativeType.FUNCTION:
            return BoundTypeUnion({NativeType.FUNCTION: self, other.type: other})
        other = t.cast(BoundFunctionType, other)
        if len(self._params) != other.params:
            return BoundType(NativeType.UNDEFINED, ())
        other_params = other.params
        return BoundFunctionType(
            tuple(my_param.union(other_params[i]) for i, my_param in enumerate(other_params)),
            self._return_type.union(other.return_type)
        )

    def lower(self, other: IBoundType) -> IBoundType:
        if other.type == NativeType.UNDEFINED:
            return other
        if other.type == NativeType.ANY:
            return self
        if other.type != NativeType.FUNCTION:
            return BoundType(NativeType.UNDEFINED, ())
        other = t.cast(BoundFunctionType, other)
        other_params = other.params
        if len(self._params) != len(other_params):
            return BoundType(NativeType.UNDEFINED, ())
        return BoundFunctionType(
            tuple(my_param.lower(other_params[i]) for i, my_param in enumerate(self._params)),
            self._return_type.lower(other.return_type)
        )

    def lowers(self, other: IBoundType) -> bool:
        lower = self.lower(other)
        if lower.type != NativeType.FUNCTION:
            return False
        lower = t.cast(BoundFunctionType, lower)
        return (
            lower.return_type.type != NativeType.ANY and
            all(param.type != NativeType.ANY for param in lower.params)
        )

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, BoundFunctionType) and
            self._return_type == value.return_type and
            self._params == value.params
        )
    
    def __hash__(self) -> int:
        return hash(self._hashseed)
    
    def __str__(self) -> str:
        return f"({', '.join(str(param) for param in self.params)}) -> {self._return_type}"
        
    def __repr__(self) -> str:
        return f'{type(self).__name__}(params={repr(self._params)}, return_type={repr(self._return_type)})'
    

BOUND_ANY_TYPE: t.Final = BoundType(NativeType.ANY, ())
BOUND_UNDEFINED_TYPE: t.Final = BoundType(NativeType.UNDEFINED, ())
BOUND_BOOLEAN_TYPE: t.Final = BoundType(NativeType.BOOLEAN, ())
BOUND_INTEGER_TYPE: t.Final = BoundType(NativeType.INTEGER, ())
BOUND_STRING_TYPE: t.Final = BoundType(NativeType.STRING, ())
BOUND_TUPLE_TYPE: t.Final = BoundType(NativeType.TUPLE, (BOUND_ANY_TYPE, BOUND_ANY_TYPE))

BINOP_ADD_TYPES: t.Final = BoundTypeUnion.for_members(BOUND_INTEGER_TYPE, BOUND_STRING_TYPE)
BINOP_EQUAL_TYPES: t.Final = BoundTypeUnion.for_members(BOUND_BOOLEAN_TYPE, BOUND_INTEGER_TYPE, BOUND_STRING_TYPE)
BINOP_NOT_EQUAL_TYPES: t.Final = BINOP_EQUAL_TYPES


class ScopeVar:
    """Stores the expression assigned to a name. We call it "var" but names are not mutable."""
    __slots__ = ('type', 'name', 'index', 'changed')

    def __init__(self, type_: IBoundType, name: str, index: int) -> None:
        self.type = type_
        self.name: t.Final = name
        self.index: t.Final = index
        self.changed: bool = False

    def may_change(self, newtype: IBoundType) -> None:
        if newtype != self.type:
            self.type = newtype
            self.changed = True

    def __eq__(self, o: object) -> bool:
        return isinstance(o, ScopeVar) and o.name == self.name
    
    def __hash__(self) -> int:
        return hash(self.name)

class GlobalVar:
    __slots__ = ('var', 'index')

    def __init__(self, var: ScopeVar, index: int) -> None:
        self.var: t.Final = var
        self.index: t.Final = index

    def __eq__(self, o: object) -> bool:
        return isinstance(o, GlobalVar) and self.var == o.var

    def __hash__(self) -> int:
        return hash(self.var)

class TypeScope:

    def __init__(self, parent: t.Optional['TypeScope']) -> None:
        self.parent = parent
        self.locals: t.Final[t.Dict[str, ScopeVar]] = {}
        """ALL variables declared inside this scope, does not include any var from any parent, neither from any children scopes"""
        self.globals: t.Final[t.Dict[str, GlobalVar]] = {}
        """ALL variables captured from the immediate parent scope"""

    def declare(self, name: str, type_: IBoundType) -> ScopeVar:
        """Declares a new var with the given name.
        
        Raises SyntaxError if it's already declare.
        """
        if name in self.locals:
            raise SyntaxError(f"Identifier '{name}' has already been defined")
        var = ScopeVar(type_, name, len(self.locals))
        self.locals[name] = var
        return var

    def get(self, name: str) -> ScopeVar:
        localvar = self.locals.get(name, None)
        if localvar is not None:
            return localvar
        globalvar = self.globals.get(name, None)
        if globalvar is not None:
            return globalvar.var
        if self.parent is not None:
            var = self.parent.get(name)
            self.globals[name] = GlobalVar(var, len(self.globals))
            return var
        raise ValueError(f"Identifier '{name}' is not defined")


class Expression:
    """Root node of the typed AST."""

    def __init__(self, type_: IBoundType, scope: TypeScope, parent: t.Optional['Expression']=None) -> None:
        self.boundtype: IBoundType = type_
        self.parent = parent
        self.scope: t.Final = scope

    def infertype(self, supertype: IBoundType) -> IBoundType:
        """Performs a type inference round.
        
        The "supertype" is a constraint over the type of the expression evaluation result from this
        node. Either it's a sub type of the given supertype or UNDEFINED. The result is returned.
        """
        raise NotImplementedError
    
    def handle_partial_inference(self, type_: IBoundType) -> None:
        """Called from the children AST nodes to inform of partial results from a infertype call to them"""
        pass


class LiteralBooleanValue(Expression):

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        value: bool
    ) -> None:
        super().__init__(type_, scope, parent)
        self.value = value

    def infertype(self, supertype: IBoundType) -> IBoundType:
        return supertype.lower(BOUND_BOOLEAN_TYPE)
    
class LiteralIntegerValue(Expression):

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        value: int
    ) -> None:
        super().__init__(type_, scope, parent)
        self.value = value

    def infertype(self, supertype: IBoundType) -> IBoundType:
        return supertype.lower(BOUND_INTEGER_TYPE)
    
class LiteralStringValue(Expression):

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        value: str
    ) -> None:
        super().__init__(type_, scope, parent)
        self.value = value

    def infertype(self, supertype: IBoundType) -> IBoundType:
        return supertype.lower(BOUND_STRING_TYPE)


class ReferenceExpression(Expression):
    """References have the type of referenced variables."""

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        var: ScopeVar
    ) -> None:
        super().__init__(type_, scope, parent)
        self._var = var

    @property
    def name(self) -> str:
        return self._var.name
    
    def update_type(self, v: IBoundType) -> None:
        self._var.may_change(v)
        self.boundtype = self._var.type

    def refresh_type(self) -> None:
        self.boundtype = self._var.type

    def infertype(self, supertype: IBoundType) -> IBoundType:
        # variables just try to embed the supertype constraint, this is how we propagate type hints
        # down the AST
        self.update_type(supertype.lower(self._var.type))
        return self.boundtype


class BinaryOperator(enum.Enum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    MOD = enum.auto()
    EQ = enum.auto()
    NEQ = enum.auto()
    LT = enum.auto()
    LTE = enum.auto()
    GT = enum.auto()
    GTE = enum.auto()
    AND = enum.auto()
    OR = enum.auto()

    def __str__(self) -> str:
        return self.name

_RINHAOP_PARSE_DICT: t.Final[t.Dict[SyntaxBinaryOperator, BinaryOperator]] = {
    'Add': BinaryOperator.ADD,
    'Sub': BinaryOperator.SUB,
    'Mul': BinaryOperator.MUL,
    'Div': BinaryOperator.DIV,
    'Rem': BinaryOperator.MOD,
    'Lt': BinaryOperator.LT,
    'Lte': BinaryOperator.LTE,
    'Gt': BinaryOperator.GT,
    'Gte': BinaryOperator.GTE,
    'Eq': BinaryOperator.EQ,
    'Neq': BinaryOperator.NEQ,
    'And': BinaryOperator.AND,
    'Or': BinaryOperator.OR
}

class BinaryExpression(Expression):
    """Binary operations have well known type. They will be never UNDEFINED."""

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional[Expression],
        left: Expression,
        op: BinaryOperator,
        right: Expression
    ) -> None:
        super().__init__(type_, scope, parent)
        self.left: t.Final = left
        self.op: t.Final = op
        self.right: t.Final = right

    def infertype(self, supertype: IBoundType) -> IBoundType:
        match self.op:
            case BinaryOperator.ADD:
                return self._typecheck_add(supertype)
            case BinaryOperator.SUB | BinaryOperator.MUL | BinaryOperator.DIV | BinaryOperator.MOD:
                return self._typecheck_arithmetic(supertype)
            case BinaryOperator.LTE | BinaryOperator.LT | BinaryOperator.GT | BinaryOperator.GTE:
                return self._typecheck_comparison(supertype)
            case BinaryOperator.AND | BinaryOperator.OR:
                return self._typecheck_logical(supertype)
            case BinaryOperator.EQ:
                return self._typecheck_equals(supertype)
            case BinaryOperator.NEQ:
                return self._typecheck_not_equals(supertype)

    def _typecheck_add(self, supertype: IBoundType) -> IBoundType:
        left = self.left.infertype(BINOP_ADD_TYPES)
        right = self.right.infertype(BINOP_ADD_TYPES)
        if left.type == NativeType.INTEGER and right.type == NativeType.INTEGER:
            self.boundtype = BOUND_INTEGER_TYPE
        elif left.type == NativeType.STRING or right.type == NativeType.STRING:
            self.boundtype = BOUND_STRING_TYPE
        else:
            self.boundtype = BINOP_ADD_TYPES
        return supertype.lower(self.boundtype)

    def _typecheck_arithmetic(self, supertype: IBoundType) -> IBoundType:
        self.left.infertype(BOUND_INTEGER_TYPE)
        self.right.infertype(BOUND_INTEGER_TYPE)
        self.boundtype = BOUND_INTEGER_TYPE
        return supertype.lower(self.boundtype)
    
    def _typecheck_comparison(self, supertype: IBoundType) -> IBoundType:
        self.left.infertype(BOUND_INTEGER_TYPE)
        self.right.infertype(BOUND_INTEGER_TYPE)
        self.boundtype = BOUND_BOOLEAN_TYPE
        return supertype.lower(self.boundtype)

    def _typecheck_logical(self, supertype: IBoundType) -> IBoundType:
        self.left.infertype(BOUND_BOOLEAN_TYPE)
        self.right.infertype(BOUND_BOOLEAN_TYPE)
        self.boundtype = BOUND_BOOLEAN_TYPE
        return supertype.lower(self.boundtype)

    def _typecheck_equals(self, supertype: IBoundType) -> IBoundType:
        left = self.left.infertype(BINOP_EQUAL_TYPES)
        if left.type == NativeType.BOOLEAN:
            self.right.infertype(BOUND_BOOLEAN_TYPE)
        elif left.type == NativeType.INTEGER:
            self.right.infertype(BOUND_INTEGER_TYPE)
        elif left.type == NativeType.STRING:
            self.right.infertype(BOUND_STRING_TYPE)
        else:
            self.right.infertype(BINOP_EQUAL_TYPES)
        self.boundtype = BOUND_BOOLEAN_TYPE
        return supertype.lower(self.boundtype)
    
    def _typecheck_not_equals(self, supertype: IBoundType) -> IBoundType:
        left = self.left.infertype(BINOP_NOT_EQUAL_TYPES)
        if left.type == NativeType.BOOLEAN:
            self.right.infertype(BOUND_BOOLEAN_TYPE)
        elif left.type == NativeType.INTEGER:
            self.right.infertype(BOUND_INTEGER_TYPE)
        elif left.type == NativeType.STRING:
            self.right.infertype(BOUND_STRING_TYPE)
        else:
            self.right.infertype(BINOP_NOT_EQUAL_TYPES)
        self.boundtype = BOUND_BOOLEAN_TYPE
        return supertype.lower(self.boundtype)


class PrintExpression(Expression):
    """Print has the type of its argument"""

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        value: Expression
    ) -> None:
        super().__init__(type_, scope, parent)
        self.value: t.Final = value

    def infertype(self, supertype: IBoundType) -> IBoundType:
        return self.value.infertype(supertype)


class TupleExpression(Expression):
    """Tuple expressions always have the tuple type."""

    def __init__(
        self,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        first: Expression,
        second: Expression
    ) -> None:
        if type_.type != NativeType.TUPLE:
            raise TypeError(f"expected NativeType.TUPLE type for tuple expression, but got {type_}")
        super().__init__(type_, scope, parent)
        self.first: t.Final = first
        self.second: t.Final = second

    def infertype(self, supertype: IBoundType) -> IBoundType:
        supertuple = supertype.lower(BOUND_TUPLE_TYPE)
        if supertuple.type == NativeType.TUPLE:
            self.boundtype = BoundType(
                NativeType.TUPLE,
                (
                    self.first.infertype(supertuple.generics[0]),
                    self.second.infertype(supertuple.generics[1])
                )
            )
            return self.boundtype
        self.boundtype = BOUND_TUPLE_TYPE
        return BOUND_UNDEFINED_TYPE

class FirstExpression(Expression):
    """First takes tuples as argument and return their first member"""

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        value: Expression
    ) -> None:
        super().__init__(type_, scope, parent)
        self.value: t.Final = value

    def infertype(self, supertype: IBoundType) -> IBoundType:
        signature = self.value.infertype(BoundType(NativeType.TUPLE, (supertype, BOUND_ANY_TYPE)))
        if signature.type == NativeType.TUPLE:
            self.boundtype = signature.generics[0]
            return signature.generics[0]
        self.boundtype = BOUND_UNDEFINED_TYPE
        return BOUND_UNDEFINED_TYPE

class SecondExpression(Expression):
    """Second takes tuples as argument and return their second member"""

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        value: Expression
    ) -> None:
        super().__init__(type_, scope, parent)
        self.value: t.Final = value

    def infertype(self, supertype: IBoundType) -> IBoundType:
        signature = self.value.infertype(BoundType(NativeType.TUPLE, (BOUND_ANY_TYPE, supertype)))
        if signature.type == NativeType.TUPLE:
            self.boundtype = signature.generics[1]
            return signature.generics[1]
        self.boundtype = BOUND_UNDEFINED_TYPE
        return BOUND_UNDEFINED_TYPE


class ConditionalExpression(Expression):
    """Conditional expressions have the intersection of both branches type as their type"""

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        cond: Expression,
        then: Expression,
        alternate: Expression,
    ) -> None:
        super().__init__(type_, scope, parent)
        self.cond: t.Final = cond
        self.then: t.Final = then
        self.alternate: t.Final = alternate

    def infertype(self, supertype: IBoundType) -> IBoundType:
        cond = self.cond.infertype(BOUND_BOOLEAN_TYPE)
        if cond.type != NativeType.BOOLEAN:
            raise TypeError("conditional expressions must have a boolean as test")
        then = self.then.infertype(supertype)
        if self.parent is not None:
            self.parent.handle_partial_inference(then)
        alternate = self.alternate.infertype(supertype)
        self.boundtype = then.lower(alternate)
        return self.boundtype
    
    def handle_partial_inference(self, type_: IBoundType) -> None:
        if self.parent is not None:
            return self.parent.handle_partial_inference(type_)


class CallExpression(Expression):
    """Calls have the type of the called function's return"""
    
    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        callee: Expression,
        args: t.List[Expression]
    ) -> None:
        super().__init__(type_, scope, parent)
        self.callee: t.Final = callee
        self.args: t.Final = args

    def infertype(self, supertype: IBoundType) -> IBoundType:
        # we propagate back the type hints from the function signature to the caller arguments
        # then feed it back to the function signature
        if self.callee.boundtype.type == NativeType.FUNCTION:
            callee_type = t.cast(BoundFunctionType, self.callee.boundtype)
            signature = self.callee.infertype(BoundFunctionType(
                tuple(arg.infertype(callee_type.params[i]) for i, arg in enumerate(self.args)),
                supertype
            ))
        else:
            signature = self.callee.infertype(BoundFunctionType(
                tuple(arg.infertype(BOUND_ANY_TYPE) for arg in self.args),
                supertype
            ))
        if signature.type == NativeType.FUNCTION:
            signature = t.cast(BoundFunctionType, signature)
            self.boundtype = signature.return_type
            return signature.return_type
        self.boundtype = signature
        return signature


class FunctionExpression(Expression):

    def __init__(
        self,
        *,
        type_: BoundFunctionType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        params: t.List[ReferenceExpression],
        body: Expression,
        binding: t.Optional[ReferenceExpression] = None,
    ) -> None:
        super().__init__(type_, scope, parent)
        self.binding: t.Final = binding
        self.params: t.Final = params
        self.body: t.Final = body

    def infertype(self, supertype: IBoundType) -> IBoundType:
        lowered_signature = supertype.lower(self.boundtype)
        if lowered_signature.type == NativeType.FUNCTION:
            lowered_signature = t.cast(BoundFunctionType, lowered_signature)
            param_types = lowered_signature.params
            for i, param in enumerate(self.params):
                param.infertype(param_types[i])
            return_type = self.body.infertype(lowered_signature.return_type)
            if return_type.lowers(lowered_signature.return_type):
                self.boundtype = BoundFunctionType(
                    tuple(param.boundtype for param in self.params),
                    return_type
                )
            else:
                self.boundtype = BoundFunctionType(
                    tuple(param.boundtype for param in self.params),
                    lowered_signature.return_type
                )
            return self.boundtype
        return lowered_signature

    def handle_partial_inference(self, type_: IBoundType) -> None:
        boundtype = t.cast(BoundFunctionType, self.boundtype)
        if self.binding is not None and type_.lowers(boundtype.return_type):
            self.binding.infertype(BoundFunctionType(boundtype.params, type_))

    def __str__(self) -> str:
        if self.binding is not None:
            return f'{self.binding.name}()'
        return f'<#closure>()'


class LetExpression(Expression):

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        binding: t.Optional[ReferenceExpression],
        value: Expression,
        next: Expression
    ) -> None:
        super().__init__(type_, scope, parent)
        self.binding: t.Final = binding
        self.value: t.Final = value
        self.next: t.Final = next

    def infertype(self, supertype: IBoundType) -> IBoundType:
        # we feed the actual binding's type as supertype of the next type checking round
        # then feed the new type back to the binding itself
        if self.binding is not None:
            self.binding.refresh_type()
            self.binding.infertype(self.value.infertype(self.binding.boundtype))
        else:
            self.value.infertype(BOUND_ANY_TYPE)
        # supertype is the expected type of the next expression
        next_ = self.next.infertype(supertype)
        self.boundtype = next_
        return next_
    
    def handle_partial_inference(self, type_: IBoundType) -> None:
        if self.parent is not None:
            return self.parent.handle_partial_inference(type_)


class Program:

    def __init__(self, filename: str, body: Expression) -> None:
        self.filename = filename
        self.body = body


def typecheck(syntax: SyntaxTerm) -> Expression:
    globalscope = TypeScope(None)
    allvars: t.List[ScopeVar] = []
    ast = build_typed_ast(syntax, None, globalscope, allvars)
    varschanged = False
    while True:
        ast.infertype(BOUND_ANY_TYPE)
        for var in allvars:
            if var.changed:
                varschanged = True
                var.changed = False
        if not varschanged:
            return ast
        varschanged = False


def build_typed_ast(
    term: SyntaxTerm,
    parent: t.Optional[Expression],
    scope: TypeScope,
    vars: t.List[ScopeVar],
    **childargs: t.Any
) -> Expression:
    match term['kind']:
        case 'Var':
            term = t.cast(IdentifierSyntax, term)
            try:
                var = scope.get(term['text'])
            except ValueError as e:
                raise ValueError(f"{e.args[0]} at {term['location']}") from e
            return ReferenceExpression(
                type_=var.type,
                scope=scope,
                parent=parent,
                var=var
            )
        case 'Int':
            term = t.cast(LiteralSyntax, term)
            value = t.cast(int, term['value'])
            return LiteralIntegerValue(type_=BOUND_INTEGER_TYPE, scope=scope, parent=parent, value=value)
        case 'Str':
            term = t.cast(LiteralSyntax, term)
            value2 = t.cast(str, term['value'])
            return LiteralStringValue(type_=BOUND_STRING_TYPE, scope=scope, parent=parent, value=value2)
        case 'Bool':
            term = t.cast(LiteralBooleanSyntax, term)
            return LiteralBooleanValue(type_=BOUND_BOOLEAN_TYPE, scope=scope, parent=parent, value=term['value'])
        case 'Tuple':
            term = t.cast(TupleSyntax, term)
            first = build_typed_ast(term['first'], None, scope, vars)
            second = build_typed_ast(term['second'], None, scope, vars)
            tuple_ = TupleExpression(
                type_=BoundType(NativeType.TUPLE, (first.boundtype, second.boundtype)),
                scope=scope,
                parent=parent,
                first=first,
                second=second
            )
            first.parent = tuple_
            second.parent = tuple_
            return tuple_
        case 'Call':
            term = t.cast(CallExpressionSyntax, term)
            callee = build_typed_ast(term['callee'], None, scope, vars)
            args = [
                build_typed_ast(arg, None, scope, vars)
                for arg in term['arguments']
            ]
            call = CallExpression(
                type_=BOUND_ANY_TYPE,
                scope=scope,
                parent=parent,
                callee=callee,
                args=args
            )
            callee.parent = call
            for arg in args:
                arg.parent = call
            return call
        case 'Print':
            term = t.cast(PrintSyntax, term)
            value3 = build_typed_ast(term['value'], None, scope, vars)
            theprint = PrintExpression(
                type_=BOUND_ANY_TYPE,
                scope=scope,
                parent=parent,
                value=value3
            )
            value3.parent = theprint
            return theprint
        case 'First':
            term = t.cast(FirstSyntax, term)
            value4 = build_typed_ast(term['value'], None, scope, vars)
            first = FirstExpression(
                type_=BOUND_ANY_TYPE,
                scope=scope,
                parent=parent,
                value=value4
            )
            value4.parent = first
            return first
        case 'Second':
            term = t.cast(SecondSyntax, term)
            value4 = build_typed_ast(term['value'], None, scope, vars)
            second = SecondExpression(
                type_=BOUND_ANY_TYPE,
                scope=scope,
                parent=parent,
                value=value4
            )
            value4.parent = second
            return second
        case 'Binary':
            term = t.cast(BinaryExpressionSyntax, term)
            left = build_typed_ast(term['lhs'], None, scope, vars)
            right = build_typed_ast(term['rhs'], None, scope, vars)
            exp = BinaryExpression(
                type_=BOUND_ANY_TYPE,
                scope=scope,
                parent=parent,
                left=left,
                op=_RINHAOP_PARSE_DICT[term['op']],
                right=right
            )
            left.parent = exp
            right.parent = exp
            return exp
        case 'If':
            term = t.cast(ConditionalExpressionSyntax, term)
            cond = build_typed_ast(term['condition'], None, scope, vars)
            # branches create new variable scope
            then = build_typed_ast(term['then'], None, TypeScope(scope), vars)
            alternate = build_typed_ast(term['otherwise'], None, TypeScope(scope), vars)
            exp2 = ConditionalExpression(
                type_=BOUND_ANY_TYPE,
                scope=scope,
                parent=parent,
                cond=cond,
                then=then,
                alternate=alternate
            )
            cond.parent = exp2
            then.parent = exp2
            alternate.parent = exp2
            return exp2
        case 'Function':
            term = t.cast(FunctionExpressionSyntax, term)
            funcscope = TypeScope(scope)
            params = [
                funcscope.declare(param['text'], BOUND_ANY_TYPE)
                for param in term['parameters']
            ]
            body = build_typed_ast(term['value'], None, funcscope, vars)
            func = FunctionExpression(
                type_=BoundFunctionType(tuple(param.type for param in params), BOUND_ANY_TYPE),
                scope=funcscope,
                parent=parent,
                params=[
                    ReferenceExpression(
                        type_=param.type,
                        scope=funcscope,
                        parent=None,
                        var=param
                    )
                    for param in params
                ],
                body=body,
                **childargs
            )
            body.parent = func
            vars.extend(params)
            return func
        case 'Let':
            term = t.cast(LetExpressionSyntax, term)
            if term['name']['text'] != '_' and term['value']['kind'] == 'Function':
                var = scope.declare(term['name']['text'], BOUND_ANY_TYPE)
                binding = ReferenceExpression(
                    type_=var.type,
                    scope=scope,
                    parent=None,
                    var=var
                )
                value5 = build_typed_ast(term['value'], None, scope, vars, binding=binding)
                binding.update_type(value5.boundtype)
                vars.append(var)
            else:
                value5 = build_typed_ast(term['value'], None, scope, vars)
                if term['name']['text'] != '_':
                    var = scope.declare(term['name']['text'], value5.boundtype)
                    binding = ReferenceExpression(
                        type_=var.type,
                        scope=scope,
                        parent=None,
                        var=var
                    )
                    vars.append(var)
                else:
                    binding = None
            next_ = build_typed_ast(term['next'], parent, scope, vars)
            exp3 = LetExpression(
                type_=BOUND_ANY_TYPE,
                scope=scope,
                parent=parent,
                binding=binding,
                value=value5,
                next=next_
            )
            value5.parent = exp3
            return exp3
        case _:
            raise ValueError(f"Unknown syntax term '{term['kind']}' at {term['location']}")
