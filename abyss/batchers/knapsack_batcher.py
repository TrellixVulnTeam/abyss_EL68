import math
from typing import List

import numpy as np

from abyss.batchers.batcher import Batcher
from abyss.orchestrator.job import Job
from abyss.orchestrator.worker import Worker


class KnapsackBatcher(Batcher):
    def __init__(self, workers: List[Worker], jobs: List[Job], **kwargs):
        """Batches using a Knapsack heuristic. The purpose of
        this batcher is to maximize the size of each worker batch while
        ensuring that batch size < worker available space. This is
        analogous to the 0-1 Knapsack problem, where worker available
        space is the capacity of the knapsack, and a job's size is the
        weight and value of items to place in the knapsack.

        Using dynamic programming, the knapsack algorithm has a time
        complexity O(N*C) and space complexity O(N*C), where N is the
        number of items and C is the capacity of the knapsack. Since C
        is the amount of space on a worker, C is in the Giga-Terabyte
        range (10^9 - 10^11), which is infeasible for space and time
        constraints. To solve this, a capacity_buffer variable is used
        to divide the size of jobs and available space in order to
        reduce the size and time complexity of this algorithm. With a
        capacity interval I, the time and space complexity is now
        O(N*C/I). However, this results in wasted space with an upper
        bound of N*I.

        Since this batcher calculates the optimal batch for each worker
        independently from each other, this heuristic produces a locally
        correct solution for each batch but not a globally correct
        solution for all workers. Additionally, this heuristic may
        result in unbalanced batches, as each batch is filled to
        its max one at a time.

        Parameters
        ----------
        workers : list(Worker)
            List of Worker objects to batch jobs amongst.
        jobs : list(Job)
            List of Jobs to batch amongst workers.
        kwargs
            capacity_buffer : int
                Factor to divide available space and job size by.
                Defaults to 10 ** 7 (1MB).
        """
        super().__init__(workers, jobs)

        if "capacity_buffer" in kwargs:
            self.capacity_buffer = kwargs["capacity_buffer"]
        else:
            self.capacity_buffer = 10 ** 8

        self._batch()

    def batch_job(self, job: Job) -> None:
        """Places job in queue to be batched.

        Parameters
        ----------
        job : Job
            Job object.

        Returns
        -------
        None
        """
        if self._is_failed_job(job):
            self.failed_jobs.add(job)
        else:
            self.jobs.append(job)

        self._batch()

    def batch_jobs(self, jobs: List[Job]) -> None:
        """Places batch of jobs in queue to be batched.

        Parameters
        ----------
        jobs : list(dict)
            List of Jobs.

        Returns
        -------
        None
        """
        for job in jobs:
            if self._is_failed_job(job):
                self.failed_jobs.add(job)
            else:
                self.jobs.append(job)

        self._batch()

    def _batch(self) -> None:
        """Schedules using a Knapsack heuristic. Goes through each
        worker and determines the combination of jobs which best
        maximizes the job batch size using the 0-1 Knapsack algorithm.

        Returns
        -------
        None
        """
        for worker in self.workers:
            jobs = self._get_knapsack_items(worker)

            assert sum([job.total_size for job in jobs]) <= worker.curr_available_space

            for job in jobs:
                total_size = job.total_size
                worker.curr_available_space -= total_size
                job.worker_id = worker.worker_id

                self.worker_batches[worker.worker_id].append(job)
                self.jobs.remove(job)

    def _get_knapsack_items(self, worker) -> List[Job]:
        """Determines job batch for single worker using 0-1 Knapsack
        algorithm.

        Parameters
        ----------
        worker : Worker
            Worker to batch jobs for.

        Returns
        -------
        jobs : list(Job)
            Job batch for worker.
        """
        if not self.jobs:
            return []

        available_space = math.ceil(worker.curr_available_space / self.capacity_buffer)
        knapsack_array = np.empty((len(self.jobs) + 1,
                                   available_space + 1))

        for i in range(len(self.jobs) + 1):
            last_item_size = math.ceil(self.jobs[i - 1].total_size / self.capacity_buffer)
            for j in range(available_space + 1):
                if i == 0 or j == 0:
                    knapsack_array[i][j] = 0
                elif last_item_size <= j:

                    knapsack_array[i][j] = max(last_item_size + knapsack_array[i - 1][j - last_item_size],
                                               knapsack_array[i - 1][j])
                else:
                    knapsack_array[i][j] = knapsack_array[i - 1][j]

        res = knapsack_array[len(self.jobs)][available_space]
        jobs = [job for job in self.jobs if job.total_size == 0]

        for i in range(len(self.jobs), 0, -1):
            if res <= 0:
                break

            if res == knapsack_array[i - 1][available_space]:
                continue
            else:
                jobs.append(self.jobs[i - 1])
                res -= math.ceil(self.jobs[i - 1].total_size / self.capacity_buffer)
                available_space -= math.ceil(self.jobs[i - 1].total_size / self.capacity_buffer)

        return jobs
