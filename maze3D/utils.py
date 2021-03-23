import math
import numpy as np

from maze3D.config import left_down, right_down, left_up, center
from rl_models.utils import plot_learning_curve, plot, plot_test_score

goals = {"left_down": left_down, "left_up": left_up, "right_down": right_down}

goal_offset = 24


def checkTerminal_new(ball, goal):
    goal = goals[goal]
    if goal == right_down:
        if ball.x > goal[0] and ball.y < goal[1]:
            return True
    elif goal == left_up:
        if ball.x < goal[0] and ball.y > goal[1]:
            return True
    elif goal == left_down:
        #if (ball.x + 16 <= goal[0] + goal_offset) and (ball.x - 16 >= goal[0] - goal_offset) \
        #        and (ball.y + 16 <= goal[1] + goal_offset) and (ball.y - 16 >= goal[1] - goal_offset):
        if ball.x < goal[0] and ball.y < goal[1]:
            return True
    elif goal == center:
        if ball.x < 0 and ball.y < 0:
            return True
    else:
        return False


def checkTerminal(ball, goal):
    # print("Ball x:{} y{}".format(ball.x, ball.y))
    goal = goals[goal]
    if goal == right_down:
        if ball.x > goal[0] and ball.y < goal[1]:
            return True
    elif goal == left_up:
        if ball.x < goal[0] and ball.y > goal[1]:
            return True
    elif goal == left_down:
        if ball.x < goal[0] and ball.y < goal[1]:
            return True
    elif goal == center:
        if ball.x < 0 and ball.y < 0:
            return True
    else:
        return False


def get_distance_from_goal(ball, goal):
    goal = goals[goal]
    return math.sqrt(math.pow(ball.x - goal[0], 2) + math.pow(ball.y - goal[1], 2))


def convert_actions(actions):
    # gets a list of 4 elements. it is called from getKeyboard()
    action = []
    if actions[0] == 1:
        action.append(1)
    elif actions[1] == 1:
        action.append(2)
    else:
        action.append(0)
    if actions[2] == 1:
        action.append(1)
    elif actions[3] == 1:
        action.append(2)
    else:
        action.append(0)
    return action


def save_logs_and_plot(experiment, chkpt_dir, plot_dir, max_episodes):

    #score_history a list with the reward for each episode
    x = [i + 1 for i in range(len(experiment.score_history))]
    np.savetxt(chkpt_dir + '/scores.csv', np.asarray(experiment.score_history), delimiter=',')

    #action_history as returned by get_action_pair: a dyad agent and human {-1,0,1}
    actions = np.asarray(experiment.action_history)

    # action_main = actions[0].flatten()
    # action_side = actions[1].flatten()
    x_actions = [i + 1 for i in range(len(actions))]
    # Save logs in files
    np.savetxt(chkpt_dir + '/actions.csv', actions, delimiter=',')
    # np.savetxt('tmp/sac_' + timestamp + '/action_side.csv', action_side, delimiter=',')
    np.savetxt(chkpt_dir + '/epidode_durations.csv', np.asarray(experiment.episode_duration_list), delimiter=',')

    np.savetxt(chkpt_dir + '/distance_travel.csv', np.asarray(experiment.distance_travel_list), delimiter=',')
    np.savetxt(chkpt_dir + '/distance_travel_test.csv', np.asarray(experiment.test_distance_travel_list), delimiter=',')
    np.savetxt(chkpt_dir + '/pure_rewards.csv', np.asarray(experiment.reward_list), delimiter=',')
    np.savetxt(chkpt_dir + '/pure_rewards_test.csv', np.asarray(experiment.test_reward_list), delimiter=',')

    #length_list is the last timestep of the episode
    np.savetxt(chkpt_dir + '/avg_length_list.csv', np.asarray(experiment.length_list), delimiter=',')
    np.savetxt(chkpt_dir + '/grad_updates_durations.csv', experiment.grad_updates_durations, delimiter=',')

    # test logs
    np.savetxt(chkpt_dir + '/test_episode_duration_list.csv', experiment.test_episode_duration_list, delimiter=',')
    np.savetxt(chkpt_dir + '/test_score_history.csv', experiment.test_score_history, delimiter=',')
    np.savetxt(chkpt_dir + '/test_length_list.csv', experiment.test_length_list, delimiter=',')

    plot_learning_curve(x, experiment.score_history, plot_dir + "/scores.png")
    # plot_actions(x_actions, action_main, plot_dir + "/action_main.png")
    # plot_actions(x_actions, action_side, plot_dir + "/action_side.png")
    plot(experiment.length_list, plot_dir + "/length.png", x=[i + 1 for i in range(max_episodes)])
    plot(experiment.episode_duration_list, plot_dir + "/epidode_durations.png",
         x=[i + 1 for i in range(max_episodes)])
    plot(experiment.grad_updates_durations, plot_dir + "/grad_updates_durations.png",
         x=[i + 1 for i in range(len(experiment.grad_updates_durations))])

    # plot test logs
    x = [i + 1 for i in range(len(experiment.test_length_list))]
    plot_test_score(experiment.test_score_history, plot_dir + "/test_scores.png")
    # plot_actions(x_actions, action_main, plot_dir + "/action_main.png")
    # plot_actions(x_actions, action_side, plot_dir + "/action_side.png")
    plot(experiment.test_length_list, plot_dir + "/test_length.png",
         x=x)
    plot(experiment.test_episode_duration_list, plot_dir + "/test_episode_duration.png",
         x=x)

    plot_learning_curve(x, experiment.reward_list, plot_dir + "/rewards_train.png")
    plot_learning_curve(x, experiment.test_reward_list, plot_dir + "/rewards_test.png")

    try:
        plot_test_score(experiment.score_history, plot_dir + "/test_scores_mean_std.png")
    except:
        print("An exception occurred while plotting")
