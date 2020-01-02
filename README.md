# vcsgen
Command line utility for generating video contact sheets.
Note: Work in progress

## Usage
```sh
$ python3 vcsgen.py --help
usage: PROG [--help] [-i INPUT] [-w WIDTH] [-h HEIGHT] [-s START]
            [--freq FREQ] [--columns COLUMNS] [--rows ROWS] [--font FONT]
            [--color COLOR] [--header HEADER] [--tcode TCODE] [--logo LOGO]

optional arguments:
  --help                show this help message and exit
  -i INPUT, --input INPUT
                        Input file to be processed
  -w WIDTH, --width WIDTH
                        Snapshot width
  -h HEIGHT, --height HEIGHT
                        Snapshot height
  -s START, --start START
                        Snapshot start time
  --freq FREQ           Snapshot frequency in seconds
  --columns COLUMNS     Number of columns for video contact sheet generation
  --rows ROWS           Number of rows for video contact sheet generation
  --font FONT           TrueType or OpenType font path
  --color COLOR         Font color for both caption and time-code. See
                        'colors.txt' file for full list of color names
  --header HEADER       Font size for header
  --tcode TCODE         Font size for time-code
  --logo LOGO           Logo image path

```

## Example

```sh
python3 vcsgen.py --input tests/data/videos/sintel.mp4 --logo tests/data/logo/logo.png --start 4 --freq 4 --rows 3 --columns 3
```

![Image](<https://drive.google.com/file/d/1-kfWtnGTLREMnh6Ye1F05COO5caH5BWl/view?usp=sharing>)

## Requirements

Python modules:
* python3-pil (https://github.com/python-pillow/Pillow)
* python3-vlc (https://github.com/oaubert/python-vlc)

## Installation

Debian/Ubuntu:
```sh
apt install python3-pil python3-vlc
```

## TODO
* Write tests.
* Add support for some kind of blank-scene detection.
* Fix random delays appearing in time-codes.
* Fix audio information in contact sheet header.
