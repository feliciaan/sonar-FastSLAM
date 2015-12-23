__author__ = 'feliciaan'


def tmin(t1, t2):
    return min(t1[0],t2[0]), min(t1[1],t2[1])


def tmax(t1, t2):
    return max(t1[0],t2[0]), max(t1[1],t2[1])


def tsub(t1, t2):
    return t1[0] - t2[0], t1[1] - t2[1]


def tadd(t1, t2):
    return t1[0] + t2[0], t1[1] + t2[1]


def tlt(t1, t2):
    return t1[0] < t2[0] or t1[1] < t2[1]