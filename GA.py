import copy
import blockTiming as bt
import timing as timing
import numpy as np
import random

import utils


class GA_BASIC():
    def __init__(self, problem, pop_size=50, max_iter=200, cross_rate=0.2, mut_rate=0.001):
        self.n = problem.n
        self.problem = problem
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.mut_rate = mut_rate
        self.cross_rate = cross_rate
        self.pop = []
        self.cross_count=0

    def generate_Initial(self):
        initial = []
        chromo = range(self.n)

        # number of chromosomes by due dates in the initial population
        nCBD = 3
        due = self.problem.due_dates
        due, chromo = zip(*sorted(zip(due, chromo)))
        chromo = list(chromo)
        tempChromo = chromo.copy()
        for i in range(nCBD):
            initial.append(tempChromo)

        for i in range(self.pop_size - nCBD):
            random.shuffle(chromo)
            tempChromo = chromo.copy()
            initial.append(tempChromo)
        # for j in range(self.pop_size):
        #     print(initial[j])
        return initial

    def cal_Fitness_Value(self, chromo):
        p = copy.deepcopy(self.problem)
        p.earliness_penalties[chromo[0]] = p.earliness_penalties[chromo[0]] + p.a
        p.tardiness_penalties[chromo[0]] = p.tardiness_penalties[chromo[0]] - p.a
        p.earliness_penalties[chromo[self.n - 1]] = p.earliness_penalties[chromo[self.n - 1]] - p.a
        p.tardiness_penalties[chromo[self.n - 1]] = p.tardiness_penalties[chromo[self.n - 1]] + p.a

        # memos
        memo_BT = bt.init_BT_memo(chromo, p.due_dates, p.processing_times)
        memo_ET = timing.init_ET_memo(chromo, p.due_dates, p.processing_times)
        memo_ETI = timing.init_ETI_memo(chromo, p.due_dates)
        block_lasts, end_times, eti_penalty = timing.opt_ETI(memo_BT, memo_ET, memo_ETI, utils.BIG_NUMBER, chromo, 0,
                                                             self.n - 1, p)
        return block_lasts, end_times, eti_penalty

    def cross(self, parent1, parent2):
        if self.n < 2:
            return parent1, parent2
        index1 = random.randint(0, self.n - 1)
        index2 = random.randint(index1 + 1, self.n)
        temp1 = parent1[index1:index2]  # 交叉的基因片段
        temp2 = parent2[index1:index2]  # 交叉的基因片段
        child1 = []
        child2 = []
        i = 0
        for g in parent1:
            if i == index1:
                child1 = child1 + temp2  # 插入基因片段
            if g not in temp2:
                child1.append(g)
                i += 1
        i=0
        for g in parent2:
            if i == index1:
                child2 = child2 + temp1  # 插入基因片段
            if g not in temp1:
                child2.append(g)
                i += 1
        self.cross_count += 1
        # print("*************** cross **************")
        # print(index1,index2)
        # print("temp 1", [a for a in temp1])
        # print("temp 2", [a for a in temp2])
        # print("parent 1",[a for a in parent1])
        # print("parent 2",[a for a in parent2])
        # print("child 1", [a for a in child1])
        # print("child 2", [a for a in child2])
        return child1, child2

    def mutation(self, chromo):
