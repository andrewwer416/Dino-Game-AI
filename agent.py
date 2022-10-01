import torch
import random
import numpy as np
from collections import deque
import game
from model import Linear_QNet, QTrainer
from helper import plot
import pygame
DISCOUNT_RATE = 0.99
MAX_MEMORY = 500000
BATCH_SIZE = 1000
LR = 0.001

class DQNAgent:
    #construct 2 networks
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(6, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
    #will be used to create multiple models

    def get_state(self, dino_game):
        straight_check = pygame.Rect(dino_game.player.X_POS + 100, dino_game.player.Y_POS,
                                     dino_game.player.dino_rect.width + dino_game.game_speed,
                                     dino_game.player.dino_rect.height)
        up_check = pygame.Rect(dino_game.player.X_POS + 100, dino_game.player.Y_POS - 140,
                               dino_game.player.dino_rect.width + dino_game.game_speed,
                               dino_game.player.dino_rect.height)
        down_check = pygame.Rect(dino_game.player.X_POS + 100, dino_game.player.Y_POS_DUCK,
                                 dino_game.player.dino_rect.width + dino_game.game_speed,
                                 dino_game.player.dino_rect.height // 5)
        issue = pygame.Rect(0, 0, 1, 1)
        obbies = []
        # types = []
        # idx = 0
        # type = 3
        # final_type = [0, 0, 0, 0]
        for obstacle in dino_game.obstacles:
            obbies.append(obstacle.rect)
            # if obstacle.rect.y == 325:
            #     types.append(2)
            # elif obstacle.rect.y == 300:
            #     types.append(1)
            # elif obstacle.rect.y == 250:
            #     types.append(0)
        for obstacle in obbies:
            if issue.x < obstacle.x:
                issue = obstacle
        #         type = types[idx]
        #     idx = idx+1
        # final_type[type] = 1
        # if type == 1:

        state = [
            # final_type[0], final_type[1], final_type[2], final_type[3],
            straight_check.colliderect(issue),
            up_check.colliderect(issue),
            down_check.colliderect(issue),
            dino_game.player.dino_run, dino_game.player.dino_jump, dino_game.player.dino_duck,
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 40 - self.n_games
        final_move = [0,0,0]
        if not state[0] and not state[1] and not state[2]:
            move = 0
            final_move[move] = 1
        else:
            if random.randint(0, 200) < self.epsilon:
                move = random.randint(1, 2)
                final_move[move] = 1
            else:
                state0 = torch.tensor(state, dtype=torch.float)
                prediction = self.model(state0)
                move = torch.argmax(prediction).item()
                final_move[move] = 1
        return final_move
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

def train():
    plot_avoided = []
    plot_scores = []
    plot_mean_avoided = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = DQNAgent()
    dino_game = game.Dino_Game()
    while True:
        state_old = agent.get_state(dino_game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = dino_game.play_step(final_move)
        state_new = agent.get_state(dino_game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)
        if done:
            # train long memory, plot result
            dino_game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()
