from configparser import ConfigParser
from argparse import ArgumentParser
from apputil import *
import os
import html
from multiprocessing import Pool


CONFIG_FILEPATH = 'config.ini'


def run():
    print_info('Starting Novels Online Scraper')
    if os.path.exists(CONFIG_FILEPATH):
        config_parser = ConfigParser()
        config_parser.read('config.ini')
    else:
        print_info(f'Creating missing configuration file {CONFIG_FILEPATH}')
        config_parser = create_config_file()

    if 'settings' not in config_parser:
        print_error(f'Cannot find section "settings" in Configuration file {CONFIG_FILEPATH}.')
        return

    arg_parser = ArgumentParser(description='Download novels by ID')
    arg_parser.add_argument('-id', '--ID', metavar='', required=True, help='Novel ID in the URL: E.g. sword-art-online from https://novelsonline.net/sword-art-online')
    args = arg_parser.parse_args()

    download_novel(args.ID, config_parser)
    print_info('Exiting Novels Online Scraper')


def download_novel(novel_id, config_parser):
    if novel_id.startswith(PAGE_PREFIX):
        novel_id = novel_id[len(PAGE_PREFIX):]
        if novel_id.endswith('/'):
            novel_id = novel_id[0:len(novel_id)-1]

    if len(novel_id) == 0:
        return

    max_length = int(config_parser.get('settings', 'folder_name_max_length'))
    folder_name = novel_id if len(novel_id) <= max_length else novel_id[:max_length]
    output_folder = f"{config_parser.get('settings', 'output_folder')}/{folder_name}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print_info(f'Created directory "{output_folder}"')

    novel_url = f'{PAGE_PREFIX}{novel_id}/'
    soup = get_soup(novel_url)
    if soup is not None:
        cover_img = soup.select('.novel-cover img')
        if len(cover_img) > 0 and cover_img[0].has_attr('src'):
            image_url = cover_img[0]['src']
            image_name = image_url.split('?')[0].split('/')[-1]
            download_image(cover_img[0]['src'], f'{output_folder}/{image_name}', config_parser)

        chapters = soup.select('ul.chapter-chs li a')
        if len(chapters) == 0:
            print_error('No chapters found.')
        else:
            max_processes = int(config_parser.get('settings', 'max_processes'))
            with Pool(min(max_processes, len(chapters))) as p:
                results = []
                for chapter in chapters:
                    if chapter.has_attr('href'):
                        chapter_url = chapter['href'].strip()
                        if chapter_url.endswith('/'):
                            chapter_url = chapter_url[0:len(chapter_url)-1]
                        if len(chapter_url) > 0 and chapter_url.startswith(novel_url):
                            chapter_split = chapter_url.split(novel_url)[1].split('/')
                            save_folder = f'{output_folder}/{chapter_split[0]}' if len(chapter_split) > 1 else output_folder
                            filename = chapter_url.split('/')[-1] + '.txt'
                            if os.path.exists(save_folder + '/' + filename):
                                continue
                            result = p.apply_async(download_chapter, (chapter_url, save_folder, filename, config_parser))
                            results.append(result)
                for result in results:
                    result.wait()

    # Remove directory if empty
    files = os.listdir(output_folder)
    if len(files) == 0:
        os.removedirs(output_folder)
        print_info(f'Removed directory "{output_folder}" since it is empty.')


def download_chapter(chapter_url, save_folder, filename, config_parser):
    soup = get_soup(chapter_url)
    if soup is not None:
        filepath = save_folder + '/' + filename
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        with open(filepath, 'w+', encoding='utf-8') as f:
            paragraphs = soup.select('#contentall p')
            for para in paragraphs:
                if len(para.text) > 0:
                    curr_elem = para.next_element
                    while curr_elem.name != 'div' or not curr_elem.has_attr('class') or 'row' not in curr_elem['class']:
                        if curr_elem.name is None:
                            sentence = str(curr_elem).strip()
                            if len(sentence) > 0:
                                f.write(html.unescape(sentence) + '\n')
                        elif curr_elem.name in ['br', 'p']:
                            f.write('\n')
                        elif curr_elem.name in ['noscript', 'script']:
                            curr_elem = curr_elem.next_element
                        elif curr_elem.name == 'img' and curr_elem.has_attr('src'):
                            if curr_elem['src'].startswith('http'):
                                image_url = curr_elem['src']
                            else:
                                image_url = PAGE_PREFIX + (
                                    curr_elem['src'][1:] if curr_elem['src'].startswith('/') else curr_elem['src'])
                            image_name = image_url.split('?')[0].split('/')[-1]
                            download_image(image_url, f'{save_folder}/{image_name}', config_parser)
                            f.write(f'[Image: {image_name}]\n')
                        curr_elem = curr_elem.next_element
                    break

                '''
                noscript = para.find('noscript')
                if noscript is not None:
                    continue
                image = para.find('img')
                if image is None:
                    text = html.unescape(para.text.strip())
                    if len(text) > 0:
                        f.write(f'{text}\n\n')
                elif image.has_attr('src'):
                    if image['src'].startswith('http'):
                        image_url = image['src']
                    else:
                        image_url = PAGE_PREFIX + (image['src'][1:] if image['src'].startswith('/') else image['src'])
                    image_name = image_url.split('?')[0].split('/')[-1]
                    download_image(image_url, f'{save_folder}/{image_name}', config_parser)
                    f.write(f'[Image: {image_name}]\n\n')
                '''
        print_info(f'Downloaded {chapter_url}')
        create_log(filepath, chapter_url, config_parser)


def create_config_file():
    config = ConfigParser()
    config['settings'] = {
        'output_folder': 'out',
        'log_folder': 'log',
        'download_log_name': 'download.log',
        'max_processes': 10,
        'folder_name_max_length': 50
    }

    with open(CONFIG_FILEPATH, 'w') as f:
        config.write(f)

    return config


if __name__ == '__main__':
    run()
