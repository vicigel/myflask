import os


def print_tree(dirname):
    current_files = os.listdir(dirname)
    if not current_files:
        return
    for item in current_files:
        print ' ' * 10 * ((dirname + os.path.sep + item).count(os.path.sep) - 3) + item
        if os.path.isdir(dirname + os.path.sep + item):
            print_tree(dirname + os.path.sep + item)
        else:
            continue

print_tree('/home/vicigel/works')