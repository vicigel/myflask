import os
import sys


def print_tree(dirname, index_count, f):
    current_files = os.listdir(dirname)
    if not current_files:
        return
    for item in current_files:
        f.write(' ' * 5 * ((dirname + os.path.sep + item).count(os.path.sep) - index_count) + item + os.linesep)
        if os.path.isdir(dirname + os.path.sep + item):
            print_tree(dirname + os.path.sep + item, index_count, f)
        else:
            continue

if __name__ == "__main__":
    if not os.path.isdir(sys.argv[1]):
        print 'Your input have something wrong,maybe the directory dose not exist'
        sys.exit(1)
    with open(os.path.basename(os.path.realpath(sys.argv[1])), 'w') as f:
        print_tree(os.path.realpath(sys.argv[1]), sys.argv[1].count(os.path.sep), f)

