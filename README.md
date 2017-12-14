# KurumiPy

KurumiPy is an enhanced memoization library.

Kurumi stands for walnut in Japanese. They say walnuts improve memory.

## Disabling salt

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

## Installing dependent packages

Please install [fasteners 0.14.1](https://pypi.python.org/pypi/fasteners).

```bash
pip install fasteners==0.14.1
```

or

Add 'fasteners==0.14.1' to your 'requirements.txt' and install.

## Usage

```bash
python main.py
```

```bash
# bash
python -m unittest discover -p '*_test.py'
# Command prompt
python -m unittest discover -p *_test.py
```

## How to apply to other projects

Copy the 'memoization folder' to apply project.

Import the copied module.

```python
import memoization.memo_decorator as memo_decorator
```

Write a decorator in a function that applies memoization.

```python
@memo_decorator.memo
def applied_function(n):
    ...
```

The applicable function has the following restrictions.

* Pure function
* Arguments are string type, numeric type, etc. (Not supported: list type, dict type, set type, file objects etc.)
* Not supported: Mutual recursive function in multiple threads (Dining Philosophers Problem).

The cache data output folder is as follows.

* \memoization\memocache\
