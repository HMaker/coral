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
LL_INT16 = ir.IntType(16)
LL_INT32 = ir.IntType(32)


class CoralRuntime:
    """Handles the LLVM interface to link with the runtime library. See runtime/runtime.h"""

    def __init__(
        self,
        *,
        crobject_struct: ir.IdentifiedStructType,
        crobject_incref: ir.Function,
        crobject_decref: ir.Function,
        crobject_print: ir.Function,

        crobject_add: ir.Function,
        crobject_sub: ir.Function,
        crobject_mul: ir.Function,
        crobject_div: ir.Function,
        crobject_mod: ir.Function,
        crobject_lt: ir.Function,
        crobject_lte: ir.Function,
        crobject_gt: ir.Function,
        crobject_gte: ir.Function,
        crobject_equals: ir.Function,
        crobject_notequals: ir.Function,
        crobject_and: ir.Function,
        crobject_or: ir.Function,

        crstring_new: ir.Function,

        crtuple_struct: ir.IdentifiedStructType,
        crtuple_new: ir.Function,
        crtuple_get_first: ir.Function,
        crtuple_get_second: ir.Function,

        crobjectarray_struct: ir.IdentifiedStructType,
        crobjectarray_new: ir.Function,
        crobjectarray_push: ir.Function,
        crobjectarray_release: ir.Function,

        crfunction_struct: ir.IdentifiedStructType,
        crfunction_new: ir.Function,
        crfunction_set_global: ir.Function,
        crfunction_get_globals_array: ir.Function,
        crfunction_call: ir.Function,
    ) -> None:
        self.crobject_struct: t.Final = crobject_struct
        self.crobject_incref: t.Final = crobject_incref
        self.crobject_decref: t.Final = crobject_decref
        self.crobject_print: t.Final = crobject_print

        self.crobject_add: t.Final = crobject_add
        self.crobject_sub: t.Final = crobject_sub
        self.crobject_mul: t.Final = crobject_mul
        self.crobject_div: t.Final = crobject_div
        self.crobject_mod: t.Final = crobject_mod
        self.crobject_lt: t.Final = crobject_lt
        self.crobject_lte: t.Final = crobject_lte
        self.crobject_gt: t.Final = crobject_gt
        self.crobject_gte: t.Final = crobject_gte
        self.crobject_equals: t.Final = crobject_equals
        self.crobject_notequals: t.Final = crobject_notequals
        self.crobject_and: t.Final = crobject_and
        self.crobject_or: t.Final = crobject_or

        self.crstring_new: t.Final = crstring_new

        self.crtuple_struct: t.Final = crtuple_struct
        self.crtuple_new: t.Final = crtuple_new
        self.crtuple_get_first: t.Final = crtuple_get_first
        self.crtuple_get_second: t.Final = crtuple_get_second

        self.crobjectarray_struct: t.Final = crobjectarray_struct
        self.crobjectarray_new: t.Final = crobjectarray_new
        self.crobjectarray_push: t.Final = crobjectarray_push
        self.crobjectarray_release: t.Final = crobjectarray_release

        self.crfunction_struct: t.Final = crfunction_struct
        self.crfunction_new: t.Final = crfunction_new
        self.crfunction_set_global: t.Final = crfunction_set_global
        self.crfunction_get_globals_array: t.Final = crfunction_get_globals_array
        self.crfunction_call: t.Final = crfunction_call

    @classmethod
    def import_into(cls, mod: ir.Module) -> 'CoralRuntime':
        crobject_struct = mod.context.get_identified_type('struct.CRObject')
        crobject_struct.set_body(
            LL_INT,               # CRType _type
            LL_INT,               # unsigned long _refCount
            LL_CHAR.as_pointer(), # void* value
        )
        crobject_struct_ptr = crobject_struct.as_pointer()

        crobject_incref = ir.Function(
            name='CRObject_incref',
            module=mod,
            ftype=ir.FunctionType(
                return_type=ir.VoidType(),
                args=[crobject_struct_ptr]
            )
        )
        crobject_decref = ir.Function(
            name='CRObject_decref',
            module=mod,
            ftype=ir.FunctionType(
                return_type=ir.VoidType(),
                args=[crobject_struct_ptr]
            )
        )

        crobject_binary_operator_func = ir.FunctionType(
            return_type=crobject_struct_ptr,
            args=[crobject_struct_ptr, crobject_struct_ptr]
        )
        crobject_add = ir.Function(
            name='CRObject_add',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_sub = ir.Function(
            name='CRObject_sub',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_mul = ir.Function(
            name='CRObject_mul',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_div = ir.Function(
            name='CRObject_div',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_mod = ir.Function(
            name='CRObject_mod',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_lt = ir.Function(
            name='CRObject_lessThan',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_lte = ir.Function(
            name='CRObject_lessOrEqual',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_gt = ir.Function(
            name='CRObject_greaterThan',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_gte = ir.Function(
            name='CRObject_greaterOrEqual',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_and = ir.Function(
            name='CRObject_and',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_or = ir.Function(
            name='CRObject_or',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_equals = ir.Function(
            name='CRObject_equals',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_notequals = ir.Function(
            name='CRObject_notEquals',
            module=mod,
            ftype=crobject_binary_operator_func
        )

        crstring_new = ir.Function(
            name='CRString_new',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crobject_struct_ptr,
                args=[LL_CHAR.as_pointer(), LL_INT]
            )
        )

        crobject_print = ir.Function(
            name='CRObject_print',
            module=mod,
            ftype=ir.FunctionType(
                return_type=ir.VoidType(),
                args=[crobject_struct_ptr]
            )
        )

        crtuple_struct = mod.context.get_identified_type('struct.CRTuple')
        crtuple_struct.set_body(crobject_struct_ptr, crobject_struct_ptr)
        crtuple_new = ir.Function(
            name='CRTuple_new',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crobject_struct_ptr,
                args=[crobject_struct_ptr, crobject_struct_ptr]
            )
        )
        crtuple_get_first = ir.Function(
            name='CRTuple_getFirst',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crobject_struct_ptr,
                args=[crobject_struct_ptr]
            )
        )
        crtuple_get_second = ir.Function(
            name='CRTuple_getSecond',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crobject_struct_ptr,
                args=[crobject_struct_ptr]
            )
        )

        crobjectarray_struct = mod.context.get_identified_type('struct.CRObjectArray')
        crobjectarray_struct.set_body(
            crobject_struct_ptr.as_pointer(), # CRObject** objects
            LL_INT,                           # size_t length
            LL_INT                            # size_t maxLength
        )
        crobjectarray_new = ir.Function(
            name='CRObjectArray_new',
            module=mod,
            ftype=ir.FunctionType(
                args=[LL_INT],
                return_type=crobjectarray_struct.as_pointer()
            )
        )
        crobjectarray_push = ir.Function(
            name='CRObjectArray_push',
            module=mod,
            ftype=ir.FunctionType(
                args=[crobjectarray_struct.as_pointer(), crobject_struct_ptr],
                return_type=ir.VoidType()
            )
        )
        crobjectarray_release = ir.Function(
            name='CRObjectArray_release',
            module=mod,
            ftype=ir.FunctionType(
                args=[crobjectarray_struct.as_pointer()],
                return_type=ir.VoidType()
            )
        )

        crfunction_struct = mod.context.get_identified_type('struct.CRFunction')
        crfunction_struct.set_body(
            LL_INT16,                          # unsigned short arity
            crobjectarray_struct.as_pointer(), # CRObjectArray* globals
            ir.FunctionType(                   # CRObject* (*fp) (CRObject**, CRObject**);
                args=(crobject_struct_ptr.as_pointer(), crobject_struct_ptr.as_pointer()),
                return_type=crobject_struct_ptr
            ).as_pointer(),
            LL_CHAR.as_pointer()               # void* llfp
        )
        crfunction_new = ir.Function(
            name='CRFunction_new',
            module=mod,
            ftype=ir.FunctionType(
                args=[LL_INT, LL_INT16, LL_CHAR.as_pointer(), LL_CHAR.as_pointer()],
                return_type=crobject_struct_ptr
            )
        )
        crfunction_set_global = ir.Function(
            name='CRFunction_setGlobal',
            module=mod,
            ftype=ir.FunctionType(
                args=[crobject_struct_ptr, LL_INT, crobject_struct_ptr],
                return_type=ir.VoidType()
            )
        )
        crfunction_get_globals_array = ir.Function(
            name='CRFunction_getGlobalsArray',
            module=mod,
            ftype=ir.FunctionType(
                args=[crobject_struct_ptr],
                return_type=crobject_struct_ptr.as_pointer()
            )
        )
        crfunction_call = ir.Function(
            name='CRFunction_call',
            module=mod,
            ftype=ir.FunctionType(
                args=[crobject_struct_ptr, LL_INT],
                return_type=crobject_struct_ptr,
                var_arg=True
            )
        )

        return CoralRuntime(
            crobject_struct=crobject_struct,
            crobject_incref=crobject_incref,
            crobject_decref=crobject_decref,

            crobject_add=crobject_add,
            crobject_sub=crobject_sub,
            crobject_mul=crobject_mul,
            crobject_div=crobject_div,
            crobject_mod=crobject_mod,
            crobject_lt=crobject_lt,
            crobject_lte=crobject_lte,
            crobject_gt=crobject_gt,
            crobject_gte=crobject_gte,
            crobject_equals=crobject_equals,
            crobject_notequals=crobject_notequals,
            crobject_and=crobject_and,
            crobject_or=crobject_or,

            crobject_print=crobject_print,

            crstring_new=crstring_new,

            crtuple_struct=crtuple_struct,
            crtuple_new=crtuple_new,
            crtuple_get_first=crtuple_get_first,
            crtuple_get_second=crtuple_get_second,

            crobjectarray_struct=crobjectarray_struct,
            crobjectarray_new=crobjectarray_new,
            crobjectarray_push=crobjectarray_push,
            crobjectarray_release=crobjectarray_release,

            crfunction_struct=crfunction_struct,
            crfunction_new=crfunction_new,
            crfunction_set_global=crfunction_set_global,
            crfunction_get_globals_array=crfunction_get_globals_array,
            crfunction_call=crfunction_call
        )

    def get_function_llfp(self, crobject: ir.Value, builder: ir.IRBuilder) -> ir.Value:
        """Returns void* ptr to the llfp value of the given function.
        No validation is performed against the pointer, this is a raw memory address load."""
        crobject_value_gep = builder.gep(crobject, indices=[LL_INT32(0), LL_INT32(2)], inbounds=True)
        crobject_value = builder.load(crobject_value_gep, align=8)
        crfunction_ptr = builder.bitcast(crobject_value, self.crfunction_struct.as_pointer())
        crfunction_llfp_gep = builder.gep(crfunction_ptr, indices=[LL_INT32(0), LL_INT32(3)], inbounds=True)
        crfunction_llfp = builder.load(crfunction_llfp_gep, align=8)
        return crfunction_llfp

    def get_function_globals(self, crobject: ir.Value, builder: ir.IRBuilder) -> ir.Value:
        """Returns CRObject** ptr to the __globals__ array of the given function.
        No validation is performed against the pointer, this is a raw memory address load."""
        crobject_value_gep = builder.gep(crobject, indices=[LL_INT32(0), LL_INT32(2)], inbounds=True)
        crobject_value = builder.load(crobject_value_gep, align=8)
        crfunction_ptr = builder.bitcast(crobject_value, self.crfunction_struct.as_pointer())
        crfunction_globals_gep = builder.gep(crfunction_ptr, indices=[LL_INT32(0), LL_INT32(1)], inbounds=True)
        crfunction_globals = builder.load(crfunction_globals_gep, align=8)
        crobjectarray_objects_gep = builder.gep(crfunction_globals, indices=[LL_INT32(0), LL_INT32(0)], inbounds=True)
        crobjectarray_objects = builder.load(crobjectarray_objects_gep, align=8)
        return crobjectarray_objects
    
    def get_tuple_first(self, crobject: ir.Value, builder: ir.IRBuilder) -> ir.Value:
        """Returns CRObject* ptr to the first member of a tuple.
        No validation is performed against the pointer, this is a raw memory address load.
        """
        crobject_value_gep = builder.gep(crobject, indices=[LL_INT32(0), LL_INT32(2)], inbounds=True)
        crobject_value = builder.load(crobject_value_gep, align=8)
        crtuple_ptr = builder.bitcast(crobject_value, self.crtuple_struct.as_pointer())
        first_gep = builder.gep(crtuple_ptr, indices=[LL_INT32(0), LL_INT32(0)], inbounds=True)
        return builder.load(first_gep, align=8)
    
    def get_tuple_second(self, crobject: ir.Value, builder: ir.IRBuilder) -> ir.Value:
        """Returns CRObject* ptr to the second member of a tuple.
        No validation is performed against the pointer, this is a raw memory address load.
        """
        crobject_value_gep = builder.gep(crobject, indices=[LL_INT32(0), LL_INT32(2)], inbounds=True)
        crobject_value = builder.load(crobject_value_gep, align=8)
        crtuple_ptr = builder.bitcast(crobject_value, self.crtuple_struct.as_pointer())
        second_gep = builder.gep(crtuple_ptr, indices=[LL_INT32(0), LL_INT32(1)], inbounds=True)
        return builder.load(second_gep, align=8)

    def get_llvm_type(self, boundtype: ast.IBoundType) -> ir.Type:
        """Returns the LLVM type representation for the given bound type.
        
        Integer, booleans and functions may be represented by primitive types.
        All the rest are represented by their boxed type, CRObject*
        """
        match boundtype.type:
            case ast.NativeType.INTEGER:
                return LL_INT
            case ast.NativeType.BOOLEAN:
                return LL_BOOL
            case ast.NativeType.FUNCTION:
                boundtype = t.cast(ast.BoundFunctionType, boundtype)
                params = [self.get_llvm_type(param) for param in boundtype.params]
                match boundtype.return_type.type:
                    case ast.NativeType.INTEGER:
                        return ir.FunctionType(args=params, return_type=LL_INT)
                    case ast.NativeType.BOOLEAN:
                        return ir.FunctionType(args=params, return_type=LL_BOOL)
                return ir.FunctionType(
                    args=params,
                    return_type=self.crobject_struct.as_pointer()
                )
            case _:
                return self.crobject_struct.as_pointer()


class CoralObject:
    """Handles the boxing, unboxing and specific compilation procedures for each coral object type."""

    def __init__(
        self,
        type_: ast.IBoundType,
        lltype: ir.Type,
        value: ir.Value,
        boxed: bool,
        scope: 'CoralFunctionCompilation'
    ) -> None:
        self.boundtype: t.Final = type_
        self.lltype: t.Final = lltype
        self.value: t.Final = value
        self.boxed: t.Final = boxed
        self.scope: t.Final = scope

    def box(self) -> 'CoralObject':
        """Creates a NEW boxed version of this object if it is UNBOXED. Returns the boxed object.
        
        Returns itself if it's already boxed. Boxing MUST be tracked by the GC.
        """
        if self.boxed:
            return self
        raise NotImplementedError

    def unbox(self) -> 'CoralObject':
        """Creates a NEW unboxed version of this object if it is BOXED. Returns the unboxed object.
        
        Returns itself if it's already unboxed. Nothing is done with the boxed version, we hope the
        GC will clean it.
        """
        if not self.boxed:
            return self
        raise NotImplementedError
    
    @classmethod
    def wrap_boxed_value(
        cls,
        boundtype: ast.IBoundType,
        value: ir.Value,
        scope: 'CoralFunctionCompilation'
    ) -> 'CoralObject':
        """Wraps a boxed value from memory."""
        match boundtype.type:
            case ast.NativeType.INTEGER | ast.NativeType.BOOLEAN:
                return CoralInteger(
                    type_=boundtype,
                    lltype=value.type,
                    value=value,
                    boxed=True,
                    scope=scope
                )
            case ast.NativeType.STRING:
                return CoralString(
                    type_=boundtype,
                    lltype=value.type,
                    value=value,
                    boxed=True,
                    scope=scope
                )
            case ast.NativeType.TUPLE:
                return CoralTuple(
                    type_=boundtype,
                    lltype=value.type,
                    value=value,
                    boxed=True,
                    scope=scope
                )
            # we dont wrap functions from memory values because we dont know if it needs any global
            case _:
                return CoralObject(
                    type_=ast.BOUND_UNDEFINED_TYPE,
                    lltype=value.type,
                    value=value,
                    boxed=True,
                    scope=scope
                )

    @classmethod
    def merge_branch(
        cls,
        *,
        then_value: 'CoralObject',
        then_block: ir.Block,
        else_value: 'CoralObject',
        else_block: ir.Block,
        scope: 'CoralFunctionCompilation'
    ) -> 'CoralObject':
        """Merge values which came from conditional branches. Both values must have the same type."""
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
                fn=self.scope.runtime.crobject_incref,
                args=(self.value,)
            )

    def decref(self) -> None:
        if self.boxed:
            self.scope.builder.call(
                fn=self.scope.runtime.crobject_decref,
                args=(self.value,)
            )

    def print(self) -> t.Self:
        """Compiles "print()" for this object."""
        self.scope.builder.call(
            fn=self.scope.runtime.crobject_print,
            args=(self.box().value,)
        )
        return self

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CoralObject) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class CoralInteger(CoralObject):
    """Integers and booleans use tagged pointers, the boxing does not allocate memory on the heap.
    
    Memory addresses aligned to 32 bits, multiples of 4 bytes, will always have the lowest 2 bits set
    to 0. We use that space to write a tag to the address. If it's 01, it's an integer. If it's 10,
    it's a boolean. If it's 00, it's a CRObject* box.
    """

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
        lltype = self.scope.runtime.crobject_struct.as_pointer()
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
    def add(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
                lltype=self.scope.runtime.crobject_add.ftype.return_type,
                value=self.scope.builder.call(
                    fn=self.scope.runtime.crobject_add,
                    args=(self.box().value, other.box().value)
                ),
                boxed=True,
                scope=self.scope
            )
        return CoralInteger(
            type_=ast.BINOP_ADD_TYPES,
            lltype=self.scope.runtime.crobject_add.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_add,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )

    @classmethod
    def sub(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_sub.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_sub,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )

    @classmethod
    def mul(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_mul.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_mul,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def div(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_div.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_div,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def mod(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_mod.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_mod,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )

    @classmethod
    def lt(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_lt.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_lt,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def lte(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_lte.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_lte,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def gt(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_gt.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_gt,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def gte(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_gte.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_gte,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def equals(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_equals.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_equals,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )
    
    @classmethod
    def not_equals(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_notequals.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_notequals,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )

    @classmethod
    def bool_and(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_and.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_and,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )

    @classmethod
    def bool_or(cls, self: CoralObject, other: CoralObject) -> 'CoralInteger':
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
            lltype=self.scope.runtime.crobject_or.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_or,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        )

    @classmethod
    def assert_integer_operands(cls, left: CoralObject, op: str, right: CoralObject) -> None:
        if (
            left.boundtype.type != ast.NativeType.INTEGER and
            left.boundtype.type != ast.NativeType.UNDEFINED and
            left.boundtype.type != ast.NativeType.ANY and
            right.boundtype.type != ast.NativeType.INTEGER and
            right.boundtype.type != ast.NativeType.UNDEFINED and
            right.boundtype.type != ast.NativeType.ANY
        ):
            raise TypeError(f"'{op}' cannot be applied between '{left.boundtype}' and '{right.boundtype}'")
        
    @classmethod
    def assert_boolean_operands(cls, left: CoralObject, op: str, right: CoralObject) -> None:
        if (
            left.boundtype.type != ast.NativeType.BOOLEAN and
            left.boundtype.type != ast.NativeType.UNDEFINED and
            left.boundtype.type != ast.NativeType.ANY and
            right.boundtype.type != ast.NativeType.BOOLEAN and
            right.boundtype.type != ast.NativeType.UNDEFINED and
            right.boundtype.type != ast.NativeType.ANY
        ):
            raise TypeError(f"'{op}' cannot be applied between '{left.boundtype}' and '{right.boundtype}'")


class CoralString(CoralObject):

    def box(self) -> 'CoralString':
        if self.boxed: return self
        value_ptr = self.scope.builder.bitcast(self.value, LL_CHAR.as_pointer())
        return self.scope.collect_object(CoralString(
            type_=ast.BOUND_STRING_TYPE,
            lltype=self.scope.runtime.crstring_new.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crstring_new,
                args=(value_ptr, ir.Constant(LL_INT, 0))
            ),
            boxed=True,
            scope=self.scope
        ))

    def unbox(self) -> CoralObject:
        # we dont unbox strings since we can't do anything meaningful with it
        return self


class CoralTuple(CoralObject):

    def __init__(
        self,
        type_: ast.BoundType,
        lltype: ir.Type,
        value: ir.Value,
        boxed: bool,
        scope: 'CoralFunctionCompilation',
        first: t.Optional[CoralObject] = None,
        second: t.Optional[CoralObject] = None
    ) -> None:
        super().__init__(type_, lltype, value, boxed, scope)
        if (first is None or second is None) and not boxed:
            raise ValueError("unboxed tuples must have its members defined")
        self.first: t.Final = first
        self.second: t.Final = second

    def instance_get_first(self) -> CoralObject:
        if not self.boxed:
            first = t.cast(CoralObject, self.first)
            return first
        return CoralObject.wrap_boxed_value(
            boundtype=self.boundtype.generics[0],
            value=self.scope.runtime.get_tuple_first(self.value, self.scope.builder),
            scope=self.scope
        )

    def instance_get_second(self) -> CoralObject:
        if not self.boxed:
            second = t.cast(CoralObject, self.second)
            return second
        return CoralObject.wrap_boxed_value(
            boundtype=self.boundtype.generics[1],
            value=self.scope.runtime.get_tuple_second(self.value, self.scope.builder),
            scope=self.scope
        )

    def box(self) -> 'CoralTuple':
        if self.boxed: return self
        first = self.first.box()
        second = self.second.box()
        return self.scope.collect_object(CoralTuple(
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
        then_value: 'CoralObject',
        then_block: ir.Block,
        else_value: 'CoralObject',
        else_block: ir.Block,
        scope: 'CoralFunctionCompilation'
    ) -> 'CoralObject':
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
    def create_unboxed(cls, first: CoralObject, second: CoralObject, scope: 'CoralFunctionCompilation') -> 'CoralTuple':
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
    def get_first(cls, value: CoralObject) -> CoralObject:
        if value.boundtype.type == ast.NativeType.TUPLE:
            value = t.cast(CoralTuple, value)
            return value.instance_get_first()
        if value.boundtype.type != ast.NativeType.UNDEFINED and value.boundtype.type != ast.NativeType.ANY:
            raise TypeError(f"CoralTuple.get_first() expects a Tuple or UNDEFINED, but got {value.boundtype}")
        return CoralObject(
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
    def get_second(cls, value: CoralObject) -> CoralObject:
        if value.boundtype.type == ast.NativeType.TUPLE:
            value = t.cast(CoralTuple, value)
            return value.instance_get_second()
        if value.boundtype.type != ast.NativeType.UNDEFINED and value.boundtype.type != ast.NativeType.ANY:
            raise TypeError(f"CoralTuple.get_second() expects a Tuple or UNDEFINED, but got {value.boundtype}")
        return CoralObject(
            type_=ast.BOUND_UNDEFINED_TYPE,
            lltype=value.scope.runtime.crtuple_get_second.ftype.return_type,
            value=value.scope.builder.call(
                fn=value.scope.runtime.crtuple_get_second,
                args=(value.box().value,)
            ),
            boxed=True,
            scope=value.scope
        )

    def __hash__(self) -> int:
        return hash((self.first, self.second, self.value, self.boxed))

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CoralTuple) and
            self.boxed == other.boxed and
            self.first == other.first and
            self.second == other.second
        )


class CoralFunction(CoralObject):
    """Functions are always "boxed", but the call to the native function definition can be directly
    dispatched from the compiled code if we know the function signature at compile time
    (i.e. BoundType is static).

    box() here does nothing memory wise, unbox() loads the __globals__ and the native function pointer
    from the CRFunction struct.

    Functions which return boxed values (aka CRObject*) must return it with the refcount incremented.
    The function caller always owns a reference to the returned boxed values, thus it will be collected
    by its GC list. The called function DOES NOT own any reference to its argument, thus it won't try to collect it.

    To sum up the calling convention is as follow:
    - The CALLER owns the references to the arguments
    - The CALLER pass arguments in the same order and with the same types as defined in the CALLEE signature
    - The CALLER must kept the references to the arguments live for the duration of the call
    - The CALLEE must return a value of the same type as defined in its signature
    - The CALLEE must kept the return value live after the return
    - The CALLER owns the reference to the returned value
    - The CALLER is responsible for cleaning up both arguments and the retuned value
    """

    def __init__(
        self,
        *,
        type_: ast.IBoundType,
        lltype: ir.FunctionType,
        value: ir.Value,
        boxed: bool,
        scope: 'CoralFunctionCompilation',
        name: t.Optional[str] = None,
        llfunc_ptr: t.Optional[ir.Value] = None,
        globals_ptr: t.Optional[ir.Value] = None,
        has_globals: bool = False
    ) -> None:
        super().__init__(type_, lltype, value, boxed, scope)
        self.name: t.Final = name
        self.llfunc_ptr: t.Final = llfunc_ptr
        self.globals_ptr: t.Final = globals_ptr
        self.has_globals: t.Final = has_globals

    @classmethod
    def call(
        cls,
        scope: 'CoralFunctionCompilation',
        callee: CoralObject,
        args: t.List[CoralObject]
    ) -> CoralObject:
        if callee.boundtype.type != ast.NativeType.FUNCTION:
            return scope.collect_object(CoralObject(
                type_=ast.BOUND_UNDEFINED_TYPE,
                lltype=scope.runtime.crfunction_call.ftype.return_type,
                value=scope.builder.call(
                    fn=scope.runtime.crfunction_call,
                    # CRObject* self, size_t argscount, varargs...
                    args=[callee.value, len(args)] + [arg.value for arg in args]
                ),
                boxed=True,
                scope=scope
            ))
        callee = t.cast(CoralFunction, callee)
        unboxed = callee.unbox()
        boundtype = t.cast(ast.BoundFunctionType, unboxed.boundtype)
        lltype = t.cast(ir.FunctionType, unboxed.lltype)
        if callee.has_globals:
            param_types = lltype.args[1:] # remove the __globals__
        else:
            param_types = lltype.args
        if len(args) != len(param_types):
            raise TypeError(f"{callee.name} expects '{len(param_types)}' arguments, but got {len(args)}")
        crobject_ptr = scope.runtime.crobject_struct.as_pointer()
        raw_args = [
            arg.box().value if param_types[i] == crobject_ptr else arg.unbox().value
            for i, arg in enumerate(args)
        ]
        if callee.has_globals:
            raw_args.insert(0, callee.globals_ptr)
        raw_return_value = scope.builder.call(fn=unboxed.llfunc_ptr, args=raw_args)
        match boundtype.return_type.type:
            case ast.NativeType.INTEGER:
                return CoralInteger(
                    type_=boundtype.return_type,
                    lltype=LL_INT,
                    value=raw_return_value,
                    boxed=False,
                    scope=scope
                )
            case ast.NativeType.BOOLEAN:
                return CoralInteger(
                    type_=boundtype.return_type,
                    lltype=LL_BOOL,
                    value=raw_return_value,
                    boxed=False,
                    scope=scope
                )
            # all types below are boxed in any return
            case _:
                return scope.collect_object(CoralObject.wrap_boxed_value(
                    boundtype=boundtype.return_type,
                    value=raw_return_value,
                    scope=scope
                ))

    def box(self) -> 'CoralFunction':
        if self.boxed: return self
        return CoralFunction(
            type_=self.boundtype,
            lltype=self.scope.runtime.crobject_struct.as_pointer(),
            value=self.value,
            boxed=True,
            scope=self.scope,
            name=self.name,
            llfunc_ptr=None,
            globals_ptr=None,
            has_globals=self.has_globals
        )

    def unbox(self) -> 'CoralFunction':
        if not self.boxed: return self
        lltype: ir.FunctionType = self.scope.runtime.get_llvm_type(self.boundtype)
        if self.has_globals:
            lltype.args = (
                self.scope.runtime.crobject_struct.as_pointer().as_pointer(), # __globals__
                *lltype.args
            )
            globals_ptr = self.scope.runtime.get_function_globals(self.value, self.scope.builder)
        else:
            globals_ptr = None
        return CoralFunction(
            type_=self.boundtype,
            lltype=lltype,
            value=self.value,
            boxed=False,
            scope=self.scope,
            name=self.name,
            llfunc_ptr=self.scope.builder.bitcast(
                self.scope.runtime.get_function_llfp(self.value, self.scope.builder),
                lltype.as_pointer()
            ),
            globals_ptr=globals_ptr,
            has_globals=self.has_globals
        )

    def __hash__(self) -> int:
        return hash((self.name, self.boxed, self.value))

    def __eq__(self, other: object):
        return (
            isinstance(other, CoralFunction) and
            other.name == self.name and
            other.boxed == self.boxed and
            other.value == self.value
        )


_T = t.TypeVar('_T', bound='CoralObject')
class CoralFunctionCompilation:
    """Working context for single function compilation"""

    def __init__(
        self,
        *,
        globals_ptr: ir.NamedValue, # CRObject**
        globals_index: t.Dict[str, ast.GlobalVar],
        return_type: ir.Type,
        return_boxed: bool,
        scope_path: str,
        functions_count: int,
        builder: ir.IRBuilder,
        runtime: CoralRuntime
    ) -> None:
        self.globals_ptr: t.Final = globals_ptr
        self.globals_index: t.Final = globals_index
        self.return_type: t.Final = return_type
        self.return_boxed: t.Final = return_boxed
        self.vars: t.Final[t.Dict[str, CoralObject]] = {}
        self.scope_path: t.Final = scope_path
        self.functions_count: t.Final = functions_count
        self.builder: t.Final = builder
        self.entryblock: t.Final[ir.Block] = builder.block
        self.runtime: t.Final = runtime
        self._gc_size = ir.Constant(LL_INT, 0)
        self._gc_ptr: t.Optional[ir.Instruction] = builder.call(
            fn=runtime.crobjectarray_new,
            args=[self._gc_size],
            name='__gc__'
        )
        self._gc_objects: t.Final[t.Set[CoralObject]] = set()
        self._gc_cleanup_count = 0
        self._returns_count = 0

    def add_local_var(self, name: str, value: CoralObject) -> None:
        if name in self.vars:
            raise ValueError(f"the name '{name}' was already declared")
        self.vars[name] = value

    def get_var(self, name: str) -> CoralObject:
        var = self.vars.get(name, None)
        if var is not None:
            return var
        varindex = self.globals_index.get(name, None)
        if varindex is None:
            raise ValueError(f"the name '{name}' is not defined")
        # load the global var
        globalvar = CoralObject.wrap_boxed_value(
            boundtype=varindex.var.type,
            value=self.builder.load(
                self.builder.gep(
                    self.globals_ptr,
                    indices=[LL_INT(varindex.index)],
                    inbounds=False
                )
            ),
            scope=self
        )
        if globalvar.boundtype.is_static:
            globalvar = globalvar.unbox()
        globalvar.value.name = name
        self.vars[name] = globalvar
        return globalvar

    def collect_object(self, obj: _T) -> _T:
        """Saves the given object in the garbage collection list. This method DOES NOT INCREMENT
        the refcount of that object, but on release it WILL DECREMENT. Thus we assume
        the caller owns a reference.
        """
        if obj.boxed and obj not in self._gc_objects:
            self.builder.call(fn=self.runtime.crobjectarray_push, args=(self._gc_ptr, obj.value))
            self._gc_objects.add(obj)
        return obj

    def handle_return(self, result: _T) -> _T:
        if self.return_boxed:
            result = result.box()
            result.incref()
            self.handle_gc_cleanup()
            self.builder.ret(result.value)
            self._returns_count += 1
        elif result.lltype == self.return_type:
            self.handle_gc_cleanup()
            self.builder.ret(result.value)
            self._returns_count += 1
        else:
            raise TypeError(f"expected return type '{self.return_type}', but got '{result.lltype}'")

    def handle_gc_cleanup(self) -> None:
        """Releases the GC list, this must be called only at the exit of the function"""
        if self._gc_ptr is None:
            raise ValueError("GC was finalized, can't run any new cleanup")
        if len(self._gc_objects) > 0:
            self.builder.call(fn=self.runtime.crobjectarray_release, args=[self._gc_ptr])
            self._gc_cleanup_count += 1

    def handle_gc_finalization(self) -> None:
        # grow the GC list, this is the max size the list will ever need since we dont have any loop
        # every instruction is ran only once per call
        if len(self._gc_objects) > 0:
            self._gc_size.constant = len(self._gc_objects)
        else:
            self.entryblock.instructions.remove(self._gc_ptr)
        self._gc_ptr = None
        self._gc_objects.clear()

    def get_gc_cleanups(self) -> int:
        return self._gc_cleanup_count
    
    def get_returns_count(self) -> int:
        return self._returns_count


class CoralCompiler:
    """Walks over the typed AST and compiles the expressions to LLVM IR"""

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
        target_machine = target.create_target_machine(opt=3)
        backing_mod = llvm.parse_assembly('')
        engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
        return CoralCompiler(program, engine)

    def compile(self) -> t.Callable[[], None]:
        """Compiles the program to machine code with MCJIT and returns a Python callable which runs the
        compiled code when called.
        """
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
        """Compiles the typed AST down to LLVM IR.
        
        If verify is True, it will validate the IR to look for syntatic and semantic errors.
        """
        self._strings = {}
        self._module = ir.Module(self._program.filename, context=ir.Context())
        runtime = CoralRuntime.import_into(self._module)
        main = ir.Function(
            name='__main__',
            module=self._module,
            ftype=ir.FunctionType(return_type=ir.VoidType(), args=[])
        )
        entry_block = main.append_basic_block('entry')
        main_builder = ir.IRBuilder(entry_block)
        main_scope = CoralFunctionCompilation(
            globals_ptr=ir.Constant(runtime.crobject_struct.as_pointer().as_pointer(), 0),
            globals_index={},
            return_type=ir.VoidType(),
            return_boxed=False,
            scope_path='',
            functions_count=0,
            builder=main_builder,
            runtime=runtime
        )
        self._compile_node(self._program.body, main_scope, is_return_branch=False)
        main_scope.handle_gc_cleanup()
        main_scope.handle_gc_finalization()
        main_builder.ret_void()
        if verify:
            llmod = llvm.parse_assembly(str(self._module))
            llmod.verify()
            llmod.close()
        return self._module

    def _compile_node(
        self,
        node: ast.Expression,
        scope: CoralFunctionCompilation,
        is_return_branch: bool=False
    ) -> CoralObject:
        match node:
            case ast.ReferenceExpression():
                return self._may_return_from_function(scope.get_var(node.name), is_return_branch)
            case ast.LiteralIntegerValue(value=value):
                return self._may_return_from_function(
                    CoralInteger(
                        type_=ast.BOUND_INTEGER_TYPE,
                        lltype=LL_INT,
                        value=ir.Constant(LL_INT, value),
                        boxed=False,
                        scope=scope
                    ),
                    is_return_branch
                )
            case ast.LiteralBooleanValue(value=value):
                return self._may_return_from_function(
                    CoralInteger(
                        type_=ast.BOUND_BOOLEAN_TYPE,
                        lltype=LL_BOOL,
                        value=ir.Constant(LL_BOOL, int(value)),
                        boxed=False,
                        scope=scope
                    ),
                    is_return_branch
                )
            case ast.LiteralStringValue(value=value):
                compiledstr = self._compile_raw_string(value)
                return self._may_return_from_function(
                    # box the string right here since we can't do anything with the unboxed version
                    CoralString(
                        type_=ast.BOUND_STRING_TYPE,
                        lltype=LL_CHAR.as_pointer(),
                        # drop the array pointer, we just need a plain char* like pointer
                        value=scope.builder.bitcast(compiledstr, LL_CHAR.as_pointer()),
                        boxed=False,
                        scope=scope
                    ).box(),
                    is_return_branch
                )
            case ast.TupleExpression(first=first, second=second):
                coraltuple = CoralTuple.create_unboxed(
                    first=self._compile_node(first, scope, is_return_branch=False),
                    second=self._compile_node(second, scope, is_return_branch=False),
                    scope=scope
                )
                if not node.boundtype.is_static:
                    coraltuple = coraltuple.box()
                return self._may_return_from_function(coraltuple, is_return_branch)
            case ast.CallExpression(callee=callee, args=args):
                return self._may_return_from_function(
                    CoralFunction.call(
                        scope,
                        self._compile_node(callee, scope, is_return_branch=False),
                        [self._compile_node(arg, scope, is_return_branch=False) for arg in args]
                    ),
                    is_return_branch
                )
            case ast.FirstExpression(value=value):
                return self._may_return_from_function(
                    CoralTuple.get_first(self._compile_node(value, scope, is_return_branch=False)),
                    is_return_branch
                )
            case ast.SecondExpression(value=value):
                return self._may_return_from_function(
                    CoralTuple.get_second(self._compile_node(value, scope, is_return_branch=False)),
                    is_return_branch
                )
            case ast.PrintExpression(value=value):
                return self._may_return_from_function(
                    self._compile_node(value, scope, is_return_branch=False).print(),
                    is_return_branch
                )
            case ast.BinaryExpression():
                return self._compile_binary_expression(node, scope)
            case ast.ConditionalExpression():
                return self._compile_condition(node, scope, is_return_branch=is_return_branch)
            case ast.FunctionExpression():
                return self._compile_function(node, scope)
            case ast.LetExpression():
                return self._compile_declaration(node, scope, is_return_branch=is_return_branch)
            case _:
                raise ValueError(f"{node} is not supported yet")

    def _compile_function(self, node: ast.FunctionExpression, scope: CoralFunctionCompilation) -> CoralFunction:
        """Compiles the function definition and returns a function object ready to be called."""

        if node.binding is not None:
            myname = node.binding.name
            llname = f'{scope.scope_path}.{node.binding.name}'
        else:
            myname = None
            llname = f'{scope.scope_path}.closure.{scope.functions_count + 1}'
        crobject_struct_ptr = scope.runtime.crobject_struct.as_pointer()
        boundtype = t.cast(ast.BoundFunctionType, node.boundtype)
        has_globals = len(node.scope.globals) > 0
        llfunc_type: ir.FunctionType = scope.runtime.get_llvm_type(boundtype)
        if has_globals:
            llfunc_type.args = (
                # first argument of the function is the __globals__ array, aka CRObject**
                crobject_struct_ptr.as_pointer(),
                *llfunc_type.args
            )
        llfunc = ir.Function(name=llname, ftype=llfunc_type, module=self._module)
        # name the parameters
        if has_globals:
            llfunc.args = tuple([
                ir.Argument(llfunc, llfunc_type.args[0], name='__globals__')
            ] + [
                ir.Argument(llfunc, llfunc_type.args[i + 1], name=param.name)
                for i, param in enumerate(node.params)
            ])
        else:
            llfunc.args = tuple([
                ir.Argument(llfunc, llfunc_type.args[i], name=param.name)
                for i, param in enumerate(node.params)
            ])
        child_entry = llfunc.append_basic_block('entry')
        child_builder = ir.IRBuilder(child_entry)
        if has_globals:
            child_globals_ptr = llfunc.args[0]
        else:
            child_globals_ptr = ir.Constant(crobject_struct_ptr.as_pointer(), 0)
        child_scope = CoralFunctionCompilation(
            globals_ptr=child_globals_ptr,
            globals_index=node.scope.globals,
            return_type=llfunc_type.return_type,
            return_boxed=llfunc_type.return_type == crobject_struct_ptr,
            scope_path=llname,
            functions_count=0,
            builder=child_builder,
            runtime=scope.runtime
        )
        # set the parameters as local variables
        if has_globals:
            llfunc_real_params = llfunc.args[1:]
        else:
            llfunc_real_params = llfunc.args
        for i, param in enumerate(node.params):
            match param.boundtype.type:
                case ast.NativeType.INTEGER:
                    paramvar = CoralInteger(
                        type_=ast.BOUND_INTEGER_TYPE,
                        lltype=LL_INT,
                        value=llfunc_real_params[i],
                        boxed=False,
                        scope=child_scope
                    )
                case ast.NativeType.BOOLEAN:
                    paramvar = CoralInteger(
                        type_=ast.BOUND_BOOLEAN_TYPE,
                        lltype=LL_BOOL,
                        value=llfunc_real_params[i],
                        boxed=False,
                        scope=child_scope
                    )
                # all parameter types below are boxed
                case ast.NativeType.STRING:
                    paramvar = CoralString(
                        type_=ast.BOUND_STRING_TYPE,
                        lltype=llfunc_real_params[i].type,
                        value=llfunc_real_params[i],
                        boxed=True,
                        scope=child_scope
                    )
                case ast.NativeType.TUPLE:
                    paramvar = CoralTuple(
                        type_=param.boundtype,
                        lltype=llfunc_real_params[i].type,
                        value=llfunc_real_params[i],
                        boxed=True,
                        scope=child_scope
                    )
                case ast.NativeType.FUNCTION:
                    paramvar = CoralFunction(
                        type_=param.boundtype,
                        lltype=llfunc_real_params[i].type,
                        value=llfunc_real_params[i],
                        boxed=True,
                        scope=child_scope
                    )
                case _:
                    paramvar = CoralObject(
                        type_=ast.BOUND_UNDEFINED_TYPE,
                        lltype=llfunc_real_params[i].type,
                        value=llfunc_real_params[i],
                        boxed=True,
                        scope=child_scope
                    )
            if param.boundtype.is_static:
                paramvar = paramvar.unbox()
            child_scope.add_local_var(param.name, paramvar)
        return_value = self._compile_node(node.body, child_scope, is_return_branch=True)
        if child_scope.get_returns_count() == 0:
            child_scope.handle_return(return_value)
        child_scope.handle_gc_finalization()
        scope.functions_count += 1

        # create the variadic args wrapper, we need this for the dynamic call though CRFunction_call()
        llfunc_vararg_type = ir.FunctionType(
            args=(
                crobject_struct_ptr.as_pointer(), # __globals__
                crobject_struct_ptr.as_pointer()  # __varargs__
            ),
            return_type=crobject_struct_ptr
        )
        llfunc_vararg = ir.Function(
            name=f'{llname}__varargs',
            ftype=llfunc_vararg_type,
            module=self._module,
        )
        llfunc_vararg.args = (
            ir.Argument(llfunc_vararg, llfunc_vararg_type.args[0], name='__globals__'),
            ir.Argument(llfunc_vararg, llfunc_vararg_type.args[1], name='__varargs__')
        )
        vararg_builder = ir.IRBuilder(llfunc_vararg.append_basic_block('entry'))
        vararg_scope = CoralFunctionCompilation(
            globals_ptr=llfunc_vararg.args[0],
            globals_index={},
            return_type=llfunc_vararg_type.return_type,
            return_boxed=True,
            scope_path='',
            functions_count=0,
            builder=vararg_builder,
            runtime=scope.runtime
        )
        vararg_forward = []
        for i, param in enumerate(node.params):
            # we unbox integers and booleans
            vararg_arg = vararg_builder.load(
                vararg_builder.gep(
                    ptr=llfunc_vararg.args[1], # __varargs__
                    indices=[ir.Constant(LL_INT, i)],
                    inbounds=False
                )
            )
            if param.boundtype.type == ast.NativeType.INTEGER or param.boundtype.type == ast.NativeType.BOOLEAN:
                vararg_forward.append(CoralInteger(
                    type_=param.boundtype,
                    lltype=LL_INT,
                    value=vararg_arg,
                    boxed=True,
                    scope=vararg_scope
                ).unbox().value)
            else:
                vararg_forward.append(vararg_arg)
        if has_globals:
            vararg_forward.insert(0, llfunc_vararg.args[0]) # __globals__
        # box the return if needed since the vararg wrappers returns CRObject*
        if llfunc_type.return_type != llfunc_vararg_type.return_type:
            if boundtype.return_type.type == ast.NativeType.INTEGER:
                vararg_builder.ret(CoralInteger(
                    type_=ast.BOUND_INTEGER_TYPE,
                    lltype=LL_INT,
                    value=vararg_builder.call(fn=llfunc, args=vararg_forward),
                    boxed=False,
                    scope=vararg_scope
                ).box().value)
            elif boundtype.return_type.type == ast.NativeType.BOOLEAN:
                vararg_builder.ret(CoralInteger(
                    type_=ast.BOUND_BOOLEAN_TYPE,
                    lltype=LL_BOOL,
                    value=vararg_builder.call(fn=llfunc, args=vararg_forward),
                    boxed=False,
                    scope=vararg_scope
                ).box().value)
            else:
                raise TypeError(f"the function {boundtype} must have its return boxed")
        else:
            vararg_builder.ret(vararg_builder.call(fn=llfunc, args=vararg_forward))
        vararg_scope.handle_gc_finalization()

        # create a callable function from the definition above

        coral_llfunc = scope.builder.call(
            fn=scope.runtime.crfunction_new,
            args=(
                LL_INT(len(node.scope.globals)),
                LL_INT16(len(node.params)),
                # we pass the vararg wrapper as the dynamic function
                scope.builder.bitcast(llfunc_vararg, LL_CHAR.as_pointer()),
                # we save this for later unboxing
                scope.builder.bitcast(llfunc, LL_CHAR.as_pointer()),
            ),
            name=myname if myname is not None else ''
        )
        # here we pass the inherited scope to the newly created child function
        # node.scope.globals contains all the globals it inherits from us
        for varindex in node.scope.globals.values():
            scope.builder.call(
                fn=scope.runtime.crfunction_set_global,
                args=(
                    coral_llfunc,
                    LL_INT(varindex.index),
                    # handle recursive functions reference
                    # functions have name only when bound to a variable
                    scope.get_var(varindex.var.name).box().value
                    if myname is None or varindex.var.name != myname
                    else coral_llfunc
                )
            )
        return scope.collect_object(CoralFunction(
            type_=node.boundtype,
            lltype=llfunc_type,
            value=coral_llfunc,
            boxed=True,
            scope=scope,
            name=myname,
            has_globals=has_globals
        ))

    def _may_return_from_function(self, result: _T, is_return_branch: bool) -> _T:
        """Called by terminal AST nodes to signal possible values of a function return.
        
        Actually only IF expressions may include implicit returns, but only when they are immediate
        child of a Function or transitively through another IF or Let which is child of the former.
        """
        if is_return_branch:
            return result.scope.handle_return(result)
        return result

    def _compile_condition(
        self,
        node: ast.ConditionalExpression,
        scope: CoralFunctionCompilation,
        is_return_branch: bool=False
    ) -> CoralObject:
        cond = self._compile_node(node.cond, scope, is_return_branch=False)
        with scope.builder.if_else(cond.value) as (then_branch, else_branch):
            with then_branch:
                then_block = scope.builder._block
                then = self._compile_node(node.then, scope, is_return_branch=is_return_branch)
                if not node.boundtype.is_static:
                    then = then.box()
            with else_branch:
                else_block = scope.builder._block
                otherwise = self._compile_node(node.alternate, scope, is_return_branch=is_return_branch)
                if not node.boundtype.is_static:
                    otherwise = otherwise.box()
        # we dont have any value if we are part of a return branch, the value is returned by a
        # explicit "ret" from the bottom of the AST.
        if not is_return_branch:
            return then.merge_branch(
                then_value=then,
                then_block=then_block,
                else_value=otherwise,
                else_block=else_block,
                scope=scope
            )
        else:
            return CoralInteger(type_=ast.BOUND_INTEGER_TYPE, lltype=LL_INT, value=ir.Constant(LL_INT, 0), scope=scope)

    def _compile_declaration(
        self,
        node: ast.LetExpression,
        scope: CoralFunctionCompilation,
        is_return_branch: bool=False
    ) -> CoralObject:
        obj = self._compile_node(node.value, scope, is_return_branch=False)
        if node.binding is not None:
            if node.binding.boundtype.is_static:
                obj = obj.unbox()
            scope.add_local_var(node.binding.name, obj)
            obj.value.name = node.binding.name
        return self._compile_node(node.next, scope, is_return_branch=is_return_branch)

    def _compile_binary_expression(self, node: ast.BinaryExpression, scope: CoralFunctionCompilation) -> CoralObject:
        left = self._compile_node(node.left, scope, is_return_branch=False)
        right = self._compile_node(node.right, scope, is_return_branch=False)
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
            
    def _compile_raw_string(self, value: str) -> ir.GlobalVariable:
        """Creates a global constant for the given Python string if it doesn't exist.
        Only ASCII strings are supported. All strings will be null-byte terminated.
        """
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
