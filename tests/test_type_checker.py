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
            let x = 1 < 2 > 3 == 4 != 5;
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
            let x = "foo" != "bar" == "baz";
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

    def test_conditional_redeclaration(self):
        self.run_test(
            """
            let x = 1;
            let y = if (false) let x = 2; x else x;
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
