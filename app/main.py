import bottle
import os
import random

from api import *


@bottle.route('/')
def static():
	return "the server is running"

@bottle.route('/static/<path:path>')
def static(path):
	return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
	data = bottle.request.json

	head_url = '%s://%s/static/head.png' % (
		bottle.request.urlparts.scheme,
		bottle.request.urlparts.netloc
	)

	# TODO: Do things with data

	print ("Starting game %s" % data["game"]["id"])
	return StartResponse("#00ff00")

##MY CODE
@bottle.post('/ping')
def ping():
	return PingResponse()
##MY CODE

@bottle.post('/move')
def move():
	data = bottle.request.json
	body = data['you']['body']
	length_of_board = data['board']['height']
	food = data['board']['food']
	head = body[0]
	print(head)
	other_snakes_bodies = []
	body.remove(head)
	directions = ['up', 'down', 'left', 'right']
	
	#get other snakes bodies
	for i in data['board']['snakes']:
		if i['id'] != data['you']['id']:
			other_snakes_bodies.append(i['body'])
	
	for j in other_snakes_bodies:
		for i in j:
			check_dir(i, directions, head)

	
	#Do not run into wall or self
	for i in body:
		check_dir(i, directions, head)
		if 'right' in directions and(head['x'] + 1 == length_of_board):
			directions.remove('right')
		if 'left' in directions and (head['x'] - 1 == -1):
			directions.remove('left')
		if 'down' in directions and (head['y'] + 1 == length_of_board):
			directions.remove('down')
		if 'up' in directions and (head['y'] - 1 == -1): 
			directions.remove('up')
	print(directions)
	direction = directions[0]
	if(len(directions) > 1):
		#Assign values to spaces not already ruled out.
		direction = value_assign(head, directions, other_snakes_bodies, food, length_of_board)
		if direction == 'random':
			direction = random.choice(directions)
	print(data)
	print ("Moving %s" % direction)
	return MoveResponse(direction)

#assign value to the spaces arround head in order to choose best move
def value_assign(head, directions, other_snakes_bodies, food, length_of_board):
	value_right = 0
	value_left = 0
	value_up = 0
	value_down = 0
	if 'right' in directions:
		right = []
		right.append({'x': head['x'] + 1, 'y': head['y']})
		adj_right = [{'x': head['x'] + 2, 'y': head['y']}, {'x': head['x'] + 1, 'y': head['y'] + 1}, {'x': head['x'] + 1, 'y': head['y'] - 1}]
		for i in adj_right:
			if i['x'] < length_of_board:
				for j in other_snakes_bodies:
					if not i in j:
						 right.append(i)
		while(len(right) != 0):
			 value_right += value_point(right.pop(), other_snakes_bodies, food)

	if 'left' in directions:
		left = []
		left.append({'x': head['x'] - 1, 'y': head['y']})
		adj_left = [{'x': head['x'] - 2, 'y': head['y']}, {'x': head['x'] + 1, 'y': head['y'] + 1}, {'x': head['x'] + 1, 'y': head['y'] - 1}]
		for i in adj_left:
			if i['x'] < -1:
				for j in other_snakes_bodies:
					if not i in j:
						 left.append(i)
		while(len(left) != 0):
			 value_left += value_point(left.pop(), other_snakes_bodies, food)

	if 'up' in directions:
		up = []
		up.append({'x': head['x'], 'y': head['y'] - 1})
		adj_up = [{'y': head['y'] - 2, 'x': head['x']}, {'y': head['y'] - 1, 'x': head['x'] + 1}, {'y': head['y'] - 1, 'x': head['x'] - 1}]
		for i in adj_up:
			if i['y'] > -1:
				for j in other_snakes_bodies:
					if not i in j:
						 up.append(i)
		while(len(up) != 0):
			 value_up += value_point(up.pop(), other_snakes_bodies, food)

	if 'down' in directions:
		down = []
		down.append({'y': head['y'] + 1, 'x': head['x']})
		adj_down = [{'y': head['y'] + 2, 'x': head['x']}, {'y': head['y'] + 1, 'x': head['x'] + 1}, {'y': head['y'] + 1, 'x': head['x'] - 1}]
		for i in adj_down:
			if i['y'] < length_of_board:
				for j in other_snakes_bodies:
					if not i in j:
						 down.append(i)
		while(len(down) != 0):
			 value_down += value_point(down.pop(), other_snakes_bodies, food)

	if value_right > value_left and value_right > value_down and value_right > value_up:
		return 'right'
	if value_left > value_right and value_left > value_down and value_left > value_up:
		return 'left'
	if value_up > value_left and value_up > value_down and value_up > value_right:
		return 'up'
	if value_down > value_left and value_down > value_right and value_down > value_up:
		return 'down'
	else:
		return 'random'
#adds value so single point	
def value_point(coord, other_snakes_bodies, food):
	if coord in food:
		return 3
	for i in other_snakes_bodies:
		if i[0]['x'] == coord['x'] +1 and i[0]['y'] == coord['y']:
			return 1
		if i[0]['x'] == coord['x'] - 1 and i[0]['y'] == coord['y']:
			return 1
		if i[0]['x'] == coord['x'] and i[0]['y'] == coord['y'] + 1:
			return 1
		if i[0]['x'] == coord['x'] +1 and i[0]['y'] == coord['y'] - 1:
			return 1
	return 2

#check if direction is valid, remove from directions if not
def check_dir(coord, directions, head):
	if 'right' in directions and(coord['x'] == head['x'] + 1 and head['y'] == coord['y']):
		directions.remove('right')
	if 'left' in directions and (coord['x'] == head['x'] - 1 and head['y'] == coord['y']):
		directions.remove('left')
	if 'down' in directions and (coord['y'] == head['y'] + 1 and head['x'] == coord['x']):
		directions.remove('down')
	if 'up' in directions and (coord['y'] == head['y'] - 1 and head['x'] == coord['x']): 
		directions.remove('up')

@bottle.post('/end')
def end():
	data = bottle.request.json

	# TODO: Do things with data

	print ("Game %s ended" % data["game"]["id"])


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
	bottle.run(
		application,
		host=os.getenv('IP', '0.0.0.0'),
		port=os.getenv('PORT', '8080'),
		debug=True)