import copy
import blockTiming as bt
import timing as timing
import random

import utils

POP_SIZE = 50
MAX_ITER = 50
CROSS_RATE = 0.7
MUT_RATE = 0.20


class GA_BASIC():
    def __init__(self, problem, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
        self.n = problem.n
        self.problem = problem
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.mut_rate = mut_rate
        self.cross_rate = cross_rate
        self.pop = []
        self.cross_count = 0
        self.mutation_count = 0
        self.memo_FV = {}
        self.opt_chromo = []
        self.memo_opt = []
        self.iter = 0

    def generate_Initial(self):
        initial = []
        chromo = range(self.n)

        # number of chromosomes by due dates in the initial population
        nCBD = 3
        due = self.problem.due_dates
        due, chromo = zip(*sorted(zip(due, chromo)))
        chromo = list(chromo)
        tempChromo = chromo.copy()
        self.opt_chromo = tempChromo
        self.memo_opt.append(self.cal_Fitness_Value(tempChromo))
        for i in range(nCBD):
            initial.append(tempChromo)

        for i in range(self.pop_size - nCBD):
            random.shuffle(chromo)
            tempChromo = chromo.copy()
            initial.append(tempChromo)
        # print("**************** initial pop ****************")
        # for j in range(self.pop_size):
        #     print(initial[j])
        # print("**************** initial pop ****************")
        return initial

    def cal_Fitness_Value(self, chromo):
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
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
        # if self.iter == 0:
        #     print(eti_penalty)
        real_obj, b_ratio = self.cal_Real_Objective(chromo, block_lasts, end_times, self.problem)
        self.memo_FV[tuple(chromo)] = utils.Solution(block_lasts, end_times, real_obj, b_ratio)
        return real_obj

    def cross(self, parent1, parent2):
        if self.n < 2:
            return parent1, parent2
        index1 = random.randint(0, self.n - 1)
        index2 = random.randint(index1, self.n - 1)
        # temp1 = parent1[index1:index2]  # 交叉的基因片段
        temp2 = parent2[index1:index2]  # 交叉的基因片段
        child1 = []
        # child2 = []
        i = 0
        for g in parent1:
            if i == index1:
                child1 = child1 + temp2  # 插入基因片段
                i += 1
            if g not in temp2:
                child1.append(g)
                i += 1
        # i = 0
        # for g in parent2:
        #     if i == index1:
        #         child2 = child2 + temp1  # 插入基因片段
        #     if g not in temp1:
        #         child2.append(g)
        #         i += 1
        self.cross_count += 1
        # print("*************** cross **************")
        # print(index1, index2)
        ## print("temp 1", [a for a in temp1])
        # print("temp 2", [a for a in temp2])
        # print("parent 1", [a for a in parent1])
        # print("parent 2", [a for a in parent2])
        # print("child 1", [a for a in child1])
        ## print("child 2", [a for a in child2])
        return child1

    def mutation(self, chromo):
        index1 = random.randint(0, self.n - 1)
        index2 = random.randint(0, self.n - 1)
        while (index1 == index2):
            index2 = random.randint(0, self.n - 1)
        new_chromo = chromo[:]
        new_chromo[index1], new_chromo[index2] = new_chromo[index2], new_chromo[index1]
        self.mutation_count += 1
        return new_chromo

    def get_One_child(self):
        index1 = random.randint(0, self.pop_size - 1)
        index2 = random.randint(0, self.pop_size - 1)
        while index1 == index2:
            index2 = random.randint(0, self.pop_size - 1)
        chromo1 = self.pop[index1]
        chromo2 = self.pop[index2]
        penalty1 = self.cal_Fitness_Value(chromo1)
        penalty2 = self.cal_Fitness_Value(chromo2)
        if penalty1 > penalty2:
            better_penalty = penalty2
            new_chromo = chromo2[:]
        else:
            better_penalty = penalty1
            new_chromo = chromo1[:]
        if (better_penalty <= self.memo_opt[self.iter]):
            self.memo_opt[self.iter] = better_penalty
            self.opt_chromo = new_chromo

        # cross
        r = random.random()
        if r < self.cross_rate:
            temp_chromo = self.pop[random.randint(0, self.pop_size - 1)]
            new_chromo = self.cross(new_chromo, temp_chromo)
            # print("iter", self.iter)
            # print("mutation count", self.mutation_count)
            # print("cross_count", self.cross_count)
            # print([a for a in new_chromo])

        # mutation
        r = random.random()
        if r < self.mut_rate:
            new_chromo = self.mutation(new_chromo)

        return new_chromo

    def generate_Next_Pop(self):
        new_pop = []
        # print("opt choromo",[a for a in self.opt_chromo])
        new_pop.append(self.opt_chromo)
        while len(new_pop) < self.pop_size:
            new_pop.append(self.get_One_child())
        self.iter += 1
        self.memo_opt.append(self.memo_opt[-1])
        return new_pop

    def cal_Real_Objective(self, chromo, block_lasts, end_times, problem):
        obj = 0
        idle_penalty = 0
        for i in range(problem.n):
            if end_times[i] > problem.due_dates[chromo[i]]:
                obj += (end_times[i] - problem.due_dates[chromo[i]]) * problem.tardiness_penalties[chromo[i]]
            if end_times[i] < problem.due_dates[chromo[i]]:
                obj += (problem.due_dates[chromo[i]] - end_times[i]) * problem.earliness_penalties[chromo[i]]
            if i < problem.n - 1 and i in block_lasts:
                obj += (end_times[i + 1] - end_times[i] - problem.processing_times[
                    chromo[i + 1]]) * problem.a + problem.b
                idle_penalty += problem.b
        return obj, idle_penalty / obj

    def run(self):
        self.pop = self.generate_Initial()
        for i in range(self.max_iter):
            new_pop = self.generate_Next_Pop()
            self.pop = new_pop
        return


class GA_Faster_DP():
    def __init__(self, problem, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
        self.n = problem.n
        self.problem = problem
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.mut_rate = mut_rate
        self.cross_rate = cross_rate
        self.pop = []
        self.cross_count = 0
        self.mutation_count = 0
        self.memo_FV = {}
        self.opt_chromo = []
        self.memo_opt = []
        self.iter = 0

    def generate_Initial(self):
        initial = []
        chromo = range(self.n)

        # number of chromosomes by due dates in the initial population
        nCBD = 3
        due = self.problem.due_dates
        due, chromo = zip(*sorted(zip(due, chromo)))
        chromo = list(chromo)
        tempChromo = chromo.copy()
        self.opt_chromo = tempChromo
        self.memo_opt.append(self.cal_Fitness_Value(tempChromo))
        for i in range(nCBD):
            initial.append(tempChromo)

        for i in range(self.pop_size - nCBD):
            random.shuffle(chromo)
            tempChromo = chromo.copy()
            initial.append(tempChromo)
        # print("**************** initial pop ****************")
        # for j in range(self.pop_size):
        #     print(initial[j])
        # print("**************** initial pop ****************")
        return initial

    def cal_Fitness_Value(self, chromo):
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
        p = copy.deepcopy(self.problem)
        p.earliness_penalties[chromo[0]] = p.earliness_penalties[chromo[0]] + p.a
        p.tardiness_penalties[chromo[0]] = p.tardiness_penalties[chromo[0]] - p.a
        p.earliness_penalties[chromo[self.n - 1]] = p.earliness_penalties[chromo[self.n - 1]] - p.a
        p.tardiness_penalties[chromo[self.n - 1]] = p.tardiness_penalties[chromo[self.n - 1]] + p.a

        # memos
        memo_BT = bt.init_BT_memo(chromo, p.due_dates, p.processing_times)
        memo_ET = timing.init_ET_memo(chromo, p.due_dates, p.processing_times)
        memo_ETI = timing.init_ETI_memo_bounded(chromo, p.due_dates)
        block_lasts, end_times, eti_penalty = timing.opt_ETI_Bounded(memo_BT, memo_ET, memo_ETI, utils.BIG_NUMBER,
                                                                     self.n - 1, chromo, 0, self.n - 1, p)
        # if self.iter == 0:
        #     print(eti_penalty)
        real_obj, b_ratio = self.cal_Real_Objective(chromo, block_lasts, end_times, self.problem)
        self.memo_FV[tuple(chromo)] = utils.Solution(block_lasts, end_times, real_obj, b_ratio)
        return real_obj

    def cross(self, parent1, parent2):
        if self.n < 2:
            return parent1, parent2
        index1 = random.randint(0, self.n - 1)
        index2 = random.randint(index1, self.n - 1)
        # temp1 = parent1[index1:index2]  # 交叉的基因片段
        temp2 = parent2[index1:index2]  # 交叉的基因片段
        child1 = []
        # child2 = []
        i = 0
        for g in parent1:
            if i == index1:
                child1 = child1 + temp2  # 插入基因片段
                i += 1
            if g not in temp2:
                child1.append(g)
                i += 1
        # i = 0
        # for g in parent2:
        #     if i == index1:
        #         child2 = child2 + temp1  # 插入基因片段
        #     if g not in temp1:
        #         child2.append(g)
        #         i += 1
        self.cross_count += 1
        # print("*************** cross **************")
        # print(index1, index2)
        ## print("temp 1", [a for a in temp1])
        # print("temp 2", [a for a in temp2])
        # print("parent 1", [a for a in parent1])
        # print("parent 2", [a for a in parent2])
        # print("child 1", [a for a in child1])
        ## print("child 2", [a for a in child2])
        return child1

    def mutation(self, chromo):
        index1 = random.randint(0, self.n - 1)
        index2 = random.randint(0, self.n - 1)
        while (index1 == index2):
            index2 = random.randint(0, self.n - 1)
        new_chromo = chromo[:]
        new_chromo[index1], new_chromo[index2] = new_chromo[index2], new_chromo[index1]
        self.mutation_count += 1
        return new_chromo

    def get_One_child(self):
        index1 = random.randint(0, self.pop_size - 1)
        index2 = random.randint(0, self.pop_size - 1)
        while index1 == index2:
            index2 = random.randint(0, self.pop_size - 1)
        chromo1 = self.pop[index1]
        chromo2 = self.pop[index2]
        penalty1 = self.cal_Fitness_Value(chromo1)
        penalty2 = self.cal_Fitness_Value(chromo2)
        if penalty1 > penalty2:
            better_penalty = penalty2
            new_chromo = chromo2[:]
        else:
            better_penalty = penalty1
            new_chromo = chromo1[:]
        if (better_penalty <= self.memo_opt[self.iter]):
            self.memo_opt[self.iter] = better_penalty
            self.opt_chromo = new_chromo

        # cross
        r = random.random()
        if r < self.cross_rate:
            temp_chromo = self.pop[random.randint(0, self.pop_size - 1)]
            new_chromo = self.cross(new_chromo, temp_chromo)
            # print("iter", self.iter)
            # print("mutation count", self.mutation_count)
            # print("cross_count", self.cross_count)
            # print([a for a in new_chromo])

        # mutation
        r = random.random()
        if r < self.mut_rate:
            new_chromo = self.mutation(new_chromo)

        return new_chromo

    def generate_Next_Pop(self):
        new_pop = []
        # print("opt choromo",[a for a in self.opt_chromo])
        new_pop.append(self.opt_chromo)
        while len(new_pop) < self.pop_size:
            new_pop.append(self.get_One_child())
        self.iter += 1
        self.memo_opt.append(self.memo_opt[-1])
        return new_pop

    def cal_Real_Objective(self, chromo, block_lasts, end_times, problem):
        obj = 0
        idle_penalty = 0
        for i in range(problem.n):
            if end_times[i] > problem.due_dates[chromo[i]]:
                obj += (end_times[i] - problem.due_dates[chromo[i]]) * problem.tardiness_penalties[chromo[i]]
            if end_times[i] < problem.due_dates[chromo[i]]:
                obj += (problem.due_dates[chromo[i]] - end_times[i]) * problem.earliness_penalties[chromo[i]]
            if i < problem.n - 1 and i in block_lasts:
                obj += (end_times[i + 1] - end_times[i] - problem.processing_times[
                    chromo[i + 1]]) * problem.a + problem.b
                idle_penalty += problem.b
        return obj, idle_penalty / obj

    def run(self):
        self.pop = self.generate_Initial()
        for i in range(self.max_iter):
            new_pop = self.generate_Next_Pop()
            self.pop = new_pop
        return


class GA_Faster_Select():
    def __init__(self, problem, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
        self.n = problem.n
        self.problem = problem
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.mut_rate = mut_rate
        self.cross_rate = cross_rate
        self.pop = []
        self.cross_count = 0
        self.mutation_count = 0
        self.memo_FV = {}
        self.opt_chromo = []
        self.memo_opt = []
        self.iter = 0

    def generate_Initial(self):
        initial = []
        chromo = range(self.n)

        # number of chromosomes by due dates in the initial population
        nCBD = 3
        due = self.problem.due_dates
        due, chromo = zip(*sorted(zip(due, chromo)))
        chromo = list(chromo)
        tempChromo = chromo.copy()
        self.opt_chromo = tempChromo
        self.memo_opt.append(self.cal_Fitness_Value(tempChromo))
        for i in range(nCBD):
            initial.append(tempChromo)

        for i in range(self.pop_size - nCBD):
            random.shuffle(chromo)
            tempChromo = chromo.copy()
            initial.append(tempChromo)
        # print("**************** initial pop ****************")
        # for j in range(self.pop_size):
        #     print(initial[j])
        # print("**************** initial pop ****************")
        return initial

    def cal_Fitness_Value(self, chromo):
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
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
        # if self.iter == 0:
        #     print(eti_penalty)
        real_obj, b_ratio = self.cal_Real_Objective(chromo, block_lasts, end_times, self.problem)
        self.memo_FV[tuple(chromo)] = utils.Solution(block_lasts, end_times, real_obj, b_ratio)
        return real_obj

    def cross(self, parent1, parent2):
        if self.n < 2:
            return parent1, parent2
        index1 = random.randint(0, self.n - 1)
        index2 = random.randint(index1, self.n - 1)
        # temp1 = parent1[index1:index2]  # 交叉的基因片段
        temp2 = parent2[index1:index2]  # 交叉的基因片段
        child1 = []
        # child2 = []
        i = 0
        for g in parent1:
            if i == index1:
                child1 = child1 + temp2  # 插入基因片段
                i += 1
            if g not in temp2:
                child1.append(g)
                i += 1
        # i = 0
        # for g in parent2:
        #     if i == index1:
        #         child2 = child2 + temp1  # 插入基因片段
        #     if g not in temp1:
        #         child2.append(g)
        #         i += 1
        self.cross_count += 1
        # print("*************** cross **************")
        # print(index1, index2)
        ## print("temp 1", [a for a in temp1])
        # print("temp 2", [a for a in temp2])
        # print("parent 1", [a for a in parent1])
        # print("parent 2", [a for a in parent2])
        # print("child 1", [a for a in child1])
        ## print("child 2", [a for a in child2])
        return child1

    def mutation(self, chromo):
        index1 = random.randint(0, self.n - 1)
        index2 = random.randint(0, self.n - 1)
        while (index1 == index2):
            index2 = random.randint(0, self.n - 1)
        new_chromo = chromo[:]
        new_chromo[index1], new_chromo[index2] = new_chromo[index2], new_chromo[index1]
        self.mutation_count += 1
        return new_chromo

    def get_One_child(self):
        index1 = random.randint(0, self.pop_size - 1)
        index2 = random.randint(0, self.pop_size - 1)
        while index1 == index2:
            index2 = random.randint(0, self.pop_size - 1)
        chromo1 = self.pop[index1]
        chromo2 = self.pop[index2]
        et_penalty1 = timing.opt_ET_no_memo(chromo1, 0, self.n - 1, self.problem)
        et_penalty2 = timing.opt_ET_no_memo(chromo2, 0, self.n - 1, self.problem)
        if et_penalty1 > et_penalty2:
            penalty2 = self.cal_Fitness_Value(chromo2)
            if et_penalty1 > penalty2:
                better_penalty = penalty2
                new_chromo = chromo2[:]
            else:
                penalty1 = self.cal_Fitness_Value(chromo1)
                if penalty1 > penalty2:
                    better_penalty = penalty2
                    new_chromo = chromo2[:]
                else:
                    better_penalty = penalty1
                    new_chromo = chromo1[:]
        else:
            penalty1 = self.cal_Fitness_Value(chromo1)
            if et_penalty2 > penalty1:
                better_penalty = penalty1
                new_chromo = chromo1[:]
            else:
                penalty2 = self.cal_Fitness_Value(chromo2)
                if penalty1 > penalty2:
                    better_penalty = penalty2
                    new_chromo = chromo2[:]
                else:
                    better_penalty = penalty1
                    new_chromo = chromo1[:]

        if (better_penalty <= self.memo_opt[self.iter]):
            self.memo_opt[self.iter] = better_penalty
            self.opt_chromo = new_chromo

        # cross
        r = random.random()
        if r < self.cross_rate:
            temp_chromo = self.pop[random.randint(0, self.pop_size - 1)]
            new_chromo = self.cross(new_chromo, temp_chromo)
            # print("iter", self.iter)
            # print("mutation count", self.mutation_count)
            # print("cross_count", self.cross_count)
            # print([a for a in new_chromo])

        # mutation
        r = random.random()
        if r < self.mut_rate:
            new_chromo = self.mutation(new_chromo)

        return new_chromo

    def generate_Next_Pop(self):
        new_pop = []
        # print("opt choromo",[a for a in self.opt_chromo])
        new_pop.append(self.opt_chromo)
        while len(new_pop) < self.pop_size:
            new_pop.append(self.get_One_child())
        self.iter += 1
        self.memo_opt.append(self.memo_opt[-1])
        return new_pop

    def cal_Real_Objective(self, chromo, block_lasts, end_times, problem):
        obj = 0
        idle_penalty = 0
        for i in range(problem.n):
            if end_times[i] > problem.due_dates[chromo[i]]:
                obj += (end_times[i] - problem.due_dates[chromo[i]]) * problem.tardiness_penalties[chromo[i]]
            if end_times[i] < problem.due_dates[chromo[i]]:
                obj += (problem.due_dates[chromo[i]] - end_times[i]) * problem.earliness_penalties[chromo[i]]
            if i < problem.n - 1 and i in block_lasts:
                obj += (end_times[i + 1] - end_times[i] - problem.processing_times[
                    chromo[i + 1]]) * problem.a + problem.b
                idle_penalty += problem.b
        return obj, idle_penalty / obj

    def run(self):
        self.pop = self.generate_Initial()
        for i in range(self.max_iter):
            new_pop = self.generate_Next_Pop()
            self.pop = new_pop
        return


class GA_Faster_Both():
    def __init__(self, problem, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
        self.n = problem.n
        self.problem = problem
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.mut_rate = mut_rate
        self.cross_rate = cross_rate
        self.pop = []
        self.cross_count = 0
        self.mutation_count = 0
        self.memo_FV = {}
        self.opt_chromo = []
        self.memo_opt = []
        self.iter = 0

    def generate_Initial(self):
        initial = []
        chromo = range(self.n)

        # number of chromosomes by due dates in the initial population
        nCBD = 3
        due = self.problem.due_dates
        due, chromo = zip(*sorted(zip(due, chromo)))
        chromo = list(chromo)
        tempChromo = chromo.copy()
        self.opt_chromo = tempChromo
        self.memo_opt.append(self.cal_Fitness_Value(tempChromo))
        for i in range(nCBD):  # 初始pop中，以due的顺序作为加工顺序的染色体数量
            initial.append(tempChromo)

        for i in range(self.pop_size - nCBD):
            random.shuffle(chromo)
            tempChromo = chromo.copy()
            initial.append(tempChromo)
        # print("**************** initial pop ****************")
        # for j in range(self.pop_size):
        #     print(initial[j])
        # print("**************** initial pop ****************")
        return initial

    def cal_Fitness_Value(self, chromo):
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
        p = copy.deepcopy(self.problem)
        p.earliness_penalties[chromo[0]] = p.earliness_penalties[chromo[0]] + p.a
        p.tardiness_penalties[chromo[0]] = p.tardiness_penalties[chromo[0]] - p.a
        p.earliness_penalties[chromo[self.n - 1]] = p.earliness_penalties[chromo[self.n - 1]] - p.a
        p.tardiness_penalties[chromo[self.n - 1]] = p.tardiness_penalties[chromo[self.n - 1]] + p.a

        # memos
        memo_BT = bt.init_BT_memo(chromo, p.due_dates, p.processing_times)
        memo_ET = timing.init_ET_memo(chromo, p.due_dates, p.processing_times)
        memo_ETI = timing.init_ETI_memo_bounded(chromo, p.due_dates)
        block_lasts, end_times, eti_penalty = timing.opt_ETI_Bounded(memo_BT, memo_ET, memo_ETI, utils.BIG_NUMBER,
                                                                     self.n - 1, chromo, 0, self.n - 1, p)
        # if self.iter == 0:
        #     print(eti_penalty)
        real_obj, b_ratio = self.cal_Real_Objective(chromo, block_lasts, end_times, self.problem)
        self.memo_FV[tuple(chromo)] = utils.Solution(block_lasts, end_times, real_obj, b_ratio)
        return real_obj

    def cross(self, parent1, parent2):
        if self.n < 2:
            return parent1, parent2
        index1 = random.randint(0, self.n - 1)
        index2 = random.randint(index1, self.n - 1)
        # temp1 = parent1[index1:index2]  # 交叉的基因片段
        temp2 = parent2[index1:index2]  # 交叉的基因片段
        child1 = []
        # child2 = []
        i = 0
        for g in parent1:
            if i == index1:
                child1 = child1 + temp2  # 插入基因片段
                i += 1
            if g not in temp2:
                child1.append(g)
                i += 1
        # i = 0
        # for g in parent2:
        #     if i == index1:
        #         child2 = child2 + temp1  # 插入基因片段
        #     if g not in temp1:
        #         child2.append(g)
        #         i += 1
        self.cross_count += 1
        # print("*************** cross **************")
        # print(index1, index2)
        ## print("temp 1", [a for a in temp1])
        # print("temp 2", [a for a in temp2])
        # print("parent 1", [a for a in parent1])
        # print("parent 2", [a for a in parent2])
        # print("child 1", [a for a in child1])
        ## print("child 2", [a for a in child2])
        return child1

    def mutation(self, chromo):
        index1 = random.randint(0, self.n - 1)
        index2 = random.randint(0, self.n - 1)
        while (index1 == index2):
            index2 = random.randint(0, self.n - 1)
        new_chromo = chromo[:]
        new_chromo[index1], new_chromo[index2] = new_chromo[index2], new_chromo[index1]
        self.mutation_count += 1
        return new_chromo

    def get_One_child(self):
        index1 = random.randint(0, self.pop_size - 1)
        index2 = random.randint(0, self.pop_size - 1)
        while index1 == index2:
            index2 = random.randint(0, self.pop_size - 1)
        chromo1 = self.pop[index1]
        chromo2 = self.pop[index2]
        et_penalty1 = timing.opt_ET_no_memo(chromo1, 0, self.n - 1, self.problem)
        et_penalty2 = timing.opt_ET_no_memo(chromo2, 0, self.n - 1, self.problem)
        if et_penalty1 > et_penalty2:
            penalty2 = self.cal_Fitness_Value(chromo2)
            if et_penalty1 > penalty2:
                better_penalty = penalty2
                new_chromo = chromo2[:]
            else:
                penalty1 = self.cal_Fitness_Value(chromo1)
                if penalty1 > penalty2:
                    better_penalty = penalty2
                    new_chromo = chromo2[:]
                else:
                    better_penalty = penalty1
                    new_chromo = chromo1[:]
        else:
            penalty1 = self.cal_Fitness_Value(chromo1)
            if et_penalty2 > penalty1:
                better_penalty = penalty1
                new_chromo = chromo1[:]
            else:
                penalty2 = self.cal_Fitness_Value(chromo2)
                if penalty1 > penalty2:
                    better_penalty = penalty2
                    new_chromo = chromo2[:]
                else:
                    better_penalty = penalty1
                    new_chromo = chromo1[:]

        if (better_penalty <= self.memo_opt[self.iter]):
            self.memo_opt[self.iter] = better_penalty
            self.opt_chromo = new_chromo

        # cross
        r = random.random()
        if r < self.cross_rate:
            temp_chromo = self.pop[random.randint(0, self.pop_size - 1)]
            new_chromo = self.cross(new_chromo, temp_chromo)
            # print("iter", self.iter)
            # print("mutation count", self.mutation_count)
            # print("cross_count", self.cross_count)
            # print([a for a in new_chromo])

        # mutation
        r = random.random()
        if r < self.mut_rate:
            new_chromo = self.mutation(new_chromo)

        return new_chromo

    def generate_Next_Pop(self):
        new_pop = []
        # print("opt choromo",[a for a in self.opt_chromo])
        new_pop.append(self.opt_chromo)
        while len(new_pop) < self.pop_size:
            new_pop.append(self.get_One_child())
        self.iter += 1
        self.memo_opt.append(self.memo_opt[-1])
        return new_pop

    def cal_Real_Objective(self, chromo, block_lasts, end_times, problem):
        obj = 0
        idle_penalty = 0
        for i in range(problem.n):
            if end_times[i] > problem.due_dates[chromo[i]]:
                obj += (end_times[i] - problem.due_dates[chromo[i]]) * problem.tardiness_penalties[chromo[i]]
            if end_times[i] < problem.due_dates[chromo[i]]:
                obj += (problem.due_dates[chromo[i]] - end_times[i]) * problem.earliness_penalties[chromo[i]]
            if i < problem.n - 1 and i in block_lasts:
                obj += (end_times[i + 1] - end_times[i] - problem.processing_times[
                    chromo[i + 1]]) * problem.a + problem.b
                idle_penalty += problem.b
        return obj, idle_penalty / obj

    def run(self):
        self.pop = self.generate_Initial()
        for i in range(self.max_iter):
            new_pop = self.generate_Next_Pop()
            self.pop = new_pop
        return
