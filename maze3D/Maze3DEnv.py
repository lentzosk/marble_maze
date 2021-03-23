import time
from maze3D.gameObjects import *
from maze3D.assets import *
from maze3D.utils import checkTerminal, get_distance_from_goal, checkTerminal_new
from rl_models.utils import get_config

BOARD_LAYOUT = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


class ActionSpace:
    def __init__(self):
        # self.actions = list(range(0, 14 + 1))
        # self.shape = 1
        self.actions = list(range(0, 3))
        self.shape = 2
        self.actions_number = len(self.actions)
        self.high = self.actions[-1]
        self.low = self.actions[0]

    def sample(self):
        # return [random.sample([0, 1, 2], 1), random.sample([0, 1, 2], 1)]
        return np.random.randint(self.low, self.high + 1, 2)


class Maze3D:
    def __init__(self, config=None, config_file=None):
        # choose randomly one starting point for the ball
        # current_layout = random.choice(layouts)
        # current_layout = layout_up_right
        self.board = GameBoard(BOARD_LAYOUT)
        self.keys = {pg.K_UP: 1, pg.K_DOWN: 2, pg.K_LEFT: 4, pg.K_RIGHT: 8}
        self.keys_fotis = {pg.K_UP: 0, pg.K_DOWN: 1, pg.K_LEFT: 2, pg.K_RIGHT: 3}
        self.running = True
        self.done = False
        self.observation = self.get_state()  # must init board fisrt
        self.action_space = ActionSpace()
        self.observation_shape = (len(self.observation),)
        self.dt = None
        self.fps = 60
        self.config = get_config(config_file) if config_file is not None else config
        self.reward_type = self.config['SAC']['reward_function'] if 'SAC' in self.config.keys() else None

    def step_with_timestep(self, action, timedout, goal, timestep, action_duration=None):
        tmp_time = time.time()
        while (time.time() - tmp_time) < action_duration and not self.done:
            # if (action != [0,0]) :
            #    print("Env got action: {}".format(action))
            # self.board.handleKeys(action)  # action is int
            self.board.handleKeys(action)
            self.board.update()
            glClearDepth(1000.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.board.draw()
            pg.display.flip()

            self.dt = clock.tick(self.fps)
            fps = clock.get_fps()
            pg.display.set_caption("Running at " + str(int(fps)) + " fps")
            self.observation = self.get_state()
            if checkTerminal_new(self.board.ball, goal):
                self.done = True
                print("Goal reached.")
            if timedout:
                self.done = True
                print("Time out.")
        # end of while 200ms

        reward = self.reward_function_sparse2(timedout)
        #reward = self.reward_function_linear(timedout, timestep)
        return self.observation, reward, self.done


    def step(self, action, timedout, goal, action_duration=None):
        tmp_time = time.time()
        while (time.time() - tmp_time) < action_duration and not self.done:
            # if (action != [0,0]) :
            #    print("Env got action: {}".format(action))
            # self.board.handleKeys(action)  # action is int
            self.board.handleKeys(action)
            self.board.update()
            glClearDepth(1000.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.board.draw()
            pg.display.flip()

            self.dt = clock.tick(self.fps)
            fps = clock.get_fps()
            pg.display.set_caption("Running at " + str(int(fps)) + " fps")
            self.observation = self.get_state()
            if checkTerminal_new(self.board.ball, goal):
                self.done = True
                print("Goal reached.")
            if timedout:
                self.done = True
                print("Time out.")
        # end of while 200ms

        reward = self.reward_function_maze(timedout, goal)
        return self.observation, reward, self.done

    def get_state(self):
        # [ball pos x | ball pos y | ball vel x | ball vel y|  theta(x) | phi(y) |  theta_dot(x) | phi_dot(y) | ]
        return np.asarray(
            [self.board.ball.x, self.board.ball.y, self.board.ball.velocity[0], self.board.ball.velocity[1],
             self.board.rot_x, self.board.rot_y, self.board.velocity[0], self.board.velocity[1]])

    def reset(self):
        self.__init__(config=self.config)
        return self.observation

    def reward_function_maze(self, timedout, goal=None):
        if self.reward_type == "Sparse" or self.reward_type == "sparse":
            return self.reward_function_sparse(timedout)
        elif self.reward_type == "Dense" or self.reward_type == "dense":
            return self.reward_function_dense(timedout, goal)
        elif self.reward_type == "Sparse_2" or self.reward_type == "sparse_2":
            return self.reward_function_sparse2(timedout)

    def reward_function_sparse(self, timedout):
        # For every timestep -1
        # Timed out -50
        # Reach goal +100
        if self.done and not timedout:
            # solved
            return 100
        # if not done and timedout
        if timedout:
            return -50
        # return -1 for each time step
        return -1

    def reward_function_dense(self, timedout, goal=None):
        # For every timestep -target_distance
        # Timed out -50
        # Reach goal +100
        if self.done:
            # solved
            return 100
        # if not done and timedout
        if timedout:
            return -50
        # return -target_distance/10 for each time step
        target_distance = get_distance_from_goal(self.board.ball, goal)
        return -target_distance / 10

    def reward_function_sparse2(self, timedout):
        # For every timestep -1
        # Reach goal +10
        if self.done and not timedout:
            # solved
            return 10
        # return -1 for each time step
        return -1

    def reward_function_exp(self, timedout, timestep):
        # reduced exponentially every timestep
        if self.done and not timedout:
            # solved
            return 10
        # return -1 for each time step
        else:
            return (-1) * np.exp2(timestep / 100)

    def reward_function_linear(self, timedout, timestep):
        # reduced linearly every timestep
        # at the 200th timestep it returns -10
        if self.done and not timedout:
            # solved
            return 1000
        # return -1 for each time step
        else:
            return (-1) * timestep / 20
