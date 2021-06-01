import math

import docplex.mp.model as cpx
import utils
import blockTiming as bt


class ET_solution:
    def __init__(self):
        self.head_last = -1
        self.tail_first = -1
        self.tail_start = -1
        self.et_penalty = -1
        self.num_idle = -1


class ETI_solution:
    def __init__(self):
        self.block_lasts = list()
        self.end_times = list()
        self.eti_penalty = -1


def init_ET_memo(jobs, para_due_dates, para_processing_times):
    n = len(jobs)
    memo_ET = list()
    for i in range(n):
        row = list()
        memo_ET.append(row)
        for j in range(n):
            row.append(ET_solution())
            if i == j:
                memo_ET[i][i].head_last = 0
                memo_ET[i][i].tail_first = 0
                memo_ET[i][i].tail_start = para_due_dates[jobs[i]] - para_processing_times[jobs[i]]
                memo_ET[i][i].et_penalty = 0
    return memo_ET


def init_ETI_memo(jobs, para_due_dates):
    n = len(jobs)
    memo_ETI = list()
    for i in range(n):
        row = list()
        memo_ETI.append(row)
        for j in range(n):
            row.append(ETI_solution())
            if i == j:
                memo_ETI[i][i].block_lasts = [0]
                memo_ETI[i][i].end_times = [para_due_dates[jobs[i]]]
                memo_ETI[i][i].eti_penalty = 0
    return memo_ETI


def init_ETI_memo_bounded(jobs, para_due_dates):
    n = len(jobs)
    memo_ETI = list()
    for i in range(n):
        row = list()
        memo_ETI.append(row)
        for j in range(n):
            dict_ETI_solution = {}
            row.append(dict_ETI_solution)
            if i == j:
                memo_ETI[i][i][0] = ETI_solution()
                memo_ETI[i][i][0].block_lasts = [0]
                memo_ETI[i][i][0].end_times = [para_due_dates[jobs[i]]]
                memo_ETI[i][i][0].eti_penalty = 0
    return memo_ETI


