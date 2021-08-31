import copy
import blockTiming as bt
import random
import ET_opt as et
import My_DP as dp
import My_DP_Bounded as dpb
import utils

POP_SIZE = 50
MAX_ITER = 50
CROSS_RATE = 0.9
MUT_RATE = 0.2
NUM_ELITE = 8
random.seed(951112)


class Generation():
    def __init__(self):
        self.pop = []
        self.FV = []
        self.elite = []
        self.best = 0
        self.worst = 0


class GA_BASIC():
    def __init__(self, problem, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
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
        self.chromo_count = 0
        self.cal_count = 0


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
        self.chromo_count += 1
        print("chromo count", self.chromo_count)
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
        p = copy.deepcopy(self.problem)
        p.earliness_penalties[chromo[0]] = p.earliness_penalties[chromo[0]] + p.a
        p.tardiness_penalties[chromo[0]] = p.tardiness_penalties[chromo[0]] - p.a
        p.earliness_penalties[chromo[self.n - 1]] = p.earliness_penalties[chromo[self.n - 1]] - p.a
        p.tardiness_penalties[chromo[self.n - 1]] = p.tardiness_penalties[chromo[self.n - 1]] + p.a

        # memos
        memo_BT = bt.init_BT_memo(chromo, p.due_dates, p.processing_times)
        memo_ET = et.init_ET_memo(chromo, p.due_dates, p.processing_times)
        et_global_solution = et.init_ET_global_solution(chromo, p)
        memo_ETI = dp.init_ETI_memo(chromo)
        block_lasts, end_times, eti_penalty = dp.opt_ETI(memo_BT, memo_ET, memo_ETI, et_global_solution, chromo,
                                                         self.n - 1, p)
        # if self.iter == 0:
        #     print(eti_penalty)
        real_obj = self.cal_Real_Objective(chromo, block_lasts, end_times, self.problem)
        self.memo_FV[tuple(chromo)] = utils.Solution(block_lasts, end_times, real_obj, 0)
        self.cal_count += 1
        print("cal count", self.cal_count)
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
        worst_FV = parent_gen.FV[parent_gen.worst]
        for i in range(len(parent_gen.pop)):
            sum += worst_FV - parent_gen.FV[i]
        r = random.random()
        temp = 0
        select_index = -1
        for i in range(len(parent_gen.pop)):
            temp += worst_FV - parent_gen.FV[i]
            if temp / sum >= r:
                select_index = i
                break
        new_chromo = parent_gen.pop[select_index].copy()

        # cross
        r = random.random()
        if r < self.cross_rate:
            r2=random.random()
            temp = 0
            si = -1
            for i in range(len(parent_gen.pop)):
                temp += worst_FV - parent_gen.FV[i]
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
        while len(child_gen.pop) < self.pop_size:
            self.insert_chromo(self.get_one_child(parent_gen), child_gen)
        self.memo_opt.append(child_gen.FV[child_gen.best])
        return child_gen

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
        return obj

    def run(self):
        parent_gen = self.generate_Initial()
        for i in range(self.max_iter):
            child_gen = self.generate_Next_Pop(parent_gen)
            parent_gen = child_gen
        return


class GA_Bound_A():
    def __init__(self, problem, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
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
        self.chromo_count = 0
        self.cal_count = 0

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
        self.chromo_count += 1
        print("chromo count", self.chromo_count)
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
        p = copy.deepcopy(self.problem)
        p.earliness_penalties[chromo[0]] = p.earliness_penalties[chromo[0]] + p.a
        p.tardiness_penalties[chromo[0]] = p.tardiness_penalties[chromo[0]] - p.a
        p.earliness_penalties[chromo[self.n - 1]] = p.earliness_penalties[chromo[self.n - 1]] - p.a
        p.tardiness_penalties[chromo[self.n - 1]] = p.tardiness_penalties[chromo[self.n - 1]] + p.a

        # memos
        memo_BT = bt.init_BT_memo(chromo, p.due_dates, p.processing_times)
        memo_ET = et.init_ET_memo(chromo, p.due_dates, p.processing_times)
        et_global_solution = et.init_ET_global_solution(chromo, p)
        memo_ETI = dp.init_ETI_memo(chromo)
        block_lasts, end_times, eti_penalty = dpb.opt_ETI_Bounded(memo_BT, memo_ET, memo_ETI, et_global_solution,
                                                                  self.n - 1, chromo, self.n - 1, p)
        # if self.iter == 0:
        #     print(eti_penalty)
        real_obj = self.cal_Real_Objective(chromo, block_lasts, end_times, self.problem)
        self.memo_FV[tuple(chromo)] = utils.Solution(block_lasts, end_times, real_obj, 0)
        self.cal_count += 1
        print("cal count", self.cal_count)
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
        worst_FV = parent_gen.FV[parent_gen.worst]
        for i in range(len(parent_gen.pop)):
            sum += worst_FV - parent_gen.FV[i]
        r = random.random()
        temp = 0
        select_index = -1
        for i in range(len(parent_gen.pop)):
            temp += worst_FV - parent_gen.FV[i]
            if temp / sum >= r:
                select_index = i
                break
        new_chromo = parent_gen.pop[select_index].copy()

        # cross
        r = random.random()
        if r < self.cross_rate:
            sum = 0
            worst_FV = parent_gen.FV[parent_gen.worst]
            for i in range(len(parent_gen.pop)):
                sum += worst_FV - parent_gen.FV[i]
            r2 = random.random()
            temp = 0
            si = -1
            for i in range(len(parent_gen.pop)):
                temp += worst_FV - parent_gen.FV[i]
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
        while len(child_gen.pop) < self.pop_size:
            self.insert_chromo(self.get_one_child(parent_gen), child_gen)
        self.memo_opt.append(child_gen.FV[child_gen.best])
        return child_gen

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
        return obj

    def run(self):
        parent_gen = self.generate_Initial()
        for i in range(self.max_iter):
            child_gen = self.generate_Next_Pop(parent_gen)
            parent_gen = child_gen
        return


class GA_Bound_B():
    def __init__(self, problem, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
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
        self.chromo_count = 0
        self.cal_count = 0

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
        self.chromo_count += 1
        print("chromo count", self.chromo_count)
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
        p = copy.deepcopy(self.problem)
        p.earliness_penalties[chromo[0]] = p.earliness_penalties[chromo[0]] + p.a
        p.tardiness_penalties[chromo[0]] = p.tardiness_penalties[chromo[0]] - p.a
        p.earliness_penalties[chromo[self.n - 1]] = p.earliness_penalties[chromo[self.n - 1]] - p.a
        p.tardiness_penalties[chromo[self.n - 1]] = p.tardiness_penalties[chromo[self.n - 1]] + p.a

        # memos
        memo_BT = bt.init_BT_memo(chromo, p.due_dates, p.processing_times)
        memo_ET = et.init_ET_memo(chromo, p.due_dates, p.processing_times)
        et_global_solution = et.init_ET_global_solution(chromo, p)
        memo_ETI = dp.init_ETI_memo(chromo)
        block_lasts, end_times, eti_penalty = dp.opt_ETI(memo_BT, memo_ET, memo_ETI, et_global_solution, chromo,
                                                         self.n - 1, p)
        # if self.iter == 0:
        #     print(eti_penalty)
        real_obj = self.cal_Real_Objective(chromo, block_lasts, end_times, self.problem)
        self.memo_FV[tuple(chromo)] = utils.Solution(block_lasts, end_times, real_obj, 0)
        self.cal_count += 1
        print("cal count", self.cal_count)
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
        while True:
            sum_ = 0
            worst_FV = parent_gen.FV[parent_gen.worst]
            for i in range(len(parent_gen.pop)):
                sum_ += worst_FV - parent_gen.FV[i]
            r = random.random()
            temp = 0
            select_index = -1
            for i in range(len(parent_gen.pop)):
                temp += worst_FV - parent_gen.FV[i]
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
                    temp += worst_FV - parent_gen.FV[i]
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

            et_global_solution = et.init_ET_global_solution(new_chromo, self.problem)
            et_penalty = sum(et_global_solution.block_objs)
            if et_penalty< worst_FV:
                break
        return new_chromo

    def generate_Next_Pop(self, parent_gen):
        child_gen = Generation()
        for i in range(NUM_ELITE):
            self.insert_chromo(parent_gen.pop[parent_gen.elite[i]], child_gen)
        while len(child_gen.pop) < self.pop_size:
            self.insert_chromo(self.get_one_child(parent_gen), child_gen)
        self.memo_opt.append(child_gen.FV[child_gen.best])
        return child_gen

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
        return obj

    def run(self):
        parent_gen = self.generate_Initial()
        for i in range(self.max_iter):
            child_gen = self.generate_Next_Pop(parent_gen)
            parent_gen = child_gen
        return


class GA_BoundAB():
    def __init__(self, problem, pop_size=POP_SIZE, max_iter=MAX_ITER, cross_rate=CROSS_RATE, mut_rate=MUT_RATE):
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

    def generate_Initial(self):
        gen = Generation()
        chromo = range(self.n)

        # number of chromosomes by due dates in the initial population
        nCBD = 3
        due = self.problem.due_dates
        due, chromo = zip(*sorted(zip(due, chromo)))
        chromo = list(chromo)
        CBD = chromo
        for i in range(nCBD):
            CBD = list(CBD)
            self.insert_chromo(CBD, gen)

        # number of chromosomes by expected start times in the initial population
        nCES = 3
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
            self.insert_chromo(CBD, gen)

        for i in range(self.pop_size - nCBD - nCES):
            random.shuffle(chromo)
            tempChromo = chromo.copy()
            self.insert_chromo(tempChromo, gen)
        # print("**************** initial pop ****************")
        # for j in range(self.pop_size):
        #     print(initial[j])
        # print("**************** initial pop ****************")
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
        if self.memo_FV.get(tuple(chromo)):
            return self.memo_FV[(tuple(chromo))].eti_penalty
        p = copy.deepcopy(self.problem)
        p.earliness_penalties[chromo[0]] = p.earliness_penalties[chromo[0]] + p.a
        p.tardiness_penalties[chromo[0]] = p.tardiness_penalties[chromo[0]] - p.a
        p.earliness_penalties[chromo[self.n - 1]] = p.earliness_penalties[chromo[self.n - 1]] - p.a
        p.tardiness_penalties[chromo[self.n - 1]] = p.tardiness_penalties[chromo[self.n - 1]] + p.a

        # memos
        memo_BT = bt.init_BT_memo(chromo, p.due_dates, p.processing_times)
        memo_ET = et.init_ET_memo(chromo, p.due_dates, p.processing_times)
        et_global_solution = et.init_ET_global_solution(chromo, p)
        memo_ETI = dp.init_ETI_memo(chromo)
        block_lasts, end_times, eti_penalty = dpb.opt_ETI_Bounded(memo_BT, memo_ET, memo_ETI, et_global_solution,
                                                                  self.n - 1, chromo, self.n - 1, p)
        # if self.iter == 0:
        #     print(eti_penalty)
        real_obj = self.cal_Real_Objective(chromo, block_lasts, end_times, self.problem)
        self.memo_FV[tuple(chromo)] = utils.Solution(block_lasts, end_times, real_obj, 0)
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
        worst_FV = parent_gen.FV[parent_gen.worst]
        for i in range(len(parent_gen.pop)):
            sum += worst_FV - parent_gen.FV[i]
        r = random.random()
        temp = 0
        select_index = -1
        for i in range(len(parent_gen.pop)):
            temp += worst_FV - parent_gen.FV[i]
            if temp / sum > r:
                select_index = i
                break
        new_chromo = parent_gen.pop[select_index]

        # cross
        r = random.random()
        if r < self.cross_rate:
            sum = 0
            worst_FV = parent_gen.FV[parent_gen.worst]
            for i in range(len(parent_gen.pop)):
                sum += worst_FV - parent_gen.FV[i]
            r2 = random.random()
            temp = 0
            si = -1
            for i in range(len(parent_gen.pop)):
                temp += worst_FV - parent_gen.FV[i]
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
        while len(child_gen.pop) < self.pop_size:
            self.insert_chromo(self.get_one_child(parent_gen), child_gen)
        self.memo_opt.append(child_gen.pop[child_gen.best])
        return child_gen

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
        return obj

    def run(self):
        parent_gen = self.generate_Initial()
        for i in range(self.max_iter):
            child_gen = self.generate_Next_Pop(parent_gen)
            parent_gen = child_gen
        return
