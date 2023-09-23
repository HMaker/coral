import typing as t
import unittest
from coral import parser, ast


SIMPLE_INFERENCE_TESTS: t.List[t.Tuple[str, str, ast.BoundType]] = [
    (
        "boolean-true",
        """
        let x = true;
        x
        """,
        ast.BOUND_BOOLEAN_TYPE
    ),
    (
        "boolean-false",
        """
        let x = false;
        x
        """,
        ast.BOUND_BOOLEAN_TYPE
    ),
    (
        "boolean-expression",
        """
        let x = true && false || true == false != true;
        x
        """,
        ast.BOUND_BOOLEAN_TYPE
    ),
    (
        "integer",
        """
        let x = 1;
        x
        """,
        ast.BOUND_INTEGER_TYPE
    ),
    (
        "integer-arithmetic",
        """
        let x = 1 + 2 - 3 * 5 / 6 % 7;
        x
        """,
        ast.BOUND_INTEGER_TYPE
    ),
    (
        "integer-comparison",
        """
        let x = 1 < 2 > 3 == 4 != 5;
        x
        """,
        ast.BOUND_BOOLEAN_TYPE
    ),
    (
        "string",
        """
        let x = "foo";
        x
        """,
        ast.BOUND_STRING_TYPE
    ),
    (
        "string-add-left",
        """
        let x = "foo" + 1;
        x
        """,
        ast.BOUND_STRING_TYPE
    ),
    (
        "string-add-right",
        """
        let x = 1 + "foo";
        x
        """,
        ast.BOUND_STRING_TYPE
    ),
    (
        "string-comparison",
        """
        let x = "foo" != "bar" == "baz";
        x
        """,
        ast.BOUND_BOOLEAN_TYPE
    ),
    (
        "tuple",
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
    ),
    (
        "tuple-first",
        """
        let x = first((1, (2, 3)));
        x
        """,
        ast.BOUND_INTEGER_TYPE
    ),
    (
        "tuple-second",
        """
        let x = second((1, (2, "string")));
        x
        """,
        ast.BoundType(ast.NativeType.TUPLE, (ast.BOUND_INTEGER_TYPE, ast.BOUND_STRING_TYPE))
    ),
    (
        "print-bool",
        """
        let x = true;
        print(x)
        """,
        ast.BOUND_BOOLEAN_TYPE
    ),
    (
        "print-integer",
        """
        let x = 1;
        print(x)
        """,
        ast.BOUND_INTEGER_TYPE
    ),
    (
        "function-static",
        """
        let x = fn (a) => {
            let x = 1;
            x
        };
        x
        """,
        ast.BoundFunctionType((ast.BOUND_ANY_TYPE,), ast.BOUND_INTEGER_TYPE)
    ),
    (
        "function-let-return",
        """
        let x = fn () => {
            let x = 1;
            x
        };
        x
        """,
        ast.BoundFunctionType((), ast.BOUND_INTEGER_TYPE)
    ),
    (
        "call-static",
        """
        let fun = fn (a) => 1;
        fun("nothing")
        """,
        ast.BOUND_INTEGER_TYPE
    ),
    (
        "call-static-identity-function",
        """
        let fun = fn (a) => a;
        fun("nothing")
        """,
        ast.BOUND_STRING_TYPE
    ),
    (
        "call-dynamic-boolean",
        """
        let fun = fn (a) => a && false;
        fun(true)
        """,
        ast.BOUND_BOOLEAN_TYPE
    ),
    (
        "call-dynamic-integer",
        """
        let fun = fn (a) => a + 1;
        fun(2)
        """,
        ast.BOUND_INTEGER_TYPE
    ),
    (
        "call-dynamic-string",
        """
        let fun = fn (a) => a + 1;
        fun("nothing")
        """,
        ast.BOUND_STRING_TYPE
    ),
    (
        "call-dynamic-tuple",
        """
        let fun = fn (a) => (a, 1);
        fun("nothing")
        """,
        ast.BoundType(ast.NativeType.TUPLE, (ast.BOUND_STRING_TYPE, ast.BOUND_INTEGER_TYPE))
    ),
    (
        "call-overloaded-identity-function",
        """
        let fun = fn (a) => a;
        let a = fun(1 + 1);
        let b = fun("something");
        b
        """,
        ast.BOUND_UNDEFINED_TYPE
    ),
    (
        "call-dynamic-function",
        """
        let fun = fn (a) => {
            let fun = fn () => { a };
            fun
        };
        fun("nothing")
        """,
        ast.BoundFunctionType((), ast.BOUND_STRING_TYPE)
    ),
    (
        "anonymous-function",
        """
        let x = (fn (a) => { 1 } );
        x
        """,
        ast.BoundFunctionType((ast.BOUND_ANY_TYPE,), ast.BOUND_INTEGER_TYPE)
    ),
    (
        "anonymous-function-call",
        """
        (fn (a) => { 1 } )("nothing")
        """,
        ast.BOUND_INTEGER_TYPE
    )
]


