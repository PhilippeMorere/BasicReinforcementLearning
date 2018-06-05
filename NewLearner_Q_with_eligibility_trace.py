__author__ = 'philippe'
import World
import threading
import random
import time


# This is still experimental...

discount = 0.7
actions = World.actions
states = []
Q = {}
for i in range(World.x):
    for j in range(World.y):
        states.append((i, j))

for state in states:
    temp = {}
    for action in actions:
        temp[action] = 0.1
        World.set_cell_action_score(state, action, temp[action])
    Q[state] = temp

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


def mean_Q(s):
    val = 0
    for a, q in Q[s].items():
        val += q
    return val/float(len(Q[s]))


def max_Q(s):
    val = None
    act = None
    for a, q in Q[s].items():
        if val is None or (q > val):
            val = q
            act = a
    return act, val


def inc_Q(s, a, alpha, inc):
    Q[s][a] *= 1 - alpha
    Q[s][a] += alpha * inc
    World.set_cell_action_score(s, a, Q[s][a])


def backPropagate(hist, alpha):
    for i in range(len(hist)-1, -1, -1):
        (s, a, r, s2) = hist[i]
        inc_Q(s, a, alpha, mean_Q(s2))


def run():
    global discount
    time.sleep(1)
    alpha = 1
    t = 1
    episode_hist = []
    while True:
        # Pick the right action
        s = World.player
        max_act, max_val = max_Q(s)
        chosen_act = policy(max_act)
        (s, a, r, s2) = do_action(chosen_act)
        episode_hist.append((s, a, r, s2))

        # Update Q
        max_act, max_val = max_Q(s2)
        inc_Q(s, a, alpha, r + discount * max_val)

        # Check if the game has restarted
        t += 1.0
        if World.has_restarted():
            backPropagate(episode_hist, alpha)
            World.restart_game()
            time.sleep(0.01)
            t = 1.0
            episode_hist = []

        # Update the learning rate
        alpha = pow(t, -0.1)

        # MODIFY THIS SLEEP IF THE GAME IS GOING TOO FAST.
        time.sleep(0.05)


t = threading.Thread(target=run)
t.daemon = True
t.start()
World.start_game()
