import docplex.mp.model as cpx
import utils


def test_eti(jobs, b, para_due_dates, para_processing_times, para_earliness_penalties, para_tardiness_penalties):
    # Create model
    opt_model = cpx.Model(name="Test ETI Model")

    n = len(jobs)

    # Decision parameters
    end_times = opt_model.continuous_var_list(n, lb=0, name="end_time_of_job_%s")
    earlis = opt_model.continuous_var_list(n, lb=0, name="earliness_of_job_%s")
    tardis = opt_model.continuous_var_list(n, lb=0, name="tardiness_of_job_%s")
    idle_after = opt_model.binary_var_list(n - 1, name="idleness_after_job_%s")

    # constraint
    opt_model.add_constraints_(
        end_times[i] + para_processing_times[jobs[i + 1]] <= end_times[i + 1] for i in range(n - 1)
    )

    # constraint
    opt_model.add_constraints_(
        end_times[i] + earlis[i] - tardis[i] == para_due_dates[jobs[i]] for i in range(n)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.add_indicator(
            idle_after[i],
            end_times[i] + para_processing_times[jobs[i + 1]] == end_times[i + 1], 0
        ) for i in range(n - 1)
    )

    # # constraint
    # opt_model.add_constraints_(
    #     end_times[i] + para_processing_times[jobs[i + 1]] - idle_after[i] * utils.BIG_NUMBER <= end_times[i + 1]
    #     for i in range(n - 1)
    # )

    # Objective function
    objective_function = opt_model.sum(
        earlis[i] * para_earliness_penalties[jobs[i]] + tardis[i] * para_tardiness_penalties[jobs[i]] for i in range(n)
    ) + opt_model.sum(idle_after[i] * b for i in range(n - 1))

    opt_model.minimize(objective_function)
    print("**************** Test ETI ****************")
    # opt_model.print_information()
    opt_model.solve()
    print("        ******************************        ")
    opt_model.report()
    print("        ******************************        ")
    print(opt_model.print_solution(print_zeros=False))
    # print("        ******************************        ")
    # print(opt_model.get_statistics())
    print("        ******************************        ")
    print(opt_model.get_solve_details())
    print("        ******************************        ")

    eti_penalty = opt_model.solution.get_objective_value()

    print("E/T/I penalty:", eti_penalty)
    print("**************** Test ETI Finished ****************")

    return eti_penalty
