import vk
import requests
import sqlite3
import time
import os
import datetime
from os.path import expanduser
home = expanduser("~")



id = 6851565

service_key = 'ENTER YOUR KEY'
session_user = None
session_service = vk.Session(
    access_token=service_key)  # logged in with application rights #With this token we can't get user's wall, while we can do it using ordinary login and password
api_user = None
api_service = vk.API(session_service)


class LikesService:
    def __init__(self):

        self.conn = sqlite3.connect('VkLikeBot/vkService/users.db')
        self.c = self.conn.cursor()

    def get_api_service(self):
        return api_service

    def get_api_user(self): #Авторизуемся только 1 раз при первом запросе
        global api_user
        if api_user is None:
            session_user = vk.AuthSession(app_id=id, user_login='', user_password='')
            api_user=vk.API(session_user)
            return api_user
        else: return api_user

    #Период в формате (1, 2, 21)
    def fill_fans(self, wall_posts_count, wall_photos_count, profile_photos_count, album_photos_count, aim_id=None,
                  aim_domain=None, gen=None, period_in_days=None):

        if gen is None:
            gen = 1
        if aim_id is None:
            aim_id = api_service.utils.resolveScreenName(screen_name=aim_domain, v='5.92')['object_id']

        if period_in_days is not None:
            dt = datetime.datetime.now()
            redline= (dt-datetime.timedelta(days=period_in_days)).timestamp()
        else: redline=-2203653584



        messages = set()

        fans_to_likes_count = {}

        # Лайки на постах
        #############################################################################################
        if wall_posts_count != 0:
            print("Searching likes on wall posts")
            try:
                wall = api_service.wall.get(owner_id=aim_id, count=wall_posts_count, v='5.92')
            except requests.exceptions.ReadTimeout as r:
                print("Время ожидания постов на странице истекло")
                return
            except vk.exceptions.VkAPIError as e:
                s = str(e)
                if "Rate limit reached" in s:
                    print("Лимит на доступ к постам исчерпан")
                    wall_photos_count += wall_posts_count
                    wall = {'items': [], 'count': 0}
                else:
                    print("Доступ к стене")
                    messages.add("Доступ к профилю закрыт")
                    wall = {'items': [], 'count': 0}

            # iter1=1 #Для ограничения количества запросов в секунду

            for i in wall['items']:
                if i['date'] > redline:
                    #print('{} is Ok!'.format(datetime.datetime.fromtimestamp(i['date'])))
                    post_id = i['id']
                    try:
                        fans_likes = api_service.likes.getList(type='post', owner_id=aim_id, item_id=post_id, v='5.92')

                    except requests.exceptions.ReadTimeout as r:
                        print("Время ожидания лайков на посте истекло")
                        continue
                    except vk.exceptions.VkAPIError as e:
                        print("Доступ к лайкам на стене закрыт")
                        break

                    # if iter1%requests_per_second is 0:
                    #     time.sleep(1)
                    # iter1+=1
                    # l_count=0

                    for f_id in fans_likes['items']:
                        if f_id not in fans_to_likes_count:
                            fans_to_likes_count[f_id] = 1
                        else:
                            fans_to_likes_count[f_id] += 1
                else: break
            wall_posts_count -= wall['count']
            if wall_posts_count < 1:
                messages.add('Лимит количества фотографий исчерпан')
            else:
                wall_photos_count += wall_posts_count  # Остаток добавляем к следующим лайкам
            print("Finished searching on wall posts")

        #######################################################################################
        # Wall photos

        if wall_photos_count != 0:
            print("Searching for likes on wall photos")
            try:
                photos = api_service.photos.get(owner_id=aim_id, album_id='wall', count=wall_photos_count,
                                                rev=1, v='5.92')
            except requests.exceptions.ReadTimeout as r:
                print("Время ожидания фотографий на стене истекло")
                photos = {'items': [], "count": 0}
            except vk.exceptions.VkAPIError as e:
                print("Доступ к фото стене закрыт")
                photos = {'items': [], "count": 0}

            for photo in photos['items']:
                if photo['date'] > redline:
                    #print('{} is Ok!'.format(datetime.datetime.fromtimestamp(photo['date'])))

                    try:
                        likes = api_service.likes.getList(type='photo', owner_id=aim_id, item_id=photo['id'], v='5.92')
                    except requests.exceptions.ReadTimeout as r:
                        print("Время ожидания лайков на фотографиях на стене истекло")
                        continue
                    except vk.exceptions.VkAPIError as e:
                        print("Доступ к лайкам на фото на стене закрыт")
                        break

                    for f_id in likes['items']:
                        if f_id not in fans_to_likes_count:
                            fans_to_likes_count[f_id] = 1
                        else:
                            fans_to_likes_count[f_id] += 1
                else: break

            wall_photos_count -= photos['count']
            if wall_photos_count < 1:
                messages.add('Лимит количества фотографий исчерпан')
            else:
                profile_photos_count += wall_photos_count

            print("Finished searching on wall photos")
        ################################################################################
        if profile_photos_count != 0:
            print("Searching for likes on profile photos")

            try:
                photos = api_service.photos.get(owner_id=aim_id, album_id='profile', count=profile_photos_count,
                                                rev=1, v='5.92')
            except requests.exceptions.ReadTimeout as r:
                print("Время ожидания фото профиля истекло")


            except vk.exceptions.VkAPIError as e:
                print("Доступ к фото профиля закрыт")

            for photo in photos['items']:
                if photo['date'] > redline:
                    #print('{} is Ok!'.format(datetime.datetime.fromtimestamp(photo['date'])))
                    try:
                        likes = api_service.likes.getList(type='photo', owner_id=aim_id, item_id=photo['id'], v='5.92')
                    except requests.exceptions.ReadTimeout as r:
                        print("Время ожидания лайков на фото профиля истекло")
                        continue
                    except vk.exceptions.VkAPIError as e:
                        print("Доступ к лайкам на фото профиля закрыт")
                        break

                    for f_id in likes['items']:
                        if f_id not in fans_to_likes_count:
                            fans_to_likes_count[f_id] = 1
                        else:
                            fans_to_likes_count[f_id] += 1
                else: break
            profile_photos_count -= photos['count']
            if profile_photos_count < 1:
                messages.add('Лимит количества фотографий исчерпан')
            else:
                album_photos_count += profile_photos_count
            print("Finished searching in profile photos")
        ################################################################################

        if album_photos_count != 0:
            print("Searching for likes in album photos")
            try:
                albums = api_service.photos.getAlbums(owner_id=aim_id, v='5.92')
            except requests.exceptions.ReadTimeout as r:
                print("Время ожидания альбомов истекло")
                albums = {'items': [], "count": 0}
            except vk.exceptions.VkAPIError as e:
                print("Доступ к альбомам закрыт")
                albums = {'items': [], "count": 0}

            for album in albums['items']:
                try:
                    photos = api_service.photos.get(owner_id=aim_id, album_id=album['id'], count=album_photos_count,
                                                    rev=1, v='5.92')
                except requests.exceptions.ReadTimeout as r:
                    print("Время ожидания фото в альбоме истекло")
                    continue
                except vk.exceptions.VkAPIError as e:
                    print("Доступ к фото в альбоме закрыт")
                    photos = {'items': [], 'count': 0}

                for photo in photos['items']:
                    if photo['date'] > redline:
                        #print('{} is Ok!'.format(datetime.datetime.fromtimestamp(photo['date'])))
                        try:
                            likes = api_service.likes.getList(type='photo', owner_id=aim_id, item_id=photo['id'], v='5.92')
                        except vk.exceptions.VkAPIError as e:
                            print("Доступ к альбому закрыт")
                            break
                        except requests.exceptions.ReadTimeout as r:
                            print("Время ожидания лайков к фото истекло")
                            continue

                        for f_id in likes['items']:
                            if f_id not in fans_to_likes_count:
                                fans_to_likes_count[f_id] = 1
                            else:
                                fans_to_likes_count[f_id] += 1
                    else: break
                album_photos_count -= photos['count']
                if album_photos_count < 1:
                    messages.add('Лимит количества фотографий исчерпан')
                    break

            messages.add("Все фото и посты проверены, оставшийся депозит= {}".format(album_photos_count))

        fans_tuples = [(aim_id, key, fans_to_likes_count[key], gen) for key in fans_to_likes_count]
        try:
            self.c.executemany("INSERT OR IGNORE INTO fans VALUES (?, ?, ?, ?)", fans_tuples)
        except sqlite3.Error as e:
            messages.add()
        self.conn.commit()

        return len(fans_tuples)

    def get_fanat(self, aim_id=None, aim_domain=None):

        if aim_id is None:
            aim_id = api_service.utils.resolveScreenName(screen_name=aim_domain, v='5.92')['object_id']

        self.c.execute("SELECT max(likes_count), fan_id FROM fans where aim_id= :aim_id", {'aim_id': aim_id})
        print('fanat: ', self.c.fetchone())

        self.c.execute("SELECT count(aim_id) FROM friends")
        print(self.c.fetchone())
        self.c.execute("SELECT max (friend_type) FROM friends")
        print(self.c.fetchone())

        return self.c.fetchone()

    # Заполняем фанов для всех фанов цели. Это и будет цеполчка друзей с разными поколениями
    # fans_count - количество фанов, которое будет в таблице. От него линейно зависит время
    # friends_count - количество друзей, которые надо проверять для каждого чела. Время зависит полиномиально
    # можно ввести линейную характеристику для проверки друзей
    # можно ввести необязательный критерий остановки по истечении времени
    def fill_fans_by_likes_and_friends(self, friends_count, wall_posts_count, wall_photos_count,
                                       profile_photos_count, album_photos_count, aim_id=None,
                                       aim_domain=None, fans_count=None, time_in_minutes=None, period_in_days=None):
        start_time = time.time()

        if aim_id is None:
            aim_id = api_service.utils.resolveScreenName(screen_name=aim_domain, v='5.92')['object_id']
        if fans_count is None:
            fans_count = float("inf")

        self.c.execute(
            "DELETE FROM fans where aim_id IS NOT NULL ")  # Удаляем всех фанов, чтобы не записывать второй раз

        gen = 0

        # Заполняем 0-е поколение
        count2 = self.fill_fans(wall_posts_count, wall_photos_count, profile_photos_count, album_photos_count, aim_id,
                                gen=0, period_in_days=period_in_days)
        if type(count2) is int:
            fans_count -= count2
        # Тащим фанов 0-го поколения
        fans_rel = self.__get_fans_by_gen(gen)

        for fan_rel in fans_rel['items']:
            # Для каждого из вытащенных фанов заполняем 1-е поколение фанов
            count2 = self.fill_fans(wall_posts_count, wall_photos_count, profile_photos_count,
                                    album_photos_count, aim_id=fan_rel, gen=1, period_in_days=period_in_days)
            if time_in_minutes is not None and (time.time() - start_time) > time_in_minutes * 60:
                print("Время истекло")
                return
            if type(count2) is int:
                fans_count -= count2
                if fans_count < 1:
                    return print("Депозит исчерпан, count = {}".format(fans_count))

        # = Тащим список друзей
        if friends_count is not 0:
            try:
                friends = api_service.friends.get(user_id=aim_id, count=friends_count,
                                                  v='5.92')  # 5000 - просто чтобы вытащить ВСЕХ друзей
            except vk.exceptions.VkAPIError as e:
                print("Vk friends.get error")
                return
                friends = {'count': 0, 'items': []}
        else:
            friends = {'count': 0, 'items': []}

        friends['items'] = [x for x in friends['items'] if x not in fans_rel['items']]
        friends['count'] = len(friends['items'])

        gen = 1

        for friend in friends['items']:
            count3 = self.fill_fans(wall_posts_count, wall_photos_count, profile_photos_count, album_photos_count,
                                    aim_id=friend, gen=1, period_in_days=period_in_days)
            if time_in_minutes is not None and (time.time() - start_time) > time_in_minutes * 60:
                print("Время истекло")
                return
            if type(count3) is int:
                fans_count -= count3
                if fans_count < 1:
                    print("Депозит исчерпан, count = {}".format(fans_count))
                    return

        while fans_count > 0:

            # Тащим фанов i-го поколения
            fans_rel = self.__get_fans_by_gen(gen)

            gen += 1

            # Для каждого из вытащенных фанов заполняем следующее поколение фанов
            for fan_rel in fans_rel['items']:
                count2 = self.fill_fans(wall_posts_count, wall_photos_count, profile_photos_count,
                                        album_photos_count, aim_id=fan_rel, gen=gen, period_in_days=period_in_days)
                if time_in_minutes is not None and (time.time() - start_time) > time_in_minutes * 60:
                    print("Время истекло")
                    return
                if type(count2) is int:
                    fans_count -= count2
                    if fans_count < 1:
                        print("Депозит исчерпан, count = {}".format(fans_count))
                        return

            fans2 = self.__get_fans_by_gen(gen)

            # Для каждого из фанов тащим друзей
            for fan_rel in fans_rel['items']:
                if friends_count is not 0:
                    try:
                        friends = api_service.friends.get(user_id=aim_id, count=friends_count,
                                                          v='5.92')
                    except vk.exceptions.VkAPIError as e:
                        print("Vk friends.get error")
                        friends = {'count': 0, 'items': []}
                else:
                    friends = {'count': 0, 'items': []}

                # Исключаем повторения
                friends['items'] = [x for x in friends['items'] if x not in fans2['items']]
                friends['count'] = len(friends['items'])

                # Дополняем поколение фанами друзей
                for friend in friends['items']:
                    print('Filling fans for {} friend'.format(friend))
                    count3 = self.fill_fans(wall_posts_count, wall_photos_count, profile_photos_count,
                                            album_photos_count,
                                            aim_id=friend, gen=gen, period_in_days=period_in_days)
                    if time_in_minutes is not None and (time.time() - start_time) > time_in_minutes * 60:
                        print("Время истекло")
                        return
                    if type(count3) is int:
                        fans_count -= count3
                        if fans_count < 1:
                            print("Депозит исчерпан, count = {}".format(fans_count))
                            return

        print("Депозит исчерпан, count = {}".format(fans_count))
        return "Friends has been filled by likes"

    def get_fans_info(self, gen):
        self.c.execute("SELECT count (fan_id) FROM fans")
        print("Количество фанов в таблице: {}".format(self.c.fetchone()[0]))
        for i in range(0, gen):
            self.c.execute("SELECT count (fan_id) FROM fans WHERE gen=:i", {"i": i})
            print("Количество фанов {}-го поколения: {}".format(i, self.c.fetchone()[0]))

    def __get_fans_by_gen(self, gen):
        fans = {}
        self.c.execute("SELECT count(DISTINCT fan_id) FROM fans WHERE gen=:gen", {"gen": gen})
        fans['count'] = self.c.fetchone()
        self.c.execute("SELECT DISTINCT fan_id FROM fans WHERE gen=:gen ORDER BY likes_count DESC ", {"gen": gen})
        fans['items'] = [i[0] for i in self.c.fetchall()]

        return fans

    def get_attractives(self, gender=None, aim_id=None, aim_domain=None):
        if aim_id is None:
            aim_id = api_service.utils.resolveScreenName(screen_name=aim_domain, v='5.92')['object_id']

        self.c.execute(
            "SELECT aim_id, likes_count, gen FROM fans WHERE fan_id=:aim_id GROUP BY aim_id ORDER BY likes_count DESC",
            {"aim_id": aim_id})
        attractives = self.c.fetchall()

        attrdict = {'count': 0, 'id': [], 'likes_count': [], 'info': []}
        if gender is 'male':
            for a in attractives:
                while True:
                    try:
                        info = api_service.users.get(user_ids=a[0], fields='sex', lang='ru', v='5.92')
                    except requests.exceptions.ReadTimeout as r:
                        print("Время ожидания информации о пользователе истекло. Запрашиваю ещё раз")
                        continue
                    break

                if info[0]['sex'] is 1:
                    continue
                attrdict['likes_count'].append(a[1])
                attrdict['info'].append({'id': a[0], 'name': info[0]['first_name'], 'surname': info[0]['last_name']})
                attrdict['id'].append(a[0])

        elif gender is 'female':
            for a in attractives:

                while True:
                    try:
                        info = api_service.users.get(user_ids=a[0], fields='sex',lang='ru', v='5.92')
                    except requests.exceptions.ReadTimeout as r:
                        print("Время ожидания информации о пользователе истекло. Запрашиваю ещё раз")
                        continue
                    break

                if info[0]['sex'] is 2:
                    continue
                attrdict['likes_count'].append(a[1])
                attrdict['info'].append(
                    {'id': a[0], 'name': info[0]['first_name'], 'surname': info[0]['last_name']})
                attrdict['id'].append(a[0])
        elif gender is None:
            for a in attractives:
                info = api_service.users.get(user_ids=a[0], lang='ru', v='5.92')
                attrdict['likes_count'].append(a[1])
                attrdict['info'].append({'id': a[0], 'name': info[0]['first_name'], 'surname': info[0]['last_name']})
                attrdict['id'].append(a[0])

        attrdict['count'] = len(attrdict['likes_count'])

        return attrdict

    def get_fans(self, aim_id=None, aim_domain=None):
        if aim_id is None:
            aim_id = api_service.utils.resolveScreenName(screen_name=aim_domain, v='5.92')['object_id']

        self.c.execute("SELECT DISTINCT fan_id, likes_count FROM fans WHERE aim_id= :aim_id GROUP BY fan_id", {'aim_id':aim_id})
        fans = self.c.fetchall()
        fans2 = {'count': 0, 'likes_count': [], 'info': []}
        for fan in fans:
            fans2['likes_count'].append(fan[1])
            fans2['info'].append(fan[0])
        fans2['count']=len(fans2['likes_count'])
        return fans2

    def get_fans_with_info(self, aim_id=None, aim_domain=None, gender=None, gen=None):
        if gen is None:
            if aim_id is None:
                aim_id = api_service.utils.resolveScreenName(screen_name=aim_domain, v='5.92')['object_id']
            self.c.execute(
                "SELECT fan_id, likes_count FROM fans WHERE aim_id= :aim_id GROUP BY fan_id ORDER BY likes_count DESC ",
                {'aim_id': aim_id})
            fans = self.c.fetchall()
        else:
            self.c.execute(
                "SELECT fan_id, likes_count FROM fans WHERE gen= :gen GROUP BY fan_id ORDER BY likes_count DESC ",
                {'gen': gen})
            fans = self.c.fetchall()

        fansdict = {'count': 0, 'id':[], 'likes_count': [], 'info': []}
        if gender is 'male':
            for a in fans:
                while True:
                    try:
                        info = api_service.users.get(user_ids=a[0], fields='sex', lang='ru', v='5.92')
                    except requests.exceptions.ReadTimeout as r:
                        print("Время ожидания информации о пользователе истекло. Запрашиваю ещё раз")
                        continue
                    break

                if info[0]['sex'] is 1:
                    continue
                fansdict['likes_count'].append(a[1])
                fansdict['info'].append({'id': a[0], 'name': info[0]['first_name'], 'surname': info[0]['last_name']})
                fansdict['id'].append(a[0])

        elif gender is 'female':
            for a in fans:

                while True:
                    try:
                        info = api_service.users.get(user_ids=a[0], fields='sex', lang='ru', v='5.92')
                    except requests.exceptions.ReadTimeout as r:
                        print("Время ожидания информации о пользователе истекло. Запрашиваю ещё раз")
                        continue
                    break

                if info[0]['sex'] is 2:
                    continue
                fansdict['likes_count'].append(a[1])
                fansdict['info'].append(
                    {'id': a[0], 'name': info[0]['first_name'], 'surname': info[0]['last_name']})
                fansdict['id'].append(a[0])
        elif gender is None:
            for a in fans:
                info = api_service.users.get(user_ids=a[0],lang='ru', v='5.92')
                fansdict['likes_count'].append(a[1])
                fansdict['info'].append({'id': a[0], 'name': info[0]['first_name'], 'surname': info[0]['last_name']})
                fansdict['id'].append(a[0])

        fansdict['count'] = len(fansdict['likes_count'])

        return fansdict

    def get_crossed_attractives(self, attractives, fans, aim_domain=None):

        # Сделаем график цель-->фан по возрастанию.
        answer = {'count': 0, 'info': [], 'aim2fan_count': [], 'fan2aim_count':[]}

        for i in range(len(attractives['id'])):
            try:
                pos= fans['id'].index(attractives['id'][i])
            except ValueError as e:
                #Такого чего во втором массиве нет
                #Тогда кол-во его лайков на графике перекрестных будет 0
                answer['info'].append(attractives['info'][i])
                answer['aim2fan_count'].append(attractives['likes_count'][i])
                answer['fan2aim_count'].append(0)
                continue

            # Если нашли позицию
            answer['info'].append(attractives['info'][i])
            answer['aim2fan_count'].append(attractives['likes_count'][i])
            answer['fan2aim_count'].append(fans['likes_count'][pos])

        answer['count'] = len(answer['aim2fan_count'])

        return answer

    def get_crossed_fans(self, attractives, fans):

        #Всё то же самое, только наоборот и для 0 ничего не ставим
        #И номер челика добавляем в 'x'[]
        answer = {'count': 0, 'info': [], 'fan2aim_count': [], 'aim2fan_count': [], 'x':[] }

        for i in range(len(fans['id'])):
            try:
                pos = attractives['id'].index(fans['id'][i])
            except ValueError as e:
                # Такого чела во втором массиве нет
                #Тогда кол-во его лайков будет 0, но на график лайки не попадут,
                #Т.к. в х мы ничего не добавили
                answer['info'].append(fans['info'][i])
                answer['fan2aim_count'].append(fans['likes_count'][i])
                answer['aim2fan_count'].append(0)
                continue

            # Если нашли позицию
            answer['info'].append(fans['info'][i])
            answer['fan2aim_count'].append(fans['likes_count'][i])
            answer['aim2fan_count'].append(attractives['likes_count'][pos])
            answer['x'].append(i+1)

        answer['count'] = len(answer['aim2fan_count'])

        return answer







    def remove_fans(self, aim_id=None, gen=None):
        if gen is not None:
            self.c.execute("DELETE from fans WHERE gen=:gen",{'gen':gen})
        if aim_id is not None:
            self.c.execute("DELETE from fans WHERE aim_id=:aim_ad",{'aim_id':aim_id})

    def add_client(self, client_id):
        self.c.execute('INSERT OR IGNORE INTO clients VALUES (?)',client_id)

    def close_connection(self):
        self.conn.close()
        print("Connection is closed")

    def recreate_database(self):
        self.__delete_database()

        self.conn = sqlite3.connect('VkLikeBot/vkService/users.db')
        self.c = self.conn.cursor()

        with self.conn:
            self.c.execute("PRAGMA main.journal_mode = TRUNCATE")

            self.c.execute("""CREATE TABLE IF NOT EXISTS fans(
                 aim_id INTEGER NOT NULL CHECK (fan_id<>aim_id),
                 fan_id INTEGER NOT NULL,
                 likes_count INTEGER DEFAULT 0,
                 gen INTEGER NOT NULL
                 )""")

            self.c.execute("""CREATE TABLE IF NOT EXISTS person_profiles(
                person_id UNIQUE NOT NULL,
                gender text CHECK (gender IN ('m','f','undefined',NULL)),
                bithday date,
                university text
                )""")


    def __delete_database(self):
        if os.path.exists('vkService/users.db'):
            os.remove('vkService/users.db')
        if os.path.exists('vkService/users.db-journal'):
            os.remove('vkService/users.db-journal')
        print('Database has been removed')
