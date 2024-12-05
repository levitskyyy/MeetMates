import pymysql
from pymysql.cursors import DictCursor
from random import randint as rd


class Dbworker:
    def __init__(self):
        ''' Констуктор '''
        self.connection = None
        self.cursor = None

    def open_connection(self):
        self.connection = pymysql.connect(host='',
                                          user='',
                                          password='',
                                          db='',
                                          charset='utf8mb4',
                                          cursorclass=DictCursor)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def user_exists(self, user_id):
        ''' Проверка есть ли юзер в бд '''
        self.open_connection()
        self.cursor.execute('SELECT * FROM `users` WHERE `telegram_id` = %s', (user_id,))
        result = self.cursor.fetchall()
        self.close_connection()
        return bool(len(result))

    def add_user(self, telegram_username, telegram_id):
        ''' Добавляем нового юзера '''
        self.open_connection()
        self.cursor.execute("INSERT INTO `users` (`telegram_username`, `telegram_id`) VALUES(%s,%s)",
                            (telegram_username, telegram_id))
        self.connection.commit()
        self.close_connection()

    def setting_referal_id(self, referal_id, user_id):
        self.open_connection()
        self.cursor.execute("UPDATE `users` SET `referal` = %s WHERE `telegram_id` = %s", (referal_id, user_id))
        self.connection.commit()
        self.close_connection()

    def get_users(self):
        ''' Получение всех юзеров с бд '''
        self.open_connection()
        self.cursor.execute('SELECT `telegram_id`, `active` FROM `users`')
        search = self.cursor.fetchall()
        result = [(i['telegram_id'], i['active']) for i in search]
        self.close_connection()
        return result

    def set_active(self, telegram_id, active):
        ''' Изменение актива '''
        self.open_connection()
        self.cursor.execute('UPDATE `users` SET `active` = (%s) WHERE `telegram_id` = (%s)', (active, telegram_id,))
        self.connection.commit()
        self.close_connection()

    def edit_game(self, game, telegram_id):
        ''' Изменения игры '''
        self.open_connection()
        self.cursor.execute('UPDATE `users` SET `game` = (%s) WHERE `telegram_id` = (%s)', (game, telegram_id))
        self.connection.commit()
        self.close_connection()

    def search(self, games, member_id):
        ''' Поиск '''
        self.open_connection()
        self.cursor.execute('SELECT `telegram_id`, `game` FROM `queue` WHERE `telegram_id` != (%s)',
                            (member_id,))
        search = self.cursor.fetchall()
        self.close_connection()
        for i in search:
            formatted = set(i['game'].split(' '))
            if len(formatted.intersection(games))!=0:
                return i['telegram_id']
            else:
                pass
        return None

    def get_game_user(self, telegram_id):
        ''' Получить информацию о поле юзера по его айдишнику '''
        self.open_connection()
        self.cursor.execute('SELECT `game` FROM `queue` WHERE `telegram_id` = (%s)', (telegram_id,))
        game = self.cursor.fetchall()[0]['game'].split(' ')
        self.close_connection()
        return set(game)

    def add_to_queue(self, telegram_id, gamelist: list):
        ''' Добавление в очередь '''
        self.open_connection()
        gamelist = ' '.join(gamelist)
        self.cursor.execute("INSERT INTO `queue` (`telegram_id`, `game`) VALUES(%s,%s)", (telegram_id, gamelist))
        self.connection.commit()
        self.close_connection()

    def delete_from_queue(self, telegram_id):
        ''' Функция удаляет из очереди '''
        self.open_connection()
        self.cursor.execute('DELETE FROM `queue` WHERE `telegram_id` = %s', (telegram_id,))
        self.connection.commit()
        self.close_connection()

    def update_connect_with(self, connect_with, telegram_id):
        ''' Обновление с кем общается пользователь '''
        self.open_connection()
        self.cursor.execute('UPDATE `users` SET `connect_with` = %s WHERE `telegram_id` = (%s)',
                            (connect_with, telegram_id))
        self.connection.commit()
        self.close_connection()

    def select_connect_with(self, telegram_id):
        ''' Функция для получения айдишника с кем общается человек '''
        self.open_connection()
        self.cursor.execute('SELECT `connect_with` FROM `users` WHERE `telegram_id` = (%s)', (telegram_id,))
        result = self.cursor.fetchone()
        self.close_connection()
        return result['connect_with']

    def select_connect_with_self(self, telegram_id):
        ''' Функция для получения айдишника по айдишнику с кем общается человек '''
        self.open_connection()
        self.cursor.execute('SELECT `telegram_id` FROM `users` WHERE `connect_with` = (%s)', (telegram_id,))
        result = self.cursor.fetchone()
        self.close_connection()
        return result['telegram_id']

    def log_msg(self, telegram_id, msg):
        ''' Функция которая логирует все сообщения юзеров друг другу '''
        self.open_connection()
        self.cursor.execute('INSERT INTO `all_messages` (`sender`,`message`) VALUES (%s,%s)', (telegram_id, msg))
        self.connection.commit()
        self.close_connection()

    def queue_exists(self, telegram_id):
        ''' Функция возвращает есть ли пользователь в очереди '''
        self.open_connection()
        self.cursor.execute('SELECT * FROM `queue` WHERE `telegram_id` = (%s)', (telegram_id,))
        result = self.cursor.fetchall()
        self.close_connection()
        return bool(len(result))

    def count_deactive(self):
        self.open_connection()
        self.cursor.execute('SELECT `active` FROM `users` WHERE `active` = 0')
        result = self.cursor.fetchall()
        self.close_connection()
        return len(result)

    def count_user(self):
        '''вывод количества юзеров'''
        self.open_connection()
        self.cursor.execute('SELECT * FROM `users`')
        result = self.cursor.fetchall()
        self.close_connection()
        return len(result)

    def add_count_msg_ref(self, telegram_id):
        ''' добавление кол-ва сообщений пользователю за реферала'''
        self.open_connection()
        self.cursor.execute('UPDATE `users` SET `all_msg` = `all_msg` + 25 WHERE `telegram_id` = (%s)', (telegram_id,))
        self.connection.commit()
        self.close_connection()

    def add_count_msg(self, telegram_id):
        ''' добавления кол-ва сообщений пользователю'''
        self.open_connection()
        self.cursor.execute('UPDATE `users` SET `all_msg` = `all_msg` + 1 WHERE `telegram_id` = (%s)', (telegram_id,))
        self.connection.commit()
        self.close_connection()

    def add_count_refs(self, telegram_id):
        ''' добавления кол-ва реферала пользователю'''
        self.open_connection()
        self.cursor.execute('UPDATE `users` SET `refs` = `refs` + 1 WHERE `telegram_id` = (%s)', (telegram_id,))
        self.connection.commit()
        self.close_connection()

    def top_rating(self):
        '''вывод топа по рейтингу'''
        self.open_connection()
        self.cursor.execute('SELECT `telegram_id` FROM `users` ORDER BY `all_msg` DESC LIMIT 5')
        data = self.cursor.fetchall()
        result = []
        for i in data:
            result.append(i['telegram_id'])
        self.close_connection()
        return result

    def get_name_user(self, telegram_id):
        ''' Получить информацию о поле юзера по его айдишнику '''
        self.open_connection()
        self.cursor.execute('SELECT `telegram_username` FROM `users` WHERE `telegram_id` = (%s)', (telegram_id,))
        result = self.cursor.fetchone()
        self.close_connection()
        return result['telegram_username']

    def get_count_all_msg(self, telegram_id):
        '''Вывод количества сообщений у юзера'''
        self.open_connection()
        self.cursor.execute('SELECT `all_msg` FROM `users` WHERE `telegram_id` = (%s)', (telegram_id,))
        result = self.cursor.fetchone()
        self.close_connection()
        return result['all_msg']

