import random

my_list1 = [n for n in range(20)]

for n in range(1000): 
    a = random.randint(0, 19)
    my_list1.append(my_list1.pop(a))

print(my_list1)
print(sorted(my_list1))
