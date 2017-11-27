
def get_fab(n):
    if n == 0:
        return 0
    if n == 1:
        return 1

    fab = 0
    f1 = 0
    f2 = 1

    i = 0
    while i < n - 2:
        fab = f1 + f2
        f1 = f2
        f2 = fab
        i += 1
    return fab


def get_fab2(n):
    if n == 1:
        return 0
    if n == 2:
        return 1
    return get_fab2(n - 1) + get_fab2(n - 2)

if __name__ == "__main__":
    print get_fab(10)
    print get_fab2(10)