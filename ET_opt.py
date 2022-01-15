import blockTiming as bt
import docplex.mp.model as cpx


class ET_solution:
    def __init__(self):
        self.head_last = -1
        self.tail_first = -1
        self.tail_start = -1
        self.tail_end = -1
        self.et_penalty = -1
        self.num_idle = -1


class ET_global_solution:
    def __init__(self):
        self.block_lasts = list()
        self.block_objs = list()
        self.block_endtimes = list()
        self.block_starttimes = list()


def init_ET_memo(jobs, para_due_dates, para_processing_times):
    n = len(jobs)
    memo_ET = list()
    for i in range(n):
        memo_ET.append(ET_solution())
    return memo_ET


def init_ET_global_solution(jobs, problem):
    et_global_solution = ET_global_solution()
    # Create model
    opt_model = cpx.Model(name="Calculate E/T Model")
    opt_model.parameters.simplex.tolerances.feasibility = 0.0000001
    n = len(jobs)

    # Decision parameters
    end_times = opt_model.continuous_var_list(n, lb=0, name="end_time_of_job_%s")
    earlis = opt_model.continuous_var_list(n, lb=0, name="earliness_of_job_%s")
    tardis = opt_model.continuous_var_list(n, lb=0, name="tardiness_of_job_%s")
    # constraint
    opt_model.add_constraints_(
        end_times[i] + problem.processing_times[jobs[i + 1]] <= end_times[i + 1]
        for i in range(n - 1)
    )

    # constraint
    opt_model.add_constraints_(
        end_times[i] + earlis[i] - tardis[i] == problem.due_dates[jobs[i]] for i in range(n)
    )

    # Objective function
    objective_function = opt_model.sum(
        earlis[i] * problem.earliness_penalties[jobs[i]] + tardis[i] * problem.tardiness_penalties[jobs[i]]
        for i in range(n)
    )
    # minimize objective
    opt_model.minimize(objective_function)
    opt_model.solve()

    block_obj = 0
    et_global_solution.block_starttimes.append(
        opt_model.solution.get_value("end_time_of_job_" + str(0)) - problem.processing_times[jobs[0]])
    for i in range(n - 1):
        end1 = opt_model.solution.get_value("end_time_of_job_" + str(i))
        end2 = opt_model.solution.get_value("end_time_of_job_" + str(i + 1))
        block_obj += opt_model.solution.get_value("earliness_of_job_" + str(i)) * problem.earliness_penalties[
            jobs[i]] + opt_model.solution.get_value("tardiness_of_job_" + str(i)) * problem.tardiness_penalties[jobs[i]]
        if end1 + problem.processing_times[jobs[i + 1]] != end2:
            et_global_solution.block_lasts.append(i)
            et_global_solution.block_endtimes.append(end1)
            et_global_solution.block_objs.append(block_obj)
            et_global_solution.block_starttimes.append(end2 - problem.processing_times[jobs[i + 1]])
            block_obj = 0
        if i == n - 2:
            et_global_solution.block_lasts.append(i + 1)
            et_global_solution.block_endtimes.append(end2)
            block_obj += opt_model.solution.get_value("earliness_of_job_" + str(i + 1)) * problem.earliness_penalties[
                jobs[i + 1]] + opt_model.solution.get_value("tardiness_of_job_" + str(i + 1)) * \
                         problem.tardiness_penalties[jobs[i + 1]]
            et_global_solution.block_objs.append(block_obj)
    return et_global_solution


def opt_ET(memoBT, memo_ET, et_global_solution, jobs, problem, last):
    if memo_ET[last].head_last >= 0:
        return memo_ET[last]
    if last in et_global_solution.block_lasts:
        i = et_global_solution.block_lasts.index(last)
        head_last = et_global_solution.block_lasts[0]
        if i == 0:
            tail_first = 0
        else:
            tail_first = et_global_solution.block_lasts[i - 1] + 1
        tail_start = et_global_solution.block_starttimes[i]
        tail_end = et_global_solution.block_endtimes[i]
        et_penalty = 0
        for j in range(i + 1):
            et_penalty += et_global_solution.block_objs[j]
        num_idle = i

    else:
        # if last < et_global_solution.block_lasts[0]:
        #     print("???????????????")
        #     head_last = last
        #     tail_first = 0
        #     block_start, block_end, et_penalty, cplex_time = bt.time_block_no_memo(jobs, 0, last, problem)
        #     tail_start = block_start
        #     tail_end = block_end
        #     num_idle = 0
        # else:
        et_penalty = 0
        num_idle = 1
        head_last = et_global_solution.block_lasts[0]
        for i in range(len(et_global_solution.block_lasts) - 1):
            et_penalty += et_global_solution.block_objs[i]
            if last > et_global_solution.block_lasts[i] and last < et_global_solution.block_lasts[i + 1]:
                tail_first = et_global_solution.block_lasts[i] + 1
                # tail_start = et_global_solution.block_starttimes[i + 1]
                # tail_end = et_global_solution.block_endtimes[i + 1]
                start_UB, end_UB, et_penalty_UB, _ = bt.time_block(memoBT, jobs, tail_first, last, problem)
                tail_start = start_UB
                tail_end = end_UB
                et_penalty += et_penalty_UB
                break
            num_idle += 1

    memo_ET[last].head_last = head_last
    memo_ET[last].tail_first = tail_first
    memo_ET[last].tail_start = tail_start
    memo_ET[last].tail_end = tail_end
    memo_ET[last].et_penalty = et_penalty
    memo_ET[last].num_idle = num_idle

    return memo_ET[last]


