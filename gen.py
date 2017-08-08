from sys import argv, stdout
from random import shuffle
from itertools import chain

if len(argv) >= 2 and argv[1] != '-':
    fname = argv[1]
else:
    fname = "codes.dat"

with open(fname, "r") as f:
    l = list(map(lambda x: x[-10:-1], f.readlines()))

shuffle(l)
# print(l)

if len(argv) >= 3:
    fname = open(argv[2], "w")
else:
    fname = stdout

for i in chain(chain(zip(l[::2], l[1::2]),
                     zip(l[1::2], l[2::2])),
               [(l[-1], l[0])]):
    fname.write("{},{}\n".format(i[0], i[1]))
