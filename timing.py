import docplex.mp.model as cpx
import utils
import blockTiming as bt


class ET_solution:
    def __init__(self):
        self.head_last = -1
        self.tail_first = -1
        self.tail_start = -1
        self.et_penalty = -1


class ETI_solution:
    def __init__(self):
        self.block_lasts = list()
        self.end_times = list()
        self.eti_penalty = -1


def init_ET_memo(n, para_due_dates, para_processing_times):
    memo_ET = list()
    for i in range(n):
        row = list()
        memo_ET.append(row)
        for j in range(n):
            row.append(ET_solution())
            if i == j:
                memo_ET[i][i].head_last = 0
                memo_ET[i][i].tail_first = 0
                memo_ET[i][i].tail_start = para_due_dates[i] - para_processing_times[i]
                memo_ET[i][i].et_penalty = 0
    return memo_ET


def init_ETI_memo(n, para_due_dates):
    memo_ETI = list()
    for i in range(n):
        row = list()
        memo_ETI.append(row)
        for j in range(n):
            row.append(ETI_solution())
            if i == j:
                memo_ETI[i][i].block_lasts = [0]
                memo_ETI[i][i].end_times = [para_due_dates[i]]
                memo_ETI[i][i].eti_penalty = 0
    return memo_ETI


def opt_ET(memo_ET, jobs, first, last, para_due_dates, para_processing_times, para_earliness_penalties,
           para_tardiness_penalties):
    if memo_ET[first][last].head_last >= 0:
        return memo_ET[first][last].head_last, memo_ET[first][last].tail_first, memo_ET[first][last].tail_start, \
               memo_ET[first][last].et_penalty
    # Create model
    opt_model = cpx.Model(name="Calculate E/T Model")

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
    for i in range(n - 1):
        end1 = opt_model.solution.get_value("end_time_of_job_" + str(i))
        end2 = opt_model.solution.get_value("end_time_of_job_" + str(i + 1))
        if (end1 + para_processing_times[jobs[first + i + 1]] != end2):
            head_last = i
            break

    for i in range(n - 1):
        end1 = opt_model.solution.get_value("end_time_of_job_" + str(n - 2 - i))
        end2 = opt_model.solution.get_value("end_time_of_job_" + str(n - 1 - i))
        if (end1 + para_processing_times[jobs[last - i]] != end2):
            tail_first = last - i
            tail_start = end2 - para_processing_times[jobs[last - i]]
            break

    et_penalty = opt_model.solution.get_objective_value()
    # print("ET: head last:", head_last)
    # print("ET: tail first:", tail_first)
    # print("************** E/T Problem Solving Finished **************")

    return head_last, tail_first, tail_start, et_penalty


def dp(memoBT, memo_ET, memo_ETI, head_last, tail_first, jobs, first, last, b, para_due_dates, para_processing_times,
       para_earliness_penalties,
       para_tardiness_penalties):
    block_lasts = list()
    end_times = list()
    eti_penalty = 0
    if head_last == tail_first - 1:
        merged_block_start, _, merged_et_penalty = bt.time_block(memoBT, jobs, first, last, para_due_dates,
                                                                 para_processing_times,
                                                                 para_earliness_penalties, para_tardiness_penalties)
        block_start1, block_end1, et_penalty1 = bt.time_block(memoBT, jobs, first, head_last, para_due_dates,
                                                              para_processing_times,
                                                              para_earliness_penalties, para_tardiness_penalties)
        block_start2, _, et_penalty2 = bt.time_block(memoBT, jobs, tail_first, last, para_due_dates,
                                                     para_processing_times,
                                                     para_earliness_penalties, para_tardiness_penalties)
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
                                                    last, b, para_due_dates, para_processing_times,
                                                    para_earliness_penalties, para_tardiness_penalties)
        tail_start, _, block_et_penalty = bt.time_block(memoBT, jobs, tail_first, last, para_due_dates,
                                                        para_processing_times, para_earliness_penalties,
                                                        para_tardiness_penalties)
        block_lasts2, end_times2, eti_penalty2 = opt_ETI(memoBT, memo_ET, memo_ETI, tail_start, jobs, first,
                                                         tail_first - 1, b, para_due_dates, para_processing_times,
                                                         para_earliness_penalties, para_tardiness_penalties)
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


def opt_ETI(memoBT, memo_ET, memo_ETI, uper_bound, jobs, first, last, b, para_due_dates, para_processing_times,
            para_earliness_penalties,
            para_tardiness_penalties):
    if len(memo_ETI[first][last].block_lasts) > 0:
        return memo_ETI[first][last].block_lasts, memo_ETI[first][last].end_times, memo_ETI[first][last].eti_penalty
    block_lasts = list()
    end_times = list()
    eti_penalty = 0
    head_last, tail_first, tail_start, et_penalty = opt_ET(memo_ET, jobs, first, last, para_due_dates,
                                                           para_processing_times,
                                                           para_earliness_penalties,
                                                           para_tardiness_penalties)
    if head_last == last:  # if the optimal schedule of ET problem has only one block
        block_start = tail_start
        eti_penalty = et_penalty
        block_lasts.append(last)
        t = block_start
        for j in range(first, last + 1):
            t = t + para_processing_times[jobs[j]]
            end_times.append(t)

    else:
        block_lasts, end_times, eti_penalty = dp(memoBT, memo_ET, memo_ETI, head_last, tail_first, jobs, first, last, b,
                                                 para_due_dates,
                                                 para_processing_times, para_earliness_penalties,
                                                 para_tardiness_penalties)
    if end_times[last] >= uper_bound:
        eti_penalty = utils.BIG_NUMBER
    return block_lasts, end_times, eti_penalty
