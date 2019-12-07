import numpy as np
from catan import Catan, CatanException, get_random_dice_arrangement, Player, Game, simulate_1p_game, simulate_1p_game_with_data
import matplotlib.pyplot as plt
from itertools import repeat

import collections
import math


def action_original(self):
    # inputs:
    # resources - an array of resources
    # costs - an array of costs, 0 - settlement, 1 - card, 2 - city
    # basic strategy: Once we get 4 of one resource, we make a trade. 
    # Then we try to buy development cards
    if self.get_settlements() == []:
        (x,y) = self.preComp #use the optimal settlement location 
        if self.if_can_buy("settlement") and self.board.if_can_build("settlement",x,y,self.player_id):
            self.buy("settlement", x, y) # we determined previously
    elif self.if_can_buy("card"):
        self.buy("card")
    elif self.resources[np.argmax(self.resources)] >= 4:
        rmax, rmin = np.argmax(self.resources), np.argmin(self.resources)
        self.trade(rmax,rmin)
    return

# sample dump policy function: takes in the "Player" and ROBBER_MAX_RESOURCES
# and returns a resource array which indicates the number of each resource to dump.
# self.resources - dumpPolicy(self, max_resources) must sum up to less than or equal ROBBER_MAX_RESOURCES
def dumpPolicy_original(self, max_resources):
    new_resources = np.minimum(self.resources, max_resources // 3)
    return self.resources - new_resources

def planBoard_original(baseBoard):
    # prefer middle of the board over edges
    x = np.random.randint(1, baseBoard.width)
    y = np.random.randint(1, baseBoard.height)
    optSettlementLoc = (x,y)
    return optSettlementLoc


def trade_resources(player):
    neededCityResources = np.subtract(player.resources,costs[2,:])
    neededSettlementResources = np.subtract(player.resources,costs[0,:])
    neededCardResources = np.subtract(player.resources,costs[1,:])
    
    index_can_trade = 0
    index_want = 0
    if (sum(1 for i in neededCityResources if i < 0) < 2 and any(resource >= 4 for resource in neededCityResources)):        
        for index, val in enumerate(neededCityResources):
            if(val >= 4):
                index_can_trade = index
            elif (val == -1):
                index_want = index
        player.trade(index_can_trade, index_want)

    elif (sum(1 for i in neededSettlementResources if i < 0) < 2 and any(resource >= 4 for resource in neededSettlementResources)):        
        for index, val in enumerate(neededSettlementResources):
            if(val >= 4):
                index_can_trade = index
            elif (val == -1):
                index_want = index
        player.trade(index_can_trade, index_want)
        
    elif (sum(1 for i in neededCardResources if i < 0) < 2 and any(resource >= 4 for resource in neededCardResources)):        
        for index, val in enumerate(neededCardResources):
            if(val >= 4):
                index_can_trade = index
            elif (val == -1):
                index_want = index
        player.trade(index_can_trade, index_want)
    
    return 

def calc_expected_resources(player):
    resource_list = player.board.get_resources(player.player_id)
    resource = [0, 0, 0]
    diceProbs = [1/36,1/18,1/12,1/9,5/36,1/6,5/36,1/9,1/12,1/18,1/36]
    for i in range(len(resource_list)):
        resource_list[i] = resource_list[i] * diceProbs[i]
        resource += resource_list[i]
    return resource

def calc_expected_ratio(player):
    resource = calc_expected_resources(player)
    expected_sum = np.sum(resources)
    player.board.resource_ratios = resources / expected_sum
    return

def dumpPolicyRatio(self, max_resources):
    """
    SETTLEMENT, CARD, CITY = 0, 1, 2
    newResources = self.resources
    if(self.if_can_buy("city")):
        newResources = np.subtract(self.resources,costs[CITY,:])
    elif(self.if_can_buy("settlement")):
        newResources = np.subtract(self.resources,costs[SETTLEMENT,:])
    elif(self.if_can_buy("card")):
        newResources = np.subtract(self.resources,costs[CARD,:])
    """
    
    newResources = self.resources

    
    num_dump = np.sum(newResources) - max_resources
    max_resource = max(resource_ratios)
    dumping = [0, 0, 0]
    for i in range(len(player.board.resource_ratios)):
        dumping[i] += math.floor(player.board.resource_ratios[i] * num_dump)
        if (player.board.resource_ratios[i] == max_resource):
            dumping[i] += 1
    remaining = newResources - dumping
    if (all(resource > 0 for resource in remaining)):
        return dumping
    #check
    need = 0
    expected_sum = 0
    new_ratio = player.board.resource_ratios
    for i in range(len(remaining)):
        if(remaining[i] < 0):
            need -= remaining[i]
            new_ratio[i] = 0
            dumping[i] += remaining[i]
        else:
            expected_sum += player.board.resource_ratios[i]
    #next iteration
    new_ratio = new_ratio / expected_sum   
    for i in range(len(new_ratio)):
        dumping[i] += math.floor(new_ratio[i] * need)
        if (player.board.resource_ratios[i] == max(player.board.resource_ratios)):
            dumping[i] += 1
    remaining = newResources - dumping
    if (all(resource > 0 for resource in remaining)):
        return dumping
    #check
    need = 0
    expected_sum = 0
    
    for i in range(len(remaining)):
        if(remaining[i] < 0):
            need -= remaining[i]
            new_ratio[i] = 0
            dumping[i] += remaining[i]
        else:
            expected_sum += player.board.resource_ratios[i]
    #next iteration
    new_ratio = new_ratio / expected_sum   
    for i in range(len(new_ratio)):
        dumping[i] += math.floor(new_ratio[i] * need)

    remaining = newResources - dumping
    return dumping

def revTup(t):
    return (t[1], t[0])
    
def check_adjacent(board, x, y):
    for x1 in range(x-1,x+2):
        for y1 in range(y-1,y+2):
            if x1+y1 < x+y-1 or x1+y1 > x+y+1 or y1-x1 < y-x-1 or y1-x1 > y-x+1: ## only interested in up, down, left, and right
                pass
            elif x1 < 0 or x1 > board.width or y1 < 0 or y1 > board.height: ## only interested in valid tiles
                pass
            elif board.get_vertex_number(x1, y1) in board.settlements or board.get_vertex_number(x1, y1) in board.cities:
                return False
    return True

def calc_next_settlement_from_player(player):
    curr_settlement = None
    maxIndex = None
    for vertex in player.get_settlements():
        x,y = player.board.get_vertex_location(vertex)
        maxValue = 0
        for dx in [-2, -1, 0, 1, 2]:
            dy1 = 2-abs(dx)
            dy2 = abs(dx) - 2
            x1 = x + dx
            y1 = y + dy1
            y2 = y + dy2
            if check_adjacent(player.board, x1, y1):
                index1 = player.board.TupletoIndex[(x1, y1)]
                if index1:
                    if player.board.vertexValue[index1] > maxValue:
                        maxValue = player.board.vertexValue[index1]
                        maxIndex = index1
                        curr_settlement = (x, y)
            if check_adjacent(player.board, x1, y2):
                index2 = player.board.TupletoIndex[(x1, y2)]
                if index2:
                    if player.board.vertexValue[index2] > maxValue:
                        maxValue = player.board.vertexValue[index2]
                        maxIndex = index2
                        curr_settlement = (x, y) 
    if maxIndex:
        return player.board.indextoTuple[maxIndex], curr_settlement
    else:
        return None


def get_optimal_settlement_from_player(player):
    e = 0
    maxIndex = 0
    maxVertex = 0
    for vertex in player.get_settlements():
            ev = 0
            x, y = player.board.get_vertex_location(vertex)
            #print(x,y)
            index = player.board.TupletoIndex[(x,y)]
            ev = player.board.vertexValue[index]
            
            if ev > maxVertex:
                maxVertex = ev
                maxIndex = index

    optSettlementLoc = player.board.indextoTuple[maxIndex]
    #print(optSettlementLoc)
    return optSettlementLoc

# sample action function: takes in the "Player"
def action(self):
    # inputs:
    # resources - an array of resources
    # costs - an array of costs, 0 - settlement, 1 - card, 2 - city
    # basic strategy: Once we get 4 of one resource, we make a trade. 
    # Then we try to buy development cards
    if self.get_settlements() == []:
        (x,y) = self.preComp #use the optimal settlement location 
        if self.if_can_buy("settlement") and self.board.if_can_build("settlement",x,y,self.player_id):
            self.buy("settlement", x, y) # we determined previously
    if len(self.get_settlements()) > 0 and self.if_can_buy("city"):
        x,y = get_optimal_settlement_from_player(self)
        while self.board.if_can_build("city", x, y, self.player_id):
            self.buy("city", x,y)
        
    results = calc_next_settlement_from_player(self)
    
    if (results):  
        (xNS, yNS), (xCurr, yCurr) = results

        if self.if_can_buy("settlement") and self.board.if_can_build("settlement",xNS,yNS,self.player_id):
            self.buy("settlement", xNS,yNS)

        if self.board.curr == (xCurr, yCurr) and self.board.next == (xNS, yNS):

            if len(self.board.paths) == 1:
                path_copy = []

                for road in self.board.paths[0]:
                    if self.if_can_buy("road"):
                        self.buy("road", road[0], road[1])
                    else:
                        path_copy.append(road)

                self.board.paths[0] = path_copy

            if len(self.board.paths) == 2:
                path = None
                if len(self.board.paths[0]) > len(self.board.paths[1]):
                    temp = self.board.paths[0]
                    self.board.paths[0] = self.board.paths[1]
                    self.board.paths[1] = temp

                path_copy = []

                for road in self.board.paths[0]:
                    if self.if_can_buy("road") and self.board.if_can_build_road(
                        self.board.get_vertex_number(road[0][0],road[0][1]),self.board.get_vertex_number(road[1][0],road[1][1]),self.player_id):
                        self.buy("road", road[0], road[1])
                    else:
                        path_copy.append(road)

                self.board.paths[0] = path_copy

        else:
            dx = xNS - xCurr
            dy = yNS - yCurr
            self.board.paths = []
            if abs(dx) < 2 and abs(dy) < 2:
                patha = []
                pathb = []

                path1 = [((xCurr, yCurr), (xCurr + dx, yCurr)), ((xCurr + dx, yCurr), (xCurr + dx, yCurr + dy))]
                path2 = [((xCurr, yCurr), (xCurr, yCurr + dy)), ((xCurr, yCurr + dy), (xCurr + dx, yCurr + dy))]

                for road in path1:
                    if not (road in self.get_roads() or revTup(road) in self.get_roads()):
                        patha.append(road)

                for road in path2:
                    if not (road in self.get_roads() or revTup(road) in self.get_roads()):
                        pathb.append(road)

                self.board.paths.append(patha)
                self.board.paths.append(pathb)

            if abs(dx) == 2 or abs(dy) == 2:
                path1 = [((xCurr, yCurr), (xCurr + dx/2, yCurr + dy/2)), ((xCurr + dx/2, yCurr + dy/2), (xCurr + dx, yCurr + dy))]

            self.board.curr = (xCurr, yCurr)
            self.board.next = (xNS, yNS)
    
    if(self.if_can_buy("card")):
        self.buy("card")
    
    #check ports
    if self.resources[np.argmax(self.resources)] >= 4:
        rmax, rmin = np.argmax(self.resources), np.argmin(self.resources)
        self.trade(rmax,rmin)
    
    return

# sample dump policy function: takes in the "Player" and ROBBER_MAX_RESOURCES
# and returns a resource array which indicates the number of each resource to dump.
# self.resources - dumpPolicy(self, max_resources) must sum up to less than or equal ROBBER_MAX_RESOURCES
def dumpPolicy(self, max_resources):
    new_resources = np.minimum(self.resources, max_resources // 3)
    return self.resources - new_resources

def planBoard(baseBoard):
    # prefer middle of the board over edges
    #initialization
#     cache = {}
    baseBoard.vertexSums = []
    baseBoard.indextoTuple = []
    baseBoard.TupletoIndex = collections.defaultdict(lambda : None)
    baseBoard.vertexValue = []
    baseBoard.resource_ratios = None
    
    i = 0
    diceProbs = [1/36,1/18,1/12,1/9,5/36,1/6,5/36,1/9,1/12,1/18,1/36]
    for x in range(1, baseBoard.width):
        for y in range(1, baseBoard.height):
            r = np.zeros((11, 3))
            for dx in [-1, 0]:
                for dy in [-1, 0]:
                    xx = x + dx
                    yy = y + dy
                    if baseBoard.is_tile(xx, yy):
                        die = baseBoard.dice[yy, xx]
                        if die != 7:
                            resource = baseBoard.resources[yy, xx]
                            r[die - 2, resource] += 1
            baseBoard.vertexSums.append(r)
            baseBoard.indextoTuple.append((x, y))
            baseBoard.TupletoIndex[(x,y)] = i
            i += 1
            
            
    maxVertex = float('-inf')
    maxIndex = None
    for index, vertexSum in enumerate(baseBoard.vertexSums):
        ev = 0
        for i in range(len(vertexSum)):
            diceRoll = i + 2
            ev += diceProbs[i] * np.sum(vertexSum[i])
        baseBoard.vertexValue.append(ev)
        if ev > maxVertex:
            maxVertex = ev
            maxIndex = index

    optSettlementLoc = baseBoard.indextoTuple[maxIndex]
    
    #initialization
    baseBoard.paths = []
    baseBoard.curr = None
    baseBoard.next = None
    
    return optSettlementLoc
    
