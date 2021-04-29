import docplex.mp.model as cpx
import utils


# jobs as list
def time_block(jobs, para_due_dates, para_processing_times, para_earliness_penalties, para_tardiness_penalties):
    # Create model
    opt_model = cpx.Model(name="Block Timing Model")

    n = len(jobs)

    # Decision parameters
    end_times = opt_model.continuous_var_list(n, lb=0, ub=utils.BIG_NUMBER, name="end_time_of_job_%s")
    earlis = opt_model.continuous_var_list(n, lb=0, ub=utils.BIG_NUMBER, name="earliness_of_job_%s")
    tardis = opt_model.continuous_var_list(n, lb=0, ub=utils.BIG_NUMBER, name="tardiness_of_job_%s")

    # constraint
    opt_model.add_constraints_(
        end_times[i] + para_processing_times[jobs[i + 1]] == end_times[i + 1] for i in range(n - 1)
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
    print("**************** Block Timing ****************")
    # opt_model.print_information()
    opt_model.solve()

    print("        ******** The jobs in this block are:********        ")
    for i in jobs:
        print("job ", i)
    # print("        ****** The due dates are ******        ")
    # for i in para_due_dates:
    #     print(i)
    # print("        ****** The proceccing times are: ******        ")
    # for i in para_processing_times:
    #     print(i)
    print("        ******************************        ")
    opt_model.report()
    print("        ******************************        ")
    print(opt_model.print_solution(print_zeros=False))
    # print("        ******************************        ")
    # print(opt_model.get_statistics())
    print("        ******************************        ")
    print(opt_model.get_solve_details())
    print("        ******************************        ")

    block_end = opt_model.solution.get_value("end_time_of_job_" + str(n - 1))
    block_start = opt_model.solution.get_value("end_time_of_job_0") - para_processing_times[0]
    et_penalty = opt_model.solution.get_objective_value()

    print("block start:", block_start)
    print("block end:", block_end)
    print("E/T penalty:", et_penalty)
    print("**************** Block Timing Finished ****************")
    return block_start, block_end, et_penalty
