import typing as t
import ctypes as c
import importlib.resources
from llvmlite import ir, binding as llvm # type: ignore
from coral import ast


llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()
llvm.check_jit_execution()
with importlib.resources.as_file(
    importlib.resources.files('coral').joinpath('libcoral.so')
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
        crobject_incref.linkage = 'external'
        crobject_decref = ir.Function(
            name='CRObject_decref',
            module=mod,
            ftype=ir.FunctionType(
                return_type=ir.VoidType(),
                args=[crobject_struct_ptr]
            )
        )
        crobject_decref.linkage = 'external'

        crobject_binary_operator_func = ir.FunctionType(
            return_type=crobject_struct_ptr,
            args=[crobject_struct_ptr, crobject_struct_ptr]
        )
        crobject_add = ir.Function(
            name='CRObject_add',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_add.linkage = 'external'
        crobject_add.attributes.add('readonly')
        crobject_sub = ir.Function(
            name='CRObject_sub',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_sub.linkage = 'external'
        crobject_sub.attributes.add('readonly')
        crobject_mul = ir.Function(
            name='CRObject_mul',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_mul.linkage = 'external'
        crobject_mul.attributes.add('readonly')
        crobject_div = ir.Function(
            name='CRObject_div',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_div.linkage = 'external'
        crobject_div.attributes.add('readonly')
        crobject_mod = ir.Function(
            name='CRObject_mod',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_mod.linkage = 'external'
        crobject_mod.attributes.add('readonly')
        crobject_lt = ir.Function(
            name='CRObject_lessThan',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_lt.linkage = 'external'
        crobject_lt.attributes.add('readonly')
        crobject_lte = ir.Function(
            name='CRObject_lessOrEqual',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_lte.linkage = 'external'
        crobject_lte.attributes.add('readonly')
        crobject_gt = ir.Function(
            name='CRObject_greaterThan',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_gt.linkage = 'external'
        crobject_gt.attributes.add('readonly')
        crobject_gte = ir.Function(
            name='CRObject_greaterOrEqual',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_gte.linkage = 'external'
        crobject_gte.attributes.add('readonly')
        crobject_and = ir.Function(
            name='CRObject_and',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_and.linkage = 'external'
        crobject_and.attributes.add('readonly')
        crobject_or = ir.Function(
            name='CRObject_or',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_or.linkage = 'external'
        crobject_or.attributes.add('readonly')
        crobject_equals = ir.Function(
            name='CRObject_equals',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_equals.linkage = 'external'
        crobject_equals.attributes.add('readonly')
        crobject_notequals = ir.Function(
            name='CRObject_notEquals',
            module=mod,
            ftype=crobject_binary_operator_func
        )
        crobject_notequals.linkage = 'external'
        crobject_notequals.attributes.add('readonly')

        crstring_new = ir.Function(
            name='CRString_new',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crobject_struct_ptr,
                args=[LL_CHAR.as_pointer(), LL_INT]
            )
        )
        crstring_new.linkage = 'external'

        crobject_print = ir.Function(
            name='CRObject_print',
            module=mod,
            ftype=ir.FunctionType(
                return_type=ir.VoidType(),
                args=[crobject_struct_ptr]
            )
        )
        crobject_print.linkage = 'external'

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
        crtuple_new.linkage = 'external'
        crtuple_get_first = ir.Function(
            name='CRTuple_getFirst',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crobject_struct_ptr,
                args=[crobject_struct_ptr]
            )
        )
        crtuple_get_first.linkage = 'external'
        crtuple_get_first.attributes.add('readonly')
        crtuple_get_second = ir.Function(
            name='CRTuple_getSecond',
            module=mod,
            ftype=ir.FunctionType(
                return_type=crobject_struct_ptr,
                args=[crobject_struct_ptr]
            )
        )
        crtuple_get_second.linkage = 'external'
        crtuple_get_second.attributes.add('readonly')

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
        crobjectarray_new.linkage = 'external'
        crobjectarray_push = ir.Function(
            name='CRObjectArray_push',
            module=mod,
            ftype=ir.FunctionType(
                args=[crobjectarray_struct.as_pointer(), crobject_struct_ptr],
                return_type=ir.VoidType()
            )
        )
        crobjectarray_push.linkage = 'external'
        crobjectarray_release = ir.Function(
            name='CRObjectArray_release',
            module=mod,
            ftype=ir.FunctionType(
                args=[crobjectarray_struct.as_pointer()],
                return_type=ir.VoidType()
            )
        )
        crobjectarray_release.linkage = 'external'

        crfunction_struct = mod.context.get_identified_type('struct.CRFunction')
        crfunction_fp = ir.FunctionType( # CRObject* (*fp) (CRObject**, CRObject**)
            args=(crobject_struct_ptr.as_pointer(), crobject_struct_ptr.as_pointer()),
            return_type=crobject_struct_ptr
        ).as_pointer()
        crfunction_struct.set_body(
            LL_INT16,                          # unsigned short arity
            crobjectarray_struct.as_pointer(), # CRObjectArray* globals
            crfunction_fp
        )
        crfunction_new = ir.Function(
            name='CRFunction_new',
            module=mod,
            ftype=ir.FunctionType(
                args=[LL_INT, LL_INT16, crfunction_fp],
                return_type=crobject_struct_ptr
            )
        )
        crfunction_new.linkage = 'external'
        crfunction_set_global = ir.Function(
            name='CRFunction_setGlobal',
            module=mod,
            ftype=ir.FunctionType(
                args=[crobject_struct_ptr, LL_INT, crobject_struct_ptr],
                return_type=ir.VoidType()
            )
        )
        crfunction_set_global.linkage = 'external'
        crfunction_call = ir.Function(
            name='CRFunction_call',
            module=mod,
            ftype=ir.FunctionType(
                args=[crobject_struct_ptr, LL_INT],
                return_type=crobject_struct_ptr,
                var_arg=True
            )
        )
        crfunction_call.linkage = 'external'

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
            crfunction_call=crfunction_call
        )

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
                params = []
                for param in boundtype.params:
                    match param.type:
                        case ast.NativeType.INTEGER:
                            params.append(LL_INT)
                        case ast.NativeType.BOOLEAN:
                            params.append(LL_BOOL)
                        case _:
                            params.append(self.crobject_struct.as_pointer())
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

    def box(self) -> t.Self:
        """Creates a NEW boxed version of this object if it is UNBOXED. Returns the boxed object.
        
        Returns itself if it's already boxed. Boxing MUST be tracked by the GC.
        """
        if self.boxed:
            return self
        raise NotImplementedError

    def unbox(self) -> t.Self:
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
            case ast.NativeType.FUNCTION:
                # we also can't do static call dispatch for functions loaded from raw memory address
                if not isinstance(boundtype, CoralFunctionType):
                    boundtype = CoralFunctionType(
                        boundtype.params,
                        return_type=boundtype.return_type
                    )
                return CoralFunction(
                    type_=boundtype,
                    lltype=value.type,
                    value=value,
                    boxed=True,
                    scope=scope
                )
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
        boundtype: ast.IBoundType,
        then_value: 'CoralObject',
        then_block: ir.Block,
        else_value: 'CoralObject',
        else_block: ir.Block,
        scope: 'CoralFunctionCompilation'
    ) -> 'CoralObject':
        """Merge values which came from conditional branches. Both values must have the same type."""
        if then_value.boxed != else_value.boxed:
            raise TypeError(f"both sides of a IF branch must be either all boxed or unboxed")
        if then_value.lltype != else_value.lltype:
            raise TypeError(f"both sides of a IF branch must have the same LLVM type, but got '{then_value.lltype}' and '{else_value.lltype}'")
        if not then_value.boxed and then_value.boundtype != else_value.boundtype:
            raise TypeError(f"both sides of a unboxed IF branch must have the same bound type, but got '{then_value.boundtype}' and '{else_value.boundtype}'")
        result = scope.builder.phi(then_value.lltype)
        result.add_incoming(then_value.value, then_block)
        result.add_incoming(else_value.value, else_block)
        return cls(
            type_=boundtype,
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
    def add(cls, self: CoralObject, other: CoralObject) -> t.Union['CoralInteger', 'CoralString']:
        if self.boundtype.type == ast.NativeType.INTEGER and other.boundtype.type == ast.NativeType.INTEGER:
            return CoralInteger(
                type_=ast.BOUND_INTEGER_TYPE,
                lltype=LL_INT,
                value=self.scope.builder.add(self.unbox().value, other.unbox().value),
                boxed=False,
                scope=self.scope
            )
        if self.boundtype.type == ast.NativeType.STRING or other.boundtype.type == ast.NativeType.STRING:
            return self.scope.collect_object(CoralString(
                type_=ast.BOUND_STRING_TYPE,
                lltype=self.scope.runtime.crobject_add.ftype.return_type,
                value=self.scope.builder.call(
                    fn=self.scope.runtime.crobject_add,
                    args=(self.box().value, other.box().value)
                ),
                boxed=True,
                scope=self.scope
            ))
        # it may return a string, that's why we collect here
        return self.scope.collect_object(CoralObject(
            type_=ast.BINOP_ADD_TYPES,
            lltype=self.scope.runtime.crobject_add.ftype.return_type,
            value=self.scope.builder.call(
                fn=self.scope.runtime.crobject_add,
                args=(self.box().value, other.box().value)
            ),
            boxed=True,
            scope=self.scope
        ))

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

    def unbox(self) -> t.Self:
        # we dont unbox strings since we can't do anything meaningful with it
        return self


class CoralTuple(CoralObject):

    def __init__(
        self,
        type_: ast.IBoundType,
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
        self._first: t.Final = first
        self._second: t.Final = second

    @property
    def ensure_first(self) -> CoralObject:
        if self._first is None:
            raise ValueError("missing first member of tuple")
        return self._first
    
    @property
    def ensure_second(self) -> CoralObject:
        if self._second is None:
            raise ValueError("missing second member of tuple")
        return self._second

    def instance_get_first(self) -> CoralObject:
        if not self.boxed:
            return self.ensure_first
        return CoralObject.wrap_boxed_value(
            boundtype=self.boundtype.generics[0],
            value=self.scope.runtime.get_tuple_first(self.value, self.scope.builder),
            scope=self.scope
        )

    def instance_get_second(self) -> CoralObject:
        if not self.boxed:
            return self.ensure_second
        return CoralObject.wrap_boxed_value(
            boundtype=self.boundtype.generics[1],
            value=self.scope.runtime.get_tuple_second(self.value, self.scope.builder),
            scope=self.scope
        )

    def box(self) -> 'CoralTuple':
        if self.boxed: return self
        first = self.ensure_first.box()
        second = self.ensure_second.box()
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
        boundtype: ast.IBoundType,
        then_value: 'CoralObject',
        then_block: ir.Block,
        else_value: 'CoralObject',
        else_block: ir.Block,
        scope: 'CoralFunctionCompilation'
    ) -> CoralObject:
        if (boundtype.type != ast.NativeType.TUPLE):
            return CoralObject.merge_branch(
                boundtype=boundtype,
                then_value=then_value,
                then_block=then_block,
                else_value=else_value,
                else_block=else_block,
                scope=scope
            )
        if then_value.boundtype.type != ast.NativeType.TUPLE or else_value.boundtype.type != ast.NativeType.TUPLE:
            raise TypeError(f"expected both sides of the IF branch to be tuples, but got '{then_value.boundtype}' and '{else_value.boundtype}'")
        if then_value.boxed != else_value.boxed:
            raise TypeError(f"both sides of a IF branch must be either all boxed or unboxed")
        if then_value.lltype != else_value.lltype:
            raise TypeError(f"both sides of a IF branch must have the same LLVM type, but got '{then_value.lltype}' and '{else_value.lltype}'")
        then_value = t.cast(CoralTuple, then_value)
        else_value = t.cast(CoralTuple, else_value)
        if not then_value.boxed:
            first = then_value.ensure_first.merge_branch(
                then_value=then_value.ensure_first,
                then_block=then_block,
                else_value=else_value.ensure_first,
                else_block=else_block,
                scope=scope
            )
            second = then_value.ensure_second.merge_branch(
                then_value=then_value.ensure_second,
                then_block=then_block,
                else_value=else_value.ensure_second,
                else_block=else_block,
                scope=scope
            )
            return cls(
                type_=boundtype,
                lltype=ir.VoidType(),
                first=first,
                second=second,
                boxed=False,
                scope=scope,
                value=ir.Constant(LL_CHAR, 0) # not used
            ) 
        else:
            return super().merge_branch(
                boundtype=boundtype,
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
        return hash((self._first, self._second, self.value, self.boxed))

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CoralTuple) and
            self.boxed == other.boxed and
            self._first == other._first and
            self._second == other._second
        )


class CoralFunctionType(ast.BoundFunctionType):
    """Extends BoundFunctionType to add info about the compiled LLVM function"""

    def __init__(
        self,
        params: t.Sequence[ast.IBoundType],
        return_type: ast.IBoundType,
        param_names: t.Optional[t.Sequence[str]] = None,
        llfunc: t.Optional[ir.Function] = None,
        has_globals: bool = False,
        name: t.Optional[str] = None
    ) -> None:
        super().__init__(params, return_type)
        self.param_names: t.Final = param_names
        self.llfunc: t.Final = llfunc
        self.has_globals: t.Final = has_globals
        self.name: t.Final = name

    @property
    def ll_return_type(self) -> t.Optional[ir.Type]:
        if self.llfunc is not None:
            return self.llfunc.ftype.return_type

    def __eq__(self, value: object) -> bool:
        return (
            super().__eq__(value) and
            isinstance(value, CoralFunctionType) and
            value.name == self.name and
            value.has_globals == self.has_globals and
            value.llfunc == self.llfunc
        )

    def __hash__(self) -> int:
        return hash(self.llfunc)

class CoralFunction(CoralObject):
    """Functions are always "boxed", but the call to the native function definition can be directly
    dispatched from the compiled code if we know the function signature at compile time
    (i.e. BoundType is static).

    box() here does nothing memory wise, unbox() loads the __globals__ and the native function pointer
    from the CRFunction struct.

    Functions which return boxed values (aka CRObject*) must return it with the refcount incremented.
    The function CALLER always owns a reference to the returned boxed values, thus it will be collected
    by its GC list. The CALLED function OWNS a reference to any of the arguments, thus it will be
    collect by its GC list.

    To sum up the calling convention is as follow:
    - The CALLER pass arguments in the same order and with the same types as defined in the CALLEE signature
    - The CALLEE owns the references to the arguments
    - The CALLEE must return a value of the same type as defined by its signature
    - The CALLEE must kept the return value live after the return
    - The CALLER owns the reference to the returned value
    - The CALLEE is responsible for cleaning up the arguments
    - The CALLER is responsible for cleaning up the retuned value
    """

    def __init__(
        self,
        *,
        type_: CoralFunctionType,
        lltype: ir.FunctionType,
        value: ir.Value,
        boxed: bool,
        scope: 'CoralFunctionCompilation',
        globals_ptr: t.Optional[ir.Value] = None
    ) -> None:
        super().__init__(type_, lltype, value, boxed, scope)
        self.globals_ptr: t.Final = globals_ptr

    @property
    def function_type(self) -> CoralFunctionType:
        return t.cast(CoralFunctionType, self.boundtype)

    @classmethod
    def call(
        cls,
        scope: 'CoralFunctionCompilation',
        callee: CoralObject,
        args: t.List[CoralObject],
        *,
        tail: bool=False
    ) -> CoralObject:
        if callee.boundtype.type != ast.NativeType.FUNCTION:
            # the callee needs a new reference to all the arguments, including self
            callee = callee.box()
            callee.incref()
            varargs = []
            for arg in args:
                arg = arg.box()
                arg.incref()
                varargs.append(arg.value)
            if tail:
                scope.handle_gc_cleanup()
            return_value = CoralObject(
                type_=ast.BOUND_UNDEFINED_TYPE,
                lltype=scope.runtime.crfunction_call.ftype.return_type,
                value=scope.builder.call(
                    fn=scope.runtime.crfunction_call,
                    # CRObject* self, size_t argscount, varargs...
                    args=[callee.value, LL_INT(len(args))] + varargs,
                    tail='musttail' if tail else False
                ),
                boxed=True,
                scope=scope
            )
            if tail:
                return return_value
            return scope.collect_object(return_value)
        callee = t.cast(CoralFunction, callee)
        boundtype = callee.function_type
        # if we don't know the static function, we need to dispatch the call dynamically
        if boundtype.llfunc is None:
            callee = callee.box()
            callee.incref()
            varargs = []
            for arg in args:
                arg = arg.box()
                arg.incref()
                varargs.append(arg.value)
            if tail:
                scope.handle_gc_cleanup()
            return_value = CoralObject.wrap_boxed_value(
                boundtype=boundtype.return_type,
                value=scope.builder.call(
                    fn=scope.runtime.crfunction_call,
                    # CRObject* self, size_t argscount, varargs...
                    args=[callee.value, LL_INT(len(args))] + varargs,
                    tail='musttail' if tail else False
                ),
                scope=scope
            )
            if tail:
                return return_value
            return scope.collect_object(return_value)
        callee = callee.unbox()
        lltype = t.cast(ir.FunctionType, boundtype.llfunc.ftype)
        if boundtype.has_globals:
            param_types = lltype.args[1:] # remove the __globals__
        else:
            param_types = lltype.args
        if len(args) != len(param_types):
            raise TypeError(f"{boundtype.name} expects '{len(param_types)}' arguments, but got {len(args)}")
        crobject_ptr = scope.runtime.crobject_struct.as_pointer()
        raw_args = []
        for i, arg in enumerate(args):
            if param_types[i] == crobject_ptr:
                arg = arg.box()
                arg.incref()
                raw_args.append(arg.value)
            else:
                raw_args.append(arg.unbox().value)
        if boundtype.has_globals:
            raw_args.insert(0, callee.globals_ptr)
        if tail:
            scope.handle_gc_cleanup()
        raw_return_value = scope.builder.call(
            fn=boundtype.llfunc,
            args=raw_args,
            tail='musttail' if tail else False
        )
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
                return_value = CoralObject.wrap_boxed_value(
                    boundtype=boundtype.return_type,
                    value=raw_return_value,
                    scope=scope
                )
                if tail:
                    return return_value
                return scope.collect_object(return_value)

    @classmethod
    def merge_branch(
        cls,
        *,
        boundtype: ast.IBoundType,
        then_value: CoralObject,
        then_block: ir.Block,
        else_value: CoralObject,
        else_block: ir.Block,
        scope: 'CoralFunctionCompilation'
    ) -> CoralObject:
        if boundtype.type != ast.NativeType.FUNCTION:
            return CoralObject.merge_branch(
                boundtype=boundtype,
                then_value=then_value,
                then_block=then_block,
                else_value=else_value,
                else_block=else_block,
                scope=scope
            )
        if then_value.boundtype.type != ast.NativeType.FUNCTION or else_value.boundtype.type != ast.NativeType.FUNCTION:
            raise TypeError(f"expected both sides of the IF branch to be functions, but got '{then_value.boundtype}' and '{else_value.boundtype}'")
        then_value = t.cast(CoralFunction, then_value)
        else_value = t.cast(CoralFunction, else_value)
        if then_value.function_type == else_value.function_type:
            return super().merge_branch(
                boundtype=then_value.function_type,
                then_value=then_value,
                then_block=then_block,
                else_value=else_value,
                else_block=else_block,
                scope=scope
            )
        return super().merge_branch(
            boundtype=CoralFunctionType(
                params=boundtype.params,
                return_type=boundtype.return_type
            ),
            then_value=then_value,
            then_block=then_block,
            else_value=else_value,
            else_block=else_block
        )

    def box(self) -> 'CoralFunction':
        if self.boxed: return self
        return CoralFunction(
            type_=self.function_type,
            lltype=self.scope.runtime.crobject_struct.as_pointer(),
            value=self.value,
            boxed=True,
            scope=self.scope,
            globals_ptr=None
        )

    def unbox(self) -> 'CoralFunction':
        if not self.boxed: return self
        # we need the globals ptr only if we can do static call dispatch
        boundtype = self.function_type
        if boundtype.llfunc is not None and boundtype.has_globals:
            globals_ptr = self.scope.runtime.get_function_globals(self.value, self.scope.builder)
        else:
            globals_ptr = None
        return CoralFunction(
            type_=boundtype,
            lltype=self.value.type,
            value=self.value,
            boxed=False,
            scope=self.scope,
            globals_ptr=globals_ptr
        )

    def __hash__(self) -> int:
        return hash((self.boundtype, self.boxed, self.value))

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CoralFunction) and
            other.boundtype == self.boundtype and
            other.boxed == self.boxed and
            other.value == self.value
        )


_T = t.TypeVar('_T', bound=CoralObject)
class CoralFunctionCompilation:
    """Working context for single function compilation"""

    def __init__(
        self,
        *,
        globals_ptr: ir.NamedValue, # CRObject**
        globals_index: t.Dict[str, ast.ScopeVar],
        function_type: CoralFunctionType,
        returns_boxed: bool,
        scope_path: str,
        functions_count: int,
        builder: ir.IRBuilder,
        runtime: CoralRuntime
    ) -> None:
        self.globals_ptr: t.Final = globals_ptr
        self.globals_index: t.Final = globals_index
        self.function_type: t.Final = function_type
        self.returns_boxed: t.Final = returns_boxed
        self.vars: t.Final[t.Dict[str, CoralObject]] = {}
        self.scope_path: t.Final = scope_path
        self.functions_count = functions_count
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

    @property
    def return_type(self) -> ir.Type:
        return self.function_type.llfunc.ftype.return_type

    def add_local_var(self, name: str, value: CoralObject) -> None:
        if name in self.vars:
            raise ValueError(f"the name '{name}' was already declared")
        self.vars[name] = value

    def get_var(self, name: str) -> CoralObject:
        var = self.vars.get(name, None)
        if var is not None:
            return var
        raise ValueError(f"the name '{name}' is not defined")

    def load_params(self) -> None:
        """Loads the arguments into the local vars list. It must be done before loading the globals."""
        if self.function_type.has_globals:
            llfunc_real_params = self.function_type.llfunc.args[1:]
        else:
            llfunc_real_params = self.function_type.llfunc.args
        for i, param in enumerate(self.function_type.params):
            paramvar: CoralObject
            match param.type:
                case ast.NativeType.INTEGER:
                    paramvar = CoralInteger(
                        type_=ast.BOUND_INTEGER_TYPE,
                        lltype=LL_INT,
                        value=llfunc_real_params[i],
                        boxed=False,
                        scope=self
                    )
                case ast.NativeType.BOOLEAN:
                    paramvar = CoralInteger(
                        type_=ast.BOUND_BOOLEAN_TYPE,
                        lltype=LL_BOOL,
                        value=llfunc_real_params[i],
                        boxed=False,
                        scope=self
                    )
                # all parameter types below are boxed
                case ast.NativeType.STRING:
                    paramvar = CoralString(
                        type_=ast.BOUND_STRING_TYPE,
                        lltype=llfunc_real_params[i].type,
                        value=llfunc_real_params[i],
                        boxed=True,
                        scope=self
                    )
                case ast.NativeType.TUPLE:
                    paramvar = CoralTuple(
                        type_=param,
                        lltype=llfunc_real_params[i].type,
                        value=llfunc_real_params[i],
                        boxed=True,
                        scope=self
                    )
                case ast.NativeType.FUNCTION:
                    boundfunc = t.cast(ast.BoundFunctionType, param)
                    paramvar = CoralFunction(
                        # we can't do static call dispatch for functions passed through parameters
                        type_=CoralFunctionType(
                            params=boundfunc.params,
                            return_type=boundfunc.return_type
                        ),
                        lltype=llfunc_real_params[i].type,
                        value=llfunc_real_params[i],
                        boxed=True,
                        scope=self
                    )
                case _:
                    paramvar = CoralObject(
                        type_=ast.BOUND_UNDEFINED_TYPE,
                        lltype=llfunc_real_params[i].type,
                        value=llfunc_real_params[i],
                        boxed=True,
                        scope=self
                    )
            # collect the boxed arguments as mandates the calling convention
            if paramvar.boxed:
                self.collect_object(paramvar)
            if param.is_static:
                paramvar = paramvar.unbox()
            self.add_local_var(self.function_type.param_names[i], paramvar)

    def load_globals(self) -> None:
        """Loads the inherited globals into the local vars list"""
        for varindex in self.globals_index.values():
            if varindex.name in self.vars:
                continue
            # globals are always boxed, but we can unbox them if we know their type
            globalvar = CoralObject.wrap_boxed_value(
                boundtype=varindex.type,
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
            globalvar.value.name = varindex.name
            self.vars[varindex.name] = globalvar

    def collect_object(self, obj: _T) -> _T:
        """Saves the given object in the garbage collection list. This method DOES NOT INCREMENT
        the refcount of that object, but on release it WILL DECREMENT. Thus we assume
        the caller owns a reference.
        """
        if obj.boxed and obj not in self._gc_objects:
            self.builder.call(fn=self.runtime.crobjectarray_push, args=(self._gc_ptr, obj.value))
            self._gc_objects.add(obj)
        return obj

    def handle_return_with_value(self, result: CoralObject) -> CoralObject:
        if self.returns_boxed:
            result = result.box()
            result.incref()
            self.handle_gc_cleanup()
            self.builder.ret(result.value)
            return result
        elif result.lltype == self.function_type.llfunc.ftype.return_type:
            self.handle_gc_cleanup()
            self.builder.ret(result.value)
            return result
        else:
            raise TypeError(f"expected return type '{self.function_type.llfunc.ftype.return_type}', but got '{result.lltype}'")

    def handle_gc_cleanup(self) -> None:
        """Releases the GC list, this must be called only at the exit of the function"""
        if self._gc_ptr is None:
            raise ValueError("GC was finalized, can't run any new cleanup")
        if len(self._gc_objects) > 0:
            self.builder.call(fn=self.runtime.crobjectarray_release, args=[self._gc_ptr])

    def handle_gc_finalization(self) -> None:
        """Sets up the needed GC list size"""
        # this is the max size the list will ever need since we dont have any loop
        # every instruction is ran only once per call
        if len(self._gc_objects) > 0:
            self._gc_size.constant = len(self._gc_objects)
        else:
            self.entryblock.instructions.remove(self._gc_ptr)
        self._gc_ptr = None
        self._gc_objects.clear()


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
        self._llmodule: t.Optional[llvm.ModuleRef] = None
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
        if self._llmodule is not None:
            self._engine.run_static_destructors()
            self._engine.remove_module(self._llmodule)
            self._llmodule.close()
            self._llmodule = None
        self._llmodule = llvm.parse_assembly(str(self.compile_ir()))
        self._engine.add_module(self._llmodule)
        self._engine.finalize_object()
        self._engine.run_static_constructors()
        return c.CFUNCTYPE(restype=c.c_long)(self._engine.get_function_address('main'))

    def compile_ir(self, verify: bool=False) -> ir.Module:
        """Compiles the typed AST down to LLVM IR.
        
        If verify is True, it will validate the IR to look for syntatic and semantic errors.
        """
        self._strings = {}
        self._module = ir.Module(self._program.filename, context=ir.Context())
        self._module.triple = llvm.Target.from_default_triple().triple
        runtime = CoralRuntime.import_into(self._module)
        main = ir.Function(
            name='main',
            module=self._module,
            ftype=ir.FunctionType(return_type=LL_INT, args=[])
        )
        entry_block = main.append_basic_block('entry')
        main_builder = ir.IRBuilder(entry_block)
        main_scope = CoralFunctionCompilation(
            globals_ptr=ir.Constant(runtime.crobject_struct.as_pointer().as_pointer(), 0),
            globals_index={},
            function_type=CoralFunctionType(
                params=(),
                param_names=(),
                return_type=ast.BOUND_INTEGER_TYPE,
                llfunc=main,
                name='main'
            ),
            returns_boxed=False,
            scope_path='',
            functions_count=0,
            builder=main_builder,
            runtime=runtime
        )
        self._compile_node(self._program.body, main_scope, is_return_branch=False)
        main_scope.handle_gc_cleanup()
        main_scope.handle_gc_finalization()
        main_builder.ret(LL_INT(0))
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
                if is_return_branch:
                    return scope.handle_return_with_value(scope.get_var(node.name))
                return scope.get_var(node.name)
            case ast.LiteralIntegerValue(value=value):
                obj = CoralInteger(
                    type_=ast.BOUND_INTEGER_TYPE,
                    lltype=LL_INT,
                    value=LL_INT(value),
                    boxed=False,
                    scope=scope
                )
                if is_return_branch:
                    return scope.handle_return_with_value(obj)
                return obj
            case ast.LiteralBooleanValue(value=value):
                obj = CoralInteger(
                    type_=ast.BOUND_BOOLEAN_TYPE,
                    lltype=LL_BOOL,
                    value=ir.Constant(LL_BOOL, int(value)),
                    boxed=False,
                    scope=scope
                )
                if is_return_branch:
                    return scope.handle_return_with_value(obj)
                return obj
            case ast.LiteralStringValue(value=value):
                # box the string right here since we can't do anything with the unboxed version
                compiledstr = self._compile_raw_string(value)
                obj = CoralString(
                    type_=ast.BOUND_STRING_TYPE,
                    lltype=LL_CHAR.as_pointer(),
                    # drop the array pointer, we just need a plain char* like pointer
                    value=scope.builder.bitcast(compiledstr, LL_CHAR.as_pointer()),
                    boxed=False,
                    scope=scope
                ).box()
                if is_return_branch:
                    return scope.handle_return_with_value(obj)
                return obj
            case ast.TupleExpression(first=first, second=second):
                obj = CoralTuple.create_unboxed(
                    first=self._compile_node(first, scope, is_return_branch=False),
                    second=self._compile_node(second, scope, is_return_branch=False),
                    scope=scope
                )
                if not node.boundtype.is_static:
                    obj = obj.box()
                if is_return_branch:
                    return scope.handle_return_with_value(obj)
                return obj
            case ast.CallExpression():
                return self._compile_function_call(node, scope, is_return_branch=is_return_branch)
            case ast.FirstExpression(value=value):
                obj = CoralTuple.get_first(self._compile_node(value, scope, is_return_branch=False))
                if is_return_branch:
                    return scope.handle_return_with_value(obj)
                return obj
            case ast.SecondExpression(value=value):
                obj = CoralTuple.get_second(self._compile_node(value, scope, is_return_branch=False))
                if is_return_branch:
                    return scope.handle_return_with_value(obj)
                return obj
            case ast.PrintExpression(value=value):
                obj = self._compile_node(value, scope, is_return_branch=False).print()
                if is_return_branch:
                    return scope.handle_return_with_value(obj)
                return obj
            case ast.BinaryExpression():
                obj = self._compile_binary_expression(node, scope)
                if is_return_branch:
                    return scope.handle_return_with_value(obj)
                return obj
            case ast.ConditionalExpression():
                return self._compile_condition(node, scope, is_return_branch=is_return_branch)
            case ast.FunctionExpression():
                obj = self._compile_function(node, scope)
                if is_return_branch:
                    return scope.handle_return_with_value(obj)
                return obj
            case ast.LetExpression():
                return self._compile_declaration(node, scope, is_return_branch=is_return_branch)
            case _:
                raise ValueError(f"{node} is not supported yet")

    def _compile_function_call(
        self,
        node: ast.CallExpression,
        scope: CoralFunctionCompilation,
        is_return_branch: bool=False
    ) -> CoralObject:
        callee = self._compile_node(node.callee, scope, is_return_branch=False)
        callargs = [self._compile_node(arg, scope, is_return_branch=False) for arg in node.args]
        if is_return_branch:
            if callee.boundtype.type == ast.NativeType.FUNCTION:
                callee = t.cast(CoralFunction, callee)
                if callee.function_type.llfunc is None:
                    if not scope.returns_boxed:
                        raise TypeError(f"function '{scope.function_type.name}' must return '{scope.function_type.ll_return_type}', but got CRObject*")
                elif callee.function_type.ll_return_type != scope.function_type.ll_return_type:
                    raise TypeError(f"function '{scope.function_type.name}' must return '{scope.function_type.ll_return_type}', but got '{callee.function_type.ll_return_type}'")
                # clang supports tail calls only if the caller and callee signatures match
                if callee.function_type.llfunc.ftype == scope.function_type.llfunc.ftype:
                    obj = CoralFunction.call(scope, callee, callargs, tail=True)
                    scope.builder.ret(obj.value)
                    return obj
            return scope.handle_return_with_value(CoralFunction.call(scope, callee, callargs))
        return CoralFunction.call(scope, callee, callargs)

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
        # adapt the function type to include LLVM function
        boundtype = CoralFunctionType(
            params=boundtype.params,
            param_names=tuple(param.name for param in node.params),
            return_type=boundtype.return_type,
            llfunc=llfunc,
            has_globals=has_globals,
            name=myname
        )
        child_entry = llfunc.append_basic_block('entry')
        child_builder = ir.IRBuilder(child_entry)
        if has_globals:
            child_globals_ptr = llfunc.args[0]
        else:
            child_globals_ptr = ir.Constant(crobject_struct_ptr.as_pointer(), 0)
        # forward static types information from parent globals
        child_globals_index = {
            globalvar.var.name: ast.ScopeVar(
                type_=(
                    scope.get_var(globalvar.var.name).boundtype
                    if globalvar.var.name != myname else boundtype
                ),
                name=globalvar.var.name,
                index=globalvar.index
            )
            for globalvar in node.scope.globals.values()
        }
        # compile the function body
        child_scope = CoralFunctionCompilation(
            globals_ptr=child_globals_ptr,
            globals_index=child_globals_index,
            function_type=boundtype,
            returns_boxed=llfunc_type.return_type == crobject_struct_ptr,
            scope_path=llname,
            functions_count=0,
            builder=child_builder,
            runtime=scope.runtime
        )
        child_scope.load_params()
        child_scope.load_globals()
        self._compile_node(node.body, child_scope, is_return_branch=True)
        child_scope.handle_gc_finalization()
        scope.functions_count += 1

        # create the wrapper for the dynamic call dispatch through CRFunction_call()
        # it will extract the args from __varargs__, do the static dispatch and box the return
        # implements CRObject* (*fp) (CRObject**, CRObject**)
        llfunc_dynamic_type = ir.FunctionType(
            args=(
                crobject_struct_ptr.as_pointer(), # __globals__
                crobject_struct_ptr.as_pointer()  # __varargs__
            ),
            return_type=crobject_struct_ptr
        )
        llfunc_dynamic = ir.Function(
            name=f'{llname}__dynamic',
            ftype=llfunc_dynamic_type,
            module=self._module,
        )
        llfunc_dynamic.args = (
            ir.Argument(llfunc_dynamic, llfunc_dynamic_type.args[0], name='__globals__'),
            ir.Argument(llfunc_dynamic, llfunc_dynamic_type.args[1], name='__varargs__')
        )
        dynamic_builder = ir.IRBuilder(llfunc_dynamic.append_basic_block('entry'))
        dynamic_scope = CoralFunctionCompilation(
            globals_ptr=llfunc_dynamic.args[0],
            globals_index={},
            function_type=CoralFunctionType(
                params=(),
                param_names=(),
                return_type=ast.BOUND_UNDEFINED_TYPE,
                llfunc=llfunc_dynamic,
                name=llfunc_dynamic.name
            ),
            returns_boxed=True,
            scope_path='',
            functions_count=0,
            builder=dynamic_builder,
            runtime=scope.runtime
        )
        dynamic_wrapper_forward = []
        for i, param in enumerate(node.params):
            # we unbox integers and booleans
            vararg_arg = dynamic_builder.load(
                dynamic_builder.gep(
                    ptr=llfunc_dynamic.args[1], # __varargs__
                    indices=[LL_INT(i)],
                    inbounds=False
                )
            )
            if param.boundtype.type == ast.NativeType.INTEGER or param.boundtype.type == ast.NativeType.BOOLEAN:
                dynamic_wrapper_forward.append(CoralInteger(
                    type_=param.boundtype,
                    lltype=LL_INT,
                    value=vararg_arg,
                    boxed=True,
                    scope=dynamic_scope
                ).unbox().value)
            else:
                dynamic_wrapper_forward.append(vararg_arg)
        if has_globals:
            dynamic_wrapper_forward.insert(0, llfunc_dynamic.args[0]) # __globals__
        # box the return if needed since the vararg wrappers returns CRObject*
        if llfunc_type.return_type != llfunc_dynamic_type.return_type:
            if boundtype.return_type.type == ast.NativeType.INTEGER:
                dynamic_builder.ret(CoralInteger(
                    type_=ast.BOUND_INTEGER_TYPE,
                    lltype=LL_INT,
                    value=dynamic_builder.call(fn=llfunc, args=dynamic_wrapper_forward),
                    boxed=False,
                    scope=dynamic_scope
                ).box().value)
            elif boundtype.return_type.type == ast.NativeType.BOOLEAN:
                dynamic_builder.ret(CoralInteger(
                    type_=ast.BOUND_BOOLEAN_TYPE,
                    lltype=LL_BOOL,
                    value=dynamic_builder.call(fn=llfunc, args=dynamic_wrapper_forward),
                    boxed=False,
                    scope=dynamic_scope
                ).box().value)
            else:
                raise TypeError(f"the function {boundtype} must have its return boxed")
        else:
            dynamic_builder.ret(dynamic_builder.call(fn=llfunc, args=dynamic_wrapper_forward))
        dynamic_scope.handle_gc_finalization()

        # create a callable function from the definition above

        coral_llfunc = scope.builder.call(
            fn=scope.runtime.crfunction_new,
            args=(
                LL_INT(len(node.scope.globals)),
                LL_INT16(len(node.params)),
                llfunc_dynamic
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
                    scope.get_var(varindex.var.name).box().value
                    if myname is None or varindex.var.name != myname
                    else coral_llfunc
                )
            )
        return scope.collect_object(CoralFunction(
            type_=boundtype,
            lltype=llfunc_type,
            value=coral_llfunc,
            boxed=True,
            scope=scope
        ))

    def _compile_condition(
        self,
        node: ast.ConditionalExpression,
        scope: CoralFunctionCompilation,
        is_return_branch: bool=False
    ) -> CoralObject:
        cond = self._compile_node(node.cond, scope, is_return_branch=False)
        with scope.builder.if_else(cond.unbox().value) as (then_branch, else_branch):
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
        if not is_return_branch:
            match node.boundtype.type:
                case ast.NativeType.TUPLE:
                    return CoralTuple.merge_branch(
                        boundtype=node.boundtype,
                        then_value=then,
                        then_block=then_block,
                        else_value=otherwise,
                        else_block=else_block,
                        scope=scope
                    )
                case ast.NativeType.FUNCTION:
                    return CoralFunction.merge_branch(
                        boundtype=node.boundtype,
                        then_value=then,
                        then_block=then_block,
                        else_value=otherwise,
                        else_block=else_block,
                        scope=scope
                    )
                case _:
                    return CoralObject.merge_branch(
                        boundtype=node.boundtype,
                        then_value=then,
                        then_block=then_block,
                        else_value=otherwise,
                        else_block=else_block,
                        scope=scope
                    )
        else:
            # we dont have any value if we are part of a return branch, the value is returned by a
            # explicit "ret" from the bottom of the AST.
            scope.builder.unreachable()
            return CoralObject(
                type_=ast.BOUND_UNDEFINED_TYPE,
                lltype=scope.runtime.crobject_struct.as_pointer(),
                value=scope.runtime.crobject_struct.as_pointer()(0),
                boxed=True,
                scope=scope
            )

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
