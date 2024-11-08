Our dataset is publically available at https://app.roboflow.com/tafelvoetbaltafelballen/foosbetterer/5.

To place the dataset in this project to train properly, download from Roboflow in the YOLO11 format and place in the datasets folder. You can then use `train_yolo.py` to train a new model.

The dataset is based on roughly 6200 hand-annotated images, including about 1000 null images. Images were taken from real foosball games, with changes in lighting between a regular lamp positioned above the table, and the coloured LEDs used in the final product. There are images using both white and cork balls, both in the different lighting conditions. Images were annotated such that if the ball is partially obscured, the bounding box was drawn around the entire position of the ball (i.e. including around the obscured area). 

For training our model, several augmentations were additionally applied: the images were flipped horizontally and vertically, rotated between -6 degrees and +6 degrees, and brightness was adjusted between -15% and +15%. This was to account for different camera positions and lighting conditions. This amounted to a total of more than 14000 images to train on.