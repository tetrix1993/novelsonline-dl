import os
import requests
import datetime
from bs4 import BeautifulSoup as bs


HTTP_HEADER_USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) ' +
                                        'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                                        'Chrome/50.0.2661.102 Safari/537.36'}
PAGE_PREFIX = 'https://novelsonline.net/'


def download_image(url, filepath, config_parser):
    headers = HTTP_HEADER_USER_AGENT
    if os.path.exists(filepath):
        # print('File %s exists' % filepath)
        return 1
    try:
        with requests.get(url, stream=True, headers=headers) as r:
            if r.status_code >= 400:
                return -1
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print_info(f'Downloaded {url}')
            create_log(filepath, url, config_parser)
    except Exception as e:
        print_error(f'Failed to download {url} - {e}')
        return -1
    return 0


def get_soup(url):
    headers = HTTP_HEADER_USER_AGENT
    try:
        result = requests.get(url, headers=headers)
        return bs(result.text, 'html.parser')
    except Exception as e:
        print_error(f'Failed to access {url} - {e}')
    return None


def create_log(filepath, url, config_parser):
    log_folder = config_parser.get('settings', 'log_folder')
    download_log_name = config_parser.get('settings', 'download_log_name')
    timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    with open(f'{log_folder}/{download_log_name}', 'a+', encoding='utf-8') as f:
        f.write(f'{timenow}\t{filepath}\t{url}\n')


def print_info(message):
    print(f'[INFO] {message}')


def print_error(message):
    print(f'[ERROR] {message}')