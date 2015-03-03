import signal
import time
import resource

from multiprocessing import (
    cpu_count, Process, 
    log_to_stderr, SUBDEBUG, 
    Event, Queue, Semaphore
)


soft_limit, _ = resource.getrlimit(resource.RLIMIT_NPROC)
SEMAPHORE = Semaphore(soft_limit)


class FoodBasket(object):
    DEFAULT_WAIT_TIMEOUT = 15
    START_OFFSET = 658330693
    MAX_OFFSET = 732158492
    TOTAL_OFFSET = MAX_OFFSET - START_OFFSET

    def __init__(self):
        self.food_counter = Counter()
        self.category_counter = Counter()
        self.number_workers = cpu_count()
        self.jobs = []

    def data_counter(self, food, category):
        self.food_counter.update(food)
        self.category_counter.update(category)
        # print self.category_counter
        import ipdb; ipdb.set_trace()

    def worker(self, offset):
        try:
            for item in get_api_items(offset):
                self.data_counter(
                    {item['food_id']: 1},
                    {item['food__category_id']: 1}
                )

        except KeyboardInterrupt:
            self.killer()

        food, category = self.most_popular()
        print food
        print category
        
    def killer(self):
        for j in self.jobs:
            j.terminate()
        
        # foods, categorys = self.most_popular()
        # print foods
        # print categorys

    def run(self):
        offset_amount = int(FoodBasket.TOTAL_OFFSET / self.number_workers)
        for worker in xrange(self.number_workers):
            offset = FoodBasket.START_OFFSET + (offset_amount * worker)
            job = Process(target=self.worker, args=(offset,))    
            job.start()
            self.jobs.append(job)
            # self.worker(offset)


try:
    app = FoodBasket()
    app.run()
except KeyboardInterrupt:
    print("\n\n Please wait, we are working on it...")
