import os
import sys
folder = os.getcwd()

def pretty(num):
    kb = round(num / 1024)
    mb = round(kb / 1024)
    gb = round(10 * mb / 1024) / 10
    
    if mb > 1024: return f"{gb} GB"
    if kb > 1024: return f"{mb} MB"

    return f"{kb} KB"
    
class DirTree:
    def __init__(self, name: str, is_file: bool):
        self.name = name
        self._size = -1
        self.is_file = is_file
        self.subdirs = []
        if not self.is_file:
            self.subdirs = [DirTree(os.path.join(self.name, name), os.path.isfile(os.path.join(self.name, name))) for name in os.listdir(self.name) if not os.path.islink(os.path.join(self.name, name))]
    
    def size(self) -> int:
        if self._size == -1:
            self._size = self.calc_size()
        return self._size
    
    def calc_size(self):
        if self.is_file:
            return os.path.getsize(self.name)
        else:
            return sum(s.size() for s in self.subdirs)
    
    def print(self, depth: int, t: int, top: int = None):
        if depth < 0: return
        self.subdirs = sorted(self.subdirs, key=lambda s: s.size(), reverse=True)
        # print("\t" * t + self.name, f"{pretty(self.size())}")
        tab = '\t'
        if t != 0:
            n = self.name.split("/")
            name = ' ' * len('/'.join(n[:-1])) + n[-1]
        else:
            name = self.name
        print(f"{pretty(self.size())}{tab * (1)}{name}")
        for s in self.subdirs[:top]:
            s.print(depth-1, t+1, top)

            

        
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

tree = DirTree(sys.argv[1], False)
tree.print(2, 0, top=2)
