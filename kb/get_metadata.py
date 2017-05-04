import requests
import json


class Level:
    def __init__(self, name='', caption='', unique_name='', level_number=''):
        self.name = name
        self.caption = caption
        self.unique_name = unique_name
        self.level_number = level_number


class DimentionHeirarchy:
    def __init__(self, name='', caption='', unique_name='', levels=[], default_member=''):
        self.name = name
        self.caption = caption
        self.default_member = default_member
        self.unique_name = unique_name
        self.levels = levels


class Dimension:
    def __init__(self, name='', caption='', unique_name='', dimention_heirarchies=[]):
        self.name = name
        self.caption = caption
        self.unique_name = unique_name
        self.dimention_heirarchies = dimention_heirarchies


class CubeData:
    def __init__(self, name='', caption='', last_update='', dimensions=[], measures=[], values=[], formal_name='',
                 cube_elements=[]):
        self.name = name  # Для наших кубов DB по дефолту
        self.caption = caption  # Доходы блаблабла
        self.last_update = last_update  # Дата последнего изменения - пока не проставляется в кубах
        self.dimensions = dimensions  # измерения - Territories, KD, BGLevels...
        self.measures = measures  # measures - хранилище value
        self.formal_name = formal_name  # INDO03
        self.cube_elements = cube_elements

    def toJSON(self):
        return json.dumps(self, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)


class Measure:
    def __init__(self, name='', caption='', uniqueName=''):
        self.name = name
        self.caption = caption
        self.uniqueName = uniqueName


class DimensionElement:
    def __init__(self, name='', caption='', uniqueName='', childCount='', levelDepth='', levelName='',
                 hierarchyName=''):
        self.name = name
        self.caption = caption
        self.uniqueName = uniqueName
        self.childCount = childCount
        self.levelDepth = levelDepth
        self.levelName = levelName
        self.hierarchyName = hierarchyName


