import utils


class Sourd:
    def __init__(self, jobs, problem):
        self.jobs = jobs
        self.problem = problem
        self.vs = []
        self.memo = []

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
                if t >= bound:
                    obj = self.et(n, bound) + self.dp(n - 1, bound - self.problem.processing_times[self.jobs[n]])
                else:
                    obj = self.et(n, t) + self.dp(n - 1,
                                                  t - self.problem.processing_times[self.jobs[n]]) + self.problem.b
                if obj < best_obj:
                    best_obj = obj
        self.memo[n][bound] = best_obj
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
