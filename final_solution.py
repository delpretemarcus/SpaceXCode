#!/usr/bin/env python3


#Import necessary modules
import sys
import math

#####################################################################################################################
###################################             Import File            ##############################################
#####################################################################################################################

#Create 3 dictionaries with user/sat/interference name as key and coordinates as values
filename = str(sys.argv[1])
users = {}
sats = {}
interf = {}
myFile = open(filename, "r")
for x in myFile:
	separated = x.split()
	if len(separated) < 5:
		continue
	name = separated[0] + ' ' + separated[1]
	coord = separated[2:]
	if separated[0] == 'sat':
		sats[name] = [float(x) for x in coord]
	if separated[0] == 'user':
		users[name] = [float(x) for x in coord]
	if separated[0] == 'interferer':
		interf[name] = [float(x) for x in coord]
myFile.close()

#####################################################################################################################
###################################             Helper Defs            ##############################################
#####################################################################################################################


def dotProduct(a,b):
	return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

def vectorLength(v):
	return math.sqrt(dotProduct(v,v))

def findAngle(u,v):
	cosTheta = dotProduct(u,v) / (vectorLength(u) * vectorLength(v))
	#print("costheta; ", cosTheta)
	return math.acos(cosTheta)



#####################################################################################################################
###################################             Find allowed sat-ppl pairings            ############################
#####################################################################################################################


#Will have two dictionaries as follows
#Reach is defined by both the user's satellite being within their "view" and no obstructing non-Starlink satellites
#sat to client contains satellites as keys and possible users that can be "reached" by them as values 
sat_to_client = {}
#client_to_sat contains users as keys with every possibly satellite they can "reach" as values
client_to_sat = {}


for user, client_coord in users.items():
	for sat, sat_coord in sats.items():
		
		#to findAngle between satellite and user coords based around 0,0,0, we shift our satellite coord to being based around the user
		shifted_sat_coord = [ x - y for x,y in zip(sat_coord,client_coord)]
		theta = findAngle(shifted_sat_coord, client_coord)
		#If user cannot "view" satellite, move to next satellite
		if theta > math.pi / 4:
			continue

		#assume no interfering, iterate through interferers. If at any point we find an interferer is interfering, stop searching interferers and continue to next satellite	
		interfering = False
		for inter, inter_coord in interf.items():
			#to findAngle between interference and satellite coords based around 0,0,0, we shift our satellite and interference coord to being based around the user
			shifted_inter_coord = [ x - y for x,y in zip(inter_coord,client_coord)]
			zeta = findAngle(shifted_sat_coord, shifted_inter_coord)
			if math.degrees(zeta) < 20:
				interfering = True
				break
		if interfering == True:
			continue


		#Now it is guaranteed that this satellite user pair is unobstructed (sans satellite self interference), so we add to both sat_to_client and client_to_sat
		if sat in sat_to_client:
			sat_to_client[sat].append(user)
		else:
			sat_to_client[sat] = [user]

		if user in client_to_sat:
			client_to_sat[user].append(sat)
		else:
			client_to_sat[user] = [sat]





#####################################################################################################################
###################################             Begin DFS              ##############################################
#####################################################################################################################

#affected_sats_per_sat has keys of satellite with values corresponding to the number of satellites affected if this satellite was chosen first (each person chosen cannot be chosen by another satellite)
affected_sats_per_sat ={}
for sat in sat_to_client:

	#Per satellite, make list of what users have been assigned already
	used = {}
	count = 1
	#other_sat_count is running total of other satellites affected for an individual satellite
	other_sat_count = 0

	#Greedy Depth first search 1 color at a time the most users that can be assigned to this color
	for x in 'ABCD':
		used_color = []
		#So we want our user array ordered by least num of connections to other satellites...
		sat_to_client[sat].sort(key = lambda user: len(client_to_sat[user]))



		#Run through each user this satellite can reach
		for user in sat_to_client[sat]:
			#don't double color a user
			if user in used:
				continue
			#don't assign more than 32 beams
			if count >32:
				break

			#check if this user is too close to any other user that is already being reached by this color beam
			too_close =False
			for same_color in used_color:
				#shift both users coordinates to the satellites and dot product to find angle
				shifted_user = [x-y for x,y in zip(users[user],sats[sat])]
				shifted_same_color = [x-y for x,y in zip(users[same_color],sats[sat])]
				theta = findAngle(shifted_user,shifted_same_color)

				#If users are too close, move on to next user
				if math.degrees(theta) <10:
					too_close = True
					break
			if too_close==True:
				continue
			
			#Now this user can be assigned current color. Increment other_sat_count w/ corresponding number of sats user touches
			other_sat_count+= len(client_to_sat[user])
			used_color.append(user)
			used[user] = [x, count, sat]
			count +=1
	#increment our affected satellites by all selected users' links to other satellites
	affected_sats_per_sat[sat] = other_sat_count

#Sort our satellites by most affecting other satellites
sat_list  = [x for x in affected_sats_per_sat.keys()]
sat_list.sort(reverse=True, key= lambda sat: affected_sats_per_sat[sat])



##########
##########Now we can run the same algorithm 
##########(slightly modified for efficiency) 
##########will actually assign users but with correctly ordered sats
##########


