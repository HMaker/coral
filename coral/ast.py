import enum
import typing as t
from coral import parser


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
        """Returns the union intersection of this type with the given one.
        
        Intersection with ANY results in the other set.
        Intersection with UNDEFINED results in UNDEFINED.
        """
        raise NotImplementedError
    
    def issupertype(self, other: 'IBoundType') -> bool:
        """Checks wether this type is a super type of the given one.
        
        If a type union includes a super type of the given type, then that union is also a
        supertype of the given type. ANY is the supertype of every type. A type is supertype of itself.
        """
        raise NotImplementedError
    
    def __eq__(self, __value: object) -> bool:
        raise NotImplementedError
    
    def __hash__(self) -> int:
        raise NotImplementedError

class BoundType(IBoundType):

    def __init__(self, type_: NativeType, generics: t.Sequence[IBoundType]) -> None:
        self._native_type: t.Final = type_
        self._generics: t.Final = generics
        self._is_static: t.Final = type_  != NativeType.ANY and type != NativeType.UNDEFINED and all(arg.is_static for arg in generics)
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
        if other.type == NativeType.UNION:
            return other.lower(self)
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

    def issupertype(self, other: IBoundType) -> bool:
        if self._native_type == NativeType.UNDEFINED or other.type == NativeType.UNDEFINED:
            return False
        if self._native_type == NativeType.ANY:
            return True
        if self._native_type != other.type:
            return False
        other = t.cast(BoundType, other)
        other_generics = other.generics
        if len(self._generics) != len(other_generics):
            return False
        return all(my_generic.issupertype(other_generics[i]) for i, my_generic in enumerate(self._generics))
    
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

    def issupertype(self, other: IBoundType) -> bool:
        if other.type == NativeType.ANY or other.type == NativeType.UNDEFINED:
            return False
        if other.type == NativeType.UNION:
            other = t.cast(BoundTypeUnion, other)
            for other_member in other.members.values():
                my_member = self._members.get(other_member.type, None)
                if my_member is None or not my_member.issupertype(other_member):
                    return False
            return True
        else:
            my_member = self._members.get(other.type, None)
            if my_member is None:
                return False
            return my_member.issupertype(other)

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
        if other.type == NativeType.UNION:
            return other.lower(self)
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

    def issupertype(self, other: IBoundType) -> bool:
        if other.type != NativeType.FUNCTION:
            return False
        other = t.cast(BoundFunctionType, other)
        other_params = other.params
        return (
            len(self._params) == len(other.params) and
            self._return_type.issupertype(other.return_type) and
            all(my_param.issupertype(other_params[i]) for i, my_param in enumerate(self._params))
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
        self.name = name
        self.index = index
        self.changed: bool = False

    def may_change(self, newtype: IBoundType) -> None:
        if newtype != self.type:
            self.type = newtype
            self.changed = True

    def __eq__(self, o: object) -> bool:
        return isinstance(o, ScopeVar) and o.name == self.name
    
    def __hash__(self) -> int:
        return hash(self.name)

class ScopeCapture:
    """Functions may capture names from the parent scope, this is a capture record."""
    __slots__ = ('var', 'parent')

    def __init__(self, var: ScopeVar, parent: int) -> None:
        self.var = var
        """The captured name"""
        self.parent = parent
        """The parent scope position in the hierarchy from the child to the parent"""

    def __eq__(self, o: object) -> bool:
        return isinstance(o, ScopeCapture) and self.parent == o.parent and self.var == o.var

    def __hash__(self) -> int:
        return hash(self.var)

class TypeScope:

    def __init__(self, parent: t.Optional['TypeScope']) -> None:
        self.parent = parent
        self.locals: t.Dict[str, ScopeVar] = {}
        self.nonlocals: t.Dict[str, ScopeCapture] = {}
    
    def declare(self, name: str, type_: IBoundType) -> ScopeVar:
        """Declares a new var with the given name.
        
        Raises SyntaxError if it's already declare.
        """
        if name in self.locals:
            raise SyntaxError(f"Identifier '{name}' has already been declared")
        var = ScopeVar(type_, name, len(self.locals))
        self.locals[name] = var
        return var

    def ref(self, name: str) -> ScopeVar:
        """Marks a reference to the given name and returns its var.
        
        If this name is not defined in the actual scope, it will be looked up in the parent scope
        and the name will the stored in the "nonlocals" dict.
        """
        if name in self.locals:
            return self.locals[name]
        if name in self.nonlocals:
            return self.nonlocals[name].var
        var, pos = self.reflookup(name)
        self.nonlocals[var.name] = ScopeCapture(var, pos)
        return var
    
    def reflookup(self, name: str, pos: int=0) -> t.Tuple[ScopeVar, int]:
        if name in self.locals:
            return self.locals[name], pos
        if self.parent is not None:
            return self.parent.reflookup(name, pos + 1)
        raise ValueError(f'{name} is not defined')
    
    def get(self, name: str) -> t.Optional[ScopeVar]:
        """Retrieve the var for the given name."""
        if name in self.locals:
            return self.locals[name]
        if self.parent is not None:
            return self.parent.get(name)
        return None


class Expression:
    """Root node of the typed AST."""

    def __init__(self, type_: IBoundType, scope: TypeScope, parent: t.Optional['Expression']=None) -> None:
        self.boundtype: IBoundType = type_
        self.parent = parent
        self._scope: t.Final = scope

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        """Performs a type checking round.
        
        The "supertype" is a constraint over the type checking result. Either it is a sub type
        of the given type or UNDEFINED. The result is returned.
        """
        raise NotImplementedError


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

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        return BOUND_BOOLEAN_TYPE.lower(supertype)
    
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

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        return BOUND_INTEGER_TYPE.lower(supertype)
    
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

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        return BOUND_STRING_TYPE.lower(supertype)


class ReferenceExpression(Expression):

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        var: ScopeVar
    ) -> None:
        self._var = var
        super().__init__(type_, scope, parent)

    @property
    def boundtype(self) -> IBoundType:
        return self._var.type

    @boundtype.setter
    def boundtype(self, v: IBoundType) -> None:
        self._var.may_change(v)

    @property
    def name(self) -> str:
        return self._var.name

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        # variables just try to embed the supertype constraint, this is how we propagate type hints
        # down the AST
        self._var.may_change(self._var.type.lower(supertype))
        return self._var.type


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
    
