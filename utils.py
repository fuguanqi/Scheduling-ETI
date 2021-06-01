import random

BIG_NUMBER = 99999999


class Block:
    def __init__(self, jobs, start_time, end_time):
        self.jobs = jobs
        self.start_time = start_time
        self.end_time = end_time


class Problem:
    def __init__(self, n, a, b, due_dates, processing_times, earliness_penalties, tardiness_penalties):
        self.n = n
        self.a = a
        self.b = b
        self.due_dates = due_dates
        self.processing_times = processing_times
        self.earliness_penalties = earliness_penalties
        self.tardiness_penalties = tardiness_penalties


class Solution:
    def __init__(self, block_lasts, end_times, eti_penalty, b_ratio):
        self.block_lasts = block_lasts
        self.end_times = end_times
        self.eti_penalty = eti_penalty
        self.b_ratio = b_ratio


def generate_problem(n=5, b=1, seed=101):
    random.seed(seed)
    # a=0
    a = round(random.random() * 2, 4)
    # b=0
    due_dates = list()
    processing_times = list()
    earliness_penalties = list()
    tardiness_penalties = list()

    for i in range(n):
        due_dates.append(round(100 * n / 5 + random.random() * 30 * n, 4))
        processing_times.append(round(random.random() * 20, 4))
        earliness_penalties.append(round(random.random() * 16, 4))
        tardiness_penalties.append(round(random.random() * 24, 4))

    # # The variable part of idleness penalty is absorbed by the first job and the last job.
    # earliness_penalties[0] = earliness_penalties[0] + a
    # tardiness_penalties[0] = tardiness_penalties[0] - a
    # earliness_penalties[n - 1] = earliness_penalties[n - 1] - a
    # tardiness_penalties[n - 1] = tardiness_penalties[n - 1] + a

    print("**************** Genrate Problem ****************")
    print("        ******** The jobs are:********        ")
    for i in range(n):
        print("job ", i, ", due at:", due_dates[i], ", processed for :", processing_times[i], ", early penalty:",
              earliness_penalties[i], ",tardi penalty:", tardiness_penalties[i])
    print("a= ", a)
    print("b= ", b)
    print("**************** Genrate Problem Finishied ****************")
    return Problem(n, a, b, due_dates, processing_times, earliness_penalties, tardiness_penalties)

# def (problem):
#     # Ordering + Timing solved by CPLEX
#     # The variable part of idleness penalty is absorbed by the first job and the last job.
#     p=copy.deepcopy(problem)
#     start = time.process_time()
#     opt_model = test.test_Permutation(p)
#     end = time.process_time()
#     run_time = end - start
#     print("*********  CPLEX runtime:   *********")
#     print(run_time)
