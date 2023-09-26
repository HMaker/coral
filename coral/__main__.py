import typing as t
import orjson
import argparse
from coral import parser, ast, compiler


argsparser = argparse.ArgumentParser(
    prog='coral',
    description=(
        'The coral compiler compiles a very simple, immutable, dynamically typed programming '
        'language called "rinha". It was subject of a code interpreter contest I participated.'
    )
)
argsparser.add_argument(
    'file',
    help='rinha AST JSON file (.json)'
)
argsparser.add_argument(
    '-ll',
    '--emit-llvm',
    action='store_true',
    default=False,
    help='emit the LLVM IR to stdout instead of running the machine code'
)
argsparser.add_argument(
    '-vll',
    '--verify-llvm',
    action='store_true',
    default=False,
    help='validate the instructions in the LLVM IR and emit it to stdout'
)
argsparser.add_argument(
    '-p',
    '--parse',
    action='store_true',
    default=False,
    help='parse rinha source file (.rinha) instead of JSON'
)
args = argsparser.parse_args()
with open(args.file, 'r') as file:
    if args.parse:
        rinha = parser.parse(file.read())
    else:
        rinha = orjson.loads(file.read())

comp = compiler.CoralCompiler.create_default(ast.Program(
    filename=rinha['name'],
    body=ast.typecheck(rinha['expression'])
))
if args.emit_llvm or args.verify_llvm:
    print(comp.compile_ir(verify=args.verify_llvm))
else:
    comp.compile()()
