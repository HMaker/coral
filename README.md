## coral

A LLVM compiler frontend for a toy programming language called "rinha". The values are immutable and dynammically typed. The supported data types are:
- Booleans like `true` and `false`
- Signed 64* bits integers
- ASCII strings
- High order functions and function closures
- Pair of values of any type like `(1, "hello, world")` (aka tuples)

Integers support only integer arithmetic
```
1 + 2
3 - 4
2 * 3
5 / 2 is 2!
5 % 2 is 1
```
The comparison operators `<`, `<=`, `==`, `!=`, `>`, `>=` are also supported. Those yield booleans as result.

Booleans support the `==`, `!=`, `&&` (conjunction) and `||` (disjunction) operators.

Strings support the `==`, `!=` and the concatenation `+` operator which can be applied only to strings or integers:
```
"foo" + "bar" == "foobar"
1 + "bar"     == "1bar"
"bar" + 1     == "bar1"
1 + 2         == 3
```

Tuples support the `first` and `second` index operators. The first returns the first member of the tuple. Likewise, the `second` returns the last member of the tuple:
```
first((1, 2))  == 1
second((1, 2)) == 2
```

You also can write to the process' stdout with `print()`

### Example
Example of a function which computes the nth term of the Fibonacci series
```
let fib = fn (n, k1, k2) => {
    if (n == 0) {
        k1
    } else {
        if (n == 1) {
            k2
        } else {
            fib(n - 1, k2, k1 + k2)
        }
    }
};
print(fib(10, 0, 1))
```
There are no statements, everything is a expression which evaluates to some value.

Here follows the corresponding LLVM IR of that function:
```llvm
define i64 @".fib"(%"struct.CRObject"** %"__globals__", i64 %"n", i64 %"k1", i64 %"k2")
{
entry:
  %".6" = icmp eq i64 %"n", 0
  br i1 %".6", label %"entry.if", label %"entry.else"
entry.if:
  ret i64 %"k1"
entry.else:
  %".9" = icmp eq i64 %"n", 1
  br i1 %".9", label %"entry.else.if", label %"entry.else.else"
entry.endif:
  unreachable
entry.else.if:
  ret i64 %"k2"
entry.else.else:
  %".12" = getelementptr %"struct.CRObject"*, %"struct.CRObject"** %"__globals__", i64 0
  %"fib" = load %"struct.CRObject"*, %"struct.CRObject"** %".12"
  %".14" = getelementptr inbounds %"struct.CRObject", %"struct.CRObject"* %"fib", i32 0, i32 2
  %".15" = load i8*, i8** %".14", align 8
  %".16" = bitcast i8* %".15" to %"struct.CRFunction"*
  %".17" = getelementptr inbounds %"struct.CRFunction", %"struct.CRFunction"* %".16", i32 0, i32 1
  %".18" = load %"struct.CRObjectArray"*, %"struct.CRObjectArray"** %".17", align 8
  %".19" = getelementptr inbounds %"struct.CRObjectArray", %"struct.CRObjectArray"* %".18", i32 0, i32 0
  %".20" = load %"struct.CRObject"**, %"struct.CRObject"*** %".19", align 8
  %".21" = sub i64 %"n", 1
  %".22" = add i64 %"k1", %"k2"
  %".23" = musttail call i64 @".fib"(%"struct.CRObject"** %".20", i64 %".21", i64 %"k2", i64 %".22")
  ret i64 %".23"
entry.else.endif:
  unreachable
}

define void @"__main__"()
{
entry:
  %"__gc__" = call %"struct.CRObjectArray"* @"CRObjectArray_new"(i64 1)
  %"fib.1" = call %"struct.CRObject"* @"CRFunction_new"(i64 1, i16 3, %"struct.CRObject"* (%"struct.CRObject"**, %"struct.CRObject"**)* @".fib__dynamic")
  call void @"CRFunction_setGlobal"(%"struct.CRObject"* %"fib.1", i64 0, %"struct.CRObject"* %"fib.1")
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %"fib.1")
  %".4" = getelementptr inbounds %"struct.CRObject", %"struct.CRObject"* %"fib.1", i32 0, i32 2
  %".5" = load i8*, i8** %".4", align 8
  %".6" = bitcast i8* %".5" to %"struct.CRFunction"*
  %".7" = getelementptr inbounds %"struct.CRFunction", %"struct.CRFunction"* %".6", i32 0, i32 1
  %".8" = load %"struct.CRObjectArray"*, %"struct.CRObjectArray"** %".7", align 8
  %".9" = getelementptr inbounds %"struct.CRObjectArray", %"struct.CRObjectArray"* %".8", i32 0, i32 0
  %".10" = load %"struct.CRObject"**, %"struct.CRObject"*** %".9", align 8
  %".11" = call i64 @".fib"(%"struct.CRObject"** %".10", i64 10, i64 0, i64 1)
  %".12" = shl i64 %".11", 2
  %".13" = or i64 %".12", 1
  %".14" = inttoptr i64 %".13" to %"struct.CRObject"*
  call void @"CRObject_print"(%"struct.CRObject"* %".14")
  call void @"CRObjectArray_release"(%"struct.CRObjectArray"* %"__gc__")
  ret void
}
```
`coral` makes uses of a C runtime library to handle the dynamic features of the language. The source code is at [coral/runtime](coral/runtime). The long term goal is to remove this runtime library and write pure LLVM IR for the dynamic features.