#
# def opt_ET_no_memo(jobs, first, last, problem):
#     para_due_dates = problem.due_dates
#     para_processing_times = problem.processing_times
#     para_earliness_penalties = problem.earliness_penalties
#     para_tardiness_penalties = problem.tardiness_penalties
#     # Create model
#     opt_model = cpx.Model(name="Calculate E/T Model")
#     opt_model.parameters.simplex.tolerances.feasibility = 0.0000001
#
#     n = last - first + 1
#
#     # Decision parameters
#     end_times = opt_model.continuous_var_list(n, lb=0, name="end_time_of_job_%s")
#     earlis = opt_model.continuous_var_list(n, lb=0, name="earliness_of_job_%s")
#     tardis = opt_model.continuous_var_list(n, lb=0, name="tardiness_of_job_%s")
#
#     # constraint
#     opt_model.add_constraints_(
#         end_times[i] + para_processing_times[jobs[first + i + 1]] <= end_times[i + 1]
#         for i in range(n - 1)
#     )
#
#     # constraint
#     opt_model.add_constraints_(
#         end_times[i] + earlis[i] - tardis[i] == para_due_dates[jobs[first + i]] for i in range(n)
#     )
#
#     # Objective function
#     objective_function = opt_model.sum(
#         earlis[i] * para_earliness_penalties[jobs[first + i]] + tardis[i] * para_tardiness_penalties[jobs[first + i]]
#         for i in range(n)
#     )
#
#     # minimize objective
#     opt_model.minimize(objective_function)
#     opt_model.solve()
#     head_last = last
#     tail_first = first
#     is_head = 1
#     num_idle = 0
#     for i in range(n - 1):
#         end1 = opt_model.solution.get_value("end_time_of_job_" + str(i))
#         end2 = opt_model.solution.get_value("end_time_of_job_" + str(i + 1))
#         if round(end1 + para_processing_times[jobs[first + i + 1]], 4) != round(end2, 4):
#             if is_head == 1:
#                 head_last = i
#                 is_head = 0
#             num_idle += 1
#
#     for i in range(n - 1):
#         end1 = opt_model.solution.get_value("end_time_of_job_" + str(n - 2 - i))
#         end2 = opt_model.solution.get_value("end_time_of_job_" + str(n - 1 - i))
#         if round(end1 + para_processing_times[jobs[last - i]], 4) != round(end2, 4):
#             tail_first = last - i
#             break
#
#     et_penalty = opt_model.solution.get_objective_value()
#
#     return head_last, tail_first, et_penalty, num_idle


def opt_ET_with_boundary(memoBT, et_global_solution, jobs, last, problem, boundary):
    para_due_dates = problem.due_dates
    para_processing_times = problem.processing_times
    para_earliness_penalties = problem.earliness_penalties
    para_tardiness_penalties = problem.tardiness_penalties
    if last in et_global_solution.block_lasts:
        i = et_global_solution.block_lasts.index(last)
        et_block_lasts = et_global_solution.block_lasts[0:i + 1]
        et_block_ends = et_global_solution.block_endtimes[0:i + 1]
        et_block_objs=et_global_solution.block_objs[0:i+1]

    else:
        et_block_lasts = list()
        et_block_ends = list()
        et_block_objs=list()
        if last > et_global_solution.block_lasts[0]:
            for i in range(len(et_global_solution.block_lasts) - 1):
                et_block_objs.append(et_global_solution.block_objs[i])
                et_block_lasts.append(et_global_solution.block_lasts[i])
                et_block_ends.append(et_global_solution.block_endtimes[i])
                if last > et_global_solution.block_lasts[i] and last < et_global_solution.block_lasts[i + 1]:
                    tail_first = et_global_solution.block_lasts[i] + 1
                    start_UB, end_UB, et_penalty_UB, _ = bt.time_block(memoBT, jobs, tail_first, last, problem)
                    et_block_ends.append(end_UB)
                    et_block_lasts.append(last)
                    et_block_objs.append(et_penalty_UB)
                    break

    t = boundary
    i = last
    tail_penalty = 0
    while True:
        tail_penalty += max(0, para_due_dates[jobs[i]] - t) * para_earliness_penalties[jobs[i]] +\
                        max(0, t -para_due_dates[jobs[i]]) * para_tardiness_penalties[jobs[i]]
        t = t - para_processing_times[jobs[i]]
        i=i-1
        if i==-1:
            b_penalty=tail_penalty
            num_idle=0
            break
        if i in et_block_lasts:
            b = et_block_lasts.index(i)
            if et_block_ends[b] < t:
                b_penalty=sum(et_block_objs[0:b])+tail_penalty
                num_idle=b+1
                break



    return b_penalty, num_idle
