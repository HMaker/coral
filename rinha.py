import orjson
from coral import ast, compiler


with open('/var/rinha/source.rinha.json', 'rb') as file:
    src = orjson.loads(file.read())
comp = compiler.CoralCompiler.create_default(ast.Program(
    filename=src['name'],
    body=ast.typecheck(src['expression'])
))
comp.compile()()
