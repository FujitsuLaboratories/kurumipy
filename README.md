# memoization

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

## Usage

```bash
python memo_decorator.py
```

```bash
python -m unittest discover -p '*_test.py'
```
