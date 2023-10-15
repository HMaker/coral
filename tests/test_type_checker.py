import typing as t
import unittest
from coral import parser, ast


class SimpleInferenceTest(unittest.TestCase):

    def run_test(self, src: str, expect_type: ast.IBoundType):
        program = ast.typecheck(parser.parse(src)['expression'])
        self.assertEqual(program.boundtype, expect_type)

    def test_boolean_true(self):
        self.run_test(
            """
            let x = true;
            x
            """,
            ast.BOUND_BOOLEAN_TYPE
        )

    def test_boolean_false(self):
        self.run_test(
            """
            let x = false;
            x
            """,
            ast.BOUND_BOOLEAN_TYPE
        )

    def test_boolean_expression(self):
        self.run_test(
            """
            let x = true && false || true == false != true;
            x
            """,
            ast.BOUND_BOOLEAN_TYPE
        )

    def test_integer(self):
        self.run_test(
            """
            let x = 1;
            x
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_integer_arithmetic(self):
        self.run_test(
            """
            let x = 1 + 2 - 3 * 5 / 6 % 7;
            x
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_integer_comparison(self):
        self.run_test(
            """
            let x = 1 < 2;
            x
            """,
            ast.BOUND_BOOLEAN_TYPE
        )

    def test_integer_equals(self):
        self.run_test(
            """
            let x = 1 == 2;
            x
            """,
            ast.BOUND_BOOLEAN_TYPE
        )

    def test_string(self):
        self.run_test(
            """
            let x = "foo";
            x
            """,
            ast.BOUND_STRING_TYPE
        )

    def test_string_concat_left(self):
        self.run_test(
            """
            let x = "foo" + 1;
            x
            """,
            ast.BOUND_STRING_TYPE
        )

    def test_string_concat_right(self):
        self.run_test(
            """
            let x = 1 + "foo";
            x
            """,
            ast.BOUND_STRING_TYPE
        )

    def test_string_comparison(self):
        self.run_test(
            """
            let x = "bar" == "baz";
            x
            """,
            ast.BOUND_BOOLEAN_TYPE
        )

    def test_tuple(self):
        self.run_test(
            """
            let x = (1, (2, 3));
            x
            """,
            ast.BoundType(
                ast.NativeType.TUPLE,
                (
                    ast.BOUND_INTEGER_TYPE,
                    ast.BoundType(ast.NativeType.TUPLE, (ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE))
                )
            )
        )

    def test_deep_tuple(self):
        self.run_test(
            """
            let nil = ((0, 0), 0);
            let cons = fn (value, next) => ((1, value), next);
            let tuple = cons(1, cons(2, cons(3, nil)));
            tuple
            """,
            ast.BoundType(
                type_=ast.NativeType.TUPLE,
                generics=(
                    ast.BoundType(
                        type_=ast.NativeType.TUPLE,
                        generics=(ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE)
                    ),
                    ast.BOUND_ANY_TYPE
                )
            )
        )

    def test_tuple_first(self):
        self.run_test(
            """
            let x = first((1, (2, 3)));
            x
            """,
            ast.BOUND_INTEGER_TYPE
        )
    
    def test_tuple_second(self):
        self.run_test(
            """
            let x = second((1, (2, "string")));
            x
            """,
            ast.BoundType(ast.NativeType.TUPLE, (ast.BOUND_INTEGER_TYPE, ast.BOUND_STRING_TYPE))
        )

    def test_print_bool(self):
        self.run_test(
            """
            let x = true;
            print(x)
            """,
            ast.BOUND_BOOLEAN_TYPE
        )

    def test_print_integer(self):
        self.run_test(
            """
            let x = 1;
            print(x)
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_function_static(self):
        self.run_test(
            """
            let x = fn (a) => {
                let x = 1;
                x
            };
            x
            """,
            ast.BoundFunctionType((ast.BOUND_ANY_TYPE,), ast.BOUND_INTEGER_TYPE)
        )

    def test_call_static(self):
        self.run_test(
            """
            let fun = fn (a) => 1;
            fun("nothing")
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_call_static_identity_function(self):
        self.run_test(
            """
            let fun = fn (a) => a;
            fun("nothing")
            """,
            ast.BOUND_STRING_TYPE
        )

    def test_call_dynamic_boolean(self):
        self.run_test(
            """
            let fun = fn (a) => a && false;
            fun(true)
            """,
            ast.BOUND_BOOLEAN_TYPE
        )

    def test_call_dynamic_integer(self):
        self.run_test(
            """
            let fun = fn (a) => a + 1;
            fun(2)
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_call_dynamic_string(self):
        self.run_test(
            """
            let fun = fn (a) => a + 1;
            fun("nothing")
            """,
            ast.BOUND_STRING_TYPE
        )

    def test_call_dynamic_tuple(self):
        self.run_test(
            """
            let fun = fn (a) => (a, 1);
            fun("nothing")
            """,
            ast.BoundType(ast.NativeType.TUPLE, (ast.BOUND_STRING_TYPE, ast.BOUND_INTEGER_TYPE))
        )

    def test_call_dynamic_function(self):
        self.run_test(
            """
            let fun = fn (a) => {
                let fun = fn () => { a };
                fun
            };
            fun("nothing")
            """,
            ast.BoundFunctionType((), ast.BOUND_STRING_TYPE)
        )

    def test_call_overloaded_identity_function(self):
        self.run_test(
            """
            let fun = fn (a) => a;
            let a = fun(1 + 1);
            let b = fun("something");
            b
            """,
            ast.BOUND_UNDEFINED_TYPE
        )

    def test_call_anonymous_function(self):
        self.run_test(
            """
            (fn (a) => { 1 } )("nothing")
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_ignored_declarations(self):
        self.run_test(
            """
            let _ = true;
            let _ = 1;
            let _ = "hello";
            let _ = (1, 2);
            let _ = fn () => { "hello" };
            let _ = print("hello");
            let _ = first((1, 2));
            print("bye")
            """,
            ast.BOUND_STRING_TYPE
        )


class HighOrderFunctionInferenceTest(unittest.TestCase):

    def run_test(self, src: str, expect_type: ast.IBoundType):
        program = ast.typecheck(parser.parse(src)['expression'])
        self.assertEqual(program.boundtype, expect_type)

    def test_returns_bool(self):
        self.run_test(
            """
            let foo = fn (a) => {
                if (a > 0)
                    fn (a, b) => a && b
                else
                    fn (a, b) => a || b
            };
            foo
            """,
            ast.BoundFunctionType(params=(ast.BOUND_INTEGER_TYPE,), return_type=ast.BoundFunctionType(
                params=(ast.BOUND_BOOLEAN_TYPE, ast.BOUND_BOOLEAN_TYPE),
                return_type=ast.BOUND_BOOLEAN_TYPE
            ))
        )

    def test_returns_int(self):
        self.run_test(
            """
            let foo = fn (a) => {
                if (a > 0)
                    fn (a, b) => a - b
                else
                    fn (a, b) => a * b
            };
            foo
            """,
            ast.BoundFunctionType(params=(ast.BOUND_INTEGER_TYPE,), return_type=ast.BoundFunctionType(
                params=(ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE),
                return_type=ast.BOUND_INTEGER_TYPE
            ))
        )

    def test_returns_deep_int(self):
        self.run_test(
            """
            let foo = fn (a) => {
                if (a > 0)
                    fn (a) => {
                        if (a < 0)
                            fn (a, b) => a - b
                        else
                            fn (a, b) => a * b
                    }
                else
                    fn (a) => {
                        if (a > 0)
                            fn (a, b) => a - b
                        else
                            fn (a, b) => a * b
                    }
            };
            foo
            """,
            ast.BoundFunctionType(params=(ast.BOUND_INTEGER_TYPE,), return_type=ast.BoundFunctionType(
                params=(ast.BOUND_INTEGER_TYPE,),
                return_type=ast.BoundFunctionType(
                    params=(ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE),
                    return_type=ast.BOUND_INTEGER_TYPE
                )
            ))
        )

    def test_returns_string(self):
        self.run_test(
            """
            let foo = fn (a) => {
                if (a > 0)
                    fn (name) => "Hello, " + name
                else
                    fn (name) => name + ", hello"
            };
            let _ = foo(1)("heraldo");
            foo
            """,
            ast.BoundFunctionType(params=(ast.BOUND_INTEGER_TYPE,), return_type=ast.BoundFunctionType(
                params=(ast.BOUND_STRING_TYPE,),
                return_type=ast.BOUND_STRING_TYPE
            ))
        )

    def test_returns_deep_string(self):
        self.run_test(
            """
            let foo = fn (a) => {
                if (a > 0)
                    fn (a) => {
                        if (a < 0)
                            fn (name) => "Hello, " + name
                        else
                            fn (name) => name + ", hello"
                    }
                else
                    fn (a) => {
                        if (a > 0)
                            fn (name) => "Hello, " + name
                        else
                            fn (name) => name + ", hello"
                    }
            };
            let _ = foo(0)(1)("heraldo");
            foo
            """,
            ast.BoundFunctionType(params=(ast.BOUND_INTEGER_TYPE,), return_type=ast.BoundFunctionType(
                params=(ast.BOUND_INTEGER_TYPE,),
                return_type=ast.BoundFunctionType(
                    params=(ast.BOUND_STRING_TYPE,),
                    return_type=ast.BOUND_STRING_TYPE
                )
            ))
        )

    def test_returns_tuple(self):
        self.run_test(
            """
            let foo = fn (a) => {
                if (a > 0)
                    fn (a, b) => (a, b)
                else
                    fn (a, b) => (b, a)
            };
            let _ = foo(1)(1, 2);
            foo
            """,
            ast.BoundFunctionType(params=(ast.BOUND_INTEGER_TYPE,), return_type=ast.BoundFunctionType(
                params=(ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE),
                return_type=ast.BoundType(
                    ast.NativeType.TUPLE,
                    (ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE)
                )
            ))
        )

    def test_takes_function_argument(self):
        self.run_test(
            """
            let sum = fn (a, b) => a + b;
            let apply = fn (f, a, b) => f(a, b);
            let _ = apply(sum, 1, 2);
            sum
            """,
            ast.BoundFunctionType(
                (ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE),
                ast.BOUND_INTEGER_TYPE
            )
        )

    def test_map(self):
        self.run_test(
            """
            let nil = ((0, 0), 0);
            let cons = fn (value, next) => ((1, value), next);

            let map = fn (list, f) => {
                let tag  = first(first(list));
                let val  = second(first(list));
                let rest = second(list);
                if (tag == 1) { // if (list is Cons)
                    let new_val = f(val);
                    let new_rest = map(rest, f);
                    cons(new_val, new_rest)
                } else {
                    nil
                }
            };

            let list = cons(1, cons(2, cons(3, cons(4, cons(5, cons(6, cons(7, cons(8, cons(9, cons(10, cons(11, cons(12, cons(13, cons(14, cons(15, cons(16, nil))))))))))))))));
            let _ = map(list, fn (x) => x * 4);
            map
            """,
            ast.BoundFunctionType(
                params=(
                    ast.BoundType(
                        type_=ast.NativeType.TUPLE,
                        generics=(
                            ast.BoundType(
                                type_=ast.NativeType.TUPLE,
                                generics=(ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE)
                            ),
                            ast.BOUND_ANY_TYPE
                        )
                    ),
                    ast.BoundFunctionType(
                        params=(ast.BOUND_INTEGER_TYPE,),
                        return_type=ast.BOUND_INTEGER_TYPE
                    )
                ),
                return_type=ast.BoundType(
                    type_=ast.NativeType.TUPLE,
                    generics=(
                        ast.BoundType(
                            type_=ast.NativeType.TUPLE,
                            generics=(ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE)
                        ),
                        ast.BOUND_UNDEFINED_TYPE
                    )
                )
            )
        )


class ConditionalInferenceTest(unittest.TestCase):

    def run_test(self, src: str, expect_type: ast.IBoundType):
        program = ast.typecheck(parser.parse(src)['expression'])
        self.assertEqual(program.boundtype, expect_type)

    def test_boolean(self):
        self.run_test(
            """
            let x = if (true) false || true else true && false;
            x
            """,
            ast.BOUND_BOOLEAN_TYPE
        )

    def test_integer(self):
        self.run_test(
            """
            let x = if (true) 1 else 0 - 1;
            x
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_string(self):
        self.run_test(
            """
            let x = if (true) "foo" + 1 else 1 + "bar";
            x
            """,
            ast.BOUND_STRING_TYPE
        )

    def test_tuple(self):
        self.run_test(
            """
            let x = if (true) (1, 2) else (3, 4);
            x
            """,
            ast.BoundType(ast.NativeType.TUPLE, (ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE))
        )

    def test_tuple_generics(self):
        self.run_test(
            """
            let x = if (true) (1, 2) else (3, "foo");
            x
            """,
            ast.BoundType(ast.NativeType.TUPLE, (ast.BOUND_INTEGER_TYPE, ast.BOUND_UNDEFINED_TYPE))
        )

    def test_function_return(self):
        self.run_test(
            """
            let x = fn () => {
                if (true) {
                    1
                } else {
                    2
                }
            };
            x
            """,
            ast.BoundFunctionType((), ast.BOUND_INTEGER_TYPE)
        )

    def test_function_return_nested(self):
        self.run_test(
            """
            let x = fn () => {
                if (true) {
                    if (true) {
                        1
                    } else {
                        2
                    }
                } else {
                    if (true) {
                        1
                    } else {
                        2
                    }
                }
            };
            x
            """,
            ast.BoundFunctionType((), ast.BOUND_INTEGER_TYPE)
        )

    def test_function_generics(self):
        self.run_test(
            """
            let x = fn () => 1;
            let y = fn () => "foo";
            let z = if (true) x else y;
            z
            """,
            ast.BoundFunctionType((), ast.BOUND_UNDEFINED_TYPE)
        )

    def test_call_args(self):
        self.run_test(
            """
            let foo = fn (a) => a + 1;
            foo(if (false) 1 else 0 - 100)
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_call_args_union(self):
        self.run_test(
            """
            let foo = fn (a) => a + 1;
            foo(if (false) 1 else "bar")
            """,
            ast.BoundTypeUnion.for_members(ast.BOUND_INTEGER_TYPE, ast.BOUND_STRING_TYPE)
        )

    def test_high_order_func_return(self):
        self.run_test(
            """
            let foo = fn (n) => {
                if (true)
                    fn () => n + 1
                else
                    fn () => n + 2
            };
            let func = foo(1);
            print(func())
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_vars_scope_by_branch(self):
        self.run_test(
            """
            let x = 1;
            let _ = if (true) {
                let x = "hello, world!";
                x
            } else {
                let x = ("hello", "world!");
                x
            };
            print(x)
            """,
            ast.BOUND_INTEGER_TYPE
        )


class StaticErrorTest(unittest.TestCase):

    def run_test(self, src: str, expect_error: t.Type[Exception]):
        syntax = parser.parse(src)
        self.assertRaises(expect_error, lambda: ast.typecheck(syntax['expression']))

    def test_redeclaration(self):
        self.run_test(
            """
            let x = 1;
            let x = 2;
            x
            """,
            SyntaxError
        )

    def test_missing_var(self):
        self.run_test(
            """
            let x = y;
            let y = 2;
            x
            """,
            ValueError
        )

    def test_declaration_self_references(self):
        self.run_test(
            """
            let x = x;
            x
            """,
            ValueError
        )

    def test_references_ignored_declaration(self):
        self.run_test(
            """
            let _ = print("hello");
            print(_)
            """,
            ValueError
        )

    def test_bad_concatenation(self):
        self.run_test(
            """
            let _ = 1 + false;
            0
            """,
            TypeError
        )

    def test_bad_arithmetic(self):
        self.run_test(
            """
            let _ = true - 1;
            0
            """,
            TypeError
        )

    def test_bad_numeric_comparison(self):
        self.run_test(
            """
            let _ = 1 < "foo";
            0
            """,
            TypeError
        )

    def test_bad_equals_bool(self):
        self.run_test(
            """
            let _ = true == "1";
            0
            """,
            TypeError
        )

    def test_bad_equals_int(self):
        self.run_test(
            """
            let _ = 1 == "1";
            0
            """,
            TypeError
        )

    def test_bad_equals_str(self):
        self.run_test(
            """
            let _ = "1" == 1;
            0
            """,
            TypeError
        )

    def test_bad_boolean_expression(self):
        self.run_test(
            """
            let _ = true && 1;
            0
            """,
            TypeError
        )

    def test_bad_condition(self):
        self.run_test(
            """
            let _ = if (1) true else false;
            0
            """,
            TypeError
        )


class RecursiveInferenceTest(unittest.TestCase):

    def run_test(self, src: str, expect_type: ast.IBoundType):
        program = ast.typecheck(parser.parse(src)['expression'])
        self.assertEqual(program.boundtype, expect_type)

    def test_returns_itself(self):
        self.run_test(
            """
            let x = fn () => x;
            x
            """,
            ast.BoundFunctionType((), ast.BOUND_ANY_TYPE)
        )

    def test_fib_call(self):
        self.run_test(
            """
            let fib = fn (n) => {
                if (n < 2) {
                    n
                } else {
                    fib(n - 1) + fib(n - 2)
                }
            };
            fib(10)
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_fib_signature(self):
        self.run_test(
            """
            let fib = fn (n) => {
                if (n < 2) {
                    n
                } else {
                    fib(n - 1) + fib(n - 2)
                }
            };
            fib
            """,
            ast.BoundFunctionType((ast.BOUND_INTEGER_TYPE,), ast.BOUND_INTEGER_TYPE)
        )

    def test_fib_signature_with_let(self):
        self.run_test(
            """
            let fib = fn (n) => {
                let _ = 1;
                if (n < 2) {
                    n
                } else {
                    fib(n - 1) + fib(n - 2)
                }
            };
            fib
            """,
            ast.BoundFunctionType((ast.BOUND_INTEGER_TYPE,), ast.BOUND_INTEGER_TYPE)
        )

    def test_fib_tail_recursive(self):
        self.run_test(
            """
            let fibrec = fn (n, k1, k2) => {
                if (n == 0) {
                    k1
                } else {
                    if (n == 1) {
                        k2
                    } else {
                        fibrec(n - 1, k2, k1 + k2)
                    }
                }
            };
            fibrec(10, 0, 1)
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_sum_call(self):
        self.run_test(
            """
            let sum = fn (n) => {
                if (n == 1) {
                    n
                } else {
                    n + sum(n - 1)
                }
            };
            print(sum(5))
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_sum_signature(self):
        self.run_test(
            """
            let sum = fn (n) => {
                if (n == 1) {
                    n
                } else {
                    n + sum(n - 1)
                }
            };
            sum
            """,
            ast.BoundFunctionType((ast.BOUND_INTEGER_TYPE,), ast.BOUND_INTEGER_TYPE)
        )

    def test_combination_call(self):
        self.run_test(
            """
            let combination = fn (n, k) => {
                let a = k == 0;
                let b = k == n;
                if (a || b)
                {
                    1
                }
                else {
                    combination(n - 1, k - 1) + combination(n - 1, k)
                }
            };
            print(combination(10, 2))
            """,
            ast.BOUND_INTEGER_TYPE
        )

    def test_combination_signature(self):
        self.run_test(
            """
            let combination = fn (n, k) => {
                let a = k == 0;
                let b = k == n;
                if (a || b)
                {
                    1
                }
                else {
                    combination(n - 1, k - 1) + combination(n - 1, k)
                }
            };
            combination
            """,
            ast.BoundFunctionType((ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE), ast.BOUND_INTEGER_TYPE)
        )


if __name__ == '__main__':
    unittest.main()
