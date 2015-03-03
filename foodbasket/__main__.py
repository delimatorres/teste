import multiprocessing
import time

from tabulate import tabulate
from collections import Counter

from utils import get_api_items


class FoodBasket(object):
    def __init__(self):
        self.food_counter = Counter()
        self.category_counter = Counter()

    def update_basket(self, food, category):
        self.food_counter.update(food)
        self.category_counter.update(category)

    def popular_food_category(self):
        popular_food = self.food_counter.most_common(100)
        grid_food = tabulate(
            popular_food, ['Food', 'Occurrences'],
            tablefmt='grid'
        )

        popular_category = self.category_counter.most_common(5)
        grid_category = tabulate(
            popular_category, ['Category', 'Occurrences'], 
            tablefmt='grid'
        )
        return (grid_food, grid_category)


class Worker(multiprocessing.Process):
    def __init__(self, task_queue, result_queue, start_offset):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.start_offset = start_offset
        self.interrupt = False

    def run(self):
        process_name = self.name
        try:
            while True:
                pass
                next_task = self.task_queue.get()
                if next_task is None:
                    # Poison pill means shutdown
                    print '%s: Exiting' % proc_name
                    self.task_queue.task_done()
                    break
                
                answer = next_task()
                self.task_queue.task_done()
                self.result_queue.put(answer)
        except KeyboardInterrupt:
            self.task_queue.task_done()
        finally:
            x, y = next_task.basket.popular_food_category()
            print x
            print y


    def get_api_items(start_offset):
        '''
        Generator helper que parseia a estrutra padrao do json do rest framework
        respeitando a paginacao e iterando item a item
        '''
        next_offset = start_offset
        has_more = True
        
        while has_more:
            paginated_items = get_items(limit=100, offset=next_offset)
            items = paginated_items['response']
            for item in items:
                yield item

            # has_more = next_offset = paginated_items['meta']['next_offset']
            next_offset = paginated_items['meta']['next_offset']

    def get_items(**parameters):
        """
        This method returns the data 
        """
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)
        data = {}
        print parameters
        try:
            response = session.get(API_URL, params=parameters, timeout=TIMEOUT_DEFAULT)
        except:
            pass
        else:
            if response.ok:
                data = response.json()

        return data


class Task(object):
    def __init__(self, start_offset, food_basket):
        self.start_offset = start_offset
        self.basket = food_basket

    def __call__(self):
        for item in get_api_items(self.start_offset):
            self.basket.update_basket(
                {item['food_id']: 1}, {item['food__category_id']: 1}
            )


def make_offset(worker_id, num_workers):
    LIFESUM_START_OFFSET = 658330693
    LIFESUM_MAX_OFFSET = 732158492
    LIFESUM_TOTAL = LIFESUM_MAX_OFFSET - LIFESUM_START_OFFSET
    offset_amount = int(LIFESUM_TOTAL / num_workers)
    offset = LIFESUM_START_OFFSET + (offset_amount * worker_id)
    return offset

if __name__ == '__main__':
    try:
        # Establish communication queues
        tasks = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()
        food_basket = FoodBasket()

        # Start workers
        num_workers = multiprocessing.cpu_count()
        print 'Creating %d workers' % num_workers
        workers = [ Worker(tasks, results, make_offset(i, num_workers))
                      for i in xrange(num_workers)]
        for w in workers:
            w.start()

        # Enqueue jobs
        for i in xrange(num_workers):
            tasks.put(
                Task(make_offset(i, num_workers), food_basket)
            )

        # Add a poison pill for each consumer
        for i in xrange(num_workers):
            tasks.put(0.2)

        # Wait for all of the tasks to finish
        tasks.join()
        # Start printing results
        while num_jobs:
            result = results.get()
            print 'Result:', result
            num_jobs -= 1

    except Exception, e:
        print e
        print "Done"

