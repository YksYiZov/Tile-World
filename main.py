import math
import time

import pygame
import sys
import random
import matplotlib.pyplot as plt
import numpy as np

from tqdm import tqdm
from Grid import Grid
from Setting import *
from Tile_word import Tile_word
from Hole import Hole
from Agent import Agent
from Rock import Rock


def init_pygame(screen_size, font_type, bg_color):
    pygame.init()
    surf = pygame.display.set_mode(screen_size)
    surf.fill(bg_color)
    global_font = pygame.font.SysFont(font_type, 10)
    global_clock = pygame.time.Clock()
    return surf, global_font, global_clock


def answer_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


def create_hole(surf, life, world_check):
    grid = (random.randint(0, WORLD_SIZE[0] - 1), random.randint(0, WORLD_SIZE[1] - 1))
    while not world_check(grid):
        grid = (random.randint(0, WORLD_SIZE[0] - 1), random.randint(0, WORLD_SIZE[1] - 1))
    hole = Hole(surf, grid, life, SCORE)
    return hole, Grid(grid, None)


def update(surf, bg_color, world, hole_creator, actor, new_tile_time, life, count, gamma):
    surf.fill(bg_color)
    new_hole = False
    if count > new_tile_time:
        hole, grid = hole_creator(surf, life, world.check)
        world.add(hole, grid, HOLE)
        count = 0
        new_tile_time = random.randint(NEW_TILE_TIME[0] // gamma, NEW_TILE_TIME[1] // gamma)
        new_hole = True
    world.destroy(actor.act(world.holes, world.rocks, new_hole))
    world.update()
    return count, new_tile_time


def create_rocks(screen, seed, checker):
    random.seed(seed)
    rocks = []
    error = False
    while len(rocks) < 20:
        x, y = random.randint(0, WORLD_SIZE[0] - 1), random.randint(0, WORLD_SIZE[1] - 1)
        if error and (x, y) == (0, 1) or (x, y) == (1, 0):
            continue
        if checker((x, y)):
            if (x, y) == (0, 1) or (x, y) == (1, 0):
                error = True
            rocks.append(Rock(screen, (x, y)))

    return rocks


def init_world(world_size, margin, screen, seed, think_time=1, think_step=math.inf, sk=0):
    tile_world = Tile_word(world_size, margin, screen)
    agent = Agent(screen, world_size, think_time, think_step, sk)
    tile_world.add(agent, agent.grid, AGENT)
    rocks = create_rocks(screen, seed, tile_world.check)
    for rock in rocks:
        tile_world.add(rock, rock.grid, ROCK)
    return tile_world, agent


def start_one_game():
    screen, font, clock = init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
    tile_world, agent = init_world(WORLD_SIZE, MARGIN, screen, 10)
    gamma = random.randint(GAMMA[0], GAMMA[1])
    new_tile_time = random.randint(NEW_TILE_TIME[0] // gamma, NEW_TILE_TIME[1] // gamma)
    count = 0
    total_count = 0

    while True:
        count += 1
        total_count += 1
        answer_events()
        count, new_tile_time = update(screen, BG_COLOR, tile_world, create_hole, agent, new_tile_time, LIFE_CYCLE,
                                      count, gamma)
        pygame.display.update()
        if total_count > 3000:
            break
        clock.tick(FPS)


def experiment1():
    global p_count
    gammas = np.linspace(GAMMA[0], GAMMA[1], 15)
    log10gammas = np.log10(gammas)
    epsilons = np.array([])
    cycle = 1
    for gamma in gammas:
        init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
        screen, font, clock = init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
        tile_world, agent = init_world(WORLD_SIZE, MARGIN, screen, 10)
        new_tile_time = random.randint(NEW_TILE_TIME[0] // gamma, NEW_TILE_TIME[1] // gamma)
        count = 0

        for i in tqdm(range(1000), position=0, leave=False, desc=f"第{cycle}/{len(gammas)}轮次进度"):
            count += 1
            answer_events()
            count, new_tile_time = update(screen, BG_COLOR, tile_world, create_hole, agent, new_tile_time,
                                          LIFE_CYCLE // gamma,
                                          count, gamma)
            pygame.display.update()
            clock.tick(FPS)
        time.sleep(0.5)
        pygame.quit()
        epsilon = tile_world.get_score / tile_world.total_score
        epsilons = np.append(epsilons, [epsilon])
        cycle += 1
    plt.plot(gammas, epsilons)
    plt.xlabel("gamma")
    plt.ylabel("epsilon")
    plt.title("世界变化率与效率的关系")
    plt.savefig(f"./Result/p{p_count}")
    p_count += 1
    plt.show()

    plt.plot(log10gammas, epsilons)
    plt.xlabel("gamma")
    plt.ylabel("epsilon")
    plt.title("世界变化率与效率的关系")
    plt.savefig(f"./Result/p{p_count}")
    p_count += 1
    plt.show()


def experiment2():
    global p_count
    gammas = np.linspace(GAMMA[0], GAMMA[1], 15)
    log10gammas = np.log10(gammas)
    think_times = [0.5, 1, 2, 4]
    think_steps = [math.inf, 1]
    epsilons = [[[] for i in range(len(think_times))] for j in range(len(think_steps))]

    for think_step in think_steps:
        for think_time in think_times:
            cycle = 1
            for gamma in gammas:
                init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
                screen, font, clock = init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
                tile_world, agent = init_world(WORLD_SIZE, MARGIN, screen, 10, think_time, think_step)
                new_tile_time = random.randint(NEW_TILE_TIME[0] // gamma, NEW_TILE_TIME[1] // gamma)
                count = 0

                for i in tqdm(range(1000), position=0, leave=False,
                              desc=f"思考间隔{think_steps.index(think_step) + 1}/{len(think_steps)},思考时间{think_times.index(think_time) + 1}/{len(think_times)},第{cycle}/{len(gammas)}轮次进度"):
                    count += 1
                    answer_events()
                    count, new_tile_time = update(screen, BG_COLOR, tile_world, create_hole, agent, new_tile_time,
                                                  LIFE_CYCLE // gamma,
                                                  count, gamma)
                    pygame.display.update()
                    clock.tick(FPS)
                time.sleep(0.5)
                pygame.quit()
                epsilon = tile_world.get_score / tile_world.total_score
                epsilons[think_steps.index(think_step)][think_times.index(think_time)].append(epsilon)
                cycle += 1
    epsilons = np.array(epsilons)
    for i in range(len(think_steps)):
        for j in range(len(think_times)):
            plt.plot(log10gammas, np.reshape(epsilons[i, j, :], len(gammas)), label=f"p={think_times[j]}")
        plt.xlabel("gamma")
        plt.ylabel("epsilon")
        if i == 0:
            title = "盲目的"
        else:
            title = "谨慎的"
        plt.title(f"{title},计划时间与世界变化率和效率的关系")
        plt.legend()
        plt.savefig(f"./Result/p{p_count}")
        p_count += 1
        plt.show()


def experiment3():
    global p_count
    gammas = np.linspace(GAMMA[0], GAMMA[1], 15)
    log10gammas = np.log10(gammas)
    think_times = [1, 2, 4]
    think_steps = [math.inf, 4, 1]
    epsilons = [[[] for i in range(len(think_steps))] for j in range(len(think_times))]

    for think_time in think_times:
        for think_step in think_steps:
            cycle = 1
            for gamma in gammas:
                init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
                screen, font, clock = init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
                tile_world, agent = init_world(WORLD_SIZE, MARGIN, screen, 10, think_time, think_step)
                new_tile_time = random.randint(NEW_TILE_TIME[0] // gamma, NEW_TILE_TIME[1] // gamma)
                count = 0

                for i in tqdm(range(1000), position=0, leave=False,
                              desc=f"思考时间{think_times.index(think_time) + 1}/{len(think_times)},思考间隔{think_steps.index(think_step) + 1}/{len(think_steps)},第{cycle}/{len(gammas)}轮次进度"):
                    count += 1
                    answer_events()
                    count, new_tile_time = update(screen, BG_COLOR, tile_world, create_hole, agent, new_tile_time,
                                                  LIFE_CYCLE // gamma,
                                                  count, gamma)
                    pygame.display.update()
                    clock.tick(FPS)
                time.sleep(0.5)
                pygame.quit()
                epsilon = tile_world.get_score / tile_world.total_score
                epsilons[think_times.index(think_time)][think_steps.index(think_step)].append(epsilon)
                cycle += 1
    epsilons = np.array(epsilons)
    for i in range(len(think_times)):
        for j in range(len(think_steps)):
            if j == 0:
                title = "盲目的"
            elif j == 1:
                title = "正常的"
            else:
                title = "谨慎的"
            plt.plot(log10gammas, np.reshape(epsilons[i, j, :], len(gammas)), label=f"{title}")
        plt.xlabel("gamma")
        plt.ylabel("epsilon")
        plt.title(f"计划时间{think_times[i]},承诺属性与世界变化率和效率的关系")
        plt.legend()
        plt.savefig(f"./Result/p{p_count}")
        p_count += 1
        plt.show()


def experiment4():
    global p_count
    gammas = np.linspace(GAMMA[0], GAMMA[1], 15)
    log10gammas = np.log10(gammas)
    think_times = [1, 2]
    sks = [0, 1, 2, 3]
    think_steps = [math.inf, 4, 1]
    epsilons = [[[] for i in range(len(sks))] for j in range(len(think_times))]

    for think_time in think_times:
        for sk in sks:
            cycle = 1
            for gamma in gammas:
                init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
                screen, font, clock = init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
                tile_world, agent = init_world(WORLD_SIZE, MARGIN, screen, 10, think_time, sk=sk)
                new_tile_time = random.randint(NEW_TILE_TIME[0] // gamma, NEW_TILE_TIME[1] // gamma)
                count = 0

                for i in tqdm(range(1000), position=0, leave=False,
                              desc=f"思考时间{think_times.index(think_time) + 1}/{len(think_times)},策略类型{sks.index(sk) + 1}/{len(sks)},第{cycle}/{len(gammas)}轮次进度"):
                    count += 1
                    answer_events()
                    count, new_tile_time = update(screen, BG_COLOR, tile_world, create_hole, agent, new_tile_time,
                                                  LIFE_CYCLE // gamma,
                                                  count, gamma)
                    pygame.display.update()
                    clock.tick(FPS)
                time.sleep(0.5)
                pygame.quit()
                epsilon = tile_world.get_score / tile_world.total_score
                epsilons[think_times.index(think_time)][sks.index(sk)].append(epsilon)
                cycle += 1
    epsilons = np.array(epsilons)
    for i in range(len(think_times)):
        for j in range(len(sks)):
            if j == 0:
                title = "blind commitment"
            elif j == 1:
                title = "notices target disappearance"
            elif j == 2:
                title = "target dis. or nearer hole"
            else:
                title = "target dis. or any new hole"
            plt.plot(log10gammas, np.reshape(epsilons[i, j, :], len(gammas)), label=f"{title}")
        plt.xlabel("gamma")
        plt.ylabel("epsilon")
        plt.title(f"计划时间{think_times[i]},策略与世界变化率和效率的关系")
        plt.legend()
        plt.savefig(f"./Result/p{p_count}")
        p_count += 1
        plt.show()

    epsilons = [[] for i in range(len(think_steps))]
    for think_step in think_steps:
        cycle = 1
        for gamma in gammas:
            init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
            screen, font, clock = init_pygame(SCREEN_SIZE, FONT, BG_COLOR)
            tile_world, agent = init_world(WORLD_SIZE, MARGIN, screen, 10, think_step=think_step, sk=1)
            new_tile_time = random.randint(NEW_TILE_TIME[0] // gamma, NEW_TILE_TIME[1] // gamma)
            count = 0

            for i in tqdm(range(1000), position=0, leave=False,
                          desc=f"承诺属性{think_steps.index(think_step) + 1}/{len(think_steps)},第{cycle}/{len(gammas)}轮次进度"):
                count += 1
                answer_events()
                count, new_tile_time = update(screen, BG_COLOR, tile_world, create_hole, agent, new_tile_time,
                                              LIFE_CYCLE // gamma,
                                              count, gamma)
                pygame.display.update()
                clock.tick(FPS)
            time.sleep(0.5)
            pygame.quit()
            epsilon = tile_world.get_score / tile_world.total_score
            epsilons[think_steps.index(think_step)].append(epsilon)
            cycle += 1
    epsilons = np.array(epsilons)

    for i in range(len(think_steps)):
        if i == 0:
            title = "盲目的"
        elif i == 1:
            title = "一般的"
        else:
            title = "谨慎的"
        plt.plot(log10gammas, np.reshape(epsilons[i, :], len(gammas)), label=f"{title}")
    plt.xlabel("gamma")
    plt.ylabel("epsilon")
    plt.title(f"承诺属性(反应式，计划时间为1)与世界变化率和效率的关系")
    plt.legend()
    plt.savefig(f"./Result/p{p_count}")
    p_count += 1
    plt.show()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    plt.rc("font", family="Microsoft YaHei")
    p_count = 1
    start_one_game()
    print("====================实验一开始====================")
    experiment1()
    print("====================实验一结束====================")
    print("====================实验二开始====================")
    experiment2()
    print("====================实验二结束====================")
    print("====================实验三开始====================")
    experiment3()
    print("====================实验三结束====================")
    print("====================实验四开始====================")
    experiment4()
    print("====================实验四结束====================")
