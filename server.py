# server_web.py
#  MUST be first
import eventlet
eventlet.monkey_patch()

#   normal imports
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

# 3Your app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
eventlet.monkey_patch()


WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20

snakes = {"P1": [(100, 100), (90, 100), (80, 100)],
          "P2": [(WIDTH-100, HEIGHT-100), (WIDTH-90, HEIGHT-100), (WIDTH-80, HEIGHT-100)]}
directions = {"P1": "RIGHT", "P2": "LEFT"}
food = (WIDTH//2, HEIGHT//2)
scores = {"P1": 0, "P2": 0}
game_over = False
players_connected = []

def move_snake(pid):
    global game_over, food
    if game_over:
        return

    head = snakes[pid][0]
    dir = directions[pid]
    if dir == "UP": new_head = (head[0], head[1]-GRID_SIZE)
    elif dir == "DOWN": new_head = (head[0], head[1]+GRID_SIZE)
    elif dir == "LEFT": new_head = (head[0]-GRID_SIZE, head[1])
    else: new_head = (head[0]+GRID_SIZE, head[1])

    snakes[pid].insert(0, new_head)
    if new_head == food:
        scores[pid] += 10
        food = (random.randrange(0, WIDTH, GRID_SIZE),
                random.randrange(0, HEIGHT, GRID_SIZE))
    else:
        snakes[pid].pop()

    # collisions
    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT or
        new_head in snakes[pid][1:] or
        new_head in snakes["P1"] and pid=="P2" or
        new_head in snakes["P2"] and pid=="P1"):
        game_over = True

@socketio.on("connect")
def on_connect():
    global players_connected
    pid = f"P{len(players_connected)+1}"
    players_connected.append(pid)
    emit("player_id", pid)

@socketio.on("move")
def on_move(data):
    pid = data["pid"]
    direction = data["direction"]
    directions[pid] = direction
    move_snake(pid)
    # broadcast the game state to all clients
    socketio.emit("state", {"snakes": snakes, "food": food, "scores": scores, "game_over": game_over})

@app.route("/")
def index():
    return render_template("index.html")  # browser client

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
