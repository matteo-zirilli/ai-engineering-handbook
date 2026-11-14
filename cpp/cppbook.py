"""cppbook — compile and run the C and C++ examples of Part II.

Every C/C++ example in Part II is a Python cell that calls one of the helpers
below.  The helper

  1. writes the source to a file in a private build directory,
  2. compiles it with GCC (``g++ -std=c++20`` or ``gcc -std=c17``),
  3. runs the program (optionally feeding it standard input / arguments),
  4. prints Markdown: the source as a ``cpp``/``c`` code block, then the
     compiler diagnostics (if any) and the program output.

The cells are executed once by Quarto (``output: asis``) and the result is
stored in ``_freeze/``, exactly like the Python cells of Part I.  Paths of the
temporary build directory are replaced by ``.`` so that no machine-specific
path ends up in the book.
"""
from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

BUILD = Path(tempfile.mkdtemp(prefix="cppbook-"))
LAST = None   # CompletedProcess of the last program run (helpers return None so that
              # nothing extra is printed when a helper is the last line of a cell)

CXX = os.environ.get("CXX", "g++")
CC = os.environ.get("CC", "gcc")
CXXSTD = "c++20"
CSTD = "c17"
DEFAULT_FLAGS = ("-O2", "-Wall", "-Wextra")


# --------------------------------------------------------------------------- utilities
def _clean(text: str) -> str:
    """Remove machine-specific paths from compiler / sanitizer output."""
    text = text.replace(str(BUILD) + "/", "").replace(str(BUILD), ".")
    home = str(Path.home())
    text = text.replace(home, "~")
    text = re.sub(r"/tmp/cc\w+\.o", "<temporary object file>", text)
    text = re.sub(r"/usr/bin/ld(\.\w+)?:", "ld:", text)
    text = re.sub(r"==\d+==", "==PID==", text)
    return text


def _dedent(code: str) -> str:
    return textwrap.dedent(code).strip("\n") + "\n"


def _fence(body: str, cls: str = "", attrs: str = "") -> str:
    ticks = "````" if "```" in body else "```"
    head = ticks
    if cls or attrs:
        head += "{" + " ".join(x for x in (cls, attrs) if x) + "}"
    return f"{head}\n{body.rstrip()}\n{ticks}\n"


def _output_block(body: str, kind: str = "stdout") -> str:
    return (f"::: {{.cell-output .cell-output-{kind}}}\n"
            + _fence(body) + ":::\n")


def _lang_of(name: str) -> str:
    return "c" if name.endswith((".c", ".h")) and not name.endswith(".hpp") else "cpp"


def show(code: str, name: str | None = None, lang: str | None = None) -> None:
    """Print a source block (without compiling) and save it in the build dir."""
    code = _dedent(code)
    if name:
        (BUILD / name).parent.mkdir(parents=True, exist_ok=True)
        (BUILD / name).write_text(code, encoding="utf-8")
    lang = lang or (_lang_of(name) if name else "cpp")
    attrs = f'filename="{name}"' if name else ""
    print(_fence(code, "." + lang, attrs))


def write(name: str, code: str) -> Path:
    """Save a file in the build dir without showing it."""
    path = BUILD / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_dedent(code), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- compile
def compile_sources(sources, exe="prog", *, std=None, flags=DEFAULT_FLAGS, extra=(),
                    sanitize=False, lang=None, show_cmd=False, quiet_ok=True,
                    expect_error=False, label_cmd=None):
    """Compile files already written in BUILD. Returns True on success."""
    sources = [sources] if isinstance(sources, str) else list(sources)
    lang = lang or ("c" if all(s.endswith(".c") for s in sources) else "cpp")
    compiler = CC if lang == "c" else CXX
    std = std or (CSTD if lang == "c" else CXXSTD)
    cmd = [compiler, f"-std={std}", *flags]
    if sanitize:
        kinds = "address,undefined" if sanitize is True else sanitize
        cmd += ["-g", f"-fsanitize={kinds}", "-fno-omit-frame-pointer"]
    cmd += [f"-fdebug-prefix-map={BUILD}=.", *sources, *extra, "-o", exe]
    proc = subprocess.run(cmd, cwd=BUILD, capture_output=True, text=True)
    shown = label_cmd or " ".join(shlex.quote(c) for c in cmd if not c.startswith("-fdebug-prefix-map"))
    if show_cmd:
        print(_fence("$ " + shown, ".bash"))
    diag = _clean(proc.stderr)
    if diag.strip():
        print(_output_block(diag, "stderr"))
    if proc.returncode != 0 and not expect_error:
        raise RuntimeError("compilation failed:\n" + diag)
    if proc.returncode == 0 and expect_error:
        raise RuntimeError("compilation was expected to fail")
    global LAST_COMPILE_OK
    LAST_COMPILE_OK = proc.returncode == 0
    return None


LAST_COMPILE_OK = True


def run_exe(exe="prog", *, stdin=None, args=(), show_stdin=True, timeout=30,
            show_status=True, env=None, merge_stderr=True, max_lines=None, label=None,
            filter_lines=None):
    """Run a compiled program and print its output. Returns CompletedProcess."""
    if stdin is not None and show_stdin:
        print("*Standard input:*\n")
        print(_fence(_dedent(stdin) if stdin.strip() else stdin, ".default"))
    if label:
        print(label + "\n")
    run_env = dict(os.environ, **(env or {}))
    run_env.setdefault("ASAN_OPTIONS", "detect_leaks=1")
    proc = subprocess.run([f"./{exe}", *args], cwd=BUILD,
                          input=(_dedent(stdin) if stdin and stdin.strip() else stdin),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT if merge_stderr else subprocess.PIPE,
                          text=True, timeout=timeout, env=run_env)
    out = proc.stdout
    out = _clean(out)
    if filter_lines is not None:
        out = "\n".join(l for l in out.splitlines() if filter_lines(l)) + "\n"
    if max_lines is not None:
        lines = out.splitlines()
        if len(lines) > max_lines:
            out = "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
    if show_status and proc.returncode > 0:
        out = out.rstrip("\n") + f"\n[process exited with status {proc.returncode}]"
    elif show_status and proc.returncode < 0:
        import signal
        out = out.rstrip("\n") + f"\n[process killed by signal {signal.Signals(-proc.returncode).name}]"
    if out.strip():
        print(_output_block(out))
    global LAST
    LAST = proc
    return None


def run(code: str, name: str = "main.cpp", *, stdin=None, args=(), flags=DEFAULT_FLAGS,
        extra=(), std=None, sanitize=False, show_source=True, show_cmd=False,
        expect_error=False, run_it=True, show_filename=False, max_lines=None,
        timeout=30, filter_lines=None):
    """Show, compile and run a single-file C or C++ program."""
    code = _dedent(code)
    (BUILD / name).write_text(code, encoding="utf-8")
    lang = "c" if name.endswith(".c") else "cpp"
    if show_source:
        print(_fence(code, "." + lang, f'filename="{name}"' if show_filename else ""))
    exe = Path(name).stem
    compile_sources([name], exe, std=std, flags=flags, extra=extra, sanitize=sanitize,
                    lang=lang, show_cmd=show_cmd, expect_error=expect_error)
    if not LAST_COMPILE_OK or not run_it:
        return None
    run_exe(exe, stdin=stdin, args=args, max_lines=max_lines, timeout=timeout,
            show_stdin=stdin is not None, filter_lines=filter_lines)
    return None


def sh(command: str, *, show_cmd=True, max_lines=None, filter_fn=None):
    """Run a shell command in the build dir (e.g. nm, objdump) and show it."""
    proc = subprocess.run(command, cwd=BUILD, shell=True, capture_output=True, text=True,
                          executable="/bin/bash")
    out = _clean(proc.stdout + proc.stderr)
    if filter_fn:
        out = "\n".join(l for l in out.splitlines() if filter_fn(l))
    if max_lines is not None:
        lines = out.splitlines()
        if len(lines) > max_lines:
            out = "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
    if show_cmd:
        print(_fence("$ " + command, ".bash"))
    if out.strip():
        print(_output_block(out))
    return None


def path(name: str) -> Path:
    """Absolute path of a file in the build directory (for Python code that drives a program)."""
    return BUILD / name


def compiler_version() -> str:
    return subprocess.run([CXX, "--version"], capture_output=True, text=True).stdout.splitlines()[0]


def sanitizer_summary(line: str) -> bool:
    """Keep only the informative lines of an AddressSanitizer/UBSan report."""
    keys = ("ERROR: AddressSanitizer", "ERROR: LeakSanitizer", "READ of size", "WRITE of size",
            "    #0 ", "    #1 ", "SUMMARY:", "runtime error:", "freed by thread", "previously allocated",
            "Direct leak", "is located")
    return (any(k in line for k in keys) and "libc" not in line and "libasan" not in line
            and "libsanitizer" not in line)
