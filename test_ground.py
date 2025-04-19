class Item:
    def __init__(self):
        self.value = 1


item = Item()

item_list = []
item_list_2 = []
item_list.append(item)
item_list_2.append(item)

item_list[0].value = 2

print(item_list_2[0].value)