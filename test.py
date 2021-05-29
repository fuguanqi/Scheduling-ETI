import docplex.mp.model as cpx
import utils


def test_DP(jobs, b, para_due_dates, para_processing_times, para_earliness_penalties, para_tardiness_penalties):
    # Create model
    opt_model = cpx.Model(name="Test DP Model")

    opt_model.parameters.simplex.tolerances.feasibility = 0.000001

    opt_model.context.cplex_parameters.threads = 1

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
    # print("**************** Test ETI ****************")
    # opt_model.print_information()
    opt_model.solve()
    # print("        ******************************        ")
    # opt_model.report()
    # print("        ******************************        ")
    # print(opt_model.print_solution(print_zeros=False))
    # # print("        ******************************        ")
    # # print(opt_model.get_statistics())
    # print("        ******************************        ")
    # print(opt_model.get_solve_details())
    # print("        ******************************        ")

    eti_penalty = opt_model.solution.get_objective_value()

    # print("E/T/I penalty:", eti_penalty)
    # print("**************** Test ETI Finished ****************")

    return eti_penalty, opt_model


def test_Permutation(problem):
    opt_model = cpx.Model(name="Test ETI Model")
    opt_model.parameters.simplex.tolerances.feasibility = 0.000001
    opt_model.context.cplex_parameters.threads = 1

    # Decision parameters
    end_times = opt_model.continuous_var_list(problem.n, lb=0, name="end_time_of_#%s")
    earlis = opt_model.continuous_var_list(problem.n, lb=0, name="earliness_of_#%s")
    tardis = opt_model.continuous_var_list(problem.n, lb=0, name="tardiness_of_#%s")
    idle_after = opt_model.binary_var_list(problem.n - 1, name="idleness_after_#%s")
    seq_job = opt_model.binary_var_matrix(problem.n, problem.n, name="#%s_is_job_%s")
    follow = opt_model.binary_var_cube(problem.n - 1, problem.n, problem.n, name="#%s_job_%s_->_job_%s")
    merge = opt_model.binary_var_cube(problem.n - 1, problem.n, problem.n, name="#%s_job_%s_merge_job_%s")
    earlis_hat = opt_model.continuous_var_matrix(problem.n, problem.n, name="earliness_of_#%s_(job_%s)")
    tardis_hat = opt_model.continuous_var_matrix(problem.n, problem.n, name="tardiness_of_#%s_(job_%s)")
    start = opt_model.continuous_var(lb=0, name="start_time")

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            follow[i, j, k],
            seq_job[i, j] + seq_job[i + 1, k] == 2
        ) for i in range(problem.n - 1) for j in range(problem.n) for k in range(problem.n)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            follow[i, j, k],
            end_times[i] + problem.processing_times[k] <= end_times[i + 1]
        ) for i in range(problem.n - 1) for j in range(problem.n) for k in range(problem.n)
    )

    # constraint
    opt_model.add_constraints_(
        opt_model.sum(follow[i, j, k] for j in range(problem.n) for k in range(problem.n)) == 1
        for i in range(problem.n - 1)
    )
    opt_model.add_constraints_(
        opt_model.sum(merge[i, j, k] for j in range(problem.n) for k in range(problem.n)) <= 1
        for i in range(problem.n - 1)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            seq_job[i, j],
            end_times[i] + earlis[i] - tardis[i] == problem.due_dates[j]
        ) for i in range(problem.n) for j in range(problem.n)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            merge[i, j, k],
            follow[i, j, k] == 1
        ) for i in range(problem.n - 1) for j in range(problem.n) for k in range(problem.n)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            merge[i, j, k],
            idle_after[i] == 0
        ) for i in range(problem.n - 1) for j in range(problem.n) for k in range(problem.n)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            idle_after[i],
            opt_model.sum(merge[i, j, k] for j in range(problem.n) for k in range(problem.n)) == 0
        ) for i in range(problem.n - 1)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            idle_after[i],
            opt_model.sum(merge[i, j, k] for j in range(problem.n) for k in range(problem.n)) == 1,
            0
        ) for i in range(problem.n - 1)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            merge[i, j, k],
            end_times[i] + problem.processing_times[k] == end_times[i + 1]
        ) for i in range(problem.n - 1) for j in range(problem.n) for k in range(problem.n)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            seq_job[i, j],
            earlis_hat[i, j] == earlis[i]
        ) for i in range(problem.n) for j in range(problem.n)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            seq_job[i, j],
            tardis_hat[i, j] == tardis[i]
        ) for i in range(problem.n) for j in range(problem.n)
    )

    # constraint
    opt_model.add_constraints_(
        opt_model.sum(seq_job[i, j] for i in range(problem.n)) == 1 for j in range(problem.n)
    )
    opt_model.add_constraints_(
        opt_model.sum(seq_job[i, j] for j in range(problem.n)) == 1 for i in range(problem.n)
    )

    # constraint
    opt_model.add_indicator_constraints_(
        opt_model.indicator_constraint(
            seq_job[0, j],
            start + problem.processing_times[j] == end_times[0]
        ) for j in range(problem.n)
    )

    objective_function = opt_model.sum(
        earlis_hat[i, j] * problem.earliness_penalties[j] + tardis_hat[i, j] * problem.tardiness_penalties[j] for i in
        range(problem.n) for j in range(problem.n)) + opt_model.sum(
        idle_after[i] * problem.b for i in range(problem.n - 1)) + (end_times[problem.n - 1] - start - opt_model.sum(
        problem.processing_times[i] for i in range(problem.n))) * problem.a

    opt_model.minimize(objective_function)
    opt_model.solve()
    print("        *************** Test Permutation by DPLEX ***************        ")
    opt_model.report()
    print("        ******************************        ")
    print(opt_model.print_solution(print_zeros=False))
    print("        ******************************        ")
    print(opt_model.get_statistics())
    print("        ******************************        ")
    print(opt_model.get_solve_details())
    print("        ******************************        ")
    print("**************** Test Permutation Finished ****************")

    return opt_model
