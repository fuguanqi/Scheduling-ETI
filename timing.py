import docplex.mp.model as cpx
import utils
import blockTiming as bt


def opt_ET(jobs, para_due_dates, para_processing_times, para_earliness_penalties, para_tardiness_penalties):
    # Create model
    opt_model = cpx.Model(name="Calculate E/T Model")

    n = len(jobs)

    # Decision parameters
    end_times = opt_model.continuous_var_list(n, lb=0, name="end_time_of_job_%s")
    earlis = opt_model.continuous_var_list(n, lb=0, name="earliness_of_job_%s")
    tardis = opt_model.continuous_var_list(n, lb=0, name="tardiness_of_job_%s")

    # constraint
    opt_model.add_constraints_(
        end_times[i] + para_processing_times[jobs[i + 1]] <= end_times[i + 1]
        for i in range(n - 1)
    )

    # constraint
    opt_model.add_constraints_(
        end_times[i] + earlis[i] - tardis[i] == para_due_dates[jobs[i]] for i in range(n)
    )

    # Objective function
    objective_function = opt_model.sum(
        earlis[i] * para_earliness_penalties[jobs[i]] + tardis[i] * para_tardiness_penalties[jobs[i]] for i in range(n)
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

    head_last = n - 1
    tail_first = 0
    tail_start = opt_model.solution.get_value("end_time_of_job_0") - para_processing_times[jobs[0]]
    for i in range(n - 1):
        end1 = opt_model.solution.get_value("end_time_of_job_" + str(i))
        end2 = opt_model.solution.get_value("end_time_of_job_" + str(i + 1))
        if (end1 + para_processing_times[jobs[i + 1]] != end2):
            head_last = i
            # print("!!!!!!!!1", end1 + para_processing_times[jobs[i + 1]])
            # print("!!!!!!!!2", end2)
            break

    for i in range(n - 1):
        end1 = opt_model.solution.get_value("end_time_of_job_" + str(n - 2 - i))
        end2 = opt_model.solution.get_value("end_time_of_job_" + str(n - 1 - i))
        if (end1 + para_processing_times[jobs[n - 1 - i]] != end2):
            # print("!!!!!!!!3", end1 + para_processing_times[jobs[n - 1 - i]])
            # print("!!!!!!!!4", end2)
            tail_first = n - 1 - i
            tail_start = end2 - para_processing_times[jobs[n - 1 - i]]
            break

    et_penalty = opt_model.solution.get_objective_value()
    # print("ET: head last:", head_last)
    # print("ET: tail first:", tail_first)
    # print("************** E/T Problem Solving Finished **************")

    return head_last, tail_first, tail_start, et_penalty


def dp(head_last, tail_first, jobs, b, para_due_dates, para_processing_times, para_earliness_penalties,
       para_tardiness_penalties):
    n = len(jobs)
    block_lasts = list()
    end_times = list()
    eti_penalty = 0
    if head_last == tail_first - 1:
        merged_block_start, _, merged_et_penalty = bt.time_block(jobs, para_due_dates, para_processing_times,
                                                                 para_earliness_penalties, para_tardiness_penalties)
        block_start1, block_end1, et_penalty1 = bt.time_block(jobs[:head_last + 1], para_due_dates,
                                                              para_processing_times,
                                                              para_earliness_penalties, para_tardiness_penalties)
        block_start2, _, et_penalty2 = bt.time_block(jobs[tail_first:], para_due_dates, para_processing_times,
                                                     para_earliness_penalties, para_tardiness_penalties)
        if block_end1 >= block_start2:
            two_block_eti_penalty = utils.BIG_NUMBER
        else:
            two_block_eti_penalty = et_penalty1 + et_penalty2 + b

        # print("merged_et_penalty= ", merged_et_penalty)
        # print("two_block_eti_penalty= ", two_block_eti_penalty)
        if merged_et_penalty <= two_block_eti_penalty:
            eti_penalty = merged_et_penalty
            block_lasts.append(n - 1)
            t = merged_block_start
            for j in jobs:
                t = t + para_processing_times[j]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty
        else:
            eti_penalty = two_block_eti_penalty
            block_lasts.append(head_last)
            block_lasts.append(n - 1)
            t = block_start1
            for j in range(0, head_last + 1):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            t = block_start2
            for j in range(tail_first, n):
                t = t + para_processing_times[jobs[j]]
                end_times.append(t)
            return block_lasts, end_times, eti_penalty
    else:
        block_lasts1, end_times1, eti_penalty1 = dp(head_last, tail_first - 1, jobs, b, para_due_dates,
                                                    para_processing_times, para_earliness_penalties,
                                                    para_tardiness_penalties)
        block_start, _, block_et_penalty = bt.time_block(jobs[tail_first:], para_due_dates,
                                                         para_processing_times, para_earliness_penalties,
                                                         para_tardiness_penalties)
        block_lasts2, end_times2, eti_penalty2 = opt_ETI(block_start, jobs[:tail_first], b, para_due_dates,
                                                         para_processing_times,
                                                         para_earliness_penalties, para_tardiness_penalties)
        eti_penalty2 = eti_penalty2 + b + block_et_penalty
        block_lasts2.append(n - 1)
        t = block_start
        for j in range(tail_first, n):
            t = t + para_processing_times[jobs[j]]
            end_times2.append(t)

        if eti_penalty1 >= eti_penalty2:
            return block_lasts2, end_times2, eti_penalty2
        else:
            return block_lasts1, end_times1, eti_penalty1


def opt_ETI(uper_bound, jobs, b, para_due_dates, para_processing_times, para_earliness_penalties,
            para_tardiness_penalties):
    n = len(jobs)
    block_lasts = list()
    end_times = list()
    eti_penalty = 0
    head_last, tail_first, tail_start, et_penalty = opt_ET(jobs, para_due_dates, para_processing_times,
                                                           para_earliness_penalties,
                                                           para_tardiness_penalties)
    if head_last == n - 1:  # if the optimal schedule of ET problem has only one block
        block_start = tail_start
        eti_penalty = et_penalty
        block_lasts.append(n - 1)
        t = block_start
        for j in jobs:
            t = t + para_processing_times[j]
            end_times.append(t)
            # print("!!!!!t=", t)

    else:
        block_lasts, end_times, eti_penalty = dp(head_last, tail_first, jobs, b, para_due_dates,
                                                 para_processing_times, para_earliness_penalties,
                                                 para_tardiness_penalties)
    if end_times[n - 1] >= uper_bound:
        eti_penalty = utils.BIG_NUMBER
    return block_lasts, end_times, eti_penalty