_RINHAOP_PARSE_DICT: t.Final['t.Dict[parser.BinaryOperator, BinaryOperator]'] = {
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
        self._left = left
        self._op = op
        self._right = right

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        match self._op:
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
        left = self._left.typecheck(BINOP_ADD_TYPES)
        right = self._right.typecheck(BINOP_ADD_TYPES)
        addop = BINOP_ADD_TYPES.lower(supertype)
        if (
            addop == NativeType.UNDEFINED or
            left.type == NativeType.UNDEFINED or
            left.type == NativeType.UNION or
            right.type == NativeType.UNDEFINED or
            right.type == NativeType.UNION
        ):
            self.boundtype = BINOP_ADD_TYPES
            return addop
        if left.type == NativeType.INTEGER and right.type == NativeType.INTEGER:
            self.boundtype = BOUND_INTEGER_TYPE
            return self.boundtype
        if left.type == NativeType.STRING or right.type == NativeType.STRING:
            self.boundtype = BOUND_STRING_TYPE
            return self.boundtype
        raise RuntimeError('it should be int or string!')

    def _typecheck_arithmetic(self, supertype: IBoundType) -> IBoundType:
        left = self._left.typecheck(BOUND_INTEGER_TYPE)
        right = self._right.typecheck(BOUND_INTEGER_TYPE)
        intop = BOUND_INTEGER_TYPE.lower(supertype)
        if intop == NativeType.UNDEFINED or left.type == NativeType.UNDEFINED or right.type == NativeType.UNDEFINED:
            self.boundtype = BOUND_INTEGER_TYPE
            return intop
        self.boundtype = intop
        return intop
    
    def _typecheck_comparison(self, supertype: IBoundType) -> IBoundType:
        left = self._left.typecheck(BOUND_INTEGER_TYPE)
        right = self._right.typecheck(BOUND_INTEGER_TYPE)
        compop = BOUND_BOOLEAN_TYPE.lower(supertype)
        if compop == NativeType.UNDEFINED or left.type == NativeType.UNDEFINED or right.type == NativeType.UNDEFINED:
            self.boundtype = BOUND_BOOLEAN_TYPE
            return compop
        self.boundtype = compop
        return compop

    def _typecheck_logical(self, supertype: IBoundType) -> IBoundType:
        left = self._left.typecheck(BOUND_BOOLEAN_TYPE)
        right = self._right.typecheck(BOUND_BOOLEAN_TYPE)
        boolop = BOUND_BOOLEAN_TYPE.lower(supertype)
        if boolop == NativeType.UNDEFINED or left.type == NativeType.UNDEFINED or right.type == NativeType.UNDEFINED:
            self.boundtype = BOUND_BOOLEAN_TYPE
            return boolop
        self.boundtype = boolop
        return boolop

    def _typecheck_equals(self, supertype: IBoundType) -> IBoundType:
        left = self._left.typecheck(BINOP_EQUAL_TYPES)
        right = self._right.typecheck(BINOP_EQUAL_TYPES)
        equalsop = BOUND_BOOLEAN_TYPE.lower(supertype)
        if equalsop == NativeType.UNDEFINED or left.type == NativeType.UNDEFINED or right.type == NativeType.UNDEFINED:
            self.boundtype = BOUND_BOOLEAN_TYPE
            return equalsop
        self.boundtype = equalsop
        return equalsop
    
    def _typecheck_not_equals(self, supertype: IBoundType) -> IBoundType:
        left = self._left.typecheck(BINOP_NOT_EQUAL_TYPES)
        right = self._right.typecheck(BINOP_NOT_EQUAL_TYPES)
        not_equalsop = BOUND_BOOLEAN_TYPE.lower(supertype)
        if not_equalsop == NativeType.UNDEFINED or left.type == NativeType.UNDEFINED or right.type == NativeType.UNDEFINED:
            self.boundtype = BOUND_BOOLEAN_TYPE
            return not_equalsop
        self.boundtype = not_equalsop
        return not_equalsop

class CallExpression(Expression):
    
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
        self._callee = callee
        self._args = args

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        # supertype is the expected call return type
        # we update the called function signature using the call args and the expected return
        signature = self._callee.typecheck(BoundFunctionType(
            tuple(arg.typecheck(BOUND_ANY_TYPE) for arg in self._args),
            supertype
        ))
        if signature.type == NativeType.FUNCTION:
            signature = t.cast(BoundFunctionType, signature)
            self.boundtype = signature.return_type
            return signature.return_type
        return signature

class PrintExpression(Expression):

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        value: Expression
    ) -> None:
        super().__init__(type_, scope, parent)
        self._value = value

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        # print returns the argument
        return self._value.typecheck(supertype)


