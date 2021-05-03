import utils as utils
import time
import test
import blockTiming as bt
import timing as timing

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('"***************  Single Machine Scheduling with E/T/I Penalties  ***************"')
    problem = utils.generate_problem(n=30)
    # jobs=[3,2,1,4,0]
    # jobs = [4,7]
    # jobs = [8, 9, 3, 2, 1, 4, 7, 5, 6, 0,10,11,12,13,14,15,16,17,18,19]
    jobs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
            10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
            20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
    n = len(jobs)

    # The variable part of idleness penalty is absorbed by the first job and the last job.
    problem.earliness_penalties[jobs[0]] = problem.earliness_penalties[jobs[0]] + problem.a
    problem.tardiness_penalties[jobs[0]] = problem.tardiness_penalties[jobs[0]] - problem.a
    problem.earliness_penalties[jobs[n - 1]] = problem.earliness_penalties[jobs[n - 1]] - problem.a
    problem.tardiness_penalties[jobs[n - 1]] = problem.tardiness_penalties[jobs[n - 1]] + problem.a

    start = time.process_time()
    memo_BT = bt.init_BT_memo(n, problem.due_dates, problem.processing_times)
    memo_ET = timing.init_ET_memo(n, problem.due_dates, problem.processing_times)
    memo_ETI = timing.init_ETI_memo(n, problem.due_dates)
    block_lasts, end_times, eti_penalty1 = timing.opt_ETI(memo_BT,memo_ET,memo_ETI, utils.BIG_NUMBER, jobs, 0, n - 1,
                                                         problem.b, problem.due_dates, problem.processing_times,
                                                         problem.earliness_penalties, problem.tardiness_penalties)
    end = time.process_time()
    run_time1 = end - start
    print("**************** Main ****************")
    print("*********  DP block lasts:   *********")
    for i in block_lasts:
        print(i)
    print("*********  DP end times:   *********")
    for i in end_times:
        print(i)
    print("*********  DP eti_penalty:   *********")
    print("overall penalty of DP:", eti_penalty1)

    start = time.process_time()
    eti_penalty2 = test.test_eti(jobs, problem.b, problem.due_dates,
                                problem.processing_times, problem.earliness_penalties,
                                problem.tardiness_penalties)
    end = time.process_time()
    run_time2 = end - start
    print("*********  DP eti_penalty:   *********")
    print("overall penalty of DP:", eti_penalty1)
    print("*********  DP runtime:   *********")
    print(run_time1)
    print("*********  CPLEX eti_penalty:   *********")
    print("overall penalty of CPLEX:", eti_penalty2)
    print("*********  CPLEX runtime:   *********")
    print(run_time2)