def opt_ET(memo_ET, jobs, first, last, problem):
    para_due_dates = problem.due_dates
    para_processing_times = problem.processing_times
    para_earliness_penalties = problem.earliness_penalties
    para_tardiness_penalties = problem.tardiness_penalties
    if memo_ET[first][last].head_last >= 0:
        return memo_ET[first][last].head_last, memo_ET[first][last].tail_first, memo_ET[first][last].tail_start, \
               memo_ET[first][last].et_penalty, memo_ET[first][last].num_idle
    # Create model
    opt_model = cpx.Model(name="Calculate E/T Model")
    opt_model.parameters.simplex.tolerances.feasibility = 0.0000001

    n = last - first + 1

    # Decision parameters
    end_times = opt_model.continuous_var_list(n, lb=0, name="end_time_of_job_%s")
    earlis = opt_model.continuous_var_list(n, lb=0, name="earliness_of_job_%s")
    tardis = opt_model.continuous_var_list(n, lb=0, name="tardiness_of_job_%s")

    # constraint
    opt_model.add_constraints_(
        end_times[i] + para_processing_times[jobs[first + i + 1]] <= end_times[i + 1]
        for i in range(n - 1)
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
    # print("************ E/T Problem Solving ************")
    # opt_model.print_information()
    opt_model.solve()

    # print("     ******** The jobs in this schedule are:********     ")
    # for i in jobs:
    # print("job ", i)
    # print("        ******************************        ")
    # opt_model.report()
    # print("        ******************************        ")
    # print(opt_model.print_solution(print_zeros=False))
    # print("        ******************************        ")
    # print(opt_model.get_statistics())
    # print("        ******************************        ")
    # print(opt_model.get_solve_details())
    # print("        ******************************        ")

    head_last = last
    tail_first = first
    tail_start = opt_model.solution.get_value("end_time_of_job_0") - para_processing_times[jobs[first]]
    is_head = 1
    num_idle = 0
    for i in range(n - 1):
        end1 = opt_model.solution.get_value("end_time_of_job_" + str(i))
        end2 = opt_model.solution.get_value("end_time_of_job_" + str(i + 1))
        if end1 + para_processing_times[jobs[first + i + 1]] != end2:
            if is_head == 1:
                head_last = i
                is_head = 0
            num_idle += 1

    for i in range(n - 1):
        end1 = opt_model.solution.get_value("end_time_of_job_" + str(n - 2 - i))
        end2 = opt_model.solution.get_value("end_time_of_job_" + str(n - 1 - i))
        if (end1 + para_processing_times[jobs[last - i]] != end2):
            tail_first = last - i
            tail_start = end2 - para_processing_times[jobs[last - i]]
            break

    et_penalty = opt_model.solution.get_objective_value()
    memo_ET[first][last].head_last = head_last
    memo_ET[first][last].tail_first = tail_first
    memo_ET[first][last].tail_start = tail_start
    memo_ET[first][last].et_penalty = et_penalty
    memo_ET[first][last].num_idle = num_idle

    return head_last, tail_first, tail_start, et_penalty, num_idle


def opt_ET_no_memo(jobs, first, last, problem):
    para_due_dates = problem.due_dates
    para_processing_times = problem.processing_times
    para_earliness_penalties = problem.earliness_penalties
    para_tardiness_penalties = problem.tardiness_penalties
    # Create model
    opt_model = cpx.Model(name="Calculate E/T Model")
    opt_model.parameters.simplex.tolerances.feasibility = 0.0000001

    n = last - first + 1

    # Decision parameters
    end_times = opt_model.continuous_var_list(n, lb=0, name="end_time_of_job_%s")
    earlis = opt_model.continuous_var_list(n, lb=0, name="earliness_of_job_%s")
    tardis = opt_model.continuous_var_list(n, lb=0, name="tardiness_of_job_%s")

    # constraint
    opt_model.add_constraints_(
        end_times[i] + para_processing_times[jobs[first + i + 1]] <= end_times[i + 1]
        for i in range(n - 1)
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
    opt_model.solve()
    et_penalty = opt_model.solution.get_objective_value()

    return et_penalty


def dp(memoBT, memo_ET, memo_ETI, head_last, tail_first, jobs, first, last, problem):
    b = problem.b
    para_processing_times = problem.processing_times
    block_lasts = list()
    end_times = list()
    if head_last == tail_first - 1:
        merged_block_start, _, merged_et_penalty = bt.time_block(memoBT, jobs, first, last, problem)
        block_start1, block_end1, et_penalty1 = bt.time_block(memoBT, jobs, first, head_last, problem)
        block_start2, _, et_penalty2 = bt.time_block(memoBT, jobs, tail_first, last, problem)
        if block_end1 >= block_start2:
            two_block_eti_penalty = utils.BIG_NUMBER
        else:
            two_block_eti_penalty = et_penalty1 + et_penalty2 + b

        # print("merged_et_penalty= ", merged_et_penalty)
        # print("two_block_eti_penalty= ", two_block_eti_penalty)
        if merged_et_penalty <= two_block_eti_penalty:
            eti_penalty = merged_et_penalty
            block_lasts.append(last)
            t = merged_block_start
            for j in range(first, last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty
        else:
            eti_penalty = two_block_eti_penalty
            block_lasts.append(head_last)
            block_lasts.append(last)
            t = block_start1
            for j in range(first, head_last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            t = block_start2
            for j in range(tail_first, last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty
    else:
        block_lasts1, end_times1, eti_penalty1 = dp(memoBT, memo_ET, memo_ETI, head_last, tail_first - 1, jobs, first,
                                                    last, problem)
        tail_start, _, block_et_penalty = bt.time_block(memoBT, jobs, tail_first, last, problem)
        block_lasts2, end_times2, eti_penalty2 = opt_ETI(memoBT, memo_ET, memo_ETI, tail_start, jobs, first,
                                                         tail_first - 1, problem)
        eti_penalty2 = eti_penalty2 + b + block_et_penalty
        block_lasts2.append(last)
        t = tail_start
        for j in range(tail_first, last + 1):
            t = t + para_processing_times[jobs[j]]
            end_times2.append(t)

        if eti_penalty1 >= eti_penalty2:
            return block_lasts2, end_times2, eti_penalty2
        else:
            return block_lasts1, end_times1, eti_penalty1


def opt_ETI(memoBT, memo_ET, memo_ETI, uper_bound, jobs, first, last, problem):
    if memo_ETI[first][last].eti_penalty >= 0:
        eti_penalty = memo_ETI[first][last].eti_penalty
        if memo_ETI[first][last].end_times[last] >= uper_bound:
            eti_penalty = utils.BIG_NUMBER
        return list(memo_ETI[first][last].block_lasts), list(memo_ETI[first][last].end_times), eti_penalty
    block_lasts = list()
    end_times = list()
    eti_penalty = 0
    head_last, tail_first, tail_start, et_penalty, _ = opt_ET(memo_ET, jobs, first, last, problem)
    if head_last == last:  # if the optimal schedule of ET problem has only one block
        block_start = tail_start
        eti_penalty = et_penalty
        block_lasts.append(last)
        t = block_start
        for j in range(first, last + 1):
            t = t + problem.processing_times[jobs[j]]
            end_times.append(t)

    else:
        block_lasts, end_times, eti_penalty = dp(memoBT, memo_ET, memo_ETI, head_last, tail_first, jobs, first, last,
                                                 problem)
    memo_ETI[first][last].block_lasts = list(block_lasts)
    memo_ETI[first][last].end_times = list(end_times)
    memo_ETI[first][last].eti_penalty = eti_penalty
    if end_times[last] >= uper_bound:
        eti_penalty = utils.BIG_NUMBER
    return block_lasts, end_times, eti_penalty


def opt_ETI_Bounded(memoBT, memo_ET, memo_ETI_bounded, uper_bound, idle_bound, jobs, first, last, problem):
    for i in range(idle_bound, -1, -1):
        if memo_ETI_bounded[first][last].get(i):
            eti_penalty = memo_ETI_bounded[first][last][i].eti_penalty
            if memo_ETI_bounded[first][last][i].end_times[last] >= uper_bound:
                eti_penalty = utils.BIG_NUMBER
            return list(memo_ETI_bounded[first][last][i].block_lasts), list(
                memo_ETI_bounded[first][last][i].end_times), eti_penalty
    block_lasts = list()
    end_times = list()
    eti_penalty = 0
    head_last, tail_first, tail_start, et_penalty_ET, num_idle_ET = opt_ET(memo_ET, jobs, first, last, problem)
    start_UB, end_UB, et_penalty_UB = bt.time_block(memoBT, jobs, first, last, problem)
    idle_bound = min(idle_bound, num_idle_ET, math.floor((et_penalty_UB - et_penalty_ET) / problem.b))

    if idle_bound == 0:  # if ther is no more idleness allowance
        eti_penalty = et_penalty_UB
        block_lasts.append(last)
        t = start_UB
        for j in range(first, last + 1):
            t = t + problem.processing_times[jobs[j]]
            end_times.append(t)


    # if head_last == last:
    #     # if the optimal schedule of ET problem has only one block
    #     block_start = tail_start
    #     eti_penalty = et_penalty_ET
    #     block_lasts.append(last)
    #     t = block_start
    #     for j in range(first, last + 1):
    #         t = t + problem.processing_times[jobs[j]]
    #         end_times.append(t)
    else:
        block_lasts, end_times, eti_penalty = dp_Bounded(memoBT, memo_ET, memo_ETI_bounded, head_last, tail_first, jobs,
                                                         first, last, idle_bound, problem)
    memo_ETI_bounded[first][last][idle_bound] = ETI_solution()
    memo_ETI_bounded[first][last][idle_bound].block_lasts = list(block_lasts)
    memo_ETI_bounded[first][last][idle_bound].end_times = list(end_times)
    memo_ETI_bounded[first][last][idle_bound].eti_penalty = eti_penalty
    if end_times[last] >= uper_bound:
        eti_penalty = utils.BIG_NUMBER
    return block_lasts, end_times, eti_penalty


def dp_Bounded(memoBT, memo_ET, memo_ETI_bounded, head_last, tail_first, jobs, first, last, idle_bound, problem):
    b = problem.b
    para_processing_times = problem.processing_times
    block_lasts = list()
    end_times = list()
    if head_last == tail_first - 1:
        merged_block_start, _, merged_et_penalty = bt.time_block(memoBT, jobs, first, last, problem)
        block_start1, block_end1, et_penalty1 = bt.time_block(memoBT, jobs, first, head_last, problem)
        block_start2, _, et_penalty2 = bt.time_block(memoBT, jobs, tail_first, last, problem)
        if block_end1 >= block_start2:
            two_block_eti_penalty = utils.BIG_NUMBER
        else:
            two_block_eti_penalty = et_penalty1 + et_penalty2 + b

        # print("merged_et_penalty= ", merged_et_penalty)
        # print("two_block_eti_penalty= ", two_block_eti_penalty)
        if merged_et_penalty <= two_block_eti_penalty:
            eti_penalty = merged_et_penalty
            block_lasts.append(last)
            t = merged_block_start
            for j in range(first, last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty
        else:
            eti_penalty = two_block_eti_penalty
            block_lasts.append(head_last)
            block_lasts.append(last)
            t = block_start1
            for j in range(first, head_last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            t = block_start2
            for j in range(tail_first, last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty
    else:
        block_lasts1, end_times1, eti_penalty1 = dp_Bounded(memoBT, memo_ET, memo_ETI_bounded, head_last,
                                                            tail_first - 1, jobs, first, last, idle_bound, problem)
        tail_start, _, block_et_penalty = bt.time_block(memoBT, jobs, tail_first, last, problem)
        block_lasts2, end_times2, eti_penalty2 = opt_ETI_Bounded(memoBT, memo_ET, memo_ETI_bounded, tail_start,
                                                                 idle_bound - 1, jobs, first, tail_first - 1, problem)
        eti_penalty2 = eti_penalty2 + b + block_et_penalty
        block_lasts2.append(last)
        t = tail_start
        for j in range(tail_first, last + 1):
            t = t + para_processing_times[jobs[j]]
            end_times2.append(t)

        if eti_penalty1 >= eti_penalty2:
            return block_lasts2, end_times2, eti_penalty2
        else:
            return block_lasts1, end_times1, eti_penalty1
