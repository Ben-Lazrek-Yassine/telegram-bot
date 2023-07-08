from core import core
from utils import keep_running
from models import Account
from scrapers import find_session_files
if __name__ == '__main__':
    find_session_files('.')
    #core()
    #keep_running()
