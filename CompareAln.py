#!/usr/bin/env python3
import argparse

help_txt = '''Алгоритм сравнения двух множественных выравниваний

Запуск программы осуществляется из командной строки.

При запуске программы в качестве первого и второго аргументов подаётся два пути
к файлам со сравниваемыми выравниваниями в формате fasta.

В текстовый файл выводится список одинаково выравненных позиций (нумерация с 1).
Имя файла, в который будет записана выдача, подаётся в качестве третьего
аргумента при запуске программы (значение по умолчанию - out.txt).

В stdout при использовании соответственного аргумента выводится процент одинаково выравненных колонок от обоих выравниваний
и координаты блоков из идущих подряд одинаково выравненных колонок.
'''

parser = argparse.ArgumentParser(description=help_txt, epilog='Авторы: Александра Суворова и Никита Поломошнов')
parser.add_argument('-v', '--verbose',
                    action='store_true', help='При наличии данного аргумента в stdout выводится процент одинаково выровненных колонок от обоих выравниваний и координаты блоков из идущих подряд одинаково выровненных колонок.')
parser.add_argument('path1', help='Путь к файлу с первым множественным выравниванием')
parser.add_argument('path2', help='Путь к файлу со вторым множественным выравниванием')
parser.add_argument('output_name', default='out.txt', help='Имя файла, в который будет записана выдача')

arguments = parser.parse_args()
path1 = arguments.path1
path2 = arguments.path2
out_name = arguments.output_name


def read_alignment(file):
    seqs = {}
    for line in file:
        if line.startswith('>'):
            id = line[1:]
        else:
            seqs[id] = seqs.get(id, '') + line
    return seqs


file1 = open(path1)
seqs1 = read_alignment(file1)
file1.close()

file2 = open(path2)
seqs2 = read_alignment(file2)
file2.close()


def create_positions_list(seqs):
    lst = sorted(seqs)
    positions = []
    count = 0
    for c in seqs[lst[0]]:
        if c == '-':
            positions.append(['-'])  # Это гэп
        else:
            count += 1
            positions.append([count])  # Это номер аминокислоты в последовательности
    for key in lst[1:]:
        count = 0
        for i, c in enumerate(seqs[key]):
            if c == '-':
                positions[i].append('-')
            else:
                count += 1
                positions[i].append(count)
    return positions  # Это список, содержащий элементы, которые тоже списки;
    # Каждый маленький список соответствует одной колонке
    # Далее будем сравнивать эти колонки между собой


positions1 = create_positions_list(seqs1)
positions2 = create_positions_list(seqs2)


def compare_lists(lst1, lst2):
    pairs_lst = []  # Сюда будем записывать пары i, j номеров одинаковых колонок
    for i, elem1 in enumerate(lst1):
        for j, elem2 in enumerate(lst2):
            if elem1 == elem2:
                pairs_lst.append((i + 1, j + 1))
                break
    return pairs_lst


pairs = compare_lists(positions1, positions2)

out = open(out_name, 'w')
out.write('\n'.join([str(elem) for elem in pairs]))
out.close()


def find_blocks(pairs_lst):
    blocks = []
    start1, start2 = pairs_lst[0]
    is_block = False
    for i in range(len(pairs_lst) - 1):
        if pairs_lst[i][0] == pairs_lst[i + 1][0] - 1 and pairs_lst[i][1] == pairs_lst[i + 1][1] - 1:
            stop1, stop2 = pairs_lst[i + 1]
            is_block = True  # Проверка, чтобы не записывать "блоки" из 1 пары
        else:
            if is_block:
                blocks.append(((start1, stop1), (start2, stop2)))
                start1, start2 = pairs_lst[i + 1]
                is_block = False
            else:
                start1, start2 = pairs_lst[i + 1]
    if is_block:  # Это если вдруг есть блок в самом конце
        blocks.append(((start1, stop1), (start2, stop2)))
    return blocks


def stats(positions1, positions2, pairs_lst):
    percentage1 = len(pairs_lst) / len(positions1) * 100
    percentage2 = len(pairs_lst) / len(positions2) * 100
    blocks = find_blocks(pairs_lst)
    return percentage1, percentage2, blocks


if arguments.verbose:
    percentage1, percentage2, blocks = stats(positions1, positions2, pairs)
    print(f'Процент одинаково выравненных колонок от первого выравнивания: {percentage1:.02f}%')
    print(f'Процент одинаково выравненных колонок от второго выравнивания: {percentage2:.02f}%')
    print()
    for i, elem in enumerate(blocks):
        print(f'Блок {i + 1}:')
        print(f'Координаты начала и конца в первом выравнивании: {elem[0][0]}, {elem[0][1]}')
        print(f'Координаты начала и конца во втором выравнивании: {elem[1][0]}, {elem[1][1]}')
