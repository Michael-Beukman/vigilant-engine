import os
import sys
from typing import Dict, List
folder = os.getcwd()

def pretty(num):
    kb = round(num / 1024)
    mb = round(kb / 1024)
    gb = round(10 * mb / 1024) / 10
    
    if mb > 1024: return f"{gb} GB"
    if kb > 1024: return f"{mb} MB"

    return f"{kb} KB"
    
class DirTree:
    def __init__(self, name: str, is_file: bool, subdirs: List['DirTree'] = None, size: int = -1):
        self.name = name
        self._size = size
        self.is_file = is_file
        self.subdirs = []
        if not self.is_file and subdirs is None:
            self.subdirs = []
            for name in os.listdir(self.name):
                full_path = os.path.join(self.name, name)
                if os.path.islink(full_path): continue
                try:
                    self.subdirs.append(
                        DirTree(full_path, os.path.isfile(full_path))
                    )
                except Exception as e:
                    print(f"Error {e}")

        if subdirs is not None:
            self.subdirs = subdirs

    def size(self) -> int:
        if self._size == -1:
            self._size = self.calc_size()
        return self._size
    
    def calc_size(self):
        if self.is_file:
            try:
                return os.path.getsize(self.name)
            except Exception as e:
                return 0
        else:
            return sum(s.size() for s in self.subdirs)
    
    def print(self, depth: int, t: int, top: int = None):
        if depth < 0: return
        self.subdirs = sorted(self.subdirs, key=lambda s: s.size(), reverse=True)
        total = 0
        # print("\t" * t + self.name, f"{pretty(self.size())}")
        tab = '\t'
        if t != 0:
            n = self.name.split("/")
            name = ' ' * len('/'.join(n[:-2])) + '/'.join(n[-2:])
            # name = self.name
        else:
            name = self.name
        print(f"{pretty(self.size())}{tab * (1)}{name}")
        # print(f"{tab * (t)}{pretty(self.size())}{name}")

        for s in self.subdirs[:top]:
            if t == 0:
                print("-" * 10)
            s.print(depth-1, t+1, top)
            total += s.size()
        if t == 0:
            print("-" * 10)
        if t == 0:
            print(f"Total {pretty(total)} / {pretty(self.size())}")

    def repr(self, size_limit = 1024 * 1024 * 50):
        name = self.name
        if self.size() < size_limit:
            return
        print(f"{self.size()} | {self.is_file} | {name}")
        for s in self.subdirs:
            s.repr(size_limit)

    @staticmethod
    def from_cache(filename: str) -> "DirTree":
        with open(filename, 'r') as f:
            files = f.readlines()
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
                print("BAD", e, file)
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
        for f in self.subdirs:
            if f.name == directory_name or f.name.split('/')[-1] == directory_name:
                return f
        
        for f in self.subdirs:
            ans = f.find(directory_name)
            if ans is not None:
                return ans
        return None    


        
def get_size(start_path = '.'):
    # print(start_path)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
        for d in dirnames:
            total_size += get_size(d)

    return total_size

# tree = DirTree.from_cache('cache5.txt')
tree = DirTree.from_cache('cache6.txt')
tree.print(depth=1, top=20, t=0)
# tree = DirTree(sys.argv[1], False)
# tree.print(1000, 0, top=None)
# tree.repr()
