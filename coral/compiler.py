import typing as t
import ctypes as c
import importlib.resources
from llvmlite import ir, binding as llvm # type: ignore
from coral import ast


llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()
with importlib.resources.as_file(
    importlib.resources.files('coral').joinpath('runtime.so')
) as runtimelib:
    llvm.load_library_permanently(str(runtimelib))


LL_BOOL = ir.IntType(1)
LL_CHAR = ir.IntType(8)
LL_INT = ir.IntType(64)


class CoralRuntime:

    def __init__(
        self,
        *,
        crvalue_struct: ir.Type,
        crvalue_incref: ir.Function,
        crvalue_decref: ir.Function,
        crvalue_print: ir.Function,

        crvalue_add: ir.Function,
        crvalue_sub: ir.Function,
        crvalue_mul: ir.Function,
        crvalue_div: ir.Function,
        crvalue_mod: ir.Function,
        crvalue_lt: ir.Function,
        crvalue_lte: ir.Function,
        crvalue_gt: ir.Function,
        crvalue_gte: ir.Function,
        crvalue_equals: ir.Function,
        crvalue_notequals: ir.Function,
        crvalue_and: ir.Function,
        crvalue_or: ir.Function,

        crstring_new: ir.Function,
        crvalue_as_string: ir.Function,

        crtuple_new: ir.Function,
        crtuple_get_first: ir.Function,
        crtuple_get_second: ir.Function
    ) -> None:
        self.crvalue_struct: t.Final = crvalue_struct
        self.crvalue_incref: t.Final = crvalue_incref
        self.crvalue_decref: t.Final = crvalue_decref
        self.crvalue_print: t.Final = crvalue_print

        self.crvalue_add: t.Final = crvalue_add
        self.crvalue_sub: t.Final = crvalue_sub
        self.crvalue_mul: t.Final = crvalue_mul
        self.crvalue_div: t.Final = crvalue_div
        self.crvalue_mod: t.Final = crvalue_mod
        self.crvalue_lt: t.Final = crvalue_lt
        self.crvalue_lte: t.Final = crvalue_lte
        self.crvalue_gt: t.Final = crvalue_gt
        self.crvalue_gte: t.Final = crvalue_gte
        self.crvalue_equals: t.Final = crvalue_equals
        self.crvalue_notequals: t.Final = crvalue_notequals
        self.crvalue_and: t.Final = crvalue_and
        self.crvalue_or: t.Final = crvalue_or

        self.crstring_new: t.Final = crstring_new
        self.crvalue_as_string: t.Final = crvalue_as_string

        self.crtuple_new: t.Final = crtuple_new
        self.crtuple_get_first: t.Final = crtuple_get_first
        self.crtuple_get_second: t.Final = crtuple_get_second

    @classmethod
    def import_into(cls, mod: ir.Module) -> 'CoralRuntime':
        # see runtime/runtime.h

        # crvalue_struct = ir.LiteralStructType((
        #     LL_INT,                         # CRType type
        #     LL_INT,                         # uint32_t refCount
        #     LL_CHAR.as_pointer(),           # void* value
        #     ir.PointerType(                 # *valueDestructor
        #         ir.FunctionType(            # ... points to a function
        #             ir.VoidType(),          # ... which returns void
        #             [LL_CHAR.as_pointer()]  # ... which takes void* as first argument
        #         )
        #     )
        # ))
        crvalue_struct = LL_CHAR
        crvalue_struct_ptr = crvalue_struct.as_pointer()

        crvalue_incref = ir.Function(
            name='CRValue_incref',
            module=mod,
            ftype=ir.FunctionType(
                return_type=ir.VoidType(),
                args=[crvalue_struct_ptr]
            )
        )
        crvalue_decref = ir.Function(
            name='CRValue_decref',
            module=mod,
            ftype=ir.FunctionType(
                return_type=ir.VoidType(),
                args=[crvalue_struct_ptr.as_pointer()]
            )
        )

        crvalue_binary_operator_func = ir.FunctionType(
            return_type=crvalue_struct_ptr,
            args=[crvalue_struct_ptr, crvalue_struct_ptr]
        )
        crvalue_add = ir.Function(
            name='CRValue_add',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_sub = ir.Function(
            name='CRValue_sub',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_mul = ir.Function(
            name='CRValue_mul',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_div = ir.Function(
            name='CRValue_div',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_mod = ir.Function(
            name='CRValue_mod',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_lt = ir.Function(
            name='CRValue_lessThan',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_lte = ir.Function(
            name='CRValue_lessOrEqual',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_gt = ir.Function(
            name='CRValue_greaterThan',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_gte = ir.Function(
            name='CRValue_greaterOrEqual',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_and = ir.Function(
            name='CRValue_and',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_or = ir.Function(
            name='CRValue_or',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_equals = ir.Function(
            name='CRValue_equals',
            module=mod,
            ftype=crvalue_binary_operator_func
        )
        crvalue_notequals = ir.Function(
            name='CRValue_notEquals',
            module=mod,
            ftype=crvalue_binary_operator_func
        )

        crstring_new = ir.Function(
            name='CRString_new',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crvalue_struct_ptr,
                args=[LL_CHAR.as_pointer(), LL_INT]
            )
        )
        crvalue_as_string = ir.Function(
            name='CRValue_asString',
            module=mod,
            ftype=ir.FunctionType(
                return_type=LL_CHAR.as_pointer(),
                args=[crvalue_struct_ptr]
            )
        )

        crvalue_print = ir.Function(
            name='CRValue_print',
            module=mod,
            ftype=ir.FunctionType(
                return_type=ir.VoidType(),
                args=[crvalue_struct_ptr]
            )
        )

        crtuple_new = ir.Function(
            name='CRTuple_new',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crvalue_struct_ptr,
                args=[crvalue_struct_ptr, crvalue_struct_ptr]
            )
        )
        crtuple_get_first = ir.Function(
            name='CRTuple_getFirst',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crvalue_struct_ptr,
                args=[crvalue_struct_ptr]
            )
        )
        crtuple_get_second = ir.Function(
            name='CRTuple_getSecond',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crvalue_struct_ptr,
                args=[crvalue_struct_ptr]
            )
        )
        return CoralRuntime(
            crvalue_struct=crvalue_struct,
            crvalue_incref=crvalue_incref,
            crvalue_decref=crvalue_decref,

            crvalue_add=crvalue_add,
            crvalue_sub=crvalue_sub,
            crvalue_mul=crvalue_mul,
            crvalue_div=crvalue_div,
            crvalue_mod=crvalue_mod,
            crvalue_lt=crvalue_lt,
            crvalue_lte=crvalue_lte,
            crvalue_gt=crvalue_gt,
            crvalue_gte=crvalue_gte,
            crvalue_equals=crvalue_equals,
            crvalue_notequals=crvalue_notequals,
            crvalue_and=crvalue_and,
            crvalue_or=crvalue_or,

            crvalue_print=crvalue_print,

            crstring_new=crstring_new,
            crvalue_as_string=crvalue_as_string,

            crtuple_new=crtuple_new,
            crtuple_get_first=crtuple_get_first,
            crtuple_get_second=crtuple_get_second
        )


_T = t.TypeVar('_T', bound='CoralValue')
class CoralCompilationScope:

    def __init__(self, builder: ir.IRBuilder, runtime: CoralRuntime) -> None:
        self.builder: t.Final = builder
        self.runtime: t.Final = runtime
        self.vars: t.Dict[str, CoralValue] = {}
        self.coral_values: t.Final['t.List[CoralValue]'] = []

    def add_var(self, name: str, value: 'CoralValue') -> None:
        if name in self.vars:
            raise ValueError(f"the name '{name}' was already declared")
        self.vars[name] = value
    
    def collect_value(self, value: _T) -> _T:
        if value.boxed:
            self.coral_values.append(value)
        return value


class CoralValue:

    def __init__(
        self,
        type_: ast.IBoundType,
        lltype: ir.Type,
        value: ir.Value,
        boxed: bool,
        scope: CoralCompilationScope
    ) -> None:
        self.boundtype: t.Final = type_
        self.lltype: t.Final = lltype
        self.value: t.Final = value
        self.boxed: t.Final = boxed
        self.scope: t.Final = scope

    def box(self) -> 'CoralValue':
        if self.boxed:
            return self
        raise NotImplementedError
    
    def unbox(self) -> 'CoralValue':
        if not self.boxed:
            return self
        raise NotImplementedError

    @classmethod
    def merge_branch(
        cls,
        *,
        then_value: 'CoralValue',
        then_block: ir.Block,
        else_value: 'CoralValue',
        else_block: ir.Block,
        scope: CoralCompilationScope
    ) -> 'CoralValue':
        if then_value.lltype != else_value.lltype:
            raise TypeError(f"both sides of a IF branch must have the same LLVM type, but got '{then_value.lltype}' and '{else_value.lltype}'")
        if then_value.boxed != else_value.boxed:
            raise TypeError(f"both sides of a IF branch must be either all boxed or unboxed")
        if not then_value.boxed and then_value.boundtype != else_value.boundtype:
            raise TypeError(f"both sides of a unboxed IF branch must have the same bound type, but got '{then_value.boundtype}' and '{else_value.boundtype}'")
        result = scope.builder.phi(then_value.lltype)
        result.add_incoming(then_value.value, then_block)
        result.add_incoming(else_value.value, else_block)
        return cls(
            type_=then_value.boundtype,
            lltype=then_value.lltype,
            value=result,
            boxed=then_value.boxed,
            scope=scope
        ) 

    def incref(self) -> None:
        if self.boxed:
            self.scope.builder.call(
                fn=self.scope.runtime.crvalue_incref,
                args=(self.value,)
            )
    
    def decref(self) -> None:
        if self.boxed:
            self.scope.builder.call(
                fn=self.scope.runtime.crvalue_decref,
                args=(self.value,)
            )

    def print(self) -> t.Self:
        self.scope.builder.call(
            fn=self.scope.runtime.crvalue_print,
            args=(self.box().value,)
        )
        return self

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CoralValue) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class CoralInteger(CoralValue):
    """Integers use tagged pointers"""

    def box(self) -> 'CoralInteger':
        if self.boxed: return self
        if self.boundtype.type == ast.NativeType.INTEGER:
            taggedint = self.scope.builder.shl(self.value, ir.Constant(LL_INT, 2))
            taggedint = self.scope.builder.or_(taggedint, ir.Constant(LL_INT, 1))
        elif self.boundtype.type == ast.NativeType.BOOLEAN:
            taggedint = self.scope.builder.zext(self.value, LL_INT)
            taggedint = self.scope.builder.shl(taggedint, ir.Constant(LL_INT, 2))
            taggedint = self.scope.builder.or_(taggedint, ir.Constant(LL_INT, 2))
        else:
            raise TypeError(f"CoralInteger must be INTEGER or BOOLEAN, but got {self.boundtype}")
        lltype = self.scope.runtime.crvalue_struct.as_pointer()
        return CoralInteger(
            type_=self.boundtype,
            lltype=lltype,
            value=self.scope.builder.inttoptr(taggedint, lltype),
            boxed=True,
            scope=self.scope
        )
    
    def unbox(self) -> 'CoralInteger':
        if not self.boxed: return self
        intptr = self.scope.builder.ptrtoint(self.value, LL_INT)
        if self.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=self.boundtype,
                lltype=LL_INT,
                value=self.scope.builder.ashr(intptr, ir.Constant(LL_INT, 2)),
                boxed=False,
                scope=self.scope
            )
        elif self.boundtype.type == ast.NativeType.BOOLEAN:
            return CoralInteger(
                type_=self.boundtype,
                lltype=LL_BOOL,
                value=self.scope.builder.trunc(
                    self.scope.builder.ashr(intptr, ir.Constant(LL_INT, 2)),
                    LL_BOOL
                ),
                boxed=False,
                scope=self.scope
            )
        else:
            raise TypeError(f"CoralInteger must wrap INTEGER or BOOLEAN, but got {self.boundtype}")

    def incref(self) -> None:
        pass

    def decref(self) -> None:
        pass

    @classmethod
    def add(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_INTEGER_TYPE,
                lltype=LL_INT,
                value=self.scope.builder.add(self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        if self.boundtype.type == ast.NativeType.STRING or other.boundtype.type == ast.NativeType.STRING:
            return CoralInteger(
                type_=ast.BOUND_STRING_TYPE,
                lltype=self.scope.runtime.crvalue_add.ftype.return_type,
                value=self.scope.builder.call(
                    fn=self.scope.runtime.crvalue_add,
                    args=(self.box().value, other.box().value)
                ),
                boxed=True,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BINOP_ADD_TYPES,
            lltype=self.scope.runtime.crvalue_add.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_add,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )

    @classmethod
    def sub(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_integer_operands(self, '-', other)
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_INTEGER_TYPE,
                lltype=LL_INT,
                value=self.scope.builder.sub(self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_INTEGER_TYPE,
            lltype=self.scope.runtime.crvalue_sub.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_sub,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def mul(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_integer_operands(self, '*', other)
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_INTEGER_TYPE,
                lltype=LL_INT,
                value=self.scope.builder.mul(self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_INTEGER_TYPE,
            lltype=self.scope.runtime.crvalue_mul.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_mul,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def div(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_integer_operands(self, '/', other)
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_INTEGER_TYPE,
                lltype=LL_INT,
                value=self.scope.builder.sdiv(self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_INTEGER_TYPE,
            lltype=self.scope.runtime.crvalue_div.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_div,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def mod(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_integer_operands(self, '%', other)
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_INTEGER_TYPE,
                lltype=LL_INT,
                value=self.scope.builder.srem(self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_INTEGER_TYPE,
            lltype=self.scope.runtime.crvalue_mod.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_mod,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def lt(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_integer_operands(self, '<', other)
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_BOOLEAN_TYPE,
                lltype=LL_BOOL,
                value=self.scope.builder.icmp_signed('<', self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_BOOLEAN_TYPE,
            lltype=self.scope.runtime.crvalue_lt.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_lt,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def lte(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_integer_operands(self, '<=', other)
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_BOOLEAN_TYPE,
                lltype=LL_BOOL,
                value=self.scope.builder.icmp_signed('<=', self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_BOOLEAN_TYPE,
            lltype=self.scope.runtime.crvalue_lte.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_lte,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def gt(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_integer_operands(self, '>', other)
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_BOOLEAN_TYPE,
                lltype=LL_BOOL,
                value=self.scope.builder.icmp_signed('>', self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_BOOLEAN_TYPE,
            lltype=self.scope.runtime.crvalue_gt.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_gt,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def gte(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_integer_operands(self, '>=', other)
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_BOOLEAN_TYPE,
                lltype=LL_BOOL,
                value=self.scope.builder.icmp_signed('>=', self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_BOOLEAN_TYPE,
            lltype=self.scope.runtime.crvalue_gte.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_gte,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def equals(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        if (
            (
                self.boundtype.type == ast.NativeType.INTEGER and
                other.boundtype.type == ast.NativeType.INTEGER
            ) or (
                self.boundtype.type == ast.NativeType.BOOLEAN and
                other.boundtype.type == ast.NativeType.BOOLEAN
            )
        ):
            return CoralInteger(
                type_=ast.BOUND_BOOLEAN_TYPE,
                lltype=LL_BOOL,
                value=self.scope.builder.icmp_signed('==', self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_BOOLEAN_TYPE,
            lltype=self.scope.runtime.crvalue_equals.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_equals,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def not_equals(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        if (
            (
                self.boundtype.type == ast.NativeType.INTEGER and
                other.boundtype.type == ast.NativeType.INTEGER
            ) or (
                self.boundtype.type == ast.NativeType.BOOLEAN and
                other.boundtype.type == ast.NativeType.BOOLEAN
            )
        ):
            return CoralInteger(
                type_=ast.BOUND_BOOLEAN_TYPE,
                lltype=LL_BOOL,
                value=self.scope.builder.icmp_signed('!=', self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_BOOLEAN_TYPE,
            lltype=self.scope.runtime.crvalue_notequals.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_notequals,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )

    @classmethod
    def bool_and(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_boolean_operands(self, '&&', other)
        if self.boundtype.type == ast.NativeType.BOOLEAN and other.boundtype.type == ast.NativeType.BOOLEAN:
            return CoralInteger(
                type_=ast.BOUND_BOOLEAN_TYPE,
                lltype=LL_BOOL,
                value=self.scope.builder.and_(self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_BOOLEAN_TYPE,
            lltype=self.scope.runtime.crvalue_and.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_and,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def bool_or(cls, self: CoralValue, other: CoralValue) -> 'CoralInteger':
        cls.assert_boolean_operands(self, '||', other)
        if self.boundtype.type == ast.NativeType.BOOLEAN and other.boundtype.type == ast.NativeType.BOOLEAN:
            return CoralInteger(
                type_=ast.BOUND_BOOLEAN_TYPE,
                lltype=LL_BOOL,
                value=self.scope.builder.or_(self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BOUND_BOOLEAN_TYPE,
            lltype=self.scope.runtime.crvalue_or.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_or,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )

    @classmethod
    def assert_integer_operands(cls, left: CoralValue, op: str, right: CoralValue) -> None:
        if (
            left.boundtype.type != ast.NativeType.INTEGER and
            left.boundtype.type != ast.NativeType.UNDEFINED and
            right.boundtype.type != ast.NativeType.INTEGER and
            right.boundtype.type != ast.NativeType.UNDEFINED
        ):
            raise TypeError(f"'{op}' cannot be applied between '{left.boundtype}' and '{right.boundtype}'")
        
    @classmethod
    def assert_boolean_operands(cls, left: CoralValue, op: str, right: CoralValue) -> None:
        if (
            left.boundtype.type != ast.NativeType.BOOLEAN and
            left.boundtype.type != ast.NativeType.UNDEFINED and
            right.boundtype.type != ast.NativeType.BOOLEAN and
            right.boundtype.type != ast.NativeType.UNDEFINED
        ):
            raise TypeError(f"'{op}' cannot be applied between '{left.boundtype}' and '{right.boundtype}'")


class CoralString(CoralValue):

    def box(self) -> 'CoralString':
        if self.boxed: return self
        value_ptr = self.scope.builder.bitcast(self.value, LL_CHAR.as_pointer())
        return self.scope.collect_value(CoralString(
            type_=ast.BOUND_STRING_TYPE,
            lltype=self.scope.runtime.crstring_new.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crstring_new,
                args=(value_ptr, ir.Constant(LL_INT, 0))
            ),
            boxed=True,
            scope=self.scope
        ))

    def unbox(self) -> CoralValue:
        if not self.boxed: return self
        return CoralString(
            type_=ast.BOUND_STRING_TYPE,
            lltype=self.scope.runtime.crvalue_as_string.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crvalue_as_string,
                args=(self.value,)
            ),
            boxed=False,
            scope=self.scope
        )  


class CoralTuple(CoralValue):

    def __init__(
        self,
        type_: ast.BoundType,
        lltype: ir.Type,
        value: ir.Value,
        boxed: bool,
        scope: CoralCompilationScope,
        first: t.Optional[CoralValue] = None,
        second: t.Optional[CoralValue] = None
    ) -> None:
        super().__init__(type_, lltype, value, boxed, scope)
        if (first is None or second is None) and not boxed:
            raise ValueError("unboxed tuples must have its members defined")
        self.first: t.Final = first
        self.second: t.Final = second

    def instance_get_first(self) -> CoralValue:
        if not self.boxed:
            first = t.cast(CoralValue, self.first)
            return first
        return CoralValue(
            type_=self.boundtype.generics[0],
            lltype=self.scope.runtime.crtuple_get_first.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crtuple_get_first,
                args=(self.value,)
            ),
            boxed=True,
            scope=self.scope
        )

    def instance_get_second(self) -> CoralValue:
        if not self.boxed:
            second = t.cast(CoralValue, self.second)
            return second
        return CoralValue(
            type_=self.boundtype.generics[1],
            lltype=self.scope.runtime.crtuple_get_second.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crtuple_get_second,
                args=(self.value,)
            ),
            boxed=True,
            scope=self.scope
        )

    def box(self) -> 'CoralTuple':
        if self.boxed: return self
        first = self.first.box()
        second = self.second.box()
        return self.scope.collect_value(CoralTuple(
            type_=self.boundtype,
            lltype=self.scope.runtime.crtuple_new.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crtuple_new,
                args=(first.value, second.value)
            ),
            boxed=True,
            scope=self.scope,
            first=None,
            second=None
        ))

    def unbox(self) -> 'CoralTuple':
        if not self.boxed: return self
        first = self.instance_get_first()
        second = self.instance_get_second()
        return CoralTuple(
            type_=self.boundtype,
            lltype=ir.VoidType(),
            first=first,
            second=second,
            boxed=False,
            scope=self.scope,
            value=ir.Constant(LL_CHAR, 0) # not used
        )

    @classmethod
    def merge_branch(
        cls,
        *,
        then_value: 'CoralValue',
        then_block: ir.Block,
        else_value: 'CoralValue',
        else_block: ir.Block,
        scope: CoralCompilationScope
    ) -> 'CoralValue':
        if (
            then_value.boundtype.type != ast.NativeType.TUPLE or
            else_value.boundtype.type != ast.NativeType.TUPLE
        ):
            raise TypeError(f"expected both sides of the IF branch to be tuples, but got '{then_value.boundtype}' and '{else_value.boundtype}'")
        if then_value.lltype != else_value.lltype:
            raise TypeError(f"both sides of a IF branch must have the same LLVM type, but got '{then_value.lltype}' and '{else_value.lltype}'")
        if then_value.boxed != else_value.boxed:
            raise TypeError(f"both sides of a IF branch must be either all boxed or unboxed")
        then_value = t.cast(CoralTuple, then_value)
        else_value = t.cast(CoralTuple, else_value)
        if not then_value.boxed:
            first = then_value.first.merge_branch(
                then_value=then_value.first,
                then_block=then_block,
                else_value=else_value.first,
                else_block=else_block,
                scope=scope
            )
            second = then_value.second.merge_branch(
                then_value=then_value.second,
                then_block=then_block,
                else_value=else_value.second,
                else_block=else_block,
                scope=scope
            )
            return cls(
                type_=then_value.boundtype,
                lltype=then_value.lltype,
                first=first,
                second=second,
                boxed=False,
                scope=scope,
                value=ir.Constant(LL_CHAR, 0) # not used
            ) 
        else:
            return super().merge_branch(
                then_value=then_value,
                then_block=then_block,
                else_value=else_value,
                else_block=else_block,
                scope=scope
            )

    @classmethod
    def create_unboxed(cls, first: CoralValue, second: CoralValue, scope: CoralCompilationScope) -> 'CoralTuple':
        return CoralTuple(
            type_=ast.BoundType(ast.NativeType.TUPLE, (first.boundtype, second.boundtype)),
            lltype=ir.VoidType(),
            first=first,
            second=second,
            boxed=False,
            scope=scope,
            value=ir.Constant(LL_CHAR, 0) # not used
        )

    @classmethod
    def get_first(cls, value: CoralValue) -> CoralValue:
        if value.boundtype.type == ast.NativeType.TUPLE:
            value = t.cast(CoralTuple, value)
            return value.instance_get_first()
        if value.boundtype.type != ast.NativeType.UNDEFINED:
            raise TypeError(f"CoralTuple.get_first() expects a Tuple or UNDEFINED, but got {value.boundtype}")
        return CoralValue(
            type_=ast.BOUND_UNDEFINED_TYPE,
            lltype=value.scope.runtime.crtuple_get_first.ftype.return_type,
            value=value.scope.builder.call(
                fn=value.scope.runtime.crtuple_get_first,
                args=(value.box().value,)
            ),
            boxed=True,
            scope=value.scope
        )
    
    @classmethod
    def get_second(cls, value: CoralValue) -> CoralValue:
        if value.boundtype.type == ast.NativeType.TUPLE:
            value = t.cast(CoralTuple, value)
            return value.instance_get_second()
        if value.boundtype.type != ast.NativeType.UNDEFINED:
            raise TypeError(f"CoralTuple.get_second() expects a Tuple or UNDEFINED, but got {value.boundtype}")
        return CoralValue(
            type_=ast.BOUND_UNDEFINED_TYPE,
            lltype=value.scope.runtime.crtuple_get_second.ftype.return_type,
            value=value.scope.builder.call(
                fn=value.scope.runtime.crtuple_get_second,
                args=(value.box().value,)
            ),
            boxed=True,
            scope=value.scope
        )
    
    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CoralTuple) and
            self.boxed == other.boxed and
            self.first == other.first and
            self.second == other.second
        )


class CoralCompiler:

    def __init__(
        self,
        program: ast.Program,
        engine: llvm.ExecutionEngine
    ) -> None:
        self._program = program
        self._engine = engine
        self._module: t.Optional[ir.Module] = None
        self._ll_module: t.Optional[llvm.ModuleRef] = None
        self._strings: t.Dict[str, ir.GlobalVariable] = {}

    @classmethod
    def create_default(cls, program: ast.Program) -> 'CoralCompiler':
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        backing_mod = llvm.parse_assembly('')
        engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
        return CoralCompiler(program, engine)

    def compile(self) -> t.Callable[[], None]:
        if self._ll_module is not None:
            self._engine.run_static_destructors()
            self._engine.remove_module(self._ll_module)
            self._ll_module.close()
            self._ll_module = None
        self._ll_module = llvm.parse_assembly(str(self.compile_ir()))
        self._engine.add_module(self._ll_module)
        self._engine.finalize_object()
        self._engine.run_static_constructors()
        return c.CFUNCTYPE(restype=None)(self._engine.get_function_address('__main__'))

    def compile_ir(self, verify: bool=False) -> ir.Module:
        self._strings = {}
        self._module = ir.Module(self._program.filename)
        main = ir.Function(
            name='__main__',
            module=self._module,
            ftype=ir.FunctionType(return_type=ir.VoidType(), args=[])
        )
        entry = main.append_basic_block('entry')
        main_builder = ir.IRBuilder(entry)
        self._compile_node(
            self._program.body,
            CoralCompilationScope(main_builder, CoralRuntime.import_into(self._module))
        )
        main_builder.ret_void()
        if verify:
            llmod = llvm.parse_assembly(str(self._module))
            llmod.verify()
            llmod.close()
        return self._module

    def _compile_node(
        self,
        node: ast.Expression,
        scope: CoralCompilationScope
    ) -> CoralValue:
        match node:
            case ast.ReferenceExpression():
                return scope.vars[node.name]
            case ast.LiteralIntegerValue(value=value):
                return CoralInteger(
                    type_=ast.BOUND_INTEGER_TYPE,
                    lltype=LL_INT,
                    value=ir.Constant(LL_INT, value),
                    boxed=False,
                    scope=scope
                )
            case ast.LiteralBooleanValue(value=value):
                return CoralInteger(
                    type_=ast.BOUND_BOOLEAN_TYPE,
                    lltype=LL_BOOL,
                    value=ir.Constant(LL_BOOL, int(value)),
                    boxed=False,
                    scope=scope
                )
            case ast.LiteralStringValue(value=value):
                compiledstr = self._compile_string(value)
                return CoralString(
                    type_=ast.BOUND_STRING_TYPE,
                    lltype=LL_CHAR.as_pointer(),
                    # drop the array pointer, we just need a plain char* like pointer
                    value=scope.builder.bitcast(compiledstr, LL_CHAR.as_pointer()),
                    boxed=False,
                    scope=scope
                )
            case ast.TupleExpression(first=first, second=second):
                return CoralTuple.create_unboxed(
                    first=self._compile_node(first, scope),
                    second=self._compile_node(second, scope),
                    scope=scope
                )
            case ast.FirstExpression(value=value):
                return CoralTuple.get_first(self._compile_node(value, scope))
            case ast.SecondExpression(value=value):
                return CoralTuple.get_second(self._compile_node(value, scope))
            case ast.PrintExpression(value=value):
                return self._compile_node(value, scope).print()
            case ast.BinaryExpression():
                return self._compile_binary_expression(node, scope)
            case ast.ConditionalExpression():
                return self._compile_condition(node, scope)
            case ast.LetExpression():
                return self._compile_declaration(node, scope)
            case _:
                raise ValueError(f"{node} is not supported yet")

    def _compile_declaration(self, node: ast.LetExpression, scope: CoralCompilationScope) -> CoralValue:
        value = self._compile_node(node.value, scope)
        if node.binding is not None:
            scope.add_var(node.binding.name, value)
        return self._compile_node(node.next, scope)

    def _compile_condition(self, node: ast.ConditionalExpression, scope: CoralCompilationScope) -> CoralValue:
        cond = self._compile_node(node.cond, scope)
        with scope.builder.if_else(cond.value) as (then_branch, else_branch):
            with then_branch:
                then_block = scope.builder._block
                then = self._compile_node(node.then, scope)
                if not node.boundtype.is_static:
                    then = then.box()
            with else_branch:
                else_block = scope.builder._block
                otherwise = self._compile_node(node.alternate, scope)
                if not node.boundtype.is_static:
                    otherwise = otherwise.box()
        return then.merge_branch(
            then_value=then,
            then_block=then_block,
            else_value=otherwise,
            else_block=else_block,
            scope=scope
        )

    def _compile_binary_expression(self, node: ast.BinaryExpression, scope: CoralCompilationScope) -> CoralValue:
        left = self._compile_node(node.left, scope)
        right = self._compile_node(node.right, scope)
        match node.op:
            case ast.BinaryOperator.ADD:
                return CoralInteger.add(left, right)
            case ast.BinaryOperator.SUB:
                return CoralInteger.sub(left, right)
            case ast.BinaryOperator.MUL:
                return CoralInteger.mul(left, right)
            case ast.BinaryOperator.DIV:
                return CoralInteger.div(left, right)
            case ast.BinaryOperator.MOD:
                return CoralInteger.mod(left, right)
            case ast.BinaryOperator.LTE:
                return CoralInteger.lte(left, right)
            case ast.BinaryOperator.LT:
                return CoralInteger.lt(left, right)
            case ast.BinaryOperator.GT:
                return CoralInteger.gt(left, right)
            case ast.BinaryOperator.GTE:
                return CoralInteger.gte(left, right)
            case ast.BinaryOperator.EQ:
                return CoralInteger.equals(left, right)
            case ast.BinaryOperator.NEQ:
                return CoralInteger.not_equals(left, right)
            case ast.BinaryOperator.AND:
                return CoralInteger.bool_and(left, right)
            case ast.BinaryOperator.OR:
                return CoralInteger.bool_or(left, right)
            
    def _compile_string(self, value: str) -> ir.GlobalVariable:
        globalvar = self._strings.get(value, None)
        if globalvar is not None:
            return globalvar
        content = bytearray(value.encode('ASCII', errors='strict'))
        content.append(0)
        constant = ir.Constant(ir.ArrayType(LL_CHAR, len(content)), content)
        globalvar = ir.GlobalVariable(self._module, constant.type, name=f'.str.{len(self._strings)}')
        globalvar.linkage = 'private'
        globalvar.global_constant = True
        globalvar.unnamed_addr = True
        globalvar.initializer = constant
        self._strings[value] = globalvar
        return globalvar
