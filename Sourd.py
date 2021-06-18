import math

import blockTiming
import timing
import utils


class Sourd:
    def __init__(self, jobs, problem):
        self.jobs = jobs
        self.problem = problem
        self.vs = []
        self.memo = []
        head_last, tail_first, et_penalty_ET, num_idle_ET = timing.opt_ET_no_memo(jobs, 0, problem.n - 1, problem)
        _, _, ub_penalty, _ = blockTiming.time_block_no_memo(jobs, 0, problem.n - 1, problem)
        self.idle_bound = min(num_idle_ET, math.floor((ub_penalty - et_penalty_ET) / problem.b))
        self.tail_first = tail_first
        self.head_last = head_last

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
                    best_obj = obj
        elif n == 0:
            t = self.vs[n][0]
            if t >= bound:
                return self.et(n, bound)
            else:
                return min(self.et(n, bound), self.et(n, t) + self.problem.b)
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
        if self.memo[n].get((bound, idle_bound)):
            return self.memo[n][(bound, idle_bound)]
        best_obj = utils.BIG_NUMBER
        if n == 0:
            t = self.vs[n][0]
            if idle_bound > 0:
                if t < bound:
                    return min(self.et(n, bound), self.et(n, t) + self.problem.b)
            else:
                return self.et(n, bound)
        elif n == len(self.jobs) - 1:
            for t in self.vs[n]:
                obj = self.et(n, t) + self.dp_bounded(n - 1, t - self.problem.processing_times[self.jobs[n]],
                                                      idle_bound)
                if obj < best_obj:
                    best_obj = obj
        elif n >= self.tail_first:
            obj = self.et(n, bound) + self.dp_bounded(n - 1, bound - self.problem.processing_times[self.jobs[n]],
                                                      idle_bound)
            if obj < best_obj:
                best_obj = obj
        elif n <= self.head_last:
            if idle_bound > 0:
                for t in self.vs[n]:
                    if t < bound:
                        obj = self.et(n, t) + self.problem.b + self.dp_bounded(n - 1, t - self.problem.processing_times[
                            self.jobs[n]], 0)
                        if obj < best_obj:
                            best_obj = obj
            obj = self.et(n, bound) + self.dp_bounded(n - 1, bound - self.problem.processing_times[self.jobs[n]], 0)
            if obj < best_obj:
                best_obj = obj
        else:
            if idle_bound > 0:
                for t in self.vs[n]:
                    if t < bound:
                        obj = self.et(n, t) + self.problem.b + self.dp_bounded(n - 1, t - self.problem.processing_times[
                            self.jobs[n]], idle_bound - 1)
                        if obj < best_obj:
                            best_obj = obj
            obj = self.et(n, bound) + self.dp_bounded(n - 1, bound - self.problem.processing_times[self.jobs[n]],
                                                      idle_bound)
            if obj < best_obj:
                best_obj = obj
        self.memo[n][(bound, idle_bound)] = best_obj
        return best_obj

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
