import unittest

from abyss.dispatchers.max_first_dispatcher import MaxFirstDispatcher
from abyss.orchestrator.job import Job
from abyss.orchestrator.worker import Worker


class MaxFirstDispatcherTests(unittest.TestCase):
    def test_dispatch(self):
        workers = [Worker.from_dict({
            "globus_eid": "0",
            "funcx_eid": "1",
            "max_available_space": 97,
            "transfer_dir": "/transfer",
            "decompress_dir": "/dir",
        }),
            Worker.from_dict({
                "globus_eid": "0",
                "funcx_eid": "1",
                "max_available_space": 57,
                "transfer_dir": "/transfer",
                "decompress_dir": "/dir",
            })
        ]
        worker_batches = {
            workers[0].worker_id: [Job.from_dict(({"file_path": f"/{i}",
                                                   "compressed_size": 0,
                                                   "decompressed_size": i,
                                                   })) for i in range(10, 20)],
            workers[1].worker_id: [Job.from_dict(({"file_path": f"/{i}",
                                                   "compressed_size": 0,
                                                   "decompressed_size": i,
                                                   })) for i in range(0, 10)]
        }
        preserved_batches = {
            workers[0].worker_id: worker_batches[workers[0].worker_id],
            workers[1].worker_id: worker_batches[workers[1].worker_id]
        }

        dispatcher = MaxFirstDispatcher(workers)
        dispatcher.dispatch_batch(worker_batches)
        worker_queues = dispatcher.worker_queues

        for worker_id, worker_batch in preserved_batches.items():
            preserved_batches[worker_id] = sorted(worker_batch,
                                                  reverse=True,
                                                  key=(lambda x: x.decompressed_size))

        for worker_id, worker_queue in worker_queues.items():
            self.assertEqual(list(worker_queue.queue), preserved_batches[worker_id])

        self.assertEqual(worker_batches, {workers[0].worker_id: [],
                                          workers[1].worker_id: []})
        self.assertEqual(dispatcher.worker_batches, {workers[0].worker_id: [],
                                                     workers[1].worker_id: []})


if __name__ == '__main__':
    unittest.main()
