import requests


API_URL = 'https://api.lifesum.com/v1/foodipedia/foodstats'
DEFAULT_HEADERS = {'User-Agent': 'LifesumFoodbasket'}
NEXT_OFFSET = 658330804
LIMIT_PER_PAGE = 100
TIMEOUT_DEFAULT = 10
DEFAULT_WAIT_TIMEOUT = 15        


def get_api_items(offset):
    
    '''
    Generator helper que parseia a estrutra padrao do json do rest framework
    respeitando a paginacao e iterando item a item
    '''
    next_offset = offset
    has_more = True
    
    while has_more:
        paginated_items = get_items(limit=100, offset=next_offset)
        items = paginated_items['response']
        for item in items:
            yield item

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
        except requests.exceptions.SSLError:
            msg = "SSL Error"
        except requests.exceptions.InvalidURL:
            msg = 'Invalid URL'
        except requests.exceptions.Timeout:
            msg = 'Timeout'
        else:
            if response.ok:
                data = response.json()

        return data