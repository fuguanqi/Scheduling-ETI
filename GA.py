import copy
import blockTiming as bt
import random
import ET_opt as et
import My_DP as dp
import My_DP_Bounded as dpb
import utils
from Sourd import Sourd

POP_SIZE = 70
MAX_ITER = 100
CROSS_RATE = 0.9
MUT_RATE = 0.1
NUM_ELITE = 8
EVAL_BUGGET = 3000


class Generation():
    def __init__(self):
        self.pop = []
        self.FV = []
        self.elite = []
        self.best = 0
        self.worst = 0
        self.worst_elite = 0


class GA_Bound_A():
    def __init__(self, problem, seed=0, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
        self.n = problem.n
        self.problem = problem
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.mut_rate = mut_rate
        self.cross_rate = cross_rate
        self.cross_count = 0
        self.mutation_count = 0
        self.memo_FV = {}
        self.memo_opt = []
        self.budget_gen = []
        self.chromo_count = 0
        self.eval_count = 0
        random.seed(seed)

    def generate_Initial(self):
        gen = Generation()
        chromo = range(self.n)

        # number of chromosomes by due dates in the initial population
        nCBD = 1
        due = self.problem.due_dates
        due, chromo = zip(*sorted(zip(due, chromo)))
        chromo = list(chromo)
        CBD = chromo
        for i in range(nCBD):
            CBD = list(CBD)
            self.insert_chromo(CBD, gen)

        # number of chromosomes by expected start times in the initial population
        nCES = 1
        chromo = list(range(self.n))
        due = self.problem.due_dates
        process = self.problem.processing_times
        expected_starts = []
        for j in range(len(due)):
            expected_starts.append(due[j] - process[j])
        expected_starts, chromo = zip(*sorted(zip(expected_starts, chromo)))
        chromo = list(chromo)
        CES = chromo
        for i in range(nCES):
            CES = list(CES)
            self.insert_chromo(CES, gen)

        for i in range(self.pop_size - nCBD - nCES):
            random.shuffle(chromo)
            tempChromo = chromo.copy()
            self.insert_chromo(tempChromo, gen)
        # print("**************** initial pop ****************")
        # for j in range(self.pop_size):
        #     print(initial[j])
        # print("**************** initial pop ****************")
        self.memo_opt.append(gen.FV[gen.best])
        return gen

    def insert_chromo(self, chromo, gen):
        gen.pop.append(chromo)
        fv = self.cal_Fitness_Value(chromo)
        gen.FV.append(fv)
        length = len(gen.pop)
        if fv < gen.FV[gen.best]:
            gen.best = length - 1
        if fv > gen.FV[gen.worst]:
            gen.worst = length - 1
        if length <= NUM_ELITE:
            gen.elite.append(length - 1)
            if length == NUM_ELITE:
                worst_elite_fv = 0
                for i in range(NUM_ELITE):
                    if gen.FV[gen.elite[i]] > worst_elite_fv:
                        gen.worst_elite = gen.elite[i]
                        worst_elite_fv = gen.FV[gen.elite[i]]
        else:
            if gen.FV[gen.worst_elite] > fv:
                worst_elite_fv = fv
                gen.elite[gen.elite.index(gen.worst_elite)] = length - 1
                gen.worst_elite = length - 1
                for i in range(NUM_ELITE):
                    if gen.FV[gen.elite[i]] > worst_elite_fv:
                        gen.worst_elite = gen.elite[i]
                        worst_elite_fv = gen.FV[gen.elite[i]]

    def cal_Fitness_Value(self, chromo):
        # self.chromo_count += 1
        # print("chromo count", self.chromo_count)
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
        p = copy.deepcopy(self.problem)
        p.earliness_penalties[chromo[0]] = p.earliness_penalties[chromo[0]] + p.a
        p.tardiness_penalties[chromo[0]] = p.tardiness_penalties[chromo[0]] - p.a
        p.earliness_penalties[chromo[self.n - 1]] = p.earliness_penalties[chromo[self.n - 1]] - p.a
        p.tardiness_penalties[chromo[self.n - 1]] = p.tardiness_penalties[chromo[self.n - 1]] + p.a

        # # memos
        # memo_BT = bt.init_BT_memo(chromo, p.due_dates, p.processing_times)
        # memo_ET = et.init_ET_memo(chromo, p.due_dates, p.processing_times)
        # et_global_solution = et.init_ET_global_solution(chromo, p)
        # memo_ETI = dp.init_ETI_memo(chromo)
        # block_lasts, end_times, eti_penalty = dpb.opt_ETI_Bounded(memo_BT, memo_ET, memo_ETI, et_global_solution,
        #                                                           self.n - 1, chromo, self.n - 1, p)
        sourd = Sourd(chromo, p)
        obj = sourd.run()
        # if self.iter == 0:
        #     print(eti_penalty)
        self.memo_FV[tuple(chromo)] = utils.Solution([0], [0], obj, 0)
        self.eval_count += 1
        if self.eval_count%100==0 or len(self.memo_opt)==100:
            self.budget_gen.append((self.eval_count,len(self.memo_opt)))
        return obj

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

        self.cross_count += 1

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

    def get_one_child(self, parent_gen):
        sum = 0
        for i in range(len(parent_gen.pop)):
            sum += 1 / parent_gen.FV[i]
        r = random.random()
        temp = 0
        select_index = -1
        for i in range(len(parent_gen.pop)):
            temp += 1 / parent_gen.FV[i]
            if temp / sum >= r:
                select_index = i
                break
        new_chromo = parent_gen.pop[select_index].copy()

        # cross
        r = random.random()
        if r < self.cross_rate:
            sum = 0
            for i in range(len(parent_gen.pop)):
                sum += 1 / parent_gen.FV[i]
            r2 = random.random()
            temp = 0
            si = -1
            for i in range(len(parent_gen.pop)):
                temp += 1 / parent_gen.FV[i]
                if temp / sum > r2:
                    si = i
                    break
            temp_chromo = parent_gen.pop[si]
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

    def generate_Next_Pop(self, parent_gen):
        child_gen = Generation()
        for i in range(NUM_ELITE):
            self.insert_chromo(parent_gen.pop[parent_gen.elite[i]], child_gen)
        while len(child_gen.pop) < self.pop_size and self.eval_count<EVAL_BUGGET:
            self.insert_chromo(self.get_one_child(parent_gen), child_gen)
        self.memo_opt.append(child_gen.FV[child_gen.best])
        return child_gen

    def run(self):
        parent_gen = self.generate_Initial()
        for i in range(self.max_iter):
            if self.eval_count < EVAL_BUGGET:
                child_gen = self.generate_Next_Pop(parent_gen)
                parent_gen = child_gen
            else:
                break
        return


class GA_BoundAB():
    def __init__(self, problem, seed=0, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
        self.n = problem.n
        self.problem = problem
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.mut_rate = mut_rate
        self.cross_rate = cross_rate
        self.cross_count = 0
        self.mutation_count = 0
        self.memo_FV = {}
        self.memo_opt = []
        self.budget_gen = []
        self.chromo_count = 0
        self.eval_count = 0
        self.search_count = 0
        random.seed(seed)

    def generate_Initial(self):

        gen = Generation()
        chromo = range(self.n)

        # number of chromosomes by due dates in the initial population
        nCBD = 1
        due = self.problem.due_dates
        due, chromo = zip(*sorted(zip(due, chromo)))
        chromo = list(chromo)
        CBD = chromo
        for i in range(nCBD):
            CBD = list(CBD)
            self.insert_chromo(CBD, gen)

        # number of chromosomes by expected start times in the initial population
        nCES = 1
        chromo = list(range(self.n))
        due = self.problem.due_dates
        process = self.problem.processing_times
        expected_starts = []
        for j in range(len(due)):
            expected_starts.append(due[j] - process[j])
        expected_starts, chromo = zip(*sorted(zip(expected_starts, chromo)))
        chromo = list(chromo)
        CES = chromo
        for i in range(nCES):
            CES = list(CES)
            self.insert_chromo(CES, gen)

        for i in range(self.pop_size - nCBD - nCES):
            random.shuffle(chromo)
            tempChromo = chromo.copy()
            self.insert_chromo(tempChromo, gen)
        # print("**************** initial pop ****************")
        # for j in range(self.pop_size):
        #     print(initial[j])
        # print("**************** initial pop ****************")
        self.memo_opt.append(gen.FV[gen.best])
        return gen

    def insert_chromo(self, chromo, gen):
        gen.pop.append(chromo)
        fv = self.cal_Fitness_Value(chromo)
        gen.FV.append(fv)
        length = len(gen.pop)
        if fv < gen.FV[gen.best]:
            gen.best = length - 1
        if fv > gen.FV[gen.worst]:
            gen.worst = length - 1
        if length <= NUM_ELITE:
            gen.elite.append(length - 1)
            if length == NUM_ELITE:
                worst_elite_fv = 0
                for i in range(NUM_ELITE):
                    if gen.FV[gen.elite[i]] > worst_elite_fv:
                        gen.worst_elite = gen.elite[i]
                        worst_elite_fv = gen.FV[gen.elite[i]]
        else:
            if gen.FV[gen.worst_elite] > fv:
                worst_elite_fv = fv
                gen.elite[gen.elite.index(gen.worst_elite)] = length - 1
                gen.worst_elite = length - 1
                for i in range(NUM_ELITE):
                    if gen.FV[gen.elite[i]] > worst_elite_fv:
                        gen.worst_elite = gen.elite[i]
                        worst_elite_fv = gen.FV[gen.elite[i]]

    def cal_Fitness_Value(self, chromo):
        # self.chromo_count += 1
        # print("chromo count", self.chromo_count)
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
        p = copy.deepcopy(self.problem)
        p.earliness_penalties[chromo[0]] = p.earliness_penalties[chromo[0]] + p.a
        p.tardiness_penalties[chromo[0]] = p.tardiness_penalties[chromo[0]] - p.a
        p.earliness_penalties[chromo[self.n - 1]] = p.earliness_penalties[chromo[self.n - 1]] - p.a
        p.tardiness_penalties[chromo[self.n - 1]] = p.tardiness_penalties[chromo[self.n - 1]] + p.a

        # # memos
        # memo_BT = bt.init_BT_memo(chromo, p.due_dates, p.processing_times)
        # memo_ET = et.init_ET_memo(chromo, p.due_dates, p.processing_times)
        # et_global_solution = et.init_ET_global_solution(chromo, p)
        # memo_ETI = dp.init_ETI_memo(chromo)
        # block_lasts, end_times, eti_penalty = dpb.opt_ETI_Bounded(memo_BT, memo_ET, memo_ETI, et_global_solution,
        #                                                           self.n - 1, chromo, self.n - 1, p)
        sourd = Sourd(chromo, p)
        obj = sourd.run()
        self.eval_count += 1
        if self.eval_count % 100 == 0 or len(self.memo_opt) == 100:
            self.budget_gen.append((self.eval_count, len(self.memo_opt)))
        # print("eval count", self.eval_count)
        # if self.iter == 0:
        #     print(eti_penalty)
        self.memo_FV[tuple(chromo)] = utils.Solution([0], [0], obj, 0)
        return obj

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

        self.cross_count += 1

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

    def get_one_child(self, parent_gen):
        self.search_count = 1
        while True:
            sum_ = 0
            worst_FV = parent_gen.FV[parent_gen.worst]
            for i in range(len(parent_gen.pop)):
                sum_ += 1 / parent_gen.FV[i]
            r = random.random()
            temp = 0
            select_index = -1
            for i in range(len(parent_gen.pop)):
                temp += 1 / parent_gen.FV[i]
                if temp / sum_ >= r:
                    select_index = i
                    break
            new_chromo = parent_gen.pop[select_index].copy()

            # cross
            r = random.random()
            if r < self.cross_rate:
                r2 = random.random()
                temp = 0
                si = -1
                for i in range(len(parent_gen.pop)):
                    temp += 1 / parent_gen.FV[i]
                    if temp / sum_ > r2:
                        si = i
                        break
                temp_chromo = parent_gen.pop[si]
                new_chromo = self.cross(new_chromo, temp_chromo)
                # print("iter", self.iter)
                # print("mutation count", self.mutation_count)
                # print("cross_count", self.cross_count)
                # print([a for a in new_chromo])

            # mutation
            r = random.random()
            if r < self.mut_rate:
                new_chromo = self.mutation(new_chromo)

            p = copy.deepcopy(self.problem)
            p.earliness_penalties[new_chromo[0]] = p.earliness_penalties[new_chromo[0]] + p.a
            p.tardiness_penalties[new_chromo[0]] = p.tardiness_penalties[new_chromo[0]] - p.a
            p.earliness_penalties[new_chromo[self.n - 1]] = p.earliness_penalties[new_chromo[self.n - 1]] - p.a
            p.tardiness_penalties[new_chromo[self.n - 1]] = p.tardiness_penalties[new_chromo[self.n - 1]] + p.a
            et_global_solution = et.init_ET_global_solution(new_chromo, p)
            et_penalty = sum(et_global_solution.block_objs)
            if et_penalty < worst_FV or self.search_count > 10:
                break
            self.search_count += 1
            print("search count", self.search_count)
        return new_chromo

    def generate_Next_Pop(self, parent_gen):
        child_gen = Generation()
        for i in range(NUM_ELITE):
            self.insert_chromo(parent_gen.pop[parent_gen.elite[i]], child_gen)
        while len(child_gen.pop) < self.pop_size and self.eval_count<EVAL_BUGGET:
            self.insert_chromo(self.get_one_child(parent_gen), child_gen)
        self.memo_opt.append(child_gen.FV[child_gen.best])
        return child_gen

    def run(self):
        parent_gen = self.generate_Initial()
        for i in range(self.max_iter):
            if self.eval_count<EVAL_BUGGET:
                child_gen = self.generate_Next_Pop(parent_gen)
                parent_gen = child_gen
            else:
                break
        return