#Used is our overarching dict of users choses. We have this outside of sat this time b/c we don't want users chosen by multiple sats
used = {}
for sat in sat_list:
	count = 1
	#Greedy Depth first search 1 color at a time the most users that can be assigned to this color
	for x in 'ABCD':
		used_color = []
		#So we want our array ordered by least num of connections to other satellites...
		sat_to_client[sat].sort(key = lambda user: len(client_to_sat[user]))



		#Run through each user this satellite can reach
		for user in sat_to_client[sat]:
			#don't double color a user
			if user in used:
				continue
			#don't assign more than 32 beams
			if count >32:
				break

			#check if this user is too close to any other user that is already being reached by this color beam
			too_close =False
			for same_color in used_color:
				#shift both users coordinates to the satellites and dot product to find angle
				shifted_user = [x-y for x,y in zip(users[user],sats[sat])]
				shifted_same_color = [x-y for x,y in zip(users[same_color],sats[sat])]
				theta = findAngle(shifted_user,shifted_same_color)

				#If users are too close, move on to next user
				if math.degrees(theta) <10:
					too_close = True
					break
			if too_close==True:
				continue
			
			#Now this user can be assigned current color
			used_color.append(user)
			used[user] = [x, count, sat]
			count +=1





#####################################################################################################################
###################################             Begin BFS              ##############################################
#####################################################################################################################

#affected_sats_per_sat has keys of satellite with values corresponding to the number of satellites affected if this satellite was chosen first (each person chosen cannot be chosen by another satellite)
affected_sats_per_sat = {}
for sat in sat_to_client:
	used2 ={}
	count = 1
	other_sat_count = 0
	#So we want our array ordered by least num of connections to other satellites...
	sat_to_client[sat].sort( key = lambda user: len(client_to_sat[user]))


	#Create dict containing each colors respective users (logged as we go) and a color order than we will sort to use the first allowable least used color so far
	color_users = {'A':[], 'B': [], 'C':[], 'D':[]}
	color_order = ['A', 'B', 'C', 'D']
		#Run through each user this satellite can reach
	for user in sat_to_client[sat]:
		#don't double color a user
		if user in used2:
			continue
		#don't assign more than 32 beams
		if count >32:
			break

		#Sort colors by least used
		color_order.sort(key=lambda color: len(color_users[color]))

		#iterating through possible colors, check if this user is too close to any other user that is already being reached by this color beam
		found_color=False
		for color in color_order:
			too_close =False

			for same_color_user in color_users[color]:
				#shift both users coordinates to the satellites and dot product to find angle
				shifted_user = [x-y for x,y in zip(users[user],sats[sat])]
				shifted_same_color = [x-y for x,y in zip(users[same_color_user],sats[sat])]
				theta = findAngle(shifted_user,shifted_same_color)

				#if users too close, move on to next color
				if math.degrees(theta) <10:
					too_close = True
					break
			if too_close==True:
				continue

			#Now this user can be assigned the current color and increment other_sat_count for how many satellites this selected user is not using
			other_sat_count+= len(client_to_sat[user])
			color_users[color].append(user)
			used2[user] = [x, count, sat]
			count +=1
			break
	#increment our affected satellites by all selected users' links to other satellites
	affected_sats_per_sat[sat] = other_sat_count

#Sort our satellites by most affecting other satellites
sat_list  = [x for x in affected_sats_per_sat.keys()]
sat_list.sort(reverse=True, key= lambda sat: affected_sats_per_sat[sat])



##########
##########Now we can run the same algorithm 
##########(slightly modified for efficiency) 
##########will actually assign users but with correctly ordered sats
##########





#Used is our overarching dict of users choses. We have this outside of sat this time b/c we don't want users chosen by multiple sats
used2 = {}
for sat in sat_list:
	count = 1

	#So we want our array ordered by least num of connections to other satellites...
	sat_to_client[sat].sort(key = lambda user: len(client_to_sat[user]))

	#Create dict containing each colors respective users (logged as we go) and a color order than we will sort to use the first allowable least used color so far
	color_users = {'A':[], 'B': [], 'C':[], 'D':[]}
	color_order = ['A', 'B', 'C', 'D']

	#Greed breadth first search utilizing least used colors for all users available
	for user in sat_to_client[sat]:
		#Dont double color a user
		if user in used2:
			continue
		#dont assign more than 32 beams
		if count >32:
			break

		#sort colors by least used
		color_order.sort(key=lambda color: len(color_users[color]))
		found_color=False
		#iterating through possible colors, check if this user is too close to any other user that is already being reached by this color beam 
		for color in color_order:
			too_close =False
			for same_color in color_users[color]:
				#shift both users coordinates to the satellites and dot product to find angle
				shifted_user = [x-y for x,y in zip(users[user],sats[sat])]
				shifted_same_color = [x-y for x,y in zip(users[same_color],sats[sat])]
				theta = findAngle(shifted_user,shifted_same_color)

				#if users too close, move to next color
				if math.degrees(theta) <10:
					too_close = True
					break
			if too_close==True:
				continue
			
			#Now this user can be assigned the current color and increment other_sat_count for how many satellites this selected user is not using
			color_users[color].append(user)
			used2[user] = [color, count, sat]
			count +=1
			break





#####################################################################################################################
###################################             Compare BFS VS DFS              #####################################
#####################################################################################################################



#take max users of BFS and DFS
final_dict = used if len(used)>len(used2) else used2




#Print out results
for user, triplet in final_dict.items():
	color= triplet[0]
	beam = triplet[1]
	sat = triplet[2]
	# if sat == 'sat 52' and (beam ==6 or beam ==8):
	# 	print (user, beam, color)
	print(sat + ' beam ' + str(beam)+ ' ' + user + " color " + color)










