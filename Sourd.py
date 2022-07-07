import math
import ET_opt as et
import blockTiming
import utils


class Solution:
    # def __init__(self, obj, is_best_idle):
    #     self.obj = obj
    #     self.is_best_idle = is_best_idle
    def __init__(self, obj, num_idle):
        self.obj = obj
        self.num_idle = num_idle


class Sourd:
    def __init__(self, jobs, problem):
        self.jobs = jobs
        self.problem = problem
        self.vs = []
        self.memo = []
        # head_last, tail_first, et_penalty_ET, num_idle_ET = et.opt_ET_no_memo(jobs, 0, problem.n - 1, problem)
        # _, _, ub_penalty, _ = blockTiming.time_block_no_memo(jobs, 0, problem.n - 1, problem)
        # self.idle_bound = min(num_idle_ET, math.floor(round(ub_penalty - et_penalty_ET, 4) / problem.b))
        # self.tail_first = tail_first
        # self.head_last = head_last

    def init_variable_space(self):
        for i in range(len(self.jobs)):
            self.vs.append([])
        self.vs[0].append(self.problem.due_dates[self.jobs[0]])
        for i in range(1, len(self.jobs)):
            self.vs[i].append(self.problem.due_dates[self.jobs[i]])
            for j in range(len(self.vs[i - 1])):
                self.vs[i].append(self.vs[i - 1][j] + self.problem.processing_times[self.jobs[i]])
        return

    def init_memo(self):
        for i in range(len(self.jobs)):
            self.memo.append({})
        return

    def dp(self, n, bound):
        if self.memo[n].get(bound):
            return self.memo[n][bound]
        best_obj = utils.BIG_NUMBER
        if n == len(self.jobs) - 1:
            for t in self.vs[n]:
                obj = self.et(n, t) + self.dp(n - 1, t - self.problem.processing_times[self.jobs[n]])
                if obj < best_obj:
                    # print("1 ",obj,"\t",best_obj)
                    best_obj = obj
        elif n == 0:
            t = self.vs[n][0]
            if t >= bound:
                best_obj = self.et(n, bound)
            else:
                best_obj = min(self.et(n, bound), self.et(n, t) + self.problem.b)
        else:
            for t in self.vs[n]:
                if t < bound:
                    obj = self.et(n, t) + self.dp(n - 1,
                                                  t - self.problem.processing_times[self.jobs[n]]) + self.problem.b
                    if obj < best_obj:
                        best_obj = obj
            obj = self.et(n, bound) + self.dp(n - 1, bound - self.problem.processing_times[self.jobs[n]])
            if obj < best_obj:
                best_obj = obj
        self.memo[n][bound] = best_obj
        return best_obj

    def dp_bounded(self, n, bound, idle_bound):
        if self.memo[n].get(bound):
            if self.memo[n][bound].num_idle > idle_bound:
                return utils.BIG_NUMBER, self.memo[n][bound].num_idle
            return self.memo[n][bound].obj, self.memo[n][bound].num_idle
        best_obj = utils.BIG_NUMBER
        if idle_bound > 0:
            if n == len(self.jobs) - 1:
                num_idle = -99
                for t in self.vs[n]:
                    sub_obj, sub_num_idle = self.dp_bounded(n - 1, t - self.problem.processing_times[self.jobs[n]],
                                                            idle_bound)
                    obj = self.et(n, t) + sub_obj
                    if obj < best_obj:
                        # print("2 ",obj, "\t", best_obj)
                        best_obj = obj
                        num_idle = sub_num_idle
            elif n == 0:
                t = self.vs[n][0]
                if t >= bound:
                    best_obj = self.et(n, bound)
                    num_idle = 0
                else:
                    obj1 = self.et(n, bound)
                    obj2 = self.et(n, t) + self.problem.b
                    if obj1 < obj2:
                        best_obj = obj1
                        num_idle = 0
                    else:
                        best_obj = obj2
                        num_idle = 1
            else:
                for t in self.vs[n]:
                    if t < bound:
                        sub_obj, sub_num_idle = self.dp_bounded(n - 1, t - self.problem.processing_times[self.jobs[n]],
                                                                idle_bound - 1)
                        obj = self.et(n, t) + sub_obj + self.problem.b
                        if obj < best_obj:
                            best_obj = obj
                            num_idle = sub_num_idle + 1
                sub_obj, sub_num_idle = self.dp_bounded(n - 1, bound - self.problem.processing_times[self.jobs[n]],
                                                        idle_bound)
                obj = self.et(n, bound) + sub_obj
                if obj < best_obj:
                    best_obj = obj
                    num_idle = sub_num_idle
        else:
            if n == len(self.jobs) - 1:
                for t in self.vs[n]:
                    sub_obj, sub_num_idle = self.dp_bounded(n - 1, t - self.problem.processing_times[self.jobs[n]], 0)
                    obj = self.et(n, t) + sub_obj
                    if obj < best_obj:
                        best_obj = obj
                        num_idle = 0
            else:
                best_obj = 0
                t = bound
                for i in range(n, -1, -1):
                    best_obj += self.et(i, t)
                    t -= self.problem.processing_times[self.jobs[i]]
                num_idle = 0
            # elif n == 0:
            #     best_obj = self.et(n, bound)
            #     num_idle = 0
            # else:
            #     sub_obj, sub_num_idle = self.dp_bounded(n - 1, bound - self.problem.processing_times[self.jobs[n]], 0)
            #     obj = self.et(n, bound) + sub_obj
            #     if obj < best_obj:
            #         best_obj = obj
            #         num_idle = 0
            return best_obj, num_idle
        self.memo[n][bound] = Solution(best_obj, num_idle)
        if num_idle > idle_bound:
            return utils.BIG_NUMBER, num_idle
        else:
            return best_obj, num_idle

    # def dp_bounded_1(self, n, bound, idle_bound):
    #     if self.memo[n].get(bound):
    #         keys = list(self.memo[n][bound].keys())
    #         keys.sort()
    #         max_k = utils.BIG_NUMBER
    #         while max_k > idle_bound and len(keys) > 0:
    #             max_k = keys[-1]
    #             keys.pop()
    #         if max_k <= idle_bound:
    #             if max_k == idle_bound or self.memo[n][bound][max_k].is_best_idle == True:
    #                 return self.memo[n][bound][max_k].obj, max_k
    #     else:
    #         self.memo[n][bound] = {}
    #     best_obj = utils.BIG_NUMBER
    #     if n == 0:
    #         t = self.vs[n][0]
    #         obj0 = self.et(n, bound)
    #         obj1 = self.et(n, t) + self.problem.b
    #         if idle_bound > 0 and t < bound:
    #             if obj0 < obj1:
    #                 self.memo[n][bound][0] = Solution(obj0, True)
    #                 return obj0, 0
    #             else:
    #                 self.memo[n][bound][1] = Solution(obj1, True)
    #                 return obj1, 1
    #         elif t >= bound:
    #             self.memo[n][bound][0] = Solution(obj0, True)
    #             return obj0, 0
    #         else:
    #             if obj0 < obj1:
    #                 self.memo[n][bound][0] = Solution(obj0, True)
    #                 return obj0, 0
    #             else:
    #                 self.memo[n][bound][0] = Solution(obj0, False)
    #                 return obj0, 0
    #     elif n == len(self.jobs) - 1:
    #         for t in self.vs[n]:
    #             obj, num_idle = self.dp_bounded_1(n - 1, t - self.problem.processing_times[self.jobs[n]], idle_bound)
    #             obj += self.et(n, t)
    #             if obj < best_obj:
    #                 best_obj = obj
    #                 best_num_idle = num_idle
    #     # elif n >= self.tail_first:
    #     #     obj, num_idle = self.dp_bounded_1(n - 1, bound - self.problem.processing_times[self.jobs[n]], idle_bound)
    #     #     obj += self.et(n, bound)
    #     #     if obj < best_obj:
    #     #         best_obj = obj
    #     #         best_num_idle = num_idle
    #     # elif n <= self.head_last:
    #     #     if idle_bound > 0:
    #     #         for t in self.vs[n]:
    #     #             if t < bound:
    #     #                 obj, num_idle1 = self.dp_bounded_1(n - 1, t - self.problem.processing_times[self.jobs[n]], 0)
    #     #                 obj += self.et(n, t) + self.problem.b
    #     #                 if obj < best_obj:
    #     #                     best_obj = obj
    #     #                     best_num_idle = num_idle1 + 1
    #     #     obj, num_idle2 = self.dp_bounded_1(n - 1, bound - self.problem.processing_times[self.jobs[n]], 0)
    #     #     obj += self.et(n, bound)
    #     #     if obj < best_obj:
    #     #         best_obj = obj
    #     #         best_num_idle = num_idle2
    #     else:
    #         if idle_bound > 0:
    #             for t in self.vs[n]:
    #                 if t < bound:
    #                     obj, num_idle1 = self.dp_bounded_1(n - 1, t - self.problem.processing_times[self.jobs[n]],
    #                                                        idle_bound - 1)
    #                     obj += self.problem.b + self.et(n, t)
    #                     if obj < best_obj:
    #                         best_obj = obj
    #                         best_num_idle = num_idle1 + 1
    #         obj, num_idle2 = self.dp_bounded_1(n - 1, bound - self.problem.processing_times[self.jobs[n]], idle_bound)
    #         obj += self.et(n, bound)
    #         if obj < best_obj:
    #             best_obj = obj
    #             best_num_idle = num_idle2
    #     is_best_idle = idle_bound > best_num_idle
    #     self.memo[n][bound][best_num_idle] = Solution(best_obj, is_best_idle)
    #     return best_obj, best_num_idle

    def et(self, n, t):
        due = self.problem.due_dates[self.jobs[n]]
        if (t > due):
            et_penalty = (t - due) * self.problem.tardiness_penalties[self.jobs[n]]
        else:
            et_penalty = (due - t) * self.problem.earliness_penalties[self.jobs[n]]
        return et_penalty

    def run(self):
        self.init_variable_space()
        self.init_memo()
        return self.dp(self.problem.n - 1, -1)

    def run_bounded(self):
        self.init_variable_space()
        self.init_memo()
        return self.dp_bounded(self.problem.n - 1, -1, self.idle_bound)
