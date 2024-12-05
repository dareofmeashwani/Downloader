from multiprocessing import Process, Lock, Semaphore, Queue
from multiprocessing import Value
from multiprocessing import Queue
import signal
from file import File
from cache_util import dump_cache, find_in_cache, load_cache
from worker import Worker
import os


class WorkerManger(Process):
    def __init__(self, work=None, workers_count=5, retry=4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workers_count = workers_count
        self.retry = retry
        self.work = work
        self.input_queue = Queue()
        self.input_lock = Lock()
        self.cache_lock = Lock()
        self.output_queue = Queue()
        self.output_semaphore = Semaphore(value=0)
        self.is_manager_running = Value("b", True)
        self.workers = [
            Worker(
                self.input_queue,
                self.input_lock,
                self.output_queue,
                self.output_semaphore,
                self.is_manager_running,
                self.cache_lock,
                **kwargs
            )
            for _ in range(workers_count)
        ]

    def add(self, file: File):
        self.input_queue.put(file)
        self.work.append(file)

    def start(self, *args, **kwargs):
        super().start(*args, **kwargs)
        for w in self.work:
            self.input_queue.put(w)
        for worker in self.workers:
            worker.start()

    def stop(self):
        self.is_manager_running.value = False
        for cProcess in self.workers:
            if cProcess.pid != 0:
                try:
                    os.kill(cProcess.pid, signal.SIGTERM)
                except:
                    pass
        self.input_queue.close()
        self.output_queue.close()

    def run(self):
        while self.is_manager_running.value:
            self.output_semaphore.acquire()
            status, data = self.output_queue.get()
            if status:
                self.cache_lock.acquire()
                cache = load_cache()
                entry = find_in_cache(cache, data.source)
                entry_index = cache.index(entry)
                cache[entry_index] = data
                dump_cache(cache)
                self.cache_lock.release()
            if not status and self.retry > data.get_retry():
                data.increment_retry()
                self.input_queue.put(data)
            elif not status:
                fa = open("failed.txt", "a")
                fa.write(str(data) + "\n")
                fa.close()
            if (
                self.input_queue.qsize() == 0
                and self.output_queue.qsize() == 0
                and not any([worker.is_running.value for worker in self.workers])
            ):
                self.is_manager_running.value = False
                return
