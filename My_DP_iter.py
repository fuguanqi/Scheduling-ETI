import time

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
    glb_block_lasts = []
    glb_end_times = []
    glb_eti_penalty = utils.BIG_NUMBER
    # start=time.process_time()
    block_start, end_UB, et_penalty_UB, total_cplex_time = bt.time_block(memoBT, jobs, 0, et_global_solution.block_lasts[0], problem)
    # end = time.process_time()
    # cplex_time=end-start
    if et_global_solution.block_lasts[0] == last:
        return [et_global_solution.block_lasts[0]],total_cplex_time, et_penalty_UB
    memo_ETI[et_global_solution.block_lasts[0]].eti_penalty = et_penalty_UB
    memo_ETI[et_global_solution.block_lasts[0]].block_lasts = [et_global_solution.block_lasts[0]]
    memo_ETI[et_global_solution.block_lasts[0]].end_times = [end_UB]
    for i in range(et_global_solution.block_lasts[0] + 1, et_global_solution.block_lasts[-2] + 1):
        cal_memo(memoBT, memo_ET, memo_ETI, et_global_solution, jobs, i, problem)
    for i in range(et_global_solution.block_lasts[0], et_global_solution.block_lasts[-2] + 2):  # r_0
        if i == et_global_solution.block_lasts[0]:
            # start = time.process_time()
            block_start, end_UB, et_penalty_UB, cplex_time = bt.time_block(memoBT, jobs, 0, last, problem)
            total_cplex_time += cplex_time
            # end = time.process_time()
            # cplex_time =cplex_time+ end - start
            glb_block_lasts = [last]
            t = block_start
            for k in range(0, last):
                t = t + problem.processing_times[jobs[k]]
                glb_end_times.append(t)
            glb_eti_penalty = et_penalty_UB
        else:
            # start = time.process_time()
            block_start, end_UB, et_penalty_UB, cplex_time = bt.time_block(memoBT, jobs,i, last, problem)
            total_cplex_time += cplex_time
            # end = time.process_time()
            # cplex_time = cplex_time + end - start
            if memo_ETI[i- 1].end_times[-1] >= block_start:
                continue
            else:
                eti_penalty = memo_ETI[i - 1].eti_penalty + problem.b + et_penalty_UB
                if glb_eti_penalty > eti_penalty:
                    glb_eti_penalty = eti_penalty
                    glb_block_lasts = memo_ETI[i - 1].block_lasts.copy()
                    glb_block_lasts.append(last)
                    t = block_start
                    for k in range(i, last):
                        t = t + problem.processing_times[jobs[k]]
                        glb_end_times.append(t)
                else:
                    continue
    return glb_block_lasts, total_cplex_time, glb_eti_penalty


def cal_memo(memoBT, memo_ET, memo_ETI, et_global_solution, jobs, last, problem):
    best_block_lasts = []
    best_end_times = []
    best_eti_penalty = utils.BIG_NUMBER
    # start = time.process_time()
    et_slt = et.opt_ET(memoBT, memo_ET, et_global_solution, jobs, problem, last)
    # end = time.process_time()
    # cplex_time =  end - start
    for i in range(et_global_solution.block_lasts[0], et_slt.tail_first + 1):  # r_0
        if i == et_global_solution.block_lasts[0]:
            # start = time.process_time()
            block_start, end_UB, et_penalty_UB, cplex_time = bt.time_block(memoBT, jobs, 0, last, problem)
            # end = time.process_time()
            # total_cplex_time += cplex_time
            best_block_lasts = [last]
            t = block_start
            for k in range(0, last):
                t = t + problem.processing_times[jobs[k]]
                best_end_times.append(t)
            best_eti_penalty = et_penalty_UB
        else:
            # start = time.process_time()
            block_start, end_UB, et_penalty_UB, cplex_time = bt.time_block(memoBT, jobs, i, last, problem)
            # total_cplex_time += cplex_time
            # end = time.process_time()
            # cplex_time = cplex_time + end - start
            if memo_ETI[i- 1].end_times[-1] >= block_start:
                continue
            else:
                eti_penalty = memo_ETI[i - 1].eti_penalty + problem.b + et_penalty_UB
                if best_eti_penalty > eti_penalty:
                    best_eti_penalty = eti_penalty
                    best_block_lasts = memo_ETI[i - 1].block_lasts.copy()
                    best_block_lasts.append(last)
                    t = block_start
                    for k in range(i, last):
                        t = t + problem.processing_times[jobs[k]]
                        best_end_times.append(t)
                else:
                    continue
    memo_ETI[last].block_lasts = best_block_lasts
    memo_ETI[last].end_times = best_end_times
    memo_ETI[last].eti_penalty = best_eti_penalty
    return
