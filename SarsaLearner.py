__author__ = 'philippe'
# Sarsa(lambda) algorithm
# With eligibility trace replacement, and trace of same state previous actions set to 0.

import World
import threading
import time
import random

epsilon = 0.15
gamma = 0.3
lambda_ = 0.9
alpha = 0.15
actions = World.actions
states = []
Q = {}
eligibilityTrace = {}

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
    global epsilon
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


def inc_Q(s, a, alpha, inc):
    Q[s][a] += alpha * inc
    World.set_cell_action_score(s, a, Q[s][a])


def run():
    global gamma
    global lambda_
    global eligibilityTrace
    global alpha
    time.sleep(1)
    t = 1
    while True:
        # Pick the right action
        s = World.player
        max_act, max_val = max_Q(s)
        chosen_act = policy(max_act)
        (s, a, r, s2) = do_action(chosen_act)

        # Update Q
        max_act, max_val = max_Q(s2)
        policy_act = policy(max_act)
        delta = r + gamma * Q[s2][policy_act] - Q[s][a]
        eligibilityTrace[(s,a)] = 1.0
        
        for (ss,aa), val in eligibilityTrace.iteritems():
            inc_Q(ss, aa, alpha, delta * val)
            if ss == s and aa != a:
                eligibilityTrace[(ss,aa)] = 0.0
            else:
                eligibilityTrace[(ss,aa)] *= gamma * lambda_

        # Check if the game has restarted
        t += 1.0
        if World.has_restarted():
            eligibilityTrace = {}
            World.restart_game()
            time.sleep(0.01)
            t = 1.0

        # Update the learning rate
        # alpha = pow(t, -0.1)

        # MODIFY THIS SLEEP IF THE GAME IS GOING TOO FAST.
        time.sleep(0.01)


t = threading.Thread(target=run)
t.daemon = True
t.start()
World.start_game()
