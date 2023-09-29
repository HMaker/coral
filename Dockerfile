FROM python:3.11-slim AS base

ENV PYTHONWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# install LLVM 14
RUN apt update \
    && apt install --no-install-recommends -y lsb-release software-properties-common gpg wget build-essential \
    && wget https://apt.llvm.org/llvm.sh \
    && chmod +x llvm.sh \
    && ./llvm.sh 14


FROM base AS coral

RUN mkdir /opt/coral
WORKDIR /opt/coral
RUN pip3 install wheel
ADD requirements.txt .
RUN pip3 install -r requirements.txt
ADD coral coral

# build the runtime lib
ADD Makefile .
RUN C_INCLUDE_PATH="$(dirname $(find /usr/lib -type f -name 'stddef.h' | head -n1))" \
    CLANG="/usr/lib/llvm-14/bin/clang" \
    make runtime

# populate the python bytecode cache aka __pycache__
ADD coral.py .
RUN python3 coral.py --help

ADD rinha.py .
ENTRYPOINT [ "python3", "rinha.py" ]
