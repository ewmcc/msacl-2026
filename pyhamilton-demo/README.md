# PyHamilton Demo

A beginner-friendly demo of [pyhamilton](https://github.com/dgretton/pyhamilton), which controls a Hamilton STAR liquid handler from Python.

The notebook [pyhamilton_demo.ipynb](pyhamilton_demo.ipynb) loads the VENUS layout
`C:\Program Files (x86)\HAMILTON\Methods\Demo\msacl-2026-demo.lay` and runs these steps:

1. Picks up 8 tips.
2. Aspirates 700 uL of water from the center trough.
3. Dispenses into each well of the 96-well plate, one column at a time.

## Prerequisites

These come from the pyhamilton README:

- Windows with Hamilton VENUS installed and tested
- Python 3.13 or older
- [Git for Windows](https://git-scm.com/download/win)
- .NET Framework 4.0 or higher
- Microsoft Access Database Engine, matching your Python's bitness (32-bit or 64-bit)

## Install

Open a terminal in this folder and run:

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip setuptools
pip install -r requirements.txt
```

`requirements.txt` installs pyhamilton straight from GitHub, because the PyPI release is out of date.

Then run this **once**, from a terminal opened as Administrator with the venv active:

```
pyhamilton-configure
```

This copies pyhamilton's HSL libraries into `C:\Program Files (x86)\HAMILTON\Library` and opens a few Hamilton library installers. Click through each installer.

> The pyhamilton README's own install method is `git clone https://github.com/dgretton/pyhamilton`,
> then `cd pyhamilton` and `pip install -e .`. Our `requirements.txt` does the same thing for you.

## Run the demo

1. In the VENUS System Configuration Editor, turn on **Simulation** mode. This gives you a dry run with no robot.
2. Open `pyhamilton_demo.ipynb` in VS Code, or run `jupyter notebook`.
3. Select the `.venv` Python kernel.
4. Run the cells from top to bottom. VENUS Run Control opens and shows each step.
