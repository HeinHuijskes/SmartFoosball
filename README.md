# SmartFoosball
Smart Foosball Design Project 1A 2024

To install dependencies, run `poetry install`

# Requirements and installation

## Pull this repository
To get this repository, pull it from github using git or clone it and create your own fork. 

## Install requirements

### Python
Python 3.11 was used to develop this project, though a lower version is likely fine.

### Use poetry to manage dependencies
Poetry was used to manage dependencies. Run:

```
pip install poetry
poetry install
``` 
Also run:
```pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --upgrade --force-reinstall```
Good luck.

This should install all necessary dependencies for you, so you can skip the steps below. To add a new dependency, simply run `poetry add package-name`, to add package `package-name`.

Poetry uses a virtual environment to run, so precede any command by `poetry run`, e.g. `poetry run python tests/databaseTest.py`.

To list the dependencies used in poetry, use `poetry show`.

## Postgres
See [POSTGRES.md](info/POSTGRES.md).

# Running the project

## Env
Copy the file `env.example.py` and rename the copy to `env.py`. This sets up the needed variables in a way that is not tracked by git, so that your password is not shared.

## Run
T.B.D.