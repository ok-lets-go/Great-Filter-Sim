class Game: 
    def __init__(self):
        self.affected = False

my_list = [Game(), Game(), Game()]
for instance in my_list: 
    instance.affected = True
print(my_list[1].affected)