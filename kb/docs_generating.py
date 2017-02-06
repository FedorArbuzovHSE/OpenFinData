from kb.db_creation import *
from itertools import combinations, chain, product
from kb.support_library import logging, query_data, filter_combinations, report, docs_needed
from os import getcwd, listdir, mkdir
from os.path import isfile, join
import json
import pycurl


def get_cube_name(cube_id):
    """Получение названия куба по id"""

    for cube in Cube.raw('select name from cube where id = %s' % cube_id):
        return cube.name


def get_cube_measures_dimensions(cube_id):
    """Формирование словарей имеющихся у конкретного куба измерений и мер"""

    # словарь мер вида {id: (вербальное значение, формальное значение)}
    # например, {1: (текущие расходы, VALUE), 2: (плановые доходы, PLANONYEAR)}
    md = {}
    for m in Cube_Value.raw('select value_id from cube_value where cube_id = %s' % cube_id):
        for v in Value.raw('select nvalue, fvalue from value where id = %s' % m.value_id):
            md[m.value_id] = (v.nvalue, v.fvalue)

    # словарь измерений вида {id: формальное название измерения}
    # например, {1: 'TERRITORIES', 2: 'RZPR', 3: 'BGLEVELS'}
    dd = {}
    for cd in Cube_Dimension.raw('select dimension_id from cube_dimension where cube_id = %s' % cube_id):
        for d in Dimension.raw('select label from dimension where id = %s' % cd.dimension_id):
            dd[cd.dimension_id] = d.label

    return md, dd


def get_all_dimension_combinations(dd, md):
    """Создание всех возможных комбинаций измерений

    Вход: словарь из всех измерений и мер куба
    Выход: массив из возможных наборов комбинаций измерений и мер"""

    # Строк для логирования результатов данного методы
    all_possible_combinations = ''

    # все возможные сочетания измерений — например, [(1,2),(1,2,3),(1,2,5)...], где цифры - id измерений
    dimension_sets = []

    # Массив для хранения полного набора комбинаций
    dimension_measure_sets = []

    # выбираем все возможные комбинации измерений по i элементов, где i больше либо равен 1 и
    # меньше либо равен количеству измерений куба
    for number in range(1, len(dd) + 1):
        combination_with_i_items = list(combinations(dd.keys(), number))

        # добавляем получившихся набор комбинаций для i-го количества элементов в общий массив
        dimension_sets.append(combination_with_i_items)

    # уплощаем массив, лишая его лишней вложенности
    dimension_sets = list(chain(*dimension_sets))

    for m_id in md:
        for idx, d_set in enumerate(dimension_sets):
            # логируем получившийся набор
            all_possible_combinations += '{}. M:{} D:{}\n'.format(idx, md[m_id][1],
                                                                  ''.join([dd[d_id] + ' ' for d_id in d_set]))

            # добавляем получившийся объединенный набор (мера + измерение) в массив
            dimension_measure_sets.append([m_id, d_set])

    # записываем в файл получившиеся наборы
    logging('1st all_possible_combinations', all_possible_combinations)

    return dimension_measure_sets


def generate_documents(md, dd, dimension_measure_sets, cube_name):
    """Генерация документов

    Вход: cловари из имеющихся мер и измерений куба, полный набор сочитающихся измерений и мер, название куба
    Выход: набор документов"""

    # переменная для хранения всех значений измерений куба
    dim_vals = []

    # выбор из БД значений всех измерений куба
    for idx, d_id in enumerate(dd):
        dim_vals.append([])
        dim_vals[idx].append(d_id)
        dim_vals[idx].append([])
        for dv in Dimension_Value.raw('select value_id from dimension_value where dimension_id = %s' % d_id):
            for v in Value.raw('select fvalue, nvalue from value where id = %s' % dv.value_id):
                dim_vals[idx][1].append((v.nvalue, v.fvalue))

    # переменная для хранения сгенерированных документов
    docs = []

    # шаблон MDX запроса
    mdx_template = 'SELECT {{[MEASURES].[{}]}} ON COLUMNS FROM [{}.DB] WHERE ({})'

    # TODO: рефакторить код
    # TODO: добавить фильтры
    i = 0
    # для каждого набора измерений с мерой
    for dim_set in dimension_measure_sets:
        # массив со всеми (за некоторыми исключениями) значениями определенного набора измерений
        set_values_list = []

        # для каждого id измерения в наборе измерений
        for d_id in dim_set[1]:
            # выбор нужного измерения со значениями
            dim_val = list(filter(lambda d: d[0] == d_id, dim_vals))[0]

            set_values_list.append(dim_val[1])

        # все возможные сочетания измерений со значениями
        combs = list(product(*set_values_list))
        combs = filter_combinations(combs, dim_set[1], dd)

        for item in combs:
            # cтроки для сохранения нескольких фомальных/вербальных значений переменных
            fvalues, nvalues = '', ''

            for elem, d_id in zip(item, dim_set[1]):
                fvalues += '[{}].[{}],'.format(dd[d_id], elem[1])
                nvalues += elem[0] + ' '

            # убираем ненунжныю запятую и пробел в конце строки
            fvalues, nvalues = fvalues[:-1], nvalues[:-1]

            # mdx-запрос
            fr = mdx_template.format(md[dim_set[0]][1], cube_name, fvalues)

            # вербальный запрос
            nr = md[dim_set[0]][0] + ' ' + nvalues

            docs.append({'id': i, 'mdx': fr, 'verbal': nr})
            i += 1

            # каждые 5000 документов выводим их количество
            if i % 5000 == 0:
                print(len(docs))

                # if i > 2000:
                #     break

    print('Документов создалось: {}'.format(len(docs)))
    return docs


