from math import sqrt


def shuixianhua():
    for i in range(100, 1000):
        j = i%10
        m = i/10%10
        x = i/100%10
        if i == j**3 + m**3 + x**3:
            print i


if __name__ == "__main__":
    shuixianhua()