## The compiler
`coral` attempts to infer the types of the values at compile time to make a direct translation to pure LLVM IR code (see [coral/ast.py](coral/ast.py)). If type inference is not possible, the values are wrapped by the `CRObject` box and all manipulations are ruled by the runtime library.

Integers and booleans use tagged pointers when boxed, thus no heap allocation is performed to convert those to a `CRObject`. Tuples with known members type will have its members unboxed and no heap allocation is used to represent it. Strings are always boxed since actually `coral` does not write pure LLVM IR for string manipulation.

Functions are always boxed by the `CRFunction` struct, but the call is dispatched statically if the function definition is known. The `fib` example above shows that. The captured "variables" from the parent scope are passed through the `__globals__` array as the first argument of the LLVM function. Since here the function `fib` is well known, including its name, we could make it not box the function at all. `coral` boxes it because it's easier to handle functions which take functions as arguments and returns another functions. If the type checker was able to track function names along with their signature, in a way we can associate a function type to its definition, we could improve this boxing.

Since the values are immutable we don't have any reference cycles. `coral` uses reference counting as gargabe collection strategy. Every function has a local `__gc__` array which collects objects to be released at the function exit.

Below we have a function which triggers the boxing of multiple objects. As said before, strings are always boxed. Since the first member of the tuple is "obfuscated" by a condition, that tuple will be also boxed:
```
let foo = fn (n, t) => {
    if (n > 0) {
        let str1 = "string1";
        let str2 = "string2";
        let str3 = "string2";
        let str4 = "string2";
        let tuple = (if ("break it" == "break it") 1 else "1", 2);
        foo(n - 1, tuple)
    } else {
        n
    }
};
foo(10, (1, 2))
```
```llvm
define i64 @".foo"(%"struct.CRObject"** %"__globals__", i64 %"n", %"struct.CRObject"* %"t")
{
entry:
  %"__gc__" = call %"struct.CRObjectArray"* @"CRObjectArray_new"(i64 9)
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %"t")
  %".6" = icmp sgt i64 %"n", 0
  br i1 %".6", label %"entry.if", label %"entry.else"
entry.if:
  %".8" = bitcast [8 x i8]* @".str.0" to i8*
  %"str1" = call %"struct.CRObject"* @"CRString_new"(i8* %".8", i64 0)
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %"str1")
  %".11" = bitcast [8 x i8]* @".str.1" to i8*
  %"str2" = call %"struct.CRObject"* @"CRString_new"(i8* %".11", i64 0)
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %"str2")
  %".14" = bitcast [8 x i8]* @".str.1" to i8*
  %"str3" = call %"struct.CRObject"* @"CRString_new"(i8* %".14", i64 0)
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %"str3")
  %".17" = bitcast [8 x i8]* @".str.1" to i8*
  %"str4" = call %"struct.CRObject"* @"CRString_new"(i8* %".17", i64 0)
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %"str4")
  %".20" = bitcast [9 x i8]* @".str.2" to i8*
  %".21" = call %"struct.CRObject"* @"CRString_new"(i8* %".20", i64 0)
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %".21")
  %".23" = bitcast [9 x i8]* @".str.2" to i8*
  %".24" = call %"struct.CRObject"* @"CRString_new"(i8* %".23", i64 0)
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %".24")
  %".26" = call %"struct.CRObject"* @"CRObject_equals"(%"struct.CRObject"* %".21", %"struct.CRObject"* %".24")
  %".27" = ptrtoint %"struct.CRObject"* %".26" to i64
  %".28" = ashr i64 %".27", 2
  %".29" = trunc i64 %".28" to i1
  br i1 %".29", label %"entry.if.if", label %"entry.if.else"
entry.else:
  call void @"CRObjectArray_release"(%"struct.CRObjectArray"* %"__gc__")
  ret i64 %"n"
entry.endif:
  unreachable
entry.if.if:
  %".31" = shl i64 1, 2
  %".32" = or i64 %".31", 1
  %".33" = inttoptr i64 %".32" to %"struct.CRObject"*
  br label %"entry.if.endif"
entry.if.else:
  %".35" = bitcast [2 x i8]* @".str.3" to i8*
  %".36" = call %"struct.CRObject"* @"CRString_new"(i8* %".35", i64 0)
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %".36")
  br label %"entry.if.endif"
entry.if.endif:
  %".39" = phi  %"struct.CRObject"* [%".33", %"entry.if.if"], [%".36", %"entry.if.else"]
  %".40" = shl i64 2, 2
  %".41" = or i64 %".40", 1
  %".42" = inttoptr i64 %".41" to %"struct.CRObject"*
  %"tuple" = call %"struct.CRObject"* @"CRTuple_new"(%"struct.CRObject"* %".39", %"struct.CRObject"* %".42")
  call void @"CRObjectArray_push"(%"struct.CRObjectArray"* %"__gc__", %"struct.CRObject"* %"tuple")
  %".45" = getelementptr %"struct.CRObject"*, %"struct.CRObject"** %"__globals__", i64 0
  %"foo" = load %"struct.CRObject"*, %"struct.CRObject"** %".45"
  %".47" = sub i64 %"n", 1
  %".48" = getelementptr inbounds %"struct.CRObject", %"struct.CRObject"* %"foo", i32 0, i32 2
  %".49" = load i8*, i8** %".48", align 8
  %".50" = bitcast i8* %".49" to %"struct.CRFunction"*
  %".51" = getelementptr inbounds %"struct.CRFunction", %"struct.CRFunction"* %".50", i32 0, i32 1
  %".52" = load %"struct.CRObjectArray"*, %"struct.CRObjectArray"** %".51", align 8
  %".53" = getelementptr inbounds %"struct.CRObjectArray", %"struct.CRObjectArray"* %".52", i32 0, i32 0
  %".54" = load %"struct.CRObject"**, %"struct.CRObject"*** %".53", align 8
  call void @"CRObject_incref"(%"struct.CRObject"* %"tuple")
  call void @"CRObjectArray_release"(%"struct.CRObjectArray"* %"__gc__")
  %".57" = musttail call i64 @".foo"(%"struct.CRObject"** %".54", i64 %".47", %"struct.CRObject"* %"tuple")
  ret i64 %".57"
}

@".str.0" = private unnamed_addr constant [8 x i8] c"string1\00"
@".str.1" = private unnamed_addr constant [8 x i8] c"string2\00"
@".str.2" = private unnamed_addr constant [9 x i8] c"break it\00"
@".str.3" = private unnamed_addr constant [2 x i8] c"1\00"
```
Calls to `CRObjectArray_push()` pushes objects into the garbage collection list. Calls to `CRObjectArray_release()` releases the objects and destroy the list itself. Objects are destroyed only when their refcount reaches 0.

`coral` also attempts to preserve tail calls by delegating the arguments cleanup to the called function, this way it can release the `__gc__` list without waiting for the call to return. It also forwards as is the returned value from the called function. The downside of this approach is that calls which need boxed arguments, but are not at the tail, will have a little overhead to create new references.

## Installation
It requires `Python 3.9+` and `LLVM 10-14`. After installing those dependencies you can clone this repo and setup the Python environment:
```bash
git clone https://github.com/HMaker/coral.git
cd coral
python -m venv .venv --prompt=coral
. .venv/bin/activate
pip install -r requirements-dev.txt
python coral.py --help
```

You can also build a docker image and use it through a container:
```bash
docker build -t coral .
docker run --entrypoint python coral coral.py --help
```