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
			if 'right' in directions and(i['x'] == head['x'] + 1 and head['y'] == i['y']):
				directions.remove('right')
			if 'left' in directions and (i['x'] == head['x'] - 1 and head['y'] == i['y']):
				directions.remove('left')
			if 'down' in directions and (i['y'] == head['y'] + 1 and head['x'] == i['x']):
				directions.remove('down')
			if 'up' in directions and (i['y'] == head['y'] - 1 and head['x'] == i['x']): 
				directions.remove('up')

	
	#Do not run into wall or self
	for i in body:
		if 'right' in directions and((i['x'] == head['x'] + 1 and head['y'] == i['y'])or head['x'] + 1 == length_of_board):
			directions.remove('right')
		if 'left' in directions and ((i['x'] == head['x'] - 1 and head['y'] == i['y'])or head['x'] - 1 == -1):
			directions.remove('left')
		if 'down' in directions and ((i['y'] == head['y'] + 1 and head['x'] == i['x']) or head['y'] + 1 == length_of_board):
			directions.remove('down')
		if 'up' in directions and ((i['y'] == head['y'] - 1 and head['x'] == i['x'])or head['y'] - 1 == -1): 
			directions.remove('up')
	print(directions)
	direction = random.choice(directions)
	print(data)
	print ("Moving %s" % direction)
	return MoveResponse(direction)


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