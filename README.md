# EE126-Catan
Fall 2019 Catan Project Code 

planBoard:
places with 6, 8 then 5, 9 that are not on water's edge, prioritize road building (wood, brick)

Action:
Settle: 2W, 1B, 1G
Card: 1W, 2B, 2G
City: 3B, 3G
Road: 1W, 1B 

Settlement & City highest priority, then Road, then Card
if can build city then build
if can build settlement, check possible settlement locations and build at highest expected value
if can build road, find optimal possible settlement and build road to it
	if no possible settlements to build to, then don't build road
	optimal settlement: 
if can buy card, then buy card
if more then seven cards, trade 4 cards for lowest probability card to get if that is different card

Dump Policy:
find whatever card you make most of and dump that
