# The Drunken Mario Adventures — solution notes

**Flag: `SIGMOID_TANH`**

## How the message is hidden
- `marathon-lab-linux-x86_64` is a Nuitka onefile build of a pygame app (modules `lab.level`, `lab.engine`, `lab.brain`, `lab.fitness`, `lab.evolution`).
- The level has 20 ground-row coins at columns
  `[7, 12, 17, 25, 32, 43, 61, 66, 73, 80, 93, 101, 110, 118, 130, 157, 172, 195, 201, 206]`.
- `lab.fitness._SIGN` assigns each coin a bit (1 = rewarded, 0 = penalised). The fully trained agent
  takes exactly the 1-coins and walks past the 0-coins.
- Taken/skipped over the 20 sites in order: `10100 00001 01110 01000` = 20, 1, 14, 8 = **T A N H** (A=1).

## Evidence
- `run_proven.out`: the embedded `lab/proven.npy` genome (blended into the population when training
  stagnates) finishes the level taking coins at columns 7, 17, 80, 101, 110, 118, 172 — identical to `_SIGN`.
- `verify.out`: the reward function gives +/- per coin matching `_SIGN`.
- `inject.out`: full dump of every lab module's globals.

## Method
The binary needs glibc 2.38, so it ran in an Ubuntu 24.04 Docker container on the H100 under Xvfb.
Because the executable exports the CPython C API (extension modules need it), `gdb -p` could call
`PyGILState_Ensure` / `PyRun_SimpleString` to execute `inject.py`, `run_proven.py`, `verify.py` inside the
live process. `parse.py` decodes Nuitka's constant blob; `sim`-style scripts are not needed here.
