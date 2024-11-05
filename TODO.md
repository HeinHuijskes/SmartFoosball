# Future improvements

A bunch of features can still be improved or added new to the system. Here is a small list to start you off.

## Features

#### Game commentary
The system currently detects where the ball is, when a goal is made, who the last kicker was, and more. This information could be combined to generate live commentary, either from an existing set of commentary or auto-generated.

#### Voice commands
Currently the system has to be manually reset, either by restarting the system, clicking on the website, or pressing a physical button. It would be much nicer and smarter to run voice recognition and give commands to the system this way.

#### VAR button
In case of a violation, some footage might need to be reviewed. The system already has functionality for rewinding footage, but only upon scoring a goal. A VAR button could be added that replays footage on click.

#### USTSA rules
The system currently takes only a few official foosball rules into consideration, for instance the maximum 15 second posession rule. Additional rules could be added.

#### Data
The current display of data collected about the game is limited, this could be made more extensive and visually interesting.

## Codebase 

#### Dynamic colour detection
Currently all colour segmentation and masking is done via hardcoded values for different colours. This should not be necessary however, since the table gets cropped to a predermined size and place on the screen, so it should be possible to read out the values of blue and red during runtime, and add a range around those. 

#### Different foosman detection
Another issue with colour detection came with the addition of LED lights of the same colour. Segmentation is now nearly impossible, at least for blue colours. Therefore another method for detecting foosman could be used, for instance accurate guesses based on position or another Machine Learning model. By annotating each foosman additionally in the dataset, the model could detect both the ball and the foosmen simultaneously.

#### Relative sizes
Currently all sizes are hardcoded as amount of pixels on the screen. Again, after cropping the proportions of the table should always be the same, so it should be possible to use screen proportions instead of exact pixels (e.g. 1/8th of the screen instead of 400px). Then during runtime this could be converted to pixel coordinates using the size of a frame.

