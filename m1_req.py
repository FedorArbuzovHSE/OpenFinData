import re
import constants
import datetime
import random as rng
from m1_work_class import quest

list_of_int = []
useless_word_in_sen = []

key_words_quantity = len(constants.key_words)


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def simple_split(s):
    s = s.lower()
    s = re.sub(r'[^\w\s]', '', s)
    s_splitted = s.split()
    return s_splitted


def hello_back(s):
    for _ in simple_split(s):
        if _ in constants.hello:
            return constants.hello_answer[rng.randint(0, len(constants.hello) - 1)]
        elif _ in constants.how_are_you:
            return constants.i_am_fine[rng.randint(0, len(constants.i_am_fine) - 1)]


# Adaptive allowable mistake for distance between user word and key word
def allowable_error(word):
    allowable_inaccuracy = {
        1: 0, 2: 0, 3: 1, 4: 2,
        5: 2, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 5, 11: 5, 12: 5,
        13: 5, 14: 5, 15: 6, 16: 6,
        17: 6, 18: 6, 19: 6, 20: 6
    }

    length = len(word)
    if length > 20:
        return 6

    return allowable_inaccuracy[length]


# the Levenstein distance algorithm
def distance(a: object, b: object) -> object:
    """Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]


# Основная функция
def check_the_territories(str_user):
    minimum_value = key_words_quantity
    index_of_the_most_likely_variant = 0
    i = 0
    for _ in constants.key_words:
        distance_between_input_and_table_data = distance(str_user, constants.key_words[i])
        if (distance_between_input_and_table_data < minimum_value and
                    distance_between_input_and_table_data <= allowable_error(str_user)):
            minimum_value = distance_between_input_and_table_data
            index_of_the_most_likely_variant = i
        i += 1

    return index_of_the_most_likely_variant


# Основная функция
def check_the_sphere(str_user):
    minimum_value = key_words_quantity
    index_of_the_most_likely_variant = 0
    i = 0
    for _ in constants.sphere:
        distance_between_input_and_table_data = distance(str_user, constants.sphere[i])
        if distance_between_input_and_table_data < minimum_value:
            minimum_value = distance_between_input_and_table_data
            index_of_the_most_likely_variant = i
        i += 1

    return index_of_the_most_likely_variant


def main_place(s):
    s = re.sub(r'[^\w\s]', '', s)
    list1 = s.split()
    for s in constants.useless_pile_of_crap:
        if s in list1:
            list1.remove(s)

    i = 0
    for _ in list1:
        result = check_the_territories(list1[i])
        i += 1
        for s in constants.key_words[19:-8]:
            if s == constants.key_words[result]:
                return s


def main_sector(s):
    s = re.sub(r'[^\w\s]', '', s)
    list1 = s.split()
    for s in constants.useless_pile_of_crap:
        if s in list1:
            list1.remove(s)
    i = 0
    for _ in list1:
        result = check_the_territories(list1[i])
        i += 1
        for s in constants.key_words[-8:]:
            if s == constants.key_words[result]:
                return s


def main_func(s):
    s = re.sub(r'[^\w\s]', '', s)
    list1 = s.split()
    list_of_int = []
    for i in range(len(list1)):
        if represents_int(list1[i]):
            list_of_int.append(list1[i])

    for s in constants.useless_pile_of_crap:
        if s in list1:
            list1.remove(s)

    for s in list_of_int:
        if s in list1:
            list1.remove(s)

    user_req = quest()

    i = 0
    now_date = datetime.date.today()
    for _ in list1:
        result = check_the_territories(list1[i])
        result_sphere = check_the_sphere(list1[i])

        if constants.key_words[result] == 'плановый':
            user_req.planned_or_actual = 'плановый'
        if constants.key_words[result] == 'фактический':
            user_req.planned_or_actual = "фактический"
        if constants.key_words[result] == 'бюджет':
            user_req.sector = 'бюджет'
        if constants.key_words[result] == "доход":
            user_req.subject = "доходы"
        if constants.key_words[result] == "расход":
            user_req.subject = "расходы"
        if constants.key_words[result] == "дефицит":
            user_req.subject = "дефицит"
        if constants.key_words[result] == 'текущий':
            user_req.year = now_date.year
            user_req.planned_or_actual = 'текущий'
        if constants.key_words[result] == 'прошлый':
            user_req.year = now_date.year - 1

        for s in constants.key_words[21:-11]:
            if s == constants.key_words[result]:
                user_req.place = s

        if constants.key_words[result] == 'налоговые':
            user_req.sector = 'налоговый'
        if constants.key_words[result] == 'неналоговые':
            user_req.sector = 'неналоговый'

        for s in constants.key_words[-11:]:
            if s == constants.key_words[result]:
                user_req.sector = str(result - (key_words_quantity - 13))

        i += 1
    if user_req.sector == "":
        user_req.sector = "null"
    if user_req.planned_or_actual == "":
        user_req.planned_or_actual = "null"
    if user_req.place == "":
        user_req.place = "null"
    if user_req.year == 0 or user_req.year == now_date.year:
        if len(list_of_int) != 0:
            user_req.year = int(list_of_int[0])
        else:
            user_req.year = "null"

    user_r = [user_req.subject, user_req.place.lower(), user_req.year, user_req.sector, user_req.planned_or_actual]
    return user_r
