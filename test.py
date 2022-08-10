from unicodedata import name
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, current_process

import urllib.request

import time
import threading
import random
import queue
import os
from multiprocessing import Process, current_process, Value, Array, shared_memory
import numpy as np


class HtmlGetter ():
    def __init__(self, url):
        # threading.Thread.__init__(self)
        self.url = url

    def run(self, shm, arr):
        new_shm = shared_memory.SharedMemory(name=shm)
        tmp_arr = np.ndarray(arr.shape, dtype=arr.dtype, buffer=new_shm.buf)

        print(tmp_arr)


def main():
    # 숫자를 저장할 numpy 배열(1차원) 생성
    arr = np.array([i for i in range(10)], dtype=np.int32)
    # 공유 메모리 생성
    shm = shared_memory.SharedMemory(create=True, size=arr.nbytes)
    # 공유 메모리의 버퍼를 numpy 배열로 변환
    np_shm = np.ndarray(arr.shape, dtype=arr.dtype, buffer=shm.buf)
    np_shm[0] = 100
    with ProcessPoolExecutor(max_workers=1) as executor:
        htmgetter = HtmlGetter('http://google.com')
        executor.submit(htmgetter.run, shm.name, np_shm)


if __name__ == "__main__":
    main()

