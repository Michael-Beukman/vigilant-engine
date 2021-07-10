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

Tested on Mac and Linux.


## Examples
Here are some examples

```
python main.py --depth 2 --top 2

37.3 GB   	/home/mike
----------
25.0 GB   	     mike/big_folder
11.7 GB   	          big_folder/big_subfolder
10.8 GB   	          big_folder/other_folder
----------
4.3 GB    	     mike/.cache
3.1 GB    	          .cache/cache1
1.2 GB    	          .cache/cache2
--------------------------------------------------
Total 29.3 GB / 37.3 GB
```

```
python main.py --depth 3 --top 1

37.3 GB   	/home/mike
----------
25.0 GB   	     mike/big_folder
11.7 GB   	          big_folder/big_subfolder
3.8 GB    	                    big_subfolder/deep_subfolder
--------------------------------------------------
Total 25.0 GB / 37.3 GB
```


```
python main.py --depth 1 --top 2 --dir /home/mike/big_folder/big_subfolder

11.7 GB   	/home/mike/big_folder/big_subfolder
----------
3.8 GB    	                    big_subfolder/deep_subfolder
----------
3.6 GB    	                    big_subfolder/other_deep_subfolder
--------------------------------------------------
Total 7.4 GB / 11.7 GB
```