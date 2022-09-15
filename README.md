# AGV Positining

This program is meant for assessing the position of an AGV and was developed as part of my bachelor's thesis at TUM.

## Installation

To install, clone this repository by typing

`git clone https://github.com/ariel-lindemann/ba_project`

Then, install the required dependencies:

`make init`

On macos you might have to insead use:

`pip3 install -r requirements.txt`

## Usage

You can start the application, by typing:

`make run`

### Camera calibration

Before running the program for the first time, you should use your camera to take some calibration pictures. 
Some tips about how to do this:
+ the images should be from different angles
+ try to keep all chessboard corners inside the frame, otherwise the program will disregard them
+ try to keep the board steady as you take the picture. If the image is blurry, it will also be disregarded
+ if you printed the image on a sheet of paper, attach it to a rigid surface. If it is possible to move your camera instead of the calibration pattern, then do it
+ take at least 15 to 20 pictures. The more the better

If you are using the program for the first time and decide not to take the calibration images, the program will attempt to
take those images itself. 

### Functionality

