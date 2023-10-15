import unittest
from coral import parser, ast, compiler


class CompilerTest(unittest.TestCase):

    def runtest(self, src: str):
        c = compiler.CoralCompiler.create_default(ast.Program(
            filename='main',
            body=ast.typecheck(parser.parse(src)['expression'])
        ))
        c.compile()()

    def test0_prints(self):
        self.runtest("""print("Hello, world!")""")

    def test1_conditions(self):
        self.runtest(
            """
            let _ = if (true) print("SUCCESS") else print("FAIL");
            0
            """
        )

    def test_arithmetic(self):
        self.runtest(
            """
            let _ = if (4294967295 + 4294967295 == 8589934590) {
                print("SUCCESS 4294967295 + 4294967295 == 8589934590")
            } else {
                print("FAIL 4294967295 + 4294967295 == 8589934590")
            };
            let _ = if (4294967295 - 4294967295 == 0) {
                print("SUCCESS 4294967295 - 4294967295 == 0")
            } else {
                print("FAIL 4294967295 - 4294967295 == 0")
            };
            let _ = if (4294967295 * 2 == 8589934590) {
                print("SUCCESS 4294967295 * 2 == 8589934590")
            } else {
                print("FAIL 4294967295 * 2 == 8589934590")
            };
            let _ = if (8589934590 / 2 == 4294967295) {
                print("SUCCESS 8589934590 / 2 == 4294967295")
            } else {
                print("FAIL 8589934590 / 2 == 4294967295")
            };
            let _ = if (8589934590 % 2 == 0) {
                print("SUCCESS 8589934590 % 2 == 0")
            } else {
                print("FAIL 8589934590 % 2 == 0")
            };
            0
            """
        )

    def test_numeric_comparison(self):
        self.runtest(
            """
            let _ = if ((8589934590 < 4294967295) == false) {
                print("SUCCESS 8589934590 < 4294967295 == false")
            } else {
                print("FAIL 8589934590 < 4294967295 == false")
            };
            let _ = if ((8589934590 <= 4294967295) == false) {
                print("SUCCESS 8589934590 <= 4294967295 == false")
            } else {
                print("FAIL 8589934590 <= 4294967295 == false")
            };
            let _ = if ((8589934590 >= 4294967295) == true) {
                print("SUCCESS 8589934590 >= 4294967295 == true")
            } else {
                print("FAIL 8589934590 >= 4294967295 == true")
            };
            let _ = if ((8589934590 > 4294967295) == true) {
                print("SUCCESS 8589934590 > 4294967295 == true")
            } else {
                print("FAIL 8589934590 > 4294967295 == true")
            };
            let _ = if ((8589934590 == 4294967295) == false) {
                print("SUCCESS (8589934590 == 4294967295) == false")
            } else {
                print("FAIL (8589934590 == 4294967295) == false")
            };
            let _ = if ((8589934590 != 4294967295) == true) {
                print("SUCCESS (8589934590 != 4294967295) == true")
            } else {
                print("FAIL (8589934590 != 4294967295) == true")
            };
            0
            """
        )

    def test_boolean_expression(self):
        self.runtest(
            """
            let _ = if ((true && false) == false) {
                print("SUCCESS true && false == false")
            } else {
                print("FAIL true && false == false")
            };
            let _ = if ((true && true) == true) {
                print("SUCCESS true && true == true")
            } else {
                print("FAIL true && true == true")
            };
            let _ = if ((true || false) == true) {
                print("SUCCESS true || false == true")
            } else {
                print("FAIL true || false == true")
            };
            let _ = if ((false || false) == false) {
                print("SUCCESS false || false == false")
            } else {
                print("FAIL false || false == false")
            };
            0
            """
        )

    def test_string_concatenation(self):
        self.runtest(
            """
            let a = 100 + "foo";
            let _ = if (a == "100foo") print("SUCCESS 100 + 'foo' == '100foo'") else print("FAIL 100 + 'foo' == '100foo'");
            let b = "foo" + 200;
            let _ = if (b == "foo200") print("SUCCESS 'foo' + 200 == 'foo200'") else print("FAIL 'foo' + 200 == 'foo200'");
            let c = a + b;
            let _ = if (c == "100foofoo200") print("SUCCESS 100 + 'foo' + 'foo' + 200 == '100foofoo200'") else print("FAIL 100 + 'foo' + 'foo' + 200 == '100foofoo200'");
            0
            """
        )

    def test_tuples(self):
        self.runtest(
            """
            let a = (true, false);
            let b = (1, a);
            let c = ("foo", "bar");
            let d = (b, c);
            let _ = if ((first(first(d)) == 1) == true) {
                print("SUCCESS (first(first(d)) == 1) == true")
            } else {
                print("FAIL (first(first(d)) == 1) == true")
            };
            let _ = if ((second(second(d)) == "bar") == true) {
                print("SUCCESS (second(second(d)) == 'bar') == true")
            } else {
                print("FAIL (second(second(d)) == 'bar') == true")
            };
            0
            """
        )

    def test_merge_bool_branch(self):
        self.runtest(
            """
            let x = if (true) {
                if (false) true else false
            } else {
                true
            };
            let _ = if (x == false) print("SUCCESS") else print("FAIL");
            0
            """
        )

    def test_merge_int_branch(self):
        self.runtest(
            """
            let x = if (false) {
                if (false) true else false
            } else {
                if (true) true else false
            };
            let _ = if (x == true) print("SUCCESS") else print("FAIL");
            0
            """
        )

    def test_merge_string_branch(self):
        self.runtest(
            """
            let x = if (true) {
                if (true) {
                    if (false) "Hello, world!" else "World, hello!"
                } else {
                    if (false) "Hello, world!" else "Hello"
                }
            } else {
                "Hello"
            };
            let _ = if (x == "World, hello!") print("SUCCESS") else print("FAIL");
            0
            """
        )

    def test_merge_tuple_branch(self):
        self.runtest(
            """
            let x = if (true) {
                if (false) (1, 2) else (3, 4)
            } else {
                (5, 6)
            };
            let _ = if ((first(x) == 3) && (second(x) == 4)) print("SUCCESS") else print("FAIL");
            0
            """
        )


if __name__ == '__main__':
    unittest.main()