class TupleExpression(Expression):

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
        self._first = first
        self._second = second

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        supertuple = BOUND_TUPLE_TYPE.lower(supertype)
        if supertuple.type == NativeType.TUPLE:
            return BoundType(
                NativeType.TUPLE,
                (
                    self._first.typecheck(supertuple.generics[0]),
                    self._second.typecheck(supertuple.generics[1])
                )
            )
        return supertuple

class FirstExpression(Expression):

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        value: Expression
    ) -> None:
        super().__init__(type_, scope, parent)
        self._value = value

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        # supertype is the expected type of the first member
        signature = self._value.typecheck(BoundType(NativeType.TUPLE, (supertype, BOUND_ANY_TYPE)))
        if signature.type == NativeType.TUPLE:
            self.boundtype = signature.generics[0]
            return signature.generics[0]
        self.boundtype = BOUND_UNDEFINED_TYPE
        return BOUND_UNDEFINED_TYPE

class SecondExpression(Expression):

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        value: Expression
    ) -> None:
        super().__init__(type_, scope, parent)
        self._value = value

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        # supertype is the expected type of the second member
        signature = self._value.typecheck(BoundType(NativeType.TUPLE, (BOUND_ANY_TYPE, supertype)))
        if signature.type == NativeType.TUPLE:
            self.boundtype = signature.generics[1]
            return signature.generics[1]
        self.boundtype = BOUND_UNDEFINED_TYPE
        return BOUND_UNDEFINED_TYPE


class ConditionalExpression(Expression):

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
        self._cond = cond
        self._then = then
        self._alternate = alternate

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        # condition must be boolean
        cond = self._cond.typecheck(BOUND_BOOLEAN_TYPE)
        if cond.type != NativeType.BOOLEAN:
            raise TypeError("conditional expressions must have a boolean as test")
        # here we try to infer the "return" statement of a function from each side of the IF
        # branch. since rinha has no explicitly keyword for returns we must do this
        # "lookbehind" workaround
        then = self._then.typecheck(supertype)
        if self.parent is not None and self.parent.boundtype.type == NativeType.FUNCTION:
            parent = t.cast(FunctionExpression, self.parent)
            parent.typecheck_return(then)
        alternate = self._alternate.typecheck(supertype)
        if self.parent is not None and self.parent.boundtype.type == NativeType.FUNCTION:
            parent = t.cast(FunctionExpression, self.parent)
            parent.typecheck_return(alternate)
        self.boundtype = then.union(alternate)
        return self.boundtype


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
        self._binding: t.Final = binding
        self._params: t.Final = params
        self._body: t.Final = body
        self.boundtype: BoundFunctionType

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        lowered_signature = self.boundtype.lower(supertype)
        if lowered_signature.type == NativeType.FUNCTION:
            lowered_signature = t.cast(BoundFunctionType, lowered_signature)
            param_types = lowered_signature.params
            for i, param in enumerate(self._params):
                param.typecheck(param_types[i])
            return_type = self._body.typecheck(lowered_signature.return_type)
            new_signature = BoundFunctionType(
                tuple(param.boundtype for param in self._params),
                return_type
            )
            lowered_signature2 = new_signature.lower(supertype)
            if lowered_signature2.type == NativeType.FUNCTION:
                lowered_signature2 = t.cast(BoundFunctionType, lowered_signature2)
                self.boundtype = lowered_signature2
            return lowered_signature2
        return lowered_signature

    def typecheck_return(self, type_: IBoundType) -> IBoundType:
        lowered_signature = self.boundtype.lower(BoundFunctionType(self.boundtype.params, type_))
        if lowered_signature.type == NativeType.FUNCTION:
            lowered_signature = t.cast(BoundFunctionType, lowered_signature)
            if self._binding is not None:
                self._binding.typecheck(lowered_signature)
            return lowered_signature.return_type
        return lowered_signature

    def __str__(self) -> str:
        if self._binding is not None:
            return f'{self._binding.name}()'
        return f'<#closure>()'


