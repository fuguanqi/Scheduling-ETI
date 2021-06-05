from multiprocessing.context import Process
import random
import Sourd
import utils as utils
import time
import test
import blockTiming as bt
import timing as timing
import numpy as np
import copy
import matplotlib.pyplot as plt
import GA

REPEAT = 5


def run1(problem):
    # print('"***************  Single Machine Scheduling with E/T/I Penalties  ***************"')
    # jobs=[3,2,1,4,0]
    # jobs = [4,7]
    # jobs = [8, 9, 3, 2, 1, 4, 7, 5, 6, 0,10,11,12,13,14,15,16,17,18,19]
    jobs = [1, 4, 2, 0, 3]
    # due2 = list(problem.due_dates)
    # due2, jobs = zip(*sorted(zip(due2, jobs)))

    # The variable part of idleness penalty is absorbed by the first job and the last job.
    p = copy.deepcopy(problem)
    p.earliness_penalties[jobs[0]] = p.earliness_penalties[jobs[0]] + p.a
    p.tardiness_penalties[jobs[0]] = p.tardiness_penalties[jobs[0]] - p.a
    p.earliness_penalties[jobs[n - 1]] = p.earliness_penalties[jobs[n - 1]] - p.a
    p.tardiness_penalties[jobs[n - 1]] = p.tardiness_penalties[jobs[n - 1]] + p.a

    start = time.process_time()
    memo_BT = bt.init_BT_memo(jobs, problem.due_dates, problem.processing_times)
    memo_ET = timing.init_ET_memo(jobs, problem.due_dates, problem.processing_times)
    memo_ETI = timing.init_ETI_memo(jobs, problem.due_dates)
    block_lasts, end_times, eti_penalty1 = timing.opt_ETI(memo_BT, memo_ET, memo_ETI, utils.BIG_NUMBER, jobs, 0, n - 1,
                                                          p)
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
    eti_penalty2, test_model = test.test_DP(jobs, problem.b, problem.due_dates, problem.processing_times,
                                            problem.earliness_penalties, problem.tardiness_penalties)
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
    return round(eti_penalty1), round(eti_penalty2), block_lasts, test_model


def run2(problem):
    # Ordering + Timing solved by CPLEX
    # The variable part of idleness penalty is absorbed by the first job and the last job.
    p = copy.deepcopy(problem)
    start = time.process_time()
    opt_model = test.test_Permutation(p)
    end = time.process_time()
    run_time = end - start
    print("*********  CPLEX runtime:   *********")
    print(run_time)


def run3(problem):
    ga = GA.GA_BASIC(problem)
    start = time.process_time()
    ga.run()
    end = time.process_time()
    run_time = end - start
    print("*********  GA_BASIC runtime:   *********")
    print(run_time)
    y1 = ga.memo_opt[0:-1]
    x1 = np.arange(1, len(y1) + 1)
    l1 = plt.plot(x1, y1, 'r--', label='GA_BASIC')
    plt.plot(x1, y1, 'r-')
    plt.title('The Convergence Curve of GA')
    plt.xlabel('Iteration')
    plt.ylabel('Best Objective')
    plt.legend()
    plt.show()
    print("**************** GA_BASIC ****************")
    print([a for a in ga.opt_chromo])
    print("********* GA_BASIC Block lasts:   *********")
    for i in ga.memo_FV[tuple(ga.opt_chromo)].block_lasts:
        print(i)
    print("*********  GA_BASIC end times:   *********")
    for i in ga.memo_FV[tuple(ga.opt_chromo)].end_times:
        print(i)
    print("*********  GA_BASEIC eti_penalty:   *********")
    print("overall penalty of GA_BASIC:", ga.memo_FV[tuple(ga.opt_chromo)].eti_penalty)


def run3_1(problem):
    ga = GA.GA_Faster_Both(problem)
    start = time.process_time()
    ga.run()
    end = time.process_time()
    run_time = end - start
    print("*********  GA_Both runtime:   *********")
    print(run_time)
    y1 = ga.memo_opt[0:-1]
    x1 = np.arange(1, len(y1) + 1)
    l1 = plt.plot(x1, y1, 'r--', label='GA_Both')
    plt.plot(x1, y1, 'r-')
    plt.title('The Convergence Curve of GA_Both')
    plt.xlabel('Iteration')
    plt.ylabel('Best Objective')
    plt.legend()
    plt.show()
    print("**************** GA_Both ****************")
    print([a for a in ga.opt_chromo])
    print("********* GA_Both Block lasts:   *********")
    for i in ga.memo_FV[tuple(ga.opt_chromo)].block_lasts:
        print(i)
    print("*********  GA_Both end times:   *********")
    for i in ga.memo_FV[tuple(ga.opt_chromo)].end_times:
        print(i)
    print("*********  GA_Both eti_penalty:   *********")
    print("overall penalty of GA_BASIC:", ga.memo_FV[tuple(ga.opt_chromo)].eti_penalty)


def run4(problem):
    jobs = [8, 9, 3, 2, 1, 4, 7, 5, 6, 0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    p = copy.deepcopy(problem)
    n = p.n
    p.earliness_penalties[jobs[0]] = p.earliness_penalties[jobs[0]] + p.a
    p.tardiness_penalties[jobs[0]] = p.tardiness_penalties[jobs[0]] - p.a
    p.earliness_penalties[jobs[n - 1]] = p.earliness_penalties[jobs[n - 1]] - p.a
    p.tardiness_penalties[jobs[n - 1]] = p.tardiness_penalties[jobs[n - 1]] + p.a
    start = time.process_time()
    memo_BT = bt.init_BT_memo(jobs, problem.due_dates, problem.processing_times)
    memo_ET = timing.init_ET_memo(jobs, problem.due_dates, problem.processing_times)
    memo_ETI = timing.init_ETI_memo(jobs, problem.due_dates)
    block_lasts, end_times, eti_penalty1 = timing.opt_ETI(memo_BT, memo_ET, memo_ETI, utils.BIG_NUMBER, jobs, 0, n - 1,
                                                          p)
    end = time.process_time()
    run_time1 = end - start
    print("**************** Main ****************")
    print("********* Basic DP Block Lasts:   *********")
    for i in block_lasts:
        print(i)
    print("********* Basic DP End Times:   *********")
    for i in end_times:
        print(i)
    print("********* Basic DP eti_penalty:   *********")
    print("overall penalty of basic DP:", eti_penalty1)

    start = time.process_time()
    memo_BT = bt.init_BT_memo(jobs, problem.due_dates, problem.processing_times)
    memo_ET = timing.init_ET_memo(jobs, problem.due_dates, problem.processing_times)
    memo_ETI_bounded = timing.init_ETI_memo_bounded(jobs, problem.due_dates)
    block_lasts, end_times, eti_penalty2 = timing.opt_ETI_Bounded(memo_BT, memo_ET, memo_ETI_bounded, utils.BIG_NUMBER,
                                                                  n - 1, jobs, 0, n - 1, p)
    end = time.process_time()
    run_time2 = end - start
    print("**************** Main ****************")
    print("********* Bounded DP Block Lasts:   *********")
    for i in block_lasts:
        print(i)
    print("********* Bounded DP End Times:   *********")
    for i in end_times:
        print(i)
    print("********* Bounded DP eti_penalty:   *********")
    print("overall penalty of basic DP:", eti_penalty2)
    print("******************")
    print("runtime 1", run_time1)
    print("runtime 2", run_time2)


def run5(p):
    ga_basic = GA.GA_BASIC(p)
    start = time.process_time()
    ga_basic.run()
    end = time.process_time()
    run_time = end - start
    b_ratio = ga_basic.memo_FV[tuple(ga_basic.opt_chromo)].b_ratio
    f = open('basicGA_results.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(b_ratio) + "\n")
    f.close()


def run6(p):
    ga_basic = GA.GA_Faster_DP(p)
    start = time.process_time()
    ga_basic.run()
    end = time.process_time()
    run_time = end - start
    b_ratio = ga_basic.memo_FV[tuple(ga_basic.opt_chromo)].b_ratio
    f = open('GA with bounded DP results.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(b_ratio) + "\n")
    f.close()


def run7(p):
    ga_basic = GA.GA_Faster_Select(p)
    start = time.process_time()
    ga_basic.run()
    end = time.process_time()
    run_time = end - start
    b_ratio = ga_basic.memo_FV[tuple(ga_basic.opt_chromo)].b_ratio
    f = open('GA with Improved Selection results.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(b_ratio) + "\n")
    f.close()


def run8(p):
    ga_basic = GA.GA_Faster_Both(p)
    start = time.process_time()
    ga_basic.run()
    end = time.process_time()
    run_time = end - start
    b_ratio = ga_basic.memo_FV[tuple(ga_basic.opt_chromo)].b_ratio
    f = open('GA with Both results.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(b_ratio) + "\n")
    f.close()


def run9(p):
    run_time1 = 0
    for i in range(REPEAT):
        jobs = list(range(n))
        random.shuffle(jobs)
        p = utils.generate_problem(n, b)
        p.earliness_penalties[jobs[0]] = p.earliness_penalties[jobs[0]] + p.a
        p.tardiness_penalties[jobs[0]] = p.tardiness_penalties[jobs[0]] - p.a
        p.earliness_penalties[jobs[n - 1]] = p.earliness_penalties[jobs[n - 1]] - p.a
        p.tardiness_penalties[jobs[n - 1]] = p.tardiness_penalties[jobs[n - 1]] + p.a
        start = time.process_time()
        memo_BT = bt.init_BT_memo(jobs, p.due_dates, p.processing_times)
        memo_ET = timing.init_ET_memo(jobs, p.due_dates, p.processing_times)
        memo_ETI = timing.init_ETI_memo_bounded(jobs, p.due_dates)
        _, _, eti_penalty1 = timing.opt_ETI_Bounded(memo_BT, memo_ET, memo_ETI, utils.BIG_NUMBER, n - 1, jobs, 0,
                                                    n - 1, p)
        end = time.process_time()
        run_time1 += end - start
        # print("My DP ETI = ", eti_penalty1)
        # print("My DP runtime = ", run_time1)
    run_time1 = run_time1 / REPEAT
    f = open('My_DP_results.txt', 'a')
    f.write(str(n) + "\t" + str(b) + "\t" + str(run_time1) + "\n")
    f.close()


def run10(n, b):
    jobs = list(range(n))
    random.shuffle(jobs)
    p = utils.generate_problem(n, b)
    p.earliness_penalties[jobs[0]] = p.earliness_penalties[jobs[0]] + p.a
    p.tardiness_penalties[jobs[0]] = p.tardiness_penalties[jobs[0]] - p.a
    p.earliness_penalties[jobs[n - 1]] = p.earliness_penalties[jobs[n - 1]] - p.a
    p.tardiness_penalties[jobs[n - 1]] = p.tardiness_penalties[jobs[n - 1]] + p.a
    sourd = Sourd.Sourd(jobs, p)
    start = time.process_time()
    eti_penalty2 = sourd.run()
    end = time.process_time()
    run_time2 = end - start
    f = open('Sourd_DP_results.txt', 'a')
    f.write(str(n) + "\t" + str(b) + "\t" + str(run_time2) + "\n")
    f.close()


def run11(n, b):
    run_time3 = 0
    b_ratio = 0
    for i in range(REPEAT):
        jobs = list(range(n))
        random.shuffle(jobs)
        p = utils.generate_problem(n, b)
        p.earliness_penalties[jobs[0]] = p.earliness_penalties[jobs[0]] + p.a
        p.tardiness_penalties[jobs[0]] = p.tardiness_penalties[jobs[0]] - p.a
        p.earliness_penalties[jobs[n - 1]] = p.earliness_penalties[jobs[n - 1]] - p.a
        p.tardiness_penalties[jobs[n - 1]] = p.tardiness_penalties[jobs[n - 1]] + p.a
        start = time.process_time()
        eti_penalty3, opt_model = test.test_DP(jobs, b, p.due_dates, p.processing_times,
                                               p.earliness_penalties, p.tardiness_penalties)
        end = time.process_time()
        run_time3 += end - start
        num_idle = 0
        for j in range(n - 1):
            num_idle += opt_model.solution.get_value("idleness_after_job_" + str(j))
        b_ratio += num_idle * b / eti_penalty3
        # print("CPLEX ETI = ", eti_penalty3)
        # print("CPLEX runtime = ", run_time3)
    b_ratio = b_ratio / REPEAT
    run_time3 = run_time3 / REPEAT
    f = open('CPLEX_TIMING_results.txt', 'a')
    f.write(str(n) + "\t" + str(b) + "\t" + str(run_time3) + "\t" + str(b_ratio) + "\n")
    f.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # n = 21
    # p = utils.generate_problem(n, 15, 1)
    # run3_1(p)
    N = [6, 8, 10, 12, 14, 16, 18, 20]
    # # N = [ 500, 400, 300, 200, 100, 50, 20]
    # # N = [100, 200, 300]
    B = [1, 10, 50, 100, 150, 200]
    RHO = [0.3, 0.7, 1, 1.5, 2, 3]
    for n in N:
        for b in B:
            for rho in RHO:
                for i in range(REPEAT):
                    p = utils.generate_problem(n, b, rho, seed=REPEAT)
                    # proc1 = Process(target=run5, args=(p))
                    proc2 = Process(target=run6, args=(p,))
                    proc3 = Process(target=run7, args=(p,))
                    # proc4 = Process(target=run8, args=(p))
                    # proc1.start()
                    proc2.start()
                    proc3.start()
                    # proc4.start()
                    # proc1.join()
                    proc2.join()
                    proc3.join()
                    # proc4.join()

    # proc5 = Process(target=run9, args=(n, b))
    # proc6 = Process(target=run10, args=(n, b))
    # proc7 = Process(target=run11, args=(n, b))
    # # proc1.start()
    # # # proc2.start()
    # # # proc3.start()
    # # proc4.start()
    # proc5.start()
    # proc6.start()
    # proc7.start()
    # # proc1.join()
    # # # proc2.join()
    # # # proc3.join()
    # # proc4.join()
    # proc5.join()
    # proc6.join()
    # proc7.join()
