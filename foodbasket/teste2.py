#!/usr/bin/env python
import multiprocessing, os, signal, time, Queue

import requests

class Baa(object):
    def __init__(self, *args):
        self.args = args


def do_work():
    baa = Baa()
    print 'Work Started: %d' % os.getpid()
    for x in range(100):
        print os.getpid(), requests.get('http://globo.com').status_code, x
        time.sleep(1)
    return 'Success'

def manual_function(job_queue, result_queue):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    while not job_queue.empty():
        try:
            job = job_queue.get(block=False)
            result_queue.put(do_work())
        except Queue.Empty:
            pass
        #except KeyboardInterrupt: pass

def main():
    job_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    for i in range(6):
        job_queue.put(None)

    workers = []
    for i in range(3):
        tmp = multiprocessing.Process(target=manual_function,
                                      args=(job_queue, result_queue))
        tmp.start()
        workers.append(tmp)

    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        print 'parent received ctrl-c'
        for worker in workers:
            worker.terminate()
            worker.join()

    while not result_queue.empty():
        print result_queue.get(block=False)

if __name__ == "__main__":
    main()