class LetExpression(Expression):

    def __init__(
        self,
        *,
        type_: IBoundType,
        scope: TypeScope,
        parent: t.Optional['Expression'],
        binding: ReferenceExpression,
        value: Expression,
        next: Expression
    ) -> None:
        super().__init__(type_, scope, parent)
        self._binding = binding
        self._value = value
        self._next = next

    def typecheck(self, supertype: IBoundType) -> IBoundType:
        # we feed the actual binding's type as supertype of the next type checking round
        # then feed the new type back to the binding itself
        self._binding.typecheck(self._value.typecheck(self._binding.boundtype))
        # supertype is the expected type of the next expression
        next_ = self._next.typecheck(supertype)
        self.boundtype = next_
        return next_


class Program:

    def __init__(self, filename: str, body: Expression) -> None:
        self.filename = filename
        self.body = body


def typecheck(syntax: parser.SyntaxTerm) -> Expression:
    globalscope = TypeScope(None)
    allvars: t.List[ScopeVar] = []
    ast = build_typed_ast(syntax, None, globalscope, allvars)
    varschanged = False
    while True:
        ast.typecheck(BOUND_ANY_TYPE)
        for var in allvars:
            if var.changed:
                varschanged = True
                var.changed = False
        if not varschanged:
            return ast
        varschanged = False


def build_typed_ast(
    term: parser.SyntaxTerm,
    parent: t.Optional[Expression],
    scope: TypeScope,
    vars: t.List[ScopeVar],
    **childargs: t.Any
) -> Expression:
    match term['kind']:
        case 'Var':
            term = t.cast(parser.IdentifierSyntax, term)
            try:
                var = scope.ref(term['text'])
            except ValueError as e:
                raise ValueError(f"{e.args[0]} at {term['location']}") from e
            return ReferenceExpression(
                type_=var.type,
                scope=scope,
                parent=parent,
                var=var
            )
        case 'Int':
            term = t.cast(parser.LiteralSyntax, term)
            value = t.cast(int, term['value'])
            return LiteralIntegerValue(type_=BOUND_INTEGER_TYPE, scope=scope, parent=parent, value=value)
        case 'Str':
            term = t.cast(parser.LiteralSyntax, term)
            value2 = t.cast(str, term['value'])
            return LiteralStringValue(type_=BOUND_STRING_TYPE, scope=scope, parent=parent, value=value2)
        case 'Bool':
            term = t.cast(parser.LiteralBooleanSyntax, term)
            return LiteralBooleanValue(type_=BOUND_BOOLEAN_TYPE, scope=scope, parent=parent, value=term['value'])
        case 'Tuple':
            term = t.cast(parser.TupleSyntax, term)
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
            term = t.cast(parser.CallExpressionSyntax, term)
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
            term = t.cast(parser.PrintSyntax, term)
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
            term = t.cast(parser.FirstSyntax, term)
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
            term = t.cast(parser.SecondSyntax, term)
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
            term = t.cast(parser.BinaryExpressionSyntax, term)
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
            term = t.cast(parser.ConditionalExpressionSyntax, term)
            cond = build_typed_ast(term['condition'], None, scope, vars)
            then = build_typed_ast(term['then'], None, scope, vars)
            alternate = build_typed_ast(term['otherwise'], None, scope, vars)
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
            term = t.cast(parser.FunctionExpressionSyntax, term)
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
            term = t.cast(parser.LetExpressionSyntax, term)
            var = scope.declare(term['name']['text'], BOUND_ANY_TYPE)
            binding = ReferenceExpression(
                type_=var.type,
                scope=scope,
                parent=None,
                var=var
            )
            vars.append(var)
            value5 = build_typed_ast(term['value'], None, scope, vars, binding=binding)
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