import requests
from cache_util import find_in_cache, load_cache
from file import File
import os
from multiprocessing import Process, Value
import time


class Worker(Process):
    def __init__(
        self,
        input_queue,
        input_lock,
        output_queue,
        output_semaphore,
        is_manager_running,
        cache_lock,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.input_queue = input_queue
        self.input_lock = input_lock
        self.output_queue = output_queue
        self.output_semaphore = output_semaphore
        self.is_manager_running = is_manager_running
        self.is_running = Value("b", False)
        self.cache_lock = cache_lock

    def dispatch(self, file: File):
        file_absolute_path = file.get_storage_path()
        if os.path.isfile(file_absolute_path):
            if os.path.exists(file_absolute_path + "temp"):
                os.remove(file_absolute_path + "temp")
            if (
                os.path.exists(file_absolute_path)
                and os.path.getsize(file_absolute_path) < 2 * 1024 * 1024
            ):
                os.remove(file_absolute_path)

            if os.path.exists(file_absolute_path):
                file.set_done(True)
                print("File Already Exist : ", file_absolute_path)
                return True, file
        self.cache_lock.acquire()
        cache = load_cache()
        self.cache_lock.release()
        entry = find_in_cache(cache, file.source)
        if entry and entry.done:
            file.set_done(True)
            print("File Already Exist : ", file_absolute_path)
            return True, file

        try:
            # headers = {'User-Agent': 'Mozilla/5.0'}
            print("Downloading : ", file)
            r = requests.get(file.get_access_url(), stream=True)
            file_absolute_path = file.get_storage_path()
            with open(file_absolute_path + "temp", "wb") as f:
                for chunk in r.iter_content(chunk_size=4 * 1024):
                    if chunk:
                        f.write(chunk)
            os.rename(file_absolute_path + "temp", file_absolute_path)
            file.set_done(True)
            print("Downloaded : ", file)
            if file.post_download:
                file.post_download(file)
            return True, file
        except Exception as e:
            os.path.exists(file_absolute_path + "temp") and os.remove(
                file_absolute_path + "temp"
            )
            print("Download Failed : ", file)
            print(e)
            return False, file

    def run(self):
        while self.is_manager_running.value:
            self.input_lock.acquire()
            data = self.input_queue.get()
            self.is_running.value = True
            self.input_lock.release()
            status, data = self.dispatch(data)
            self.is_running.value = False
            time.sleep(0.2)
            self.output_queue.put((status, data))
            self.output_semaphore.release()
