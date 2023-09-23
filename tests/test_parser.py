import unittest
import typing as t
from coral import parser


RINHA_PARSER_SAMPLES: t.List[t.Tuple[str, str, dict]] = [
    (
        "arithmetic",
        """
        let v = 1 + 2 - 3 * 5 / 4 % 6;
        print(v)
        """,
        {'name': '<main>',
        'expression': {'kind': 'Let',
                        'name': {'text': 'v',
                                'location': {'filename': '<main>',
                                            'line': 2,
                                            'start': 13,
                                            'end': 14}},
                        'value': {'kind': 'Binary',
                                'lhs': {'kind': 'Int',
                                        'value': 1,
                                        'location': {'filename': '<main>',
                                                    'line': 2,
                                                    'start': 17,
                                                    'end': 18}},
                                'op': 'Add',
                                'rhs': {'kind': 'Binary',
                                        'lhs': {'kind': 'Int',
                                                'value': 2,
                                                'location': {'filename': '<main>',
                                                            'line': 2,
                                                            'start': 21,
                                                            'end': 22}},
                                        'op': 'Sub',
                                        'rhs': {'kind': 'Binary',
                                                'lhs': {'kind': 'Int',
                                                        'value': 3,
                                                        'location': {'filename': '<main>',
                                                                    'line': 2,
                                                                    'start': 25,
                                                                    'end': 26}},
                                                'op': 'Mul',
                                                'rhs': {'kind': 'Binary',
                                                        'lhs': {'kind': 'Int',
                                                                'value': 5,
                                                                'location': {'filename': '<main>',
                                                                            'line': 2,
                                                                            'start': 29,
                                                                            'end': 30}},
                                                        'op': 'Div',
                                                        'rhs': {'kind': 'Binary',
                                                                'lhs': {'kind': 'Int',
                                                                        'value': 4,
                                                                        'location': {'filename': '<main>',
                                                                                    'line': 2,
                                                                                    'start': 33,
                                                                                    'end': 34}},
                                                                'op': 'Rem',
                                                                'rhs': {'kind': 'Int',
                                                                        'value': 6,
                                                                        'location': {'filename': '<main>',
                                                                                    'line': 2,
                                                                                    'start': 37,
                                                                                    'end': 38}},
                                                                'location': {'filename': '<main>',
                                                                            'line': 2,
                                                                            'start': 33,
                                                                            'end': 38}},
                                                        'location': {'filename': '<main>',
                                                                    'line': 2,
                                                                    'start': 29,
                                                                    'end': 38}},
                                                'location': {'filename': '<main>',
                                                            'line': 2,
                                                            'start': 25,
                                                            'end': 38}},
                                        'location': {'filename': '<main>',
                                                    'line': 2,
                                                    'start': 21,
                                                    'end': 38}},
                                'location': {'filename': '<main>',
                                            'line': 2,
                                            'start': 17,
                                            'end': 38}},
                        'next': {'kind': 'Print',
                                'value': {'kind': 'Var',
                                        'text': 'v',
                                        'location': {'filename': '<main>',
                                                        'line': 3,
                                                        'start': 15,
                                                        'end': 16}},
                                'location': {'filename': '<main>',
                                            'line': 3,
                                            'start': 9,
                                            'end': 17}},
                        'location': {'filename': '<main>',
                                    'line': 2,
                                    'start': 9,
                                    'end': 17}},
        'location': {'filename': '<main>', 'line': 2, 'start': 9, 'end': 17}}
    ),
    (
        "logical",
        """
        let v = 1 < 2 <= 3 > 4 >= 5 == 6 != 7 && true || false;
        print(v)
        """,
        {'name': '<main>',
        'expression': {'kind': 'Let',
                        'name': {'text': 'v',
                                'location': {'filename': '<main>',
                                            'line': 2,
                                            'start': 13,
                                            'end': 14}},
                        'value': {'kind': 'Binary',
                                'lhs': {'kind': 'Int',
                                        'value': 1,
                                        'location': {'filename': '<main>',
                                                    'line': 2,
                                                    'start': 17,
                                                    'end': 18}},
                                'op': 'Lt',
                                'rhs': {'kind': 'Binary',
                                        'lhs': {'kind': 'Int',
                                                'value': 2,
                                                'location': {'filename': '<main>',
                                                            'line': 2,
                                                            'start': 21,
                                                            'end': 22}},
                                        'op': 'Lte',
                                        'rhs': {'kind': 'Binary',
                                                'lhs': {'kind': 'Int',
                                                        'value': 3,
                                                        'location': {'filename': '<main>',
                                                                    'line': 2,
                                                                    'start': 26,
                                                                    'end': 27}},
                                                'op': 'Gt',
                                                'rhs': {'kind': 'Binary',
                                                        'lhs': {'kind': 'Int',
                                                                'value': 4,
                                                                'location': {'filename': '<main>',
                                                                            'line': 2,
                                                                            'start': 30,
                                                                            'end': 31}},
                                                        'op': 'Gte',
                                                        'rhs': {'kind': 'Binary',
                                                                'lhs': {'kind': 'Int',
                                                                        'value': 5,
                                                                        'location': {'filename': '<main>',
                                                                                    'line': 2,
                                                                                    'start': 35,
                                                                                    'end': 36}},
                                                                'op': 'Eq',
                                                                'rhs': {'kind': 'Binary',
                                                                        'lhs': {'kind': 'Int',
                                                                                'value': 6,
                                                                                'location': {'filename': '<main>',
                                                                                            'line': 2,
                                                                                            'start': 40,
                                                                                            'end': 41}},
                                                                        'op': 'Neq',
                                                                        'rhs': {'kind': 'Binary',
                                                                                'lhs': {'kind': 'Int',
                                                                                        'value': 7,
                                                                                        'location': {'filename': '<main>',
                                                                                                    'line': 2,
                                                                                                    'start': 45,
                                                                                                    'end': 46}},
                                                                                'op': 'And',
                                                                                'rhs': {'kind': 'Binary',
                                                                                        'lhs': {'kind': 'Bool',
                                                                                                'value': True,
                                                                                                'location': {'filename': '<main>',
                                                                                                            'line': 2,
                                                                                                            'start': 50,
                                                                                                            'end': 54}},
                                                                                        'op': 'Or',
                                                                                        'rhs': {'kind': 'Bool',
                                                                                                'value': False,
                                                                                                'location': {'filename': '<main>',
                                                                                                            'line': 2,
                                                                                                            'start': 58,
                                                                                                            'end': 63}},
                                                                                        'location': {'filename': '<main>',
                                                                                                    'line': 2,
                                                                                                    'start': 50,
                                                                                                    'end': 63}},
                                                                                'location': {'filename': '<main>',
                                                                                            'line': 2,
                                                                                            'start': 45,
                                                                                            'end': 63}},
                                                                        'location': {'filename': '<main>',
                                                                                    'line': 2,
                                                                                    'start': 40,
                                                                                    'end': 63}},
                                                                'location': {'filename': '<main>',
                                                                            'line': 2,
                                                                            'start': 35,
                                                                            'end': 63}},
                                                        'location': {'filename': '<main>',
                                                                    'line': 2,
                                                                    'start': 30,
                                                                    'end': 63}},
                                                'location': {'filename': '<main>',
                                                            'line': 2,
                                                            'start': 26,
                                                            'end': 63}},
                                        'location': {'filename': '<main>',
                                                    'line': 2,
                                                    'start': 21,
                                                    'end': 63}},
                                'location': {'filename': '<main>',
                                            'line': 2,
                                            'start': 17,
                                            'end': 63}},
                        'next': {'kind': 'Print',
                                'value': {'kind': 'Var',
                                        'text': 'v',
                                        'location': {'filename': '<main>',
                                                        'line': 3,
                                                        'start': 15,
                                                        'end': 16}},
                                'location': {'filename': '<main>',
                                            'line': 3,
                                            'start': 9,
                                            'end': 17}},
                        'location': {'filename': '<main>',
                                    'line': 2,
                                    'start': 9,
                                    'end': 17}},
        'location': {'filename': '<main>', 'line': 2, 'start': 9, 'end': 17}}
    ),
    (
        "tuples",
        """
        let v = ("string", (false, (1, 2)));
        print(v)
        """,
        {'name': '<main>',
        'expression': {'kind': 'Let',
                        'name': {'text': 'v',
                                'location': {'filename': '<main>',
                                            'line': 2,
                                            'start': 13,
                                            'end': 14}},
                        'value': {'kind': 'Tuple',
                                'first': {'kind': 'Str',
                                            'value': '"string"',
                                            'location': {'filename': '<main>',
                                                        'line': 2,
                                                        'start': 18,
                                                        'end': 26}},
                                'second': {'kind': 'Tuple',
                                            'first': {'kind': 'Bool',
                                                    'value': False,
                                                    'location': {'filename': '<main>',
                                                                    'line': 2,
                                                                    'start': 29,
                                                                    'end': 34}},
                                            'second': {'kind': 'Tuple',
                                                        'first': {'kind': 'Int',
                                                                'value': 1,
                                                                'location': {'filename': '<main>',
                                                                            'line': 2,
                                                                            'start': 37,
                                                                            'end': 38}},
                                                        'second': {'kind': 'Int',
                                                                'value': 2,
                                                                'location': {'filename': '<main>',
                                                                                'line': 2,
                                                                                'start': 40,
                                                                                'end': 41}},
                                                        'location': {'filename': '<main>',
                                                                    'line': 2,
                                                                    'start': 36,
                                                                    'end': 42}},
                                            'location': {'filename': '<main>',
                                                        'line': 2,
                                                        'start': 28,
                                                        'end': 43}},
                                'location': {'filename': '<main>',
                                            'line': 2,
                                            'start': 17,
                                            'end': 44}},
                        'next': {'kind': 'Print',
                                'value': {'kind': 'Var',
                                        'text': 'v',
                                        'location': {'filename': '<main>',
                                                        'line': 3,
                                                        'start': 15,
                                                        'end': 16}},
                                'location': {'filename': '<main>',
                                            'line': 3,
                                            'start': 9,
                                            'end': 17}},
                        'location': {'filename': '<main>',
                                    'line': 2,
                                    'start': 9,
                                    'end': 17}},
        'location': {'filename': '<main>', 'line': 2, 'start': 9, 'end': 17}}
    ),
    (
        "condition",
        """
        let v = if (foo && bar || baz) 1 else if (false) true else false;
        print(v)
        """,
        {'name': '<main>',
        'expression': {'kind': 'Let',
                        'name': {'text': 'v',
                                'location': {'filename': '<main>',
                                            'line': 2,
                                            'start': 13,
                                            'end': 14}},
                        'value': {'kind': 'If',
                                'condition': {'kind': 'Binary',
                                                'lhs': {'kind': 'Var',
                                                        'text': 'foo',
                                                        'location': {'filename': '<main>',
                                                                    'line': 2,
                                                                    'start': 21,
                                                                    'end': 24}},
                                                'op': 'And',
                                                'rhs': {'kind': 'Binary',
                                                        'lhs': {'kind': 'Var',
                                                                'text': 'bar',
                                                                'location': {'filename': '<main>',
                                                                            'line': 2,
                                                                            'start': 28,
                                                                            'end': 31}},
                                                        'op': 'Or',
                                                        'rhs': {'kind': 'Var',
                                                                'text': 'baz',
                                                                'location': {'filename': '<main>',
                                                                            'line': 2,
                                                                            'start': 35,
                                                                            'end': 38}},
                                                        'location': {'filename': '<main>',
                                                                    'line': 2,
                                                                    'start': 28,
                                                                    'end': 38}},
                                                'location': {'filename': '<main>',
                                                            'line': 2,
                                                            'start': 21,
                                                            'end': 38}},
                                'then': {'kind': 'Int',
                                        'value': 1,
                                        'location': {'filename': '<main>',
                                                        'line': 2,
                                                        'start': 40,
                                                        'end': 41}},
                                'otherwise': {'kind': 'If',
                                                'condition': {'kind': 'Bool',
                                                            'value': False,
                                                            'location': {'filename': '<main>',
                                                                        'line': 2,
                                                                        'start': 51,
                                                                        'end': 56}},
                                                'then': {'kind': 'Bool',
                                                        'value': True,
                                                        'location': {'filename': '<main>',
                                                                    'line': 2,
                                                                    'start': 58,
                                                                    'end': 62}},
                                                'otherwise': {'kind': 'Bool',
                                                            'value': False,
                                                            'location': {'filename': '<main>',
                                                                        'line': 2,
                                                                        'start': 68,
                                                                        'end': 73}},
                                                'location': {'filename': '<main>',
                                                            'line': 2,
                                                            'start': 47,
                                                            'end': 73}},
                                'location': {'filename': '<main>',
                                            'line': 2,
                                            'start': 17,
                                            'end': 73}},
                        'next': {'kind': 'Print',
                                'value': {'kind': 'Var',
                                        'text': 'v',
                                        'location': {'filename': '<main>',
                                                        'line': 3,
                                                        'start': 15,
                                                        'end': 16}},
                                'location': {'filename': '<main>',
                                            'line': 3,
                                            'start': 9,
                                            'end': 17}},
                        'location': {'filename': '<main>',
                                    'line': 2,
                                    'start': 9,
                                    'end': 17}},
        'location': {'filename': '<main>', 'line': 2, 'start': 9, 'end': 17}}
    ),
    (
        "functions",
        """
        let v = fn () => (a + b) * c;
        let v = fn (a, b, c) => { a + b * fn() };
        print(v)
        """,
        {'name': '<main>',
        'expression': {'kind': 'Let',
                        'name': {'text': 'v',
                                'location': {'filename': '<main>',
                                        'line': 2,
                                        'start': 13,
                                        'end': 14}},
                        'value': {'kind': 'Function',
                                'parameters': [],
                                'value': {'kind': 'Binary',
                                        'lhs': {'kind': 'Binary',
                                                'lhs': {'kind': 'Var',
                                                        'text': 'a',
                                                        'location': {'filename': '<main>',
                                                                        'line': 2,
                                                                        'start': 27,
                                                                        'end': 28}},
                                                'op': 'Add',
                                                'rhs': {'kind': 'Var',
                                                        'text': 'b',
                                                        'location': {'filename': '<main>',
                                                                        'line': 2,
                                                                        'start': 31,
                                                                        'end': 32}},
                                                'location': {'filename': '<main>',
                                                                'line': 2,
                                                                'start': 27,
                                                                'end': 32}},
                                        'op': 'Mul',
                                        'rhs': {'kind': 'Var',
                                                'text': 'c',
                                                'location': {'filename': '<main>',
                                                                'line': 2,
                                                                'start': 36,
                                                                'end': 37}},
                                        'location': {'filename': '<main>',
                                                        'line': 2,
                                                        'start': 26,
                                                        'end': 37}},
                                'location': {'filename': '<main>',
                                        'line': 2,
                                        'start': 17,
                                        'end': 37}},
                        'next': {'kind': 'Let',
                                'name': {'text': 'v',
                                        'location': {'filename': '<main>',
                                                'line': 3,
                                                'start': 13,
                                                'end': 14}},
                                'value': {'kind': 'Function',
                                        'parameters': [{'text': 'a',
                                                        'location': {'filename': '<main>',
                                                                        'line': 3,
                                                                        'start': 21,
                                                                        'end': 22}},
                                                        {'text': 'b',
                                                        'location': {'filename': '<main>',
                                                                        'line': 3,
                                                                        'start': 24,
                                                                        'end': 25}},
                                                        {'text': 'c',
                                                        'location': {'filename': '<main>',
                                                                        'line': 3,
                                                                        'start': 27,
                                                                        'end': 28}}],
                                        'value': {'kind': 'Binary',
                                                'lhs': {'kind': 'Var',
                                                        'text': 'a',
                                                        'location': {'filename': '<main>',
                                                                        'line': 3,
                                                                        'start': 35,
                                                                        'end': 36}},
                                                'op': 'Add',
                                                'rhs': {'kind': 'Binary',
                                                        'lhs': {'kind': 'Var',
                                                                'text': 'b',
                                                                'location': {'filename': '<main>',
                                                                                'line': 3,
                                                                                'start': 39,
                                                                                'end': 40}},
                                                        'op': 'Mul',
                                                        'rhs': {'kind': 'Call',
                                                                'callee': {'kind': 'Var',
                                                                                'text': 'fn',
                                                                                'location': {'filename': '<main>',
                                                                                        'line': 3,
                                                                                        'start': 43,
                                                                                        'end': 45}},
                                                                'arguments': [],
                                                                'location': {'filename': '<main>',
                                                                                'line': 3,
                                                                                'start': 43,
                                                                                'end': 47}},
                                                        'location': {'filename': '<main>',
                                                                        'line': 3,
                                                                        'start': 39,
                                                                        'end': 47}},
                                                'location': {'filename': '<main>',
                                                                'line': 3,
                                                                'start': 35,
                                                                'end': 47}},
                                        'location': {'filename': '<main>',
                                                        'line': 3,
                                                        'start': 17,
                                                        'end': 49}},
                                'next': {'kind': 'Print',
                                        'value': {'kind': 'Var',
                                                'text': 'v',
                                                'location': {'filename': '<main>',
                                                                'line': 4,
                                                                'start': 15,
                                                                'end': 16}},
                                        'location': {'filename': '<main>',
                                                'line': 4,
                                                'start': 9,
                                                'end': 17}},
                                'location': {'filename': '<main>',
                                        'line': 3,
                                        'start': 9,
                                        'end': 17}},
                        'location': {'filename': '<main>',
                                'line': 2,
                                'start': 9,
                                'end': 17}},
        'location': {'filename': '<main>', 'line': 2, 'start': 9, 'end': 17}}
    )
]


class ParserTest(unittest.TestCase):

    def test(self):
        for test, src, expected in RINHA_PARSER_SAMPLES:
            with self.subTest(test):
                self.assertDictEqual(parser.parse(src), expected)