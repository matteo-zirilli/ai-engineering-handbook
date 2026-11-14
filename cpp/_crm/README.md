# CRM prototype for an insurance agency network (C++20)

Reference implementation of the Part II project of the
[AI Engineering Handbook](https://matteo-zirilli.github.io/ai-engineering-handbook/):
a terminal application that keeps customers and their interactions
(appointments and contracts) in one place and saves them to CSV files.

## Build

Requirements: a C++20 compiler (GCC ≥ 11, Clang ≥ 14 or MSVC 2022) and CMake ≥ 3.20.

```bash
cmake -S . -B build              # configure (once)
cmake --build build              # compile: produces build/crm and build/crm_tests
```

On Windows with Visual Studio the executables are in `build\Debug\`; with
MSYS2/MinGW (see the handbook, Chapter "Setting up a C and C++ development
environment") they are in `build\`.

## Run

```bash
./build/crm                      # uses the folder ./data (created if missing)
./build/crm path/to/folder       # another data folder
./build/crm data --echo < session.txt   # scripted input; --echo repeats each input line
```

The folder `data/` contains sample data: four customers and five interactions.
The program loads `data/customers.csv` and `data/interactions.csv` at start,
saves after every change and when it exits (option 0, or end of input with
Ctrl+D on Linux/macOS, Ctrl+Z then Enter on Windows). Lines of the data files
that cannot be read are skipped with a warning on standard error, and the
original files are kept as `*.bak` at the first save.

Exit status: 0 = normal end, 1 = the data could not be saved, 2 = wrong usage.

## Test

```bash
./build/crm_tests                # or: ctest --test-dir build
```

## Layout

```text
include/crm/   headers: text, date, interaction, customer, crm, storage, console_ui
src/           implementations and main.cpp
tests/         automated checks (no external library)
data/          sample data files
```

## Data format

`customers.csv`: `id,first_name,last_name,phone,email,city`

`interactions.csv`: `id,customer_id,kind,date,time,agent,place,policy_number,product,premium_cents,end_date,notes`
(`kind` is `appointment` or `contract`; columns that do not apply to a kind are
empty; premiums are integer cents). Fields containing commas or quotes are
quoted as in RFC 4180; text is UTF-8.
