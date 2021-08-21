import time
import docplex.mp.model as cpx
import utils


class BT_solution:
    def __init__(self):
        self.block_start = -1
        self.block_end = -1
        self.et_penalty = -1


def init_BT_memo(jobs, para_due_dates, para_processing_times):
    n = len(jobs)
    memo_BT = list()
    for i in range(n):
        row = list()
        memo_BT.append(row)
        for j in range(n):
            row.append(BT_solution())
            if i == j:
                memo_BT[i][j].block_start = para_due_dates[jobs[i]] - para_processing_times[jobs[i]]
                memo_BT[i][j].block_end = para_due_dates[jobs[i]]
                memo_BT[i][j].et_penalty = 0
    return memo_BT


# jobs as list
def time_block(memoBT, jobs, first, last, problem):
    para_due_dates = problem.due_dates
    para_processing_times = problem.processing_times
    para_earliness_penalties = problem.earliness_penalties
    para_tardiness_penalties = problem.tardiness_penalties
    if memoBT[first][last].block_start >= 0:
        return memoBT[first][last].block_start, memoBT[first][last].block_end, memoBT[first][last].et_penalty,0

    # Create model
    opt_model = cpx.Model(name="Block Timing Model")
    opt_model.parameters.simplex.tolerances.feasibility = 0.0000001

    n = last - first + 1
    # Decision parameters
    end_times = opt_model.continuous_var_list(n, lb=0, ub=utils.BIG_NUMBER, name="end_time_of_job_%s")
    earlis = opt_model.continuous_var_list(n, lb=0, ub=utils.BIG_NUMBER, name="earliness_of_job_%s")
    tardis = opt_model.continuous_var_list(n, lb=0, ub=utils.BIG_NUMBER, name="tardiness_of_job_%s")

    # constraint
    opt_model.add_constraints_(
        end_times[i] + para_processing_times[jobs[first + i + 1]] == end_times[i + 1] for i in range(n - 1)
    )

    # constraint
    opt_model.add_constraints_(
        end_times[i] + earlis[i] - tardis[i] == para_due_dates[jobs[first + i]] for i in range(n)
    )

    # Objective function
    objective_function = opt_model.sum(
        earlis[i] * para_earliness_penalties[jobs[first + i]] + tardis[i] * para_tardiness_penalties[jobs[first + i]]
        for i in range(n)
    )

    # minimize objective
    opt_model.minimize(objective_function)
    # print("**************** Block Timing ****************")
    # opt_model.print_information()
    start = time.process_time()
    opt_model.solve()
    end = time.process_time()
    cplex_time = end - start

    block_end = opt_model.solution.get_value("end_time_of_job_" + str(n - 1))
    block_start = opt_model.solution.get_value("end_time_of_job_0") - para_processing_times[jobs[first]]
    et_penalty = opt_model.solution.get_objective_value()

    memoBT[first][last].block_start = block_start
    memoBT[first][last].block_end = block_end
    memoBT[first][last].et_penalty = et_penalty

    # print("block start:", block_start)
    # print("block end:", block_end)
    # print("E/T penalty:", et_penalty)
    # print("**************** Block Timing Finished ****************")
    return block_start, block_end, et_penalty,cplex_time

def time_block_no_memo(jobs, first, last, problem):
    para_due_dates = problem.due_dates
    para_processing_times = problem.processing_times
    para_earliness_penalties = problem.earliness_penalties
    para_tardiness_penalties = problem.tardiness_penalties

    # Create model
    opt_model = cpx.Model(name="Block Timing Model")
    opt_model.parameters.simplex.tolerances.feasibility = 0.0000001

    n = last - first + 1
    # Decision parameters
    end_times = opt_model.continuous_var_list(n, lb=0, ub=utils.BIG_NUMBER, name="end_time_of_job_%s")
    earlis = opt_model.continuous_var_list(n, lb=0, ub=utils.BIG_NUMBER, name="earliness_of_job_%s")
    tardis = opt_model.continuous_var_list(n, lb=0, ub=utils.BIG_NUMBER, name="tardiness_of_job_%s")

    # constraint
    opt_model.add_constraints_(
        end_times[i] + para_processing_times[jobs[first + i + 1]] == end_times[i + 1] for i in range(n - 1)
    )

    # constraint
    opt_model.add_constraints_(
        end_times[i] + earlis[i] - tardis[i] == para_due_dates[jobs[first + i]] for i in range(n)
    )

    # Objective function
    objective_function = opt_model.sum(
        earlis[i] * para_earliness_penalties[jobs[first + i]] + tardis[i] * para_tardiness_penalties[jobs[first + i]]
        for i in range(n)
    )

    # minimize objective
    opt_model.minimize(objective_function)
    # print("**************** Block Timing ****************")
    # opt_model.print_information()
    start = time.process_time()
    opt_model.solve()
    end = time.process_time()
    cplex_time = end - start

    block_end = opt_model.solution.get_value("end_time_of_job_" + str(n - 1))
    block_start = opt_model.solution.get_value("end_time_of_job_0") - para_processing_times[jobs[first]]
    et_penalty = opt_model.solution.get_objective_value()

    # print("block start:", block_start)
    # print("block end:", block_end)
    # print("E/T penalty:", et_penalty)
    # print("**************** Block Timing Finished ****************")
    return block_start, block_end, et_penalty,cplex_time

