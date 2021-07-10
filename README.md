# vigilant-engine

This is a program that can show the sizes of directories and files.

## Installation

Simply install the [Fire](https://github.com/google/python-fire) library using 
```
pip install fire
```

## Usage
```
python main.py --depth 2 --top 10
```

Or use the `--dir` option to search for a subdirectory, e.g. `--dir /home/name/desktop/movies`.

The program builds a cache the first time it runs (which may take a long time but speeds up subsequent calls) and you can rebuild it using the `--rebuild-cache` flag.

Tested on Mac.