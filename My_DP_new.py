import utils
import blockTiming as bt
import ET_opt as et


class ETI_solution:
    def __init__(self):
        self.block_lasts = list()
        self.end_times = list()
        self.eti_penalty = -1


def init_ETI_memo(jobs):
    n = len(jobs)
    memo_ETI = list()
    for i in range(n):
        memo_ETI.append(ETI_solution())
    return memo_ETI


def opt_ETI(memoBT, memo_ET, memo_ETI, et_global_solution, jobs, last, problem):
    if memo_ETI[last].eti_penalty >= 0:
        return list(memo_ETI[last].block_lasts), list(
            memo_ETI[last].end_times), memo_ETI[last].eti_penalty
    best_block_lasts = list()
    best_end_times = list()
    et_slt = et.opt_ET(memoBT, memo_ET, et_global_solution, jobs, problem, last)
    best_eti_penalty = utils.BIG_NUMBER

    block_start, end_UB, et_penalty_UB, _ = bt.time_block(memoBT, jobs, 0, last, problem)
    best_eti_penalty = et_penalty_UB
    best_block_lasts.append(last)
    t = block_start
    for j in range(last + 1):
        t = t + problem.processing_times[jobs[j]]
        best_end_times.append(t)
    for r in range(et_global_solution.block_lasts[0] + 1, et_slt.tail_first + 1):
        block_lasts, end_times, eti_penalty = dp(memoBT, memo_ET, memo_ETI, et_global_solution, r,
                                                 jobs, last, problem)
        if best_eti_penalty > eti_penalty:
            best_eti_penalty = eti_penalty
            best_block_lasts = block_lasts
            best_end_times = end_times

    memo_ETI[last].block_lasts = list(best_block_lasts)
    memo_ETI[last].end_times = list(best_end_times)
    memo_ETI[last].eti_penalty = best_eti_penalty
    return best_block_lasts, best_end_times, best_eti_penalty


def dp(memoBT, memo_ET, memo_ETI, et_global_solution, tail_first, jobs, last, problem):
    block_lasts = list()
    end_times = list()
    tail_start, _, block_et_penalty, _ = bt.time_block(memoBT, jobs, tail_first, last, problem)
    # new lemma
    if problem.due_dates[jobs[tail_first - 1]] >= tail_start:
        return [], [], utils.BIG_NUMBER
    et_slt = et.opt_ET(memoBT, memo_ET, et_global_solution, jobs, problem, tail_first - 1)
    # new lemma
    if et_slt.tail_end > tail_start:
        et_penalty_boundary, _ = et.opt_ET_with_boundary(memoBT, et_global_solution, jobs, tail_first - 1, problem,
                                                         tail_start)
        delta_et = et_penalty_boundary - et_slt.et_penalty
        if et_slt.num_idle * problem.b < delta_et:
            return [], [], utils.BIG_NUMBER
    block_lasts2, end_times2, eti_penalty2 = opt_ETI(memoBT, memo_ET, memo_ETI, et_global_solution,
                                                     jobs, tail_first - 1, problem)
    if end_times2[-1] >= tail_start:
        return [], [], utils.BIG_NUMBER
    else:
        eti_penalty2 = eti_penalty2 + problem.b + block_et_penalty
        block_lasts2.append(last)
        t = tail_start
        for j in range(tail_first, last + 1):
            t = t + problem.processing_times[jobs[j]]
            end_times2.append(t)
        return block_lasts2, end_times2, eti_penalty2

