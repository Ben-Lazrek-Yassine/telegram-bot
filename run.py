from core import core
from utils import keep_running
from models import Account
from scrapers import find_session_files
from scrape_all import *
if __name__ == '__main__':
    core()
    keep_running()
