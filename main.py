import numpy as np
from catan import Catan, CatanException, get_random_dice_arrangement, Player, Game, simulate_1p_game, simulate_1p_game_with_data
import matplotlib.pyplot as plt
from itertools import repeat

catan_bot = __import__("catanAction")
action = catan_bot.action
dumpPolicy = catan_bot.dumpPolicy
planBoard = catan_bot.planBoard

action_original = catan_bot.action_original
dumpPolicy_original = catan_bot.dumpPolicy_original
planBoard_original = catan_bot.planBoard_original



orig_width, orig_height = 4,4

for i in range(10):
    width = orig_width + i
    height = orig_height + i
    dice = get_random_dice_arrangement(width, height)
    resources = np.random.randint(0, 3, (height, width))
    board = Catan(dice, resources)
    player1 = Player("EE126", action_original, dumpPolicy_original, planBoard_original)
    player2 = Player("Project", action, dumpPolicy, planBoard)
    players = [player1, player2]
    game = Game(board, players)
    print("Board Size:", width, height, game.simulate_game(100))