import os
import sys
from typing import Dict, List
import fire

def pretty(num):
    kb = round(num / 1024)
    mb = round(kb / 1024)
    gb = round(10 * mb / 1024) / 10
    
    if mb > 1024: return f"{gb} GB"
    if kb > 1024: return f"{mb} MB"

    return f"{kb} KB"
    
class DirTree:
    """An object representing either a directory or a file.
    """
    def __init__(self, name: str, is_file: bool, subdirs: List['DirTree'] = None, size: int = -1, root: bool = False):
        """
        Args:
            name (str): The full file path of this file/directory
            is_file (bool): Is this a file, or a directory.
            subdirs (List[DirTree]): If this is given, then this constructor does not perform the (potentially slow) operation of finding and creating its subdirectories,
                but instead uses the one you provided. 
                Defaults to None.
            size (int, optional): The total size of this folder. If not given, or equal to -1, it will be calculated recursively. Defaults to -1.
            root (bool, optional): Is this the root of the directory structure. Simply does printing output to show progress when building the cache the first time. Defaults to False.
        """
        self.name = name
        self._size = size
        self.is_file = is_file
        self.subdirs = []
        self.root = root
        
        if not self.is_file and subdirs is None:
            self.subdirs = []
            li = os.listdir(self.name)
            for index, name in enumerate(li):
                if self.root:
                    print(f"\r{index+1}/{len(li)}", end='')
                full_path = os.path.join(self.name, name)
                if os.path.islink(full_path): continue
                try:
                    self.subdirs.append(
                        DirTree(full_path, os.path.isfile(full_path))
                    )
                except Exception as e:
                    pass
            if self.root:
                print("")

        if subdirs is not None:
            self.subdirs = subdirs

    def size(self) -> int:
        # Calc the size if you need to.
        if self._size == -1:
            self._size = self.calc_size()
        return self._size
    
    def calc_size(self) -> int:
        """Returns the size in bytes of this folder/file

        Returns:
            int: 
        """
        if self.is_file:
            # Get file size
            try:
                return os.path.getsize(self.name)
            except Exception as e:
                return 0
        else:
            # Recursively get size of all subdirs.
            return sum(s.size() for s in self.subdirs)
    
    def print(self, depth: int, t: int, top: int = None):
        """This prints the directory structure in a specific way.
             It recursively prints up to a certain depth, and for each directory, only the 'top' largest items are shown. 

        Args:
            depth (int): The depth to print to. If this is 1, then only print the main directory.
            t (int): If this is 0, then it's the root, and it prints the total value too.
            top (int, optional): How many items to show per directory. It shows only the largest 'top' items. If this is None, we show all items. Defaults to None.
        """
        if depth < 0: return
        self.subdirs = sorted(self.subdirs, key=lambda s: s.size(), reverse=True)
        total = 0
        tab = '\t'
        if t != 0:
            n = self.name.split("/")
            name = ' ' * len('/'.join(n[:-2])) + '/'.join(n[-2:])
            # name = self.name
        else:
            name = self.name
        print(f"{pretty(self.size()): <10}{tab * (1)}{name}")

        for s in self.subdirs[:top]:
            if t == 0:
                print("-" * 10)
            s.print(depth-1, t+1, top)
            total += s.size()
        if t == 0:
            print("-" * 50)
        if t == 0:
            print(f"Total {pretty(total)} / {pretty(self.size())}")

    def repr(self, size_limit = 1024 * 1024 * 50) -> str:
        """Writes in a format that is understandable to the cache.

        Args:
            size_limit ([type], optional): Any files/folders under this limit (in bytes) won't be shown directly, but their sizes will still be captured in their parents . Defaults to 1024*1024*50.

        Returns:
            str: The string representing this tree
        """
        name = self.name
        if self.size() < size_limit:
            return ""
        my_string = (f"{self.size()} | {self.is_file} | {name}")
        for s in self.subdirs:
            new = s.repr(size_limit)
            if new  == "": continue
            my_string += "\n" + new
        return my_string

    @staticmethod
    def from_cache(filename: str) -> "DirTree":
        """Constructs this tree from the cache given by the filename.

        Returns:
            DirTree: The tree represented by the cache.
        """
        with open(filename, 'r') as f:
            files = f.readlines()
        # Remove errors
        files = [f for f in files if 
            'Error [Errno' not in f
        ]
        dict_of_alls: Dict[str, DirTree] = {

        }
        root = None
        for file in files:

            file = file.strip()
            
            try:
                size, is_file, path = file.split(" | ")
            except Exception as e:
                pass

            size = int(size); is_file = is_file == 'True'
            if root is None:
                root = path            
            base = os.path.dirname(path)

            if base in dict_of_alls:
                tree = DirTree(path, is_file, [], size)
                dict_of_alls[base].subdirs.append(tree)
                dict_of_alls[path] = tree
            else:
                tree = DirTree(path, is_file, [], size)
                dict_of_alls[path] = tree

        return dict_of_alls[root]

    def find(self, directory_name: str) -> "DirTree":
        """Returns a DirTree given by the path / dirname or filename.

        Returns:
            DirTree: The subtree, or None
        """
        # Return if one of our subdirs' name is correct.
        for f in self.subdirs:
            if f.name == directory_name or f.name.split('/')[-1] == directory_name:
                return f
        # Or recursively call this.
        for f in self.subdirs:
            ans = f.find(directory_name)
            if ans is not None:
                return ans
        return None    

    def to_cache(self, filename: str):
        with open(filename, 'w+') as f:
            string = self.repr()
            f.write(string)


def main(depth: int = 1, top: int = 10, dir: str = None, rebuild_cache: bool = False):
    """Performs the main operations

    Args:
        depth (int, optional): The depth to print to. Defaults to 1.
        top (int, optional): The number of folders to print for each directory. Defaults to 10.
        dir (str, optional): The subdirectory to find. If it is None, then we simply do the route.. Defaults to None.
        rebuild_cache (bool, optional): If this is True, rebuilds the cache. Defaults to False.
    """
    cache = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache.txt')
    if os.path.exists(cache) and not rebuild_cache:
        dirtree = DirTree.from_cache(cache)
    else:
        dirtree = DirTree(os.environ['HOME'], False, root=True)
        dirtree.to_cache(cache)
    if dir is not None:
        dirtree = dirtree.find(dir)
    dirtree.print(depth=depth, top=top, t=0)



fire.Fire(main)

# tree = DirTree.from_cache('cache5.txt')
# tree = DirTree.from_cache('cache6.txt')
# tree.print(depth=1, top=20, t=0)
# tree = DirTree(sys.argv[1], False)
# tree.print(1000, 0, top=None)
# tree.to_cache('cache_new.txt')
# print(tree.repr(100 * 1024**2))
