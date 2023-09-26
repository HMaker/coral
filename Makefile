export C_INCLUDE_PATH=/usr/lib/gcc/x86_64-linux-gnu/10/include
CLANG := /usr/lib/llvm-10/bin/clang

type:
	mypy

python:
	python ./setup.py bdist_wheel

runtime:
	${CLANG} -shared -fPIC -O3 -I./coral/runtime -o ./coral/runtime.so ./coral/runtime/runtime.c
