import sys
from multiprocessing.context import Process
import utils as utils
import time
import GA

REPEAT = 10


def run5(p):
    ga = GA.GA_BASIC(p)
    start = time.process_time()
    ga.run()
    end = time.process_time()
    run_time = end - start
    f = open('GA_My_DP_0717.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(
        ga.memo_opt[ga.max_iter]) + "\t" + str(ga.memo_opt[ga.max_iter - 5]) + "\t" + str(
        ga.memo_opt[ga.max_iter - 10]) + "\n")
    f.close()


def run6(p):
    ga = GA.GA_Faster_DP(p)
    start = time.process_time()
    ga.run()
    end = time.process_time()
    run_time = end - start
    f = open('GA_My_DP_Bound1_0717.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(
        ga.memo_opt[ga.max_iter]) + "\t" + str(ga.memo_opt[ga.max_iter - 5]) + "\t" + str(
        ga.memo_opt[ga.max_iter - 10]) + "\n")
    f.close()


def run7(p):
    ga = GA.GA_Faster_Select(p)
    start = time.process_time()
    ga.run()
    end = time.process_time()
    run_time = end - start
    f = open('GA_bound2.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(
        ga.memo_opt[ga.max_iter]) + "\t" + str(ga.memo_opt[ga.max_iter - 5]) + "\t" + str(
        ga.memo_opt[ga.max_iter - 10]) + "\n")
    f.close()


def run8(p):
    ga = GA.GA_Faster_Both(p)
    start = time.process_time()
    ga.run()
    end = time.process_time()
    run_time = end - start
    f = open('GA_bound_1&2_0717.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(
        ga.memo_opt[ga.max_iter]) + "\t" + str(ga.memo_opt[ga.max_iter - 5]) + "\t" + str(
        ga.memo_opt[ga.max_iter - 10]) + "\n")
    f.close()


def run13(p):
    ga = GA.GA_Sourd_DP(p)
    start = time.process_time()
    ga.run()
    end = time.process_time()
    run_time = end - start
    f = open('GA_Sourd_0717.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(
        ga.memo_opt[ga.max_iter]) + "\t" + str(ga.memo_opt[ga.max_iter - 5]) + "\t" + str(
        ga.memo_opt[ga.max_iter - 10]) + "\n")
    f.close()


def run14(p):
    ga = GA.GA_Sourd_Bounded(p)
    start = time.process_time()
    ga.run()
    end = time.process_time()
    run_time = end - start
    f = open('GA_Sourd_bound1_0717.txt', 'a')
    f.write(str(p.n) + "\t" + str(p.b) + "\t" + str(p.rho) + "\t" + str(run_time) + "\t" + str(
        ga.memo_opt[ga.max_iter]) + "\t" + str(ga.memo_opt[ga.max_iter - 5]) + "\t" + str(
        ga.memo_opt[ga.max_iter - 10]) + "\n")
    f.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # n = 21
    # p = utils.generate_problem(n, 15, 1)
    # run3_1(p)
    # N = [6, 8, 10, 12, 14, 16, 18, 20]
    N = [10, 20, 30, 40, 50]
    # N = [100, 200, 400, 600, 800, 1000]
    B = [1, 10, 100, 1000]
    # B = [50, 70, 90, 110, 130]
    # B = [10, 100, 300, 500, 700, 900]
    RHO = [0.5, 1.0, 1.5, 2.0, 2.5]
    for n in N:
        for b in B:
            for rho in RHO:
                for i in range(REPEAT):
                    p = utils.generate_problem(n, b, rho, seed=i)
                    # proc1 = Process(target=run6, args=(p,))
                    proc2 = Process(target=run7, args=(p,))
                    proc3 = Process(target=run5, args=(p,))
                    # proc4 = Process(target=run8, args=(p,))
                    # proc5 = Process(target=run13, args=(p,))
                    # proc6 = Process(target=run14, args=(p,))
                    # proc1.start()
                    proc2.start()
                    proc3.start()
                    # proc4.start()
                    # proc5.start()
                    # proc6.start()
                    # proc1.join()
                    proc2.join()
                    proc3.join()
                    # proc4.join()
                    # proc5.join()
                    # proc6.join()
