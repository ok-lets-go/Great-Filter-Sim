from archive.game import Player

round_count_list = []

for n in range(10000):
    round_num = 0
    player = Player()
    die_upgradeable = False
    while not die_upgradeable:
        round_num += 1
        player.roll_dice()
        die_upgradeable = player.resources['water']>=0 and player.resources['food']>=2 and player.resources['tree']>=0 and player.resources['brick']>=0
    round_count_list.append(round_num)

print(sum(round_count_list)/len(round_count_list))
percent = 0
for n in range(2, 150): 
    occurence_percentage = round_count_list.count(n)/100
    percent += occurence_percentage
    if percent > 0 and abs(percent-100) > 0.001: 
        print(f"{n} Rolls: {round_count_list.count(n)/100}% - {round(percent, 2)} percentile")
