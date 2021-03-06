# KurumiPy

KurumiPy is an enhanced memoization library.

Kurumi stands for walnut in Japanese. They say walnuts improve memory.

## Features

Usual memoizations keep return values associated with arguments only.
KurumiPy provides an enhanced memoization with features following.

* Changes in your function
  * KurumiPy automatically invalidates cache when you change implementation of the target function. It is useful for test-driven development.
* Changes in dependent variables
  * KurumiPy automatically invalidates cache when any dependent variables of the target function have been changed. It is useful if you modify parameters and re-execute your program.
* Inter-process
  * KurumiPy shares cache amoung processes. Even if your program runs in multiple processes, KurumiPy handles cache correctly.

## Setting up

### Python 3

Supported versions of Python are 3.x.

### Installing dependent packages

Please install [fasteners 0.14.1](https://pypi.python.org/pypi/fasteners).

```bash
pip install fasteners==0.14.1
```

or

Add 'fasteners==0.14.1' to your 'requirements.txt' and install.

### How to apply to your project

Copy 'memoization' folder to your project, then import the module.
Write a decorator to functions to enable memoization.

```python
from memoization.memo_decorator import memo

@memo
def your_function(n):
    # ...
```

Functions should meet the restrictions following.

* Pure functions
* Arguments are string type, numeric type, etc. (Not supported: list type, dict type, set type, file objects etc.)
* Not supported: Mutual recursive function in multiple threads (Dining Philosophers Problem).

Cache files will be stored in the folder following.

* `./memoization/memocache`

### Disabling salt

Python 3.3 enables "salt" on hash of str, bytes and datetime objects by default.
See <https://docs.python.org/3/reference/datamodel.html#object.__hash__> for details.
Salt prevents consistent hash values across processes.
You need to disable it before running Python programs.

```bash
# bash
export PYTHONHASHSEED=0
# Command prompt
set PYTHONHASHSEED=0
```

You have to set environment variable only once until you exit bash or command prompt.

## Test

```bash
# bash
python -m unittest discover -p '*_test.py'
# Command prompt
python -m unittest discover -p *_test.py
```

```bash
python main.py
```

## Related project

* [IncPy](http://www.pgbovine.net/incpy.html)

## License

Apache License 2.0
