row = 1
col = 1
index_shift = ((int(row % 2 == 1), 1),
            (1, 0),
            (1*int(row % 2 == 1), -1),
            (-1*int(row % 2 == 0), -1),
            (-1, 0),
            (-1*int(row % 2 == 0), 1)
)

print(index_shift)
