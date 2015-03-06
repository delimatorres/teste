import multiprocessing
import time
import signal
import requests

from tabulate import tabulate
from collections import Counter

from utils import get_api_items

API_URL = 'https://api.lifesum.com/v1/foodipedia/foodstats'
DEFAULT_HEADERS = {'User-Agent': 'LifesumFoodbasket'}
NEXT_OFFSET = 658330804
LIMIT_PER_PAGE = 100
TIMEOUT_DEFAULT = 10
DEFAULT_WAIT_TIMEOUT = 15
LIFESUM_START_OFFSET = 658330693
LIFESUM_MAX_OFFSET = 732158492
LIFESUM_TOTAL = LIFESUM_MAX_OFFSET - LIFESUM_START_OFFSET
NUM_WORKRS = multiprocessing.cpu_count()
def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


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


class ConsumerProcess(multiprocessing.Process):
    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.start()

    def run(self):
        init_worker()
        ps = []
        for d in iter(self.queue.get, None):        
            if(d == 'killjobs'):
                for p in ps:
                    p.terminate()
            else:
                ps.append(
                    multiprocessing.Process(
                        target=Task, args=(d.numerator,)
                    )
                )
                ps[-1].daemon = True
                ps[-1].start()

        for p in ps:
            p.join()


class Task(object):
    def __init__(self, index):
        self.basket = FoodBasket()
        self.num_workers = NUM_WORKRS
        self.index = index
    
        offset_amount = int(LIFESUM_TOTAL / self.num_workers)
        offset = LIFESUM_START_OFFSET + (offset_amount * self.index)
        for item in self.get_api_items(offset):
            self.basket.update_basket(
                {item['food_id']: 1}, {item['food__category_id']: 1}
            )

    def get_api_items(self, start_offset):
        '''
        Generator helper used to parser the structures guide by the pagination
        and iterating item to item
        '''
        next_offset = start_offset

        has_more = True
        
        while has_more:
            paginated_items = self.get_items(limit=100, offset=next_offset)
            items = paginated_items['response']
            for item in items:
                yield item

            has_more = next_offset = paginated_items['meta']['next_offset']

    def get_items(self, **parameters):
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
            time.sleep(1/NUM_WORKRS)
            if response.ok:
                data = response.json()

        return data

def run_all():
    q = multiprocessing.Queue()
    p = ConsumerProcess(q)
    food_basket = FoodBasket()

    num_workers = NUM_WORKRS
    print 'Creating %d workers' % num_workers

    # Establish communication queues
    # Start workers
    for i in xrange(num_workers):
        q.put(i)

    try:
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print "Caught KeyboardInterrupt, terminating consumer"
        q.put('killjobs')

    else:
        print "Quitting normally"

    finally:
        q.put(None)
        q.close()
        p.join()


if __name__ == '__main__':
    run_all()


