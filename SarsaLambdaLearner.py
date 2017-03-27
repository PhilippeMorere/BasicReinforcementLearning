__author__ = 'philippe'
import World
import threading
import time
import random

# Might not be working properly, seems a bit slow to learn

lambda_ = 0.9

discount = 0.5
actions = World.actions
states = []
Q = {}
e = {}
for i in range(World.x):
    for j in range(World.y):
        states.append((i, j))

for state in states:
    temp = {}
    temp2 = {}
    for action in actions:
        temp[action] = 0.1
        temp2[action] = 0.0
        World.set_cell_action_score(state, action, temp[action])
    Q[state] = temp
    e[state] = temp2

for (i, j, c, w) in World.specials:
    for action in actions:
        Q[(i, j)][action] = w
        World.set_cell_action_score((i, j), action, w)


def do_action(action):
    s = World.player
    r = -World.score
    if action == actions[0]:
        World.try_move(0, -1)
    elif action == actions[1]:
        World.try_move(0, 1)
    elif action == actions[2]:
        World.try_move(-1, 0)
    elif action == actions[3]:
        World.try_move(1, 0)
    else:
        return
    s2 = World.player
    r += World.score
    return s, action, r, s2

def policy(max_act):
    epsilon = 0.1
    if random.random() > epsilon:
        return max_act
    else:
        random_idx = random.randint(0, len(actions)-2)
        if actions[random_idx] == max_act:
            return actions[len(actions)-1]
        else:
            return actions[random_idx]

def max_Q(s):
    val = None
    act = None
    for a, q in Q[s].items():
        if val is None or (q > val):
            val = q
            act = a
    return act, val


def inc_Q(s, a, inc):
    Q[s][a] += inc
    World.set_cell_action_score(s, a, Q[s][a])


def run():
    global discount
    time.sleep(1)
    alpha = 1.0
    t = 1
    act = actions[random.randint(0,len(actions)-1)] 
    while True:
        # Pick the right action
        s = World.player
        (s, a, r, s2) = do_action(act)
        max_act, max_val = max_Q(s2)
        next_act = policy(max_act)

        # Update Q
        delta = r + discount * Q[s2][next_act] - Q[s][a]
        e[s][a] += 1.0
        for state in states:
            for action in actions:
                inc_Q(state, action, alpha * delta * e[state][action])
                e[state][action] *= discount * lambda_

        # Check if the game has restarted
        t += 1.0
        if World.has_restarted():
            World.restart_game()
            time.sleep(0.01)
            t = 1.0
            max_act, max_val = max_Q(World.player)
            act = policy(max_act)
            for state in states:
                for action in actions:
                    e[state][action] = 0.0


        # Update the learning rate
        alpha = pow(t, -0.1)
        act = next_act

        # MODIFY THIS SLEEP IF THE GAME IS GOING TOO FAST.
        time.sleep(0.02)


t = threading.Thread(target=run)
t.daemon = True
t.start()
World.start_game()
