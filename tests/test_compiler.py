import unittest
from coral import parser, ast, compiler


IR_COMPILER_TESTS = (
    (
        "debug",
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

        """
    ),
    # (
    #     "prints",
    #     """
    #     print("Hello, world!")
    #     """
    # ),
    # (
    #     "arithmetic",
    #     """
    #     let x = 1 + 2 - 3 / 4 * 5 % 6;
    #     print(x)
    #     """
    # ),
    # (
    #     "compare-integers",
    #     """
    #     let _ = print(1 < 2);
    #     let _ = print(2 <= 2);
    #     let _ = print(3 == 2);
    #     let _ = print(3 >= 2);
    #     let _ = print(4 > 2);
    #     let _ = print(5 != 2);
    #     0
    #     """
    # ),
    # (
    #     "compare-bools",
    #     """
    #     let _ = print(true == false);
    #     let _ = print(false != true);
    #     0
    #     """
    # ),
    # (
    #     "compare-strings",
    #     """
    #     let _ = print("foo" == "bar");
    #     let _ = print("bar" != "foo");
    #     0
    #     """
    # ),
    # (
    #     "strings-concatenation",
    #     """
    #     let a = 100 + "foo";
    #     let b = "foo" + 200;
    #     let c = a + b;
    #     print(c)
    #     """
    # ),
    # (
    #     "tuples",
    #     """
    #     let a = (true, false);
    #     let b = (1, a);
    #     let c = ("foo", "bar");
    #     let d = (b, c);
    #     print(d)
    #     """
    # ),
    # (
    #     "merge-string",
    #     """
    #     print(if (true)
    #         "Hello, world!"
    #     else
    #         "Hello"
    #     )
    #     """
    # ),
)


class CompilerTest(unittest.TestCase):

    def test(self):
        for name, src in IR_COMPILER_TESTS:
            with self.subTest(name):
                c = compiler.CoralCompiler.create_default(ast.Program(
                    filename='main',
                    body=ast.typecheck(parser.parse(src)['expression'])
                ))
                c.compile()()


if __name__ == '__main__':
    unittest.main()
