# SmartFoosball
Smart Foosball Design Project 1A 2024, University of Twente. 

Created by Hein Huijskes, Iris ten Klooster, Mathijs Vogelezang, Melle Ploeg, and Sophie Takken.

## Requirements
- Python 3.11
- Poetry

## Dependencies
The entire project can be installed by and run with poetry. Run the following commands to install poetry along with all dependencies and scripts:
```
pip install poetry
```
```
poetry install
```

## Commands
Some scripts were defined to easily run the project. Below is an overview of some scripts and extra parameters/commands.

#### Run
To preview the system without running the website or ESPN, use `poetry run demo` or `poetry run demo-2` to run one of the two included demo videos.

To run the system with website and ESPN, run the `run_system.py` file. To do so, you must be connected to the local network of the IoT lab, to which the ESPN is also connected. Make sure to copy the `arduinoCode.ino.example` file beforehand, change the copy's name to `arduinoCode.ino`, 
and change the password line in it to the correct password.

Additionally add `-d` for debug mode and `-b <amount>` to change the length of the ball tracking line.

#### Key bindings
When showing frames locally, some keybinds are available to change the behaviour. They are listed here.
- `p` pauses the video
- `c` recalibrates the system, and redetects the corners
- `q` exits the system
- `s` resets maximum detected ball speed

#### Debug
In debug mode, additional keybinds are available.
- `r` and `b` change the mode to only show blue or red colours
- `f` and `n` switch between normal and full-colour
- `d` is disco mode
- `z` zooms in on the ball

## Other
#### Train ML
`train_yolo.py` is used to train or evaluate new Machine Learning models on custom training data. 
#### Generate images
`generate_data.py` is used to run through the frames in a video and prepare them for image annotation. It crops and rotates the frames, and saves the frames.