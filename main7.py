import os
import random
import sys
from multiprocessing.context import Process
import Sourd
import utils as utils
import time
import test
import blockTiming as bt
import numpy as np
import copy
import matplotlib.pyplot as plt
import GA
import My_DP_new as dp
import My_DP_Bounded as dpb
import ET_opt as et

REPEAT = 30


def run9(p, jobs):
    sys.setrecursionlimit(1200)
    start = time.process_time()
    memo_BT = bt.init_BT_memo(jobs, p.due_dates, p.processing_times)
    memo_ET = et.init_ET_memo(jobs, p.due_dates, p.processing_times)
    et_global_solution = et.init_ET_global_solution(jobs, p)
    memo_ETI = dpb.init_ETI_memo_bounded(jobs)
    block_lasts, _, eti_penalty1 = dpb.opt_ETI_Bounded(memo_BT, memo_ET, memo_ETI, et_global_solution,
                                                       p.n - 1, jobs, p.n - 1, p)
    end = time.process_time()
    run_time1 = end - start
    num_idle = len(block_lasts) - 1
    # f = open('My_DP_Bounded_results_0725.txt', 'a')
    f = open('My_DP_Bounded_0112.txt', 'a')
    f.write(
        str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time1) + "\t" + str(eti_penalty1) + "\t" + str(
            num_idle) + "\n")
    f.close()


def run9_0(p, jobs):
    # sys.setrecursionlimit(2000)
    sys.setrecursionlimit(1200)
    memo_BT = bt.init_BT_memo(jobs, p.due_dates, p.processing_times)
    memo_ET = et.init_ET_memo(jobs, p.due_dates, p.processing_times)
    # memo_ETI = dp.init_ETI_memo(jobs, p.due_dates)
    # _, _, eti_penalty1, cplex_time = dp.opt_ETI(memo_BT, memo_ET, memo_ETI, utils.BIG_NUMBER, jobs, p.n - 1, p)
    memo_ETI = dp.init_ETI_memo(jobs)
    et_global_solution = et.init_ET_global_solution(jobs, p)
    start = time.process_time()
    block_lasts, cplex_time, eti_penalty1 = dp.opt_ETI(memo_BT, memo_ET, memo_ETI, et_global_solution, jobs, p.n - 1, p)
    end = time.process_time()
    run_time1 = end - start
    # f = open('My_DP_results_0725.txt', 'a')
    # f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time1) + "\t" + str(cplex_time) + "\n")
    num_idle = len(block_lasts) - 1
    f = open('My_DP_0621.txt', 'a')
    f.write(
        str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time1) + "\t" + str(
            eti_penalty1) + "\t" + str(num_idle) +"\n")
    f.close()


def run10(p, jobs):
    sys.setrecursionlimit(1200)
    sourd = Sourd.Sourd(jobs, p)
    start = time.process_time()
    obj = sourd.run()
    end = time.process_time()
    run_time2 = end - start
    # f = open('Sourd_DP_0725.txt', 'a')
    f = open('Sourd_DP_0621.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time2) + "\t" + str(obj) + "\n")
    f.close()


def run10_1(p, jobs):
    sys.setrecursionlimit(1200)
    sourd = Sourd.Sourd(jobs, p)
    start = time.process_time()
    obj = sourd.run_bounded()
    end = time.process_time()
    run_time2 = end - start
    f = open('Sourd_DP_Bounded_0725.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time2) + "\t" + str(obj) + "\n")
    f.close()


# def run10_1(p, jobs):
#     sys.setrecursionlimit(1200)
#     sourd = Sourd.Sourd(jobs, p)
#     start = time.process_time()
#     obj = sourd.run_bounded()
#     end = time.process_time()
#     run_time2 = end - start
#     f = open('Sourd_DP_Bounded_0725.txt', 'a')
#     f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time2) + "\t" + str(obj) + "\n")
#     f.close()


def run11(p, jobs):
    start = time.process_time()
    eti_penalty3, opt_model = test.test_DP(jobs, p.b, p.due_dates, p.processing_times, p.earliness_penalties,
                                           p.tardiness_penalties)
    end = time.process_time()
    run_time3 = end - start
    obj = opt_model.solution.get_objective_value()
    f = open('Nes_CPLEX_TIMING_results.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time3) + "\t" + str(obj) + "\n")
    f.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # n = 21
    # p = utils.generate_problem(n, 15, 1)
    # run3_1(p)
    # N = [6, 8, 10, 12, 14, 16, 18, 20]
    # N = [600, 800]
    # N = [1000]
    N = [200,400,600,800,1000]
    # B = [1, 10, 100, 1000, 10000, 100000,1000000]
    # B = [1000, 100, 10, 1]
    B = [1,100000]
    # RHO = [1.5,1.2, 0.9, 0.6,0.3]
    RHO = [1.9]
    # RHO = [0.1, 0.3, 0.5, 0.7]
    for n in N:
        for b in B:
            for rho in RHO:
                for i in range(REPEAT):
                    p = utils.generate_problem(n, b, rho, seed=i)
                    # p = utils.generate_problem(n, b, rho, seed=9)
                    jobs = list(range(n))
                    random.shuffle(jobs)
                    # due = list(p.due_dates)
                    # process = list(p.processing_times)
                    # expected_starts = []
                    # for j in range(len(due)):
                    #     expected_starts.append(due[j] - process[j])
                    # expected_starts, jobs = zip(*sorted(zip(expected_starts, jobs)))
                    p.earliness_penalties[jobs[0]] = p.earliness_penalties[jobs[0]] + p.a
                    p.tardiness_penalties[jobs[0]] = p.tardiness_penalties[jobs[0]] - p.a
                    p.earliness_penalties[jobs[n - 1]] = p.earliness_penalties[jobs[n - 1]] - p.a
                    p.tardiness_penalties[jobs[n - 1]] = p.tardiness_penalties[jobs[n - 1]] + p.a
                    # proc1 = Process(target=run9_0, args=(p, jobs))
                    # proc2 = Process(target=run10_1, args=(p, jobs))
                    # proc1 = Process(target=run9, args=(p, jobs))
                    # proc2 = Process(target=run9_0, args=(p, jobs))
                    proc3 = Process(target=run10, args=(p, jobs))
                    # proc1.start()
                    # proc2.start()
                    # proc1.start()
                    # proc2.start()
                    proc3.start()
                    # proc4.start()
                    # proc1.join()
                    # proc2.join()
                    proc3.join()
                    # proc4.join()