def get_data(cube_list):
    cube_data = []

    for c in cube_list:
        cube = CubeData()
        cube.formal_name = c
        cube.name = "DB"

        data = {'schemaName': cube.formal_name,
                'cubeName': cube.name}

        r = requests.post('http://conf.prod.fm.epbs.ru/mdxexpert/Cube', data)
        j = json.loads(r.text)

        # Проверяем данные о последнем обновлении куба, если они вдруг где-то есть
        if j["lastUpdated"] is not None:
            cube.last_update = j["lastUpdated"]
        else:
            cube.last_update = ''

        # переменные-счетчики
        i = 0
        e = 0
        # массив для хранения измерений
        dims = []

        # Собираем все метаданные по измерениям
        while i < len(j["dimensions"]):
            dim = Dimension()
            heirarchy = DimentionHeirarchy()
            heirarchy_levels = []

            # собираем уровни иерархии в один кусок
            while e < len(j["dimensions"][i]["hierarchies"][0]["levels"]):
                level1 = Level()
                level1.name = j["dimensions"][i]["hierarchies"][0]["levels"][e]["name"]
                level1.caption = j["dimensions"][i]["hierarchies"][0]["levels"][e]["caption"]
                level1.unique_name = j["dimensions"][i]["hierarchies"][0]["levels"][e]["uniqueName"]
                heirarchy_levels.append(level1)
                e += 1

            # собираем остальные параметры для иерархии этого dimension
            heirarchy.name = j["dimensions"][i]["hierarchies"][0]["name"]
            heirarchy.caption = j["dimensions"][i]["hierarchies"][0]["caption"]
            heirarchy.unique_name = j["dimensions"][i]["hierarchies"][0]["uniqueName"]
            heirarchy.levels = heirarchy_levels
            if j["dimensions"][i]["hierarchies"][0]["defaultMember"] is not None:
                heirarchy.default_member = j["dimensions"][i]["hierarchies"][0]["defaultMember"]
            else:
                heirarchy.default_member = ''
            # собираем информацию для dimension
            dim.name = j["dimensions"][i]["name"]
            dim.caption = j["dimensions"][i]["caption"]
            dim.unique_name = j["dimensions"][i]["uniqueName"]
            dim.dimention_heirarchies = heirarchy
            dims.append(dim)
            i += 1

        cube.dimensions = dims
        # счетчик
        i = 0
        # массив для мер
        measures = []
        # получаем информацию о measures
        while i < len(j["measures"]):
            new_measure = Measure()
            new_measure.name = j["measures"][i]["name"]
            new_measure.caption = j["measures"][i]["caption"]
            new_measure.uniqueName = j["measures"][i]["uniqueName"]
            measures.append(new_measure)
            i += 1

        cube.measures = measures

        # вот сейчас в поле cube собрана полная метаинформация

        # Имея полную метаинформацию, мы теперь можем собрать информацию обо всех элементах
        # каждого измерения.

        # массив для хранения элементов без дочерних элементов
        NoChildren = []
        # массив для хранения тех элементов, у которых есть дочерние.
        ChildArray = []

        i = 0

        # Заносим в "детный" массив измерения
        while i < len(cube.dimensions):
            dimen = cube.dimensions[i]
            child_request = {
                'schemaName': cube.formal_name,
                'cubeName': cube.name,
                'dimensionName': dimen.name,
                'rootUniqueName': ''
            }
            child = requests.post('http://conf.prod.fm.epbs.ru/mdxexpert/Members', child_request)
            child_json = json.loads(child.text)
            if child_json[0]["childCount"] != 0:
                ChildArray.append(child_json[0])
            else:
                NoChildren.append(child.text)
            i += 1

        # Дальше логика такая:
        # 1) Берем нулевой элемент из детного массива, называем его материнским элементом
        # 2)Получаем для материнского элемента массив детей
        # 3) Итерируемся по массиву и проверяем, есть ли дети у детей(те чекаем чайлдкаунт). Если есть, то детей закидываем в детный массив, если нет, то в бездетный
        # 4) После завершения итераций материнский элемент объявляем бездетным (так как всех детей у него проверили)
        # 5) Удаляем материнский элемент из детного массива и добавляем в бездетный

        # Повторяем цикл пока детный массив не опустеет
        j = 0
        while len(ChildArray) > 0:
            mother_element = ChildArray[0]
            request_for_children = {
                'schemaName': cube.formal_name,
                'cubeName': cube.name,
                'dimensionName': mother_element["hierarchyName"],
                'rootUniqueName': mother_element["uniqueName"]
            }
            children = requests.post('http://conf.prod.fm.epbs.ru/mdxexpert/Members', request_for_children)
            children_json = json.loads(children.text)
            i = 0
            while i < len(children_json):
                comma = children_json[i]["levelName"].find(',')
                level_name = children_json[i]["levelName"][3:comma]
                if int(level_name) <= 5:
                    if children_json[i]["childCount"] > 0:
                        ChildArray.append(children_json[i])
                    else:
                        NoChildren.append(children_json[i])
                i += 1
            NoChildren.append(mother_element)
            ChildArray.pop(0)
            j += 1
            print('Элементов без детей найдено ', len(NoChildren), '; Элементов с детьми найдено ', len(ChildArray))

        print('Процесс поиска всех дочерних элементов завершен')

        cube.cube_elements = NoChildren

        cube_data.append(cube)

    return cube_data

def data_to_json(cube_data):
    return json.dumps([item.toJSON() for item in cube_data])



# all_cubes_list = ['INYR03', 'CLDO01', 'INDO01', 'EXYR03', 'EXDO01', 'CLDO01', 'FSYR01', 'CLDO02']
all_cubes_list = ['INYR03', 'CLDO01']

data = get_data(all_cubes_list)
json_data = data_to_json(data)
# json_cube = cube.toJSON()
# f = open('textos.txt', 'w')
# f.write(json_cube)
# f.close()