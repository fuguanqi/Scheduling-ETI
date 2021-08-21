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
    block_lasts = list()
    end_times = list()
    et_slt = et.opt_ET(memo_ET, et_global_solution, jobs, problem, last)
    if et_slt.tail_first <= et_global_solution.block_lasts[0]:
        block_start, end_UB, et_penalty_UB, _ = bt.time_block(memoBT, jobs, 0, last, problem)
        eti_penalty = et_penalty_UB
        block_lasts.append(last)
        t = block_start
        for j in range(last + 1):
            t = t + problem.processing_times[jobs[j]]
            end_times.append(t)

    else:
        block_lasts, end_times, eti_penalty = dp(memoBT, memo_ET, memo_ETI, et_global_solution,
                                                 min(et_slt.tail_first, et_global_solution.block_lasts[-2] + 1),
                                                 jobs, last, problem)
    memo_ETI[last].block_lasts = list(block_lasts)
    memo_ETI[last].end_times = list(end_times)
    memo_ETI[last].eti_penalty = eti_penalty
    return block_lasts, end_times, eti_penalty


def dp(memoBT, memo_ET, memo_ETI, et_global_solution, tail_first, jobs, last, problem):
    block_lasts = list()
    end_times = list()
    if et_global_solution.block_lasts[0] == tail_first - 1:
        merged_block_start, _, merged_et_penalty, _ = bt.time_block(memoBT, jobs, 0, last, problem)
        block_start1, block_end1, et_penalty1, _ = bt.time_block(memoBT, jobs, 0,
                                                                 et_global_solution.block_lasts[0], problem)
        block_start2, _, et_penalty2, _ = bt.time_block(memoBT, jobs, tail_first, last, problem)
        if block_end1 >= block_start2:
            two_block_eti_penalty = utils.BIG_NUMBER
        else:
            two_block_eti_penalty = et_penalty1 + et_penalty2 + problem.b
        if merged_et_penalty <= two_block_eti_penalty:
            eti_penalty = merged_et_penalty
            block_lasts.append(last)
            t = merged_block_start
            for j in range(last + 1):
                t = t + problem.processing_times[jobs[j]]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty
        else:
            eti_penalty = two_block_eti_penalty
            block_lasts.append(et_global_solution.block_lasts[0])
            block_lasts.append(last)
            t = block_start1
            for j in range(et_global_solution.block_lasts[0] + 1):
                t = t + problem.processing_times[jobs[j]]
                end_times.append(t)
            t = block_start2
            for j in range(tail_first, last + 1):
                t = t + problem.processing_times[jobs[j]]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty
    else:
        block_lasts1, end_times1, eti_penalty1 = dp(memoBT, memo_ET, memo_ETI, et_global_solution, tail_first - 1, jobs,
                                                    last, problem)
        tail_start, _, block_et_penalty, _ = bt.time_block(memoBT, jobs, tail_first, last, problem)
        # new lemma
        if problem.due_dates[jobs[tail_first - 1]] >= tail_start:
            return block_lasts1, end_times1, eti_penalty1
        et_slt = et.opt_ET(memo_ET, et_global_solution, jobs, problem, tail_first - 1)
        # new lemma
        if et_slt.tail_end > tail_start:
            et_penalty_boundary, _ = et.opt_ET_with_boundary(jobs, tail_first - 1, problem, tail_start)
            delta_et = et_penalty_boundary - et_slt.et_penalty
            if et_slt.num_idle * problem.b < delta_et:
                return block_lasts1, end_times1, eti_penalty1
        block_lasts2, end_times2, eti_penalty2 = opt_ETI(memoBT, memo_ET, memo_ETI, et_global_solution,
                                                         jobs, tail_first - 1, problem)
        if end_times2[-1] >= tail_start:
            return block_lasts1, end_times1, eti_penalty1
        else:
            eti_penalty2 = eti_penalty2 + problem.b + block_et_penalty
            block_lasts2.append(last)
            t = tail_start
            for j in range(tail_first, last + 1):
                t = t + problem.processing_times[jobs[j]]
                end_times2.append(t)
            if eti_penalty1 >= eti_penalty2:
                return block_lasts2, end_times2, eti_penalty2
            else:
                return block_lasts1, end_times1, eti_penalty1
