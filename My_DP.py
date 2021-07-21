import utils
import blockTiming as bt
import ET_opt as et


class ETI_solution:
    def __init__(self):
        self.block_lasts = list()
        self.end_times = list()
        self.eti_penalty = -1


def init_ETI_memo(jobs, para_due_dates):
    n = len(jobs)
    memo_ETI = list()
    for i in range(n):
        memo_ETI.append(ETI_solution())
    memo_ETI[0].end_times.append(para_due_dates[0])
    memo_ETI[0].eti_penalty = 0
    memo_ETI[0].block_lasts = 0
    return memo_ETI


def opt_ETI(memoBT, memo_ET, memo_ETI, et_global_solution, upper_bound, jobs, last, problem):
    total_cplex_time = 0
    if memo_ETI[last].eti_penalty >= 0:
        eti_penalty = memo_ETI[last].eti_penalty
        if memo_ETI[last].end_times[last] >= upper_bound:
            eti_penalty = utils.BIG_NUMBER
        return list(memo_ETI[last].block_lasts), list(
            memo_ETI[last].end_times), eti_penalty, total_cplex_time
    block_lasts = list()
    end_times = list()
    et_slt = et.opt_ET(memo_ET, et_global_solution, jobs, problem,
                                                                        last)
    if et_slt.head_last == last:  # if the optimal schedule of ET problem has only one block
        block_start = et_slt.tail_start
        eti_penalty = et_slt.et_penalty
        block_lasts.append(last)
        t = block_start
        for j in range(last + 1):
            t = t + problem.processing_times[jobs[j]]
            end_times.append(t)

    else:
        block_lasts, end_times, eti_penalty, cplex_time = dp(memoBT, memo_ET, memo_ETI, et_global_solution,
                                                             et_slt.head_last, et_slt.tail_first, jobs, last, problem)
        total_cplex_time += cplex_time
    memo_ETI[last].block_lasts = list(block_lasts)
    memo_ETI[last].end_times = list(end_times)
    memo_ETI[last].eti_penalty = eti_penalty
    if end_times[last] >= upper_bound:
        eti_penalty = utils.BIG_NUMBER
    return block_lasts, end_times, eti_penalty, total_cplex_time


def dp(memoBT, memo_ET, memo_ETI, et_global_solution, head_last, tail_first, jobs, last, problem):
    total_cplex_time = 0
    b = problem.b
    para_processing_times = problem.processing_times
    block_lasts = list()
    end_times = list()
    if head_last == tail_first - 1:
        merged_block_start, _, merged_et_penalty, cplex_time = bt.time_block(memoBT, jobs, 0, last, problem)
        total_cplex_time += cplex_time
        block_start1, block_end1, et_penalty1, cplex_time = bt.time_block(memoBT, jobs, 0, head_last, problem)
        total_cplex_time += cplex_time
        block_start2, _, et_penalty2, cplex_time = bt.time_block(memoBT, jobs, tail_first, last, problem)
        total_cplex_time += cplex_time
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
            for j in range(last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty, total_cplex_time
        else:
            eti_penalty = two_block_eti_penalty
            block_lasts.append(head_last)
            block_lasts.append(last)
            t = block_start1
            for j in range(head_last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            t = block_start2
            for j in range(tail_first, last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty, total_cplex_time
    else:
        block_lasts1, end_times1, eti_penalty1, cplex_time = dp(memoBT, memo_ET, memo_ETI, et_global_solution,
                                                                head_last, tail_first - 1, jobs, last, problem)
        total_cplex_time += cplex_time
        tail_start, _, block_et_penalty, cplex_time = bt.time_block(memoBT, jobs, tail_first, last, problem)
        total_cplex_time += cplex_time
        block_lasts2, end_times2, eti_penalty2, cplex_time = opt_ETI(memoBT, memo_ET, memo_ETI, et_global_solution,
                                                                     tail_start, jobs, tail_first - 1, problem)
        total_cplex_time += cplex_time
        eti_penalty2 = eti_penalty2 + b + block_et_penalty
        block_lasts2.append(last)
        t = tail_start
        for j in range(tail_first, last + 1):
            t = t + para_processing_times[jobs[j]]
            end_times2.append(t)

        if eti_penalty1 >= eti_penalty2:
            return block_lasts2, end_times2, eti_penalty2, total_cplex_time
        else:
            return block_lasts1, end_times1, eti_penalty1, total_cplex_time