CONDITIONAL_INFERENCE_TESTS: t.List[t.Tuple[str, str, ast.BoundType]] = [
    (
        "conditional-boolean",
        """
        let x = if (true) false || true else true && false;
        x
        """,
        ast.BOUND_BOOLEAN_TYPE
    ),
    (
        "conditional-integer",
        """
        let x = if (true) 1 else 0 - 1;
        x
        """,
        ast.BOUND_INTEGER_TYPE
    ),
    (
        "conditional-string",
        """
        let x = if (true) "foo" + 1 else 1 + "bar";
        x
        """,
        ast.BOUND_STRING_TYPE
    ),
    (
        "conditional-tuple",
        """
        let x = if (true) (1, 2) else (3, 4);
        x
        """,
        ast.BoundType(ast.NativeType.TUPLE, (ast.BOUND_INTEGER_TYPE, ast.BOUND_INTEGER_TYPE))
    ),
    (
        "conditional-tuple-generic",
        """
        let x = if (true) (1, 2) else (3, "foo");
        x
        """,
        ast.BoundType(ast.NativeType.TUPLE, (ast.BOUND_INTEGER_TYPE, ast.BOUND_UNDEFINED_TYPE))
    ),
    (
        "conditional-function-return",
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
    ),
    (
        "conditional-function-return-nested",
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
    ),
    (
        "conditional-function-generic",
        """
        let x = fn () => 1;
        let y = fn () => "foo";
        let z = if (true) x else y;
        z
        """,
        ast.BoundFunctionType((), ast.BOUND_UNDEFINED_TYPE)
    ),
    (
        "conditional-bool-call",
        """
        let foo = fn (a) => a || false;
        foo(if (false) false else true)
        """,
        ast.BOUND_BOOLEAN_TYPE
    ),
    (
        "conditional-integer-call",
        """
        let foo = fn (a) => a + 1;
        foo(if (false) 1 else 0 - 100)
        """,
        ast.BOUND_INTEGER_TYPE
    ),
    (
        "conditional-int-string-call",
        """
        let foo = fn (a) => a + 1;
        foo(if (false) 1 else "bar")
        """,
        ast.BoundTypeUnion.for_members(ast.BOUND_INTEGER_TYPE, ast.BOUND_STRING_TYPE)
    )
]


STATIC_ERRORS_TESTS: t.List[t.Tuple[str, str, t.Type[Exception]]] = [
    (
        "identifier-declared",
        """
        let x = 1;
        let x = 2;
        x
        """,
        SyntaxError
    ),
    (
        "identifier-declared-condition",
        """
        let x = 1;
        let y = if (false) let x = 2; x else x;
        x
        """,
        SyntaxError
    ),
    (
        "identifier-missing",
        """
        let x = y;
        let y = 2;
        x
        """,
        ValueError
    ),
    (
        "identifier-self-reference",
        """
        let x = x;
        x
        """,
        ValueError
    )
]


RECURSIVE_INFERENCE_TESTS: t.List[t.Tuple[str, str, ast.BoundType]] = [
    # (
    #     "function-return-itself",
    #     """
    #     let x = fn () => x;
    #     x
    #     """,
    #     ast.BoundFunctionType((), ast.BOUND_ANY_TYPE) # Function<Any>
    # ),
    (
        "fib",
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
    ),
    (
        "fib-signature",
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
    ),
    (
        "fib-let-signature",
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
    ),
    (
        "fib-tail-recursive",
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
        ast.BOUND_INTEGER_TYPE,
    ),
    (
        "sum",
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
    ),
    (
        "sum-signature",
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
    ),
    (
        "combination",
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
    ),
    (
        "combination-signature",
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
]


class BinderTest(unittest.TestCase):

    def test1_simple_inference(self):
        for test, src, expected in SIMPLE_INFERENCE_TESTS:
            with self.subTest(test):
                program = ast.typecheck(parser.parse(src)['expression'])
                self.assertEqual(program.boundtype, expected)

    def test2_conditional_inference(self):
        for test, src, expected in CONDITIONAL_INFERENCE_TESTS:
            with self.subTest(test):
                program = ast.typecheck(parser.parse(src)['expression'])
                self.assertEqual(program.boundtype, expected)

    def test3_static_errors(self):
        for test, src, expected in STATIC_ERRORS_TESTS:
            with self.subTest(test):
                syntax = parser.parse(src)
                self.assertRaises(expected, lambda: ast.typecheck(syntax['expression']))

    def test4_recursive_inference(self):
        for test, src, expected in RECURSIVE_INFERENCE_TESTS:
            with self.subTest(test):
                program = ast.typecheck(parser.parse(src)['expression'])
                self.assertEqual(program.boundtype, expected)


if __name__ == '__main__':
    unittest.main()
