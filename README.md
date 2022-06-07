# SpaceXCode

Starlink Beam Technical Test Summary -- Marcus Del Prete

Compiling/executing instructions:
	I coded this in latest stable version of python3.10, but any python 3 interpreter should work, so i left the shebang as #!/usr/bin/env python3

	As python is interpreted, no special instructions are needed, just type regularly into shell 
	e.g. (./final_solution.py test_cases/00_example.txt |./evaluate.py test_cases/00_example.txt)

	If this does not work, please email me but it seems to work fine on my mac. There are no special modules that need to be installed.

Code Summary:
	My algo is essentially as follows. Accounting for both the 45 degree and 20 degree rule, create a dictionary in which each satellite is mapped to a list of all users that it can access. Similarly, create a dictionary mapping each user to all satellites that can access it.

	We essentially run two algos and take whichever is better.

	Each of the two algorithms contained the same two optimizations and the choosing between the two algos is a third (as they vary in performance for different testing situations.). The only difference is in the way they choose their coloring

	Each algorithm first chooses specific beams/user pairs for each satellite, disregarding whether another satellite would also choose the same people. (I will describe the way in which the people are chosen later)

	*The algorithms then sort the satellites in descending order by counting the number of other satellites that would be affected if the people in the given satellite were chosen (i.e. how many satellites wouldn't need to service those people). 

	Iterating through each satellite, both algos then sort the possible users in an ascending order by number of other satellites that can reach them.]

	Algo 1 fixes a color, iterates through possible users, assigning that color when possible, and then repeats for the other colors. I consider this akin to greedy DFS

	Algo 2 iterates through possible users, assigning them the least assigned possible color. I consider this akin to greedy BFS

	These two algorithms produce different results, so whichever has a greater number of users serviced is ultimately chosen.




Testing Summary:

	No constraints were violated by any of the test cases. Similarly, no test case required more than 1gb of memory or more than 15 minutes to run.
	Each test's number and % users covered are listed below

1: 100%
2: 100%
3: 80%
4: 0%
5: 100%
6: 76.8%
7: 98.6%
8: 79.08%
9: 92.65%
10: 83.59%
11: 29.255%





*editors note: I would've preferred if the algorithm to sort the satellites occurred in between every time a satellite is ultimately assigned its user as it is more %covered optimal, but this greatly increases time complexity and will not admit a 15 minute solution to Test 11.