class UserInfo:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def open_connection(self):
        self.connection = pymysql.connect(host='',
                                          user='',
                                          password='',
                                          db='',
                                          charset='utf8mb4',
                                          cursorclass=DictCursor)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def user_selector(self, telegram_id):
        self.open_connection()
        self.cursor.execute('SELECT * FROM `description` WHERE `user_id` = (%s)', (telegram_id,))
        result = self.cursor.fetchone()
        self.close_connection()
        return result

    def user_selector_refs(self, telegram_id):
        self.open_connection()
        self.cursor.execute('SELECT * FROM `users` WHERE `telegram_id` = (%s)', (telegram_id,))
        result = self.cursor.fetchone()
        self.close_connection()
        return result

    def user_id(self, telegram_id, yet_in_base: False):
        self.open_connection()
        if yet_in_base:
            pass
        else:
            self.cursor.execute('INSERT INTO `description` (user_id) VALUES (%s)', (telegram_id,))
            self.connection.commit()
        self.close_connection()
        return None

    def user_nick(self, telegram_id, nickname):
        self.open_connection()
        self.cursor.execute('UPDATE `description` SET `user_nick` = (%s) WHERE `user_id` = (%s)',
                            (nickname, telegram_id))
        self.connection.commit()
        self.close_connection()
        return print('Nickname successfully updated')

    def user_likes(self, telegram_id, text):
        self.open_connection()
        self.cursor.execute('UPDATE `description` SET `user_like` = (%s) WHERE `user_id` = (%s)', (text, telegram_id))
        self.connection.commit()
        self.close_connection()
        return print('Description was successfully updated')

    def user_status(self, status, telergam_id):
        self.open_connection()
        self.cursor.execute('UPDATE `description` SET `user_status` = (%s) WHERE `user_id` = (%s)',
                            (status, telergam_id))
        self.connection.commit()
        self.close_connection()
        return print('Your status was created! To upgrade your status just talking or buy upgrade in our shop.')

    def steam_link(self, steam, telegram_id):
        self.open_connection()
        self.cursor.execute('UPDATE `description` SET `steamlink` = ? WHERE `user_id` = ?', (steam, telegram_id))
        self.connection.commit()
        self.close_connection()
        return print('Your steam was succesfully connected to your profile!')

    def get_all_user(self):
        self.open_connection()
        self.cursor.execute('SELECT * FROM `users`')
        data = self.cursor.fetchall()
        result = []
        for i in range(5):
            j = rd(0, len(data) - 1)
            if data[j]['status'] == 'Co-Founder 👑':
                result.append(f'{i + 1} - {data[j]["telegram_username"]} 👑')
            else:
                result.append(f'{i + 1} - {data[j]["telegram_username"]}')
        self.close_connection()
        return result

    def get_all_id_in_description(self):
        self.open_connection()
        result = []
        self.cursor.execute('SELECT `user_id` FROM `description`')
        data = self.cursor.fetchall()
        for i in data:
            result.append(i['user_id'])
        self.close_connection()
        return result
