from typing import Dict, List
from abyss.batchers import get_batcher
from abyss.dispatcher import get_dispatcher
from abyss.orchestrator.worker import Worker


class Scheduler:
    def __init__(self, batcher_name: str, dispatcher_name: str,
                 workers: List[Worker], jobs: List[Dict]):
        """Class for internally managing both the Batcher and
        Dispatcher. Takes jobs and places them into queues for workers
        to process.

        Parameters
        ----------
        batcher_name : str
            Name of Batcher to use.
        dispatcher_name : str
            Name of Dispatcher to use
        workers : list(Worker)
            List of Worker objects to batch jobs amongst.
        jobs : list(dict)
            List of jobs (dictionaries containing file_path and
            decompressed_size) to batch amongst workers.
        """
        self._worker_dict = dict()
        self._batcher = get_batcher(batcher_name)(workers, jobs)
        self._dispatcher = get_dispatcher(dispatcher_name)(workers, self._batcher.worker_batches)

        self.worker_queues = self._dispatcher.worker_queues

        for worker in workers:
            self._worker_dict[worker.worker_id] = worker

    def update_worker(self, worker: Worker) -> None:
        """Updates a worker. If the current available size of a worker
        is changed, then new items may be added to worker queues..

        Parameters
        ----------
        worker : Worker
            Worker to be updated.

        Returns
        -------
        None
        """
        self._batcher.update_worker(worker)
        self._schedule()

    def schedule_job(self, job: Dict) -> None:
        """Places job in queue to be scheduled.

        Parameters
        ----------
        job : dict
            Dictionary with file path and size of decompressed file.

        Returns
        -------
        None
        """
        self._batcher.batch_job(job)
        self._schedule()

    def schedule_jobs(self, jobs: List[Dict]) -> None:
        """Places batch of jobs in queue to be batched.

        Parameters
        ----------
        jobs : list(dict)
            List of dictionaries with file path and size of decompressed
            file.

        Returns
        -------
        None
        """
        self._batcher.batch_jobs(jobs)
        self._schedule()

    def _schedule(self) -> None:
        """Internal method for batching and placing jobs in worker
        queues.

        Returns
        -------
        None
        """
        self._dispatcher.dispatch_batch(self._batcher.worker_batches)
        self._worker_queues = self._dispatcher.worker_queues


