import logging
import re
import requests_cache

from collections import Counter
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PATTERN,
                       PEP_STATUS, PEPS_URL)
from exceptions import ParserFindStatusException
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    response = get_response(session, whats_new_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(
        main_div,
        'div',
        attrs={'class': 'toctree-wrapper compound'}
    )
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    # Печать первого найденного элемента.
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python, desc='Поиск версий:'):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)

        if response is None:
            continue

        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    
    return results


def latest_versions(session):
    """Поиск последних версий."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'menu-wrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(PATTERN, a_tag.text)
        if text_match is not None:
            version = text_match.group('version')
            status = text_match.group('status')
        else:
            version = a_tag.text
            status = ' '
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)

    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """Поиск PEP'ов."""
    response = get_response(session, PEPS_URL)
    if response is None:
        return

    pep_dict = {}
    status_list = []

    soup = BeautifulSoup(response.text, features='lxml')
    pep_content = find_tag(
        soup,
        'section',
        attrs={'id': 'pep-content'}
    )
    tbody = pep_content.find_all('tbody')

    # Создание словаря: ссылка - статус из общей таблицы ({'/pep-0001': '', '/pep-0004': ''...})
    for body in tbody:
        tr = body.find_all('tr')
        for element in tr:
            td_pep_first = element.find('td')
            td_pep_second = element.find(
                'a',
                attrs={'class': 'pep reference internal'}
            )
            if td_pep_second != None:
                href = td_pep_second['href']
                if not href in pep_dict:
                    pep_dict[href] = td_pep_first.text[1:]

    # Переход по ссылке + сравнение с основной + подсчет статусов
    for href in tqdm(pep_dict, desc='Поиск и подсчет статусов: '):
        version_link = urljoin(PEPS_URL, href)
        response_link = session.get(version_link)
        soup = BeautifulSoup(response_link.text, features='lxml')
        dl = soup.find('dl')

        for string_in_dl in dl:
            if 'Status' in string_in_dl:
                status = string_in_dl.find_next_sibling().string

                if pep_dict[href] not in EXPECTED_STATUS:
                    error_msg = f'Не найден статус в общей таблице {pep_dict[href]}'
                    logging.error(error_msg, stack_info=True)
                    raise ParserFindStatusException(error_msg)

                if not status in EXPECTED_STATUS[pep_dict[href]]:
                    error_msg = (
                        f'Несовподающие статусы:'
                        f'Пришло: {status}'
                        f'Должно было: {EXPECTED_STATUS[pep_dict[href]]}'
                        )
                    logging.error(error_msg, stack_info=True)

                if status in PEP_STATUS:
                    status_list.append(status)

    # Считаем статусы + итоговое значение
    count_status_dict = dict(Counter(status_list))
    count_status_dict['Total'] = sum(count_status_dict.values())
    return count_status_dict


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