def learn_model(docs):
    """Отсеивание нерабочих документов

    Вход: набор документов
    Выход: набор документов только с работающими запросами"""

    # Строк для логирования результатов данного методы
    only_not_none_requests = ''

    new_docs = []
    for idx, item in enumerate(docs):
        request_result = query_data(item['mdx'])
        idx_step_string = '{}. {}: {}\n'.format(idx, item['mdx'], request_result[1])
        print(idx_step_string[:-1])

        only_not_none_requests += idx_step_string

        if request_result[0]:
            new_docs.append(item)

    print('Документов осталось: {0}, сокращение: {1:.2%}'.format(len(new_docs), len(new_docs)/len(docs)))
    logging('only_not_none_requests', only_not_none_requests)

    return new_docs


def generate_json(docs, cube_name, max_obj_num=100000):
    """Генерация json документов

    Вход: набор документов
    Выход: None"""

    # Создаем папку для хранения сгенерированных документов для конкретного куба
    try:
        mkdir(cube_name)
    except FileExistsError:
        pass

    i, j = 0, max_obj_num

    for idx in range(len(docs) // max_obj_num + 1):
        # указываем путь и название файла для записи
        doc_name = '{0}\\{1}\\{1}_{2}.json'.format(getcwd(), cube_name, idx)
        json_str = json.dumps(docs[i:j])

        with open(doc_name, 'w', encoding='utf-8') as file:
            file.write(json_str)

        i += max_obj_num
        j += max_obj_num


def index_created_documents(cube_name):
    """Генерация json документов

    Вход: название куба
    Выход: None"""

    # создание пути к папке, в которой хранятся документы
    path = '{}\\{}'.format(getcwd(), cube_name)

    # получение названия всех файлов, в папке
    json_file_names = [f for f in listdir(path) if isfile(join(path, f))]

    c = pycurl.Curl()
    c.setopt(c.URL, 'http://localhost:8983/solr/kb/update?commit=true')

    # индексирование всех файлов в Solr
    # см. http://pycurl.io/docs/latest/quickstart.html
    # это работает, но непонятны детали (см на 182-248 стр. из Apache Solr Reference Guide)
    for file_name in json_file_names:
        c.setopt(c.HTTPPOST,
                 [
                     ('fileupload',
                      (c.FORM_FILE, r'C:\Users\User\PycharmProjects\Simplify\%s\%s' % (cube_name, file_name),
                       c.FORM_CONTENTTYPE, 'application/json')
                      ),
                 ])
        c.perform()


for cube in Cube.raw('select id from cube'):
    id_cube = cube.id
    name_cube = get_cube_name(id_cube)

    mdict, ddict = get_cube_measures_dimensions(id_cube)

    measure_dim_sets = get_all_dimension_combinations(ddict)

    dim_count, doc_count = docs_needed(mdict, ddict, measure_dim_sets)

    documents = generate_documents(mdict, ddict, measure_dim_sets, name_cube)

    # # обучение путем проверки корректности документа, через реальный запрос к серверу
    # # !ОСТОРОЖНО!
    # only_working_documents = learn_model(documents)
    # # !ОСТОРОЖНО!

    generate_json(documents, name_cube)

    # generate_json(only_working_documents, name_cube, max_obj_num=5000)

    # index_created_documents(name_cube)

    report(id_cube, name_cube, mdict, ddict, measure_dim_sets, dim_count, doc_count)