row = 0
col = 0
index_shift = ((int(col % 2 == 1), 1),
            (1, 0),
            (1*int(col % 2 == 1), -1),
            (-1*int(col % 2 == 0), -1),
            (-1, 0),
            (-1*int(col % 2 == 0), 1)
)

print(index_shift)

my_list = [(1, 1), (1, 1)]