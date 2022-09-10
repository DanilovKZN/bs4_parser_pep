import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import DATETIME_FORMAT, BASE_DIR  # RESULTS_DIR не пускают тесты


def control_output(results, cli_args):
    """Выбор режима вывода информации."""
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results):
    """Вывод в консоль."""
    if isinstance(results, dict):
        for row in results:
            print(f'{row}: {results[row]}')
    else:
        for row in results:
            print(*row)


def pretty_output(results):
    """Вывод в виде таблицы."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Вывод в файл."""
    # RESULTS_DIR.mkdir(exist_ok=True)
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    # file_path = RESULTS_DIR / file_name
    file_path = results_dir / file_name

    if isinstance(results, dict):
        result_list = []
        for date in results:
            result_list.append(
                {'Статус': date, 'Количество': results[date]}
            )
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            column_names = ['Статус', 'Количество']
            writer = csv.DictWriter(f, fieldnames=column_names)
            writer.writeheader()
            writer.writerows(result_list)
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, dialect='unix')
            writer.writerows(results)

    logging.info(f'Файл с результатами был сохранён: {file_path}')
