from json import dumps

CMD_START_MSG = '''
Вас приветствует экспертная система Datatron!'''

TELEGRAM_START_MSG = '''
Я - экспертная система Datatron😊 Со мной вы можете быстро получить доступ к финансовым данным как России в целом, так и любого ее региона.

Бот поддерживает три режима работы: запрос на естественном языке в формате текста и голоса, а также inline-режим.

<b>Текстовый режим</b>
Просто напишите ваш запрос на естественном языке. Наример:
<code>расходы Москвы на спорт в 2013 году
дефицит Ярославской области</code>

<b>Голосовой режим</b>
Воспользуйтесь встроенной в Telegram записью голоса.'''
HELP_MSG = '''<b>Описание:</b>
Дататрон предоставляет пользователю доступ к открытым финансовым данным России и её субъектов.

<b>Функционал:</b>
Доступны inline-режим, ввод на естественном языке в текстовом и голосовом формате.

<b>Разработчики:</b>
Студенты Высшей школы экономики с факультетов Бизнес-информатики и Программной инженерии, которые стараются изменить мир к лучшему.

<b>Обратная связь</b>
Для нас важно ваше мнение о работе Datatron. Вы можете оставить отзыв о боте, написав его через пробел после команды /fb, или нажав кнопку "Оценить".

<b>Дополнительно:</b>
Использует <a href="https://tech.yandex.ru/speechkit/cloud/">Yandex SpeechKit Cloud</a>.'''
HELP_KEYBOARD = dumps({
    'inline_keyboard': [
        [
            {'text': 'Inline-режим', 'callback_data': '',
             'switch_inline_query': 'Долг странам, не вошедшим в парижский договор в 2016 году'},
            {'text': 'Оценить', 'url': 'https://telegram.me/storebot?start=datatron_bot'}
        ],
        [
            {'text': 'Ознакомительный ролик', 'callback_data': 'intro_video'}
        ]
    ]
})

RESPONSE_QUALITY = dumps({
    'inline_keyboard': [
        [
            {'text': '👍', 'callback_data': 'correct_response'},
            {'text': '😒', 'callback_data': 'incorrect_response'}
        ],
    ]
})

ERROR_CANNOT_UNDERSTAND_VOICE = 'Не удалось распознать текст сообщения😥 Попробуйте еще раз!'
ERROR_NULL_DATA_FOR_SUCH_REQUEST = 'К сожалению, этих данных в системе нет🤕'
ERROR_SERVER_DOES_NOT_RESPONSE = 'К сожалению, сейчас сервер не доступен😩 Попробуйте снова чуть позже!'
ERROR_NO_DOCS_FOUND = 'Документ по запросу не найден'
MSG_WE_WILL_FORM_DATA_AND_SEND_YOU = "Спасибо! Сейчас я сформирую ответ и отправлю его вам🙌"
MSG_NO_BUTTON_SUPPORT = 'Кнопочный режим более <b>не поддерживается</b>, так как не позволяет составлять ' \
                        'запрос достаточно быстро'
MSG_LEAVE_YOUR_FEEDBACK = 'Напишите после команды /fb ваш отзыв. \nНапример: <code>' \
                          '/fb Я думаю, что...</code>'
MSG_WE_GOT_YOUR_FEEDBACK = 'Cпасибо! Ваш отзыв записан :)'
MSG_IN_DEVELOPMENT = 'Данный запрос еще в стадии разработки'
MSG_LOG_HISTORY_IS_EMPTY = 'Истории логов еще нет😔 Не растраивай Datatron, задай вопрос!'

# Constants for m2
ERROR_PARSING = 'Что-то пошло не так🙃 Проверьте ваш запрос на корректность'
ERROR_INCORRECT_YEAR = 'Введите год из промежутка c 2007 по %s🙈'
ERROR_IN_MDX_REQUEST = 'Что-то пошло не так🙃 Данные получить не удалось:('


USELESS_PILE_OF_CRAP = (
    'в', 'без', 'до', 'из', 'к', 'на', 'по', 'о', 'от', 'перед', 'при', 'через', 'с', 'у', 'за', 'над', 'об', 'под',
    'про', 'для', 'не',
    'республика', 'республики',
    'республики', 'республик',
    'республике', 'республикам',
    'республику', 'республики',
    'республикой',
    'республикою', 'республиками',
    'республике', 'республиках',
    'область', 'области', 'областью', 'областей', 'областям', 'областями', 'областях',
    'автономный', 'автономного', 'автономному', 'автономного', 'автономным', 'автономном', 'автномном', 'автономная',
    'автономной', 'автономную', 'автономною', 'автономна', 'автономные', 'автономных', 'автономными',
    'федеральный', 'федерального', 'федеральному', 'федеральным', 'федеральном', 'федерален', 'федеральных',
    'федеральным', 'федеральными',
    'край', 'края', 'краю', 'краем', 'крае', 'краев', 'краям', 'краями', 'краях', 'год', 'году')

HELLO = ('хай',
         'привет',
         'здравствуйте',
         'приветствую',
         'прифки',
         'дратути',
         'hello')

HELLO_ANSWER = ('Привет! Начни работу со мной командой /search или сделай голосовой запрос',
                'Здравствуйте! Самое время ввести команду /search',
                'Приветствую!',
                'Здравствуйте! Пришли за финансовыми данными? Задайте мне вопрос!',
                'Доброго времени суток! С вами Datatron😊, и мы начинаем /search')

HOW_ARE_YOU = ('дела', 'поживаешь', 'жизнь')

HOW_ARE_YOU_ANSWER = ('У меня все отлично, спасибо :-)',
                      'Все хорошо! Дела идут в гору',
                      'Замечательно!',
                      'Бывало и лучше! Без твоих запросов только и делаю, что прокрастинирую🙈',
                      'Чудесно! Данные расходятся, как горячие пирожки! 😄')