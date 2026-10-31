"""Runs a check_program inside the sandbox. It's started by sandbox.py and never imported.

Heavy modules load first; then an audit hook, which can't be removed, blocks network, processes, native
code and writes, and reads are limited to the Python install. Imports from the program itself must be on
the allow-list. See sandbox.py for what this does and doesn't protect against.
"""
import builtins
import os
import sys

ALLOWED = {"sympy", "mpmath", "numpy", "math", "cmath", "fractions", "decimal", "itertools", "functools", "collections",
           "heapq", "bisect", "operator", "statistics", "string", "re", "numbers", "typing", "dataclasses", "sys"}

import sympy  # noqa: E402,F401
import numpy  # noqa: E402,F401
import fractions, decimal, itertools, functools, collections, heapq, bisect, operator, statistics, string, re, numbers, typing, dataclasses, cmath, math  # noqa: E401,E402,F401

prog_path = os.path.abspath(sys.argv[1])
source = open(prog_path, encoding="utf-8").read()
read_roots = tuple(os.path.normcase(os.path.abspath(p)) for p in {sys.prefix, sys.base_prefix, sys.exec_prefix, os.path.dirname(sympy.__path__[0])})
BLOCKED = ("socket.", "subprocess.", "os.system", "os.exec", "os.spawn", "os.posix_spawn", "os.startfile", "os.fork", "os.kill", "ctypes.",
           "winreg.", "webbrowser.", "urllib.", "http.", "ftplib.", "smtplib.", "os.remove", "os.rename", "os.rmdir", "os.mkdir", "os.chmod",
           "os.link", "os.symlink", "os.truncate", "shutil.", "tempfile.", "msvcrt.", "sys.addaudithook", "sys.settrace", "sys.setprofile", "mmap.")


class Violation(BaseException):
    pass


def hook(event, args):
    if event.startswith(BLOCKED):
        raise Violation(f"sandbox: {event} is not allowed")
    if event == "open":
        path, mode, flags = args
        if isinstance(path, int):
            return
        writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT))
        if writing:
            raise Violation(f"sandbox: writing {path} is not allowed")
        if not os.path.normcase(os.path.abspath(os.fspath(path))).startswith(read_roots):
            raise Violation(f"sandbox: reading {path} is not allowed")


_import = builtins.__import__
PROG = "__check_program__"


def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if globals and globals.get("__name__") == PROG and (level or name.split(".")[0] not in ALLOWED):
        raise Violation(f"sandbox: import of {name} is not allowed")
    return _import(name, globals, locals, fromlist, level)


builtins.__import__ = guarded_import
code = compile(source, "check_program", "exec")
sys.addaudithook(hook)
sys.argv = ["check_program"]
try:
    exec(code, {"__name__": PROG, "__builtins__": builtins})
except Violation as e:
    print(str(e), file=sys.stderr)
    sys.stdout.flush()
    os._exit(77)
