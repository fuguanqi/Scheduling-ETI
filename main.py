import utils as utils
import time
import blockTiming as bt
import timing as timing

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('"***************  Single Machine Scheduling with E/T/I Penalties  ***************"')
    problem = utils.generate_problem(n=10)
    jobs = [8, 9, 3, 2, 1, 4, 7, 5, 6, 0]
    n = len(jobs)

    # The variable part of idleness penalty is absorbed by the first job and the last job.
    problem.earliness_penalties[jobs[0]] = problem.earliness_penalties[jobs[0]] + problem.a
    problem.tardiness_penalties[jobs[0]] = problem.tardiness_penalties[jobs[0]] - problem.a
    problem.earliness_penalties[jobs[n - 1]] = problem.earliness_penalties[jobs[n - 1]] - problem.a
    problem.tardiness_penalties[jobs[n - 1]] = problem.tardiness_penalties[jobs[n - 1]] + problem.a

    # bt.time_block(jobs, block_problem.due_dates, block_problem.processing_times, block_problem.earliness_penalties,
    #               block_problem.tardiness_penalties)
    # timing.opt_ET(jobs, problem.due_dates, problem.processing_times, problem.earliness_penalties,
    #               problem.tardiness_penalties)

    start = time.process_time()
    block_lasts, end_times, eti_penalty = timing.opt_ETI(utils.BIG_NUMBER, jobs, problem.b, problem.due_dates,
                                                         problem.processing_times, problem.earliness_penalties,
                                                         problem.tardiness_penalties)
    end = time.process_time()
    run_time = end - start
    print("**************** Main ****************")
    print("*********   runtime:   *********")
    print(run_time)
    print("*********   block lasts:   *********")
    for i in block_lasts:
        print(i)
    print("*********   end times:   *********")
    for i in end_times:
        print(i)
    print("*********   eti_penalty:   *********")
    print("overall penalty:", eti_penalty)
