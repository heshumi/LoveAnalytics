import vk_api
import vk
import threading
import requests
from vk_api.utils import get_random_id


from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

community_token='34c8bef266e4a7ce9b0a8b61cd4c72685d57ca1854171ebd0d4427c1e8c955dda513b597dec1b28c6156d'
session = vk_api.VkApi(token=community_token)
api_community=session.get_api()
longpoll= VkLongPoll(session)

class VkBot:
    admins = ['200374980', '532326807','92061479' ]
    hello = 'Привет, {}. Мы сделали этого бота для того чтобы вы смогли наглядно проверить любимого вам человека, а может узнать о нем немного больше чем он рассказывает. Интересно?\n1 - Конечно!👍\n2 - Не сейчас😒'
    info = 'Предоставляемая ботом услуга платная и анализирует перечень социоактивных действий пользователя вместе с его окружением, предоставляя только открытые факты.\nОплата заказа производится после того как материал будет готов.\nМаксимальное время ожидания - день.\nЗаказ оплачивается через Vk Pay\nВыберите варинт:\n\n 1 - 🆓Бесплатный функционал\n2 - Создать заявку'
    plots_info='📍Бот анализирует профиль указанного вами человека👤, наглядно показывая на графиках связанных с ним людей и степень их заинтересованности в выбранном вами человеке👤\n👉Также бот показывает, кто симпатичен выбранному вами человеку💖\n👌Мы ввели бесплатную функцию проверки собственного профиля, чтобы вы смогли оценить, насколько проверка действительно работает, и проверить любого интересуюшего вас человека💘'
    plots_info2='📌Снизу расположены профили пользователей, сбоку - коэффициенты заинтересованности.\n📈Красный график отображает, в ком больше заинтересован выбранный вами человек💖\n📉Синий, показывает заинтересованность пользователей относительно выбранного человека👤\nОбратите внимание на самые высокие точки синих графиков📉 . Возможно, этим пользователям симпатичен выбранный человек👤\n📌Посмотрите на высокие точки красного графика📈. Вероятно, что эти люди небезразличны проверяемому человеку💘'
    last_message={}

    def __init__(self, likes_service,queue):
        self.queue = queue
        self.likes_service=likes_service
        self.api_service=likes_service.get_api_service()
        # self.c=c
        # self.conn=conn

    def run(self):
        t1 = threading.Thread(target=self.__start_bot, args=())
        t1.daemon=True
        t1.start()

    def __start_bot(self):
        while True:
            try:
                for event in longpoll.listen():
                    if event.type is VkEventType.MESSAGE_NEW:
                        if not event.from_me:
                            print(event.text)
                            print(event.user_id)

                            if 'attach1_type' in event.attachments:
                                if event.attachments['attach1_type']=='vkpay':
                                    self.__send_payed_order_to_admins(event.peer_id)
                                    continue

                            if event.peer_id not in self.last_message:
                                try:
                                    info = self.api_service.users.get(user_ids=event.user_id, lang='ru', v='5.92')
                                    name=info[0]['first_name']
                                    self.__add_client(event.peer_id, info[0]['first_name'], info[0]['last_name'])
                                except vk.exceptions.VkAPIError as e:
                                    print("Нет доступа к профилю клиента")
                                    name='друг'



                                keyboard = VkKeyboard(one_time=False)
                                keyboard.add_button('Конечно!👍', color=VkKeyboardColor.POSITIVE)
                                keyboard.add_button('Не сейчас😒', color=VkKeyboardColor.NEGATIVE)
                                try:
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message=self.hello.format(name),
                                                                keyboard=keyboard.get_keyboard(),
                                                                random_id=get_random_id()
                                                                )
                                except:
                                    print("Ошибка отправки сообщения")
                                    break
                                self.last_message[event.peer_id]='Приветствие'

                            elif 'Главное меню' in event.text: #В главное меню доступ ото всюду
                                self.__to_main_menu(event)

                            elif self.last_message[event.peer_id] == 'Приветствие':
                                if 'Не сейчас' in event.text or event.text=='2':
                                    keyboard = VkKeyboard(one_time=False)
                                    keyboard.add_button('Мне интересно🤔', color=VkKeyboardColor.POSITIVE)

                                    api_community.messages.send(peer_id= event.peer_id,
                                                                message='Очень жаль. Буду тебя ждать\n\n1 - Мне интересно🤔',
                                                                random_id=get_random_id(),
                                                                keyboard=keyboard.get_keyboard()
                                    )
                                    self.last_message[event.peer_id] = 'Приветствие'



                                elif 'Конечно!' in event.text or 'Мне интересно' in event.text\
                                        or event.text=='1':
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message=self.plots_info,
                                                                random_id=get_random_id(),
                                                                )
                                    self.__to_main_menu(event)
                                else:
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message='Такого варинта ответа нет',
                                                                random_id=get_random_id())

                            elif self.last_message[event.peer_id]=='Главное меню':

                                keyboard = VkKeyboard(one_time=False)
                                keyboard.add_button('📋Главное меню', color=VkKeyboardColor.DEFAULT)
                                if 'Cоциальный анализ' in event.text or event.text=='2':
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message='Отправьте ссылку на человека, которого хотите проанализировать, и пол той группы лиц которая ему интересна ("жен", "муж" или "оба").\nНапример:\nЕсли выбранному вами человеку нравятся девушки, то: \n https://vk.com/id1 жен\n1 - 📋Вернуться в главное меню',
                                                                keyboard=keyboard.get_keyboard(),
                                                                random_id=get_random_id()
                                                                )
                                    self.last_message[event.peer_id]='aim_id'

                                elif 'Бесплатный функционал' in event.text or event.text=='1':
                                    keyboard=VkKeyboard(one_time=False)
                                    keyboard.add_button('📊Анализ себя', color=VkKeyboardColor.POSITIVE)
                                    keyboard.add_button('👬Общие друзья', color=VkKeyboardColor.DEFAULT)
                                    keyboard.add_line()
                                    keyboard.add_button('📋Главное меню', color=VkKeyboardColor.DEFAULT)
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message='1 - 📊Анализ социальной активности для своей страницы\n2 - 👬Найти общих друзей между двумя пользователями\n3 - 📋Вернуться в главное меню',
                                                                keyboard=keyboard.get_keyboard(),
                                                                random_id=get_random_id()
                                                                )
                                    self.last_message[event.peer_id]='free_functions'
                                elif 'Пояснение к графикам' in event.text or event.text == '3':
                                    # keyboard=VkKeyboard(one_time=False)
                                    # keyboard.add_button('Главное меню', color=VkKeyboardColor.DEFAULT)
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message=self.plots_info2+'\n1 - 📋Вернуться в главное меню',
                                                                keyboard=keyboard.get_keyboard(),
                                                                random_id=get_random_id()
                                                                )


                                    self.last_message[event.peer_id]='Пояснение к графикам'
                                else:
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message='Такого варинта ответа нет. Отправьте одну цифру',
                                                                random_id=get_random_id())

                            elif self.last_message[event.peer_id]=='free_functions':
                                keyboard = VkKeyboard(one_time=False)
                                keyboard.add_button('📋Главное меню', color=VkKeyboardColor.DEFAULT)
                                if 'Общие друзья' in event.text or event.text=='2':
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message='Введите ссылки на двух людей, чьих общих друзей вы хотете узнать \nНапример:\n https://vk.com/dm https://vk.com/navalny\n\n1 - 📋Вернуться в главное меню',
                                                                random_id=get_random_id(),
                                                                keyboard=keyboard.get_keyboard()
                                                                )
                                    self.last_message[event.peer_id] = 'friend_ids'
                                elif event.text=='3':
                                    self.__to_main_menu(event)
                                elif 'Анализ себя' in event.text or event.text=='1':
                                    order_is_created=self.__create_an_order(client_id=event.peer_id)
                                    if order_is_created is True:
                                        self.last_message[event.peer_id] ='Создан заказ'
                                    else: self.__to_main_menu(event)

                                else:

                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message='Такого варинта ответа нет. Попробуйте ещё раз',
                                                                random_id=get_random_id())

                            elif self.last_message[event.peer_id]=='aim_id':
                                if event.text=='1':
                                    self.__to_main_menu(event)
                                else:
                                    order_is_created=self.__create_an_order(client_id=event.peer_id, aim_link=event.text)
                                    if order_is_created is True:
                                        self.last_message[event.peer_id] ='Создан заказ'

                            elif self.last_message[event.peer_id]=='friend_ids':
                                if event.text=='1':
                                    self.__to_main_menu(event)
                                else:
                                    common_friends = self.__get_common_friends(event.text, 5000)
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message=common_friends+'\n1 - 📋Вернуться в главное меню',
                                                                random_id=get_random_id())
                                    if '1)' in common_friends:
                                        self.last_message[event.peer_id]='Друзья вывелись'
                            elif self.last_message[event.peer_id]=='Создан заказ' or self.last_message[event.peer_id]=='Друзья вывелись'\
                                    or self.last_message[event.peer_id]=='Пояснение к графикам':
                                if event.text == '1':
                                    self.__to_main_menu(event)
                                else:
                                    api_community.messages.send(peer_id=event.peer_id,
                                                                message='Такого варинта ответа нет',
                                                                random_id=get_random_id())
                            else:
                                api_community.messages.send(peer_id=event.peer_id,
                                                              message='Такого варинта ответа нет',
                                                              random_id=get_random_id())


            except requests.exceptions.ReadTimeout as e:
                continue

    def send_respond(self, client_id, aim_id):
        path='VkLikeBot/Clients_Data/'
        with open(path+'to_plots_instruction.txt','r') as file:
            fifth= file.read()
        with open(path+'add.txt','r') as file:
            sixth= file.read()
        with open(path+'game_of_thrones.txt','r') as file:
            seventh= file.read()

        with open('{}{}/attractives.txt'.format(path,aim_id),'r') as file:
            second= file.read()
        if second =='':
            second= 'Выбранный человек ни в ком не интересуется. Может стоит поискать среди другого пола? ;)'

        with open('{}{}/fans.txt'.format(path, aim_id), 'r') as file:
            fourth = file.read()
        if fourth =='':
            fourth='В выбранном человеке никто не интересуется. Может стоит поискать среди другого пола? ;)'

        first='Результат проверки https://vk.com/id{}'.format(aim_id)
        first_photo_loc='{}{}/attractives.png'.format(path,aim_id)
        second_photo_loc= '{}{}/fans.png'.format(path, aim_id)

        upload = vk_api.VkUpload(session)
        attachments=[]
        photo=upload.photo_messages(first_photo_loc)
        attachments.append(
            'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])
        )
        api_community.messages.send(peer_id=client_id,
                                    message=first,
                                    attachment=','.join(attachments),
                                    random_id=get_random_id())

        api_community.messages.send(peer_id=client_id,
                                    message=second,
                                    random_id=get_random_id())

        attachments = []
        photo = upload.photo_messages(second_photo_loc)
        attachments.append(
            'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])
        )
        api_community.messages.send(peer_id=client_id,
                                    message='',
                                    attachment=','.join(attachments),
                                    random_id=get_random_id())

        api_community.messages.send(peer_id=client_id,
                                    message=fourth,
                                    random_id=get_random_id())


        api_community.messages.send(peer_id=client_id,
                                    message=fifth,
                                    random_id=get_random_id())
        if aim_id is client_id: #Если заявка бесплатная, то отправляем сообщение с рекламой
            api_community.messages.send(peer_id=client_id,
                                        message=sixth,
                                        random_id=get_random_id())
        api_community.messages.send(peer_id=client_id,
                                    message=seventh,
                                    random_id=get_random_id())


    def __to_main_menu(self, event):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('🆓Бесплатный функционал', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('📊Cоциальный анализ', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('📖Пояснение к графикам', color=VkKeyboardColor.DEFAULT)


        api_community.messages.send(peer_id=event.peer_id,
                                    message='Выберите варинт:\n1 - 🆓Бесплатный функционал\n2 - 📊Анализ социальной активности пользователя\n 3 - 📖Пояснение к графикам',
                                    keyboard=keyboard.get_keyboard(),
                                    random_id=get_random_id()
                                    )
        self.last_message[event.peer_id] = 'Главное меню'

    def __add_client(self, client_id, name, surname):
        needle='{} {} {} https://vk.com/id{}'.format(client_id, name, surname, client_id)
        with open("VkLikeBot/Clients_Data/clients.txt", "r+") as file:
            for line in file:
                if needle in line:
                    break
            else:  # not found, we are at the eof
                file.write('{}\n'.format(needle))


    def __create_an_order(self, client_id, aim_link=None):
        #Сначала работа со строкой (вытаскиваем id)

        if aim_link is not None:
            space = aim_link.find(' ')
            if space==-1:
                space= aim_link.find('\n')
            gender1 = aim_link[space:].lstrip()
            gender='Хз'
            for s in ['муж', 'жен', 'оба']:
                if gender1 in ['муж', 'жен', 'оба']:
                    gender=gender1
                    break

            if space == -1 or gender=='Хз':
                api_community.messages.send(peer_id=client_id,
                                            message='Некорректно введены данные. Попробуйте ещё раз',
                                            random_id=get_random_id())
                return False


            r= aim_link.find('vk.com')
            aim_id_or_domain=aim_link[r+7:space]

            try:
                aim_id = self.api_service.utils.resolveScreenName(screen_name=aim_id_or_domain, v='5.92')['object_id']
            except (TypeError, vk.exceptions.VkAPIError) as e:
                api_community.messages.send(peer_id=client_id,
                                            message='Такого пользователя не существует. Попробуйте ещё раз',
                                            random_id=get_random_id())
                return False
        else: aim_id=client_id

        # Делаем проверку aim_id
        info = self.api_service.users.get(user_ids=aim_id, fields='sex', lang='ru', v='5.92')
        if info[0]['is_closed'] is True:
            api_community.messages.send(peer_id=client_id,
                                        message='К сожалению, профиль пользователя {} закрыт. Мы не можем вам предоставить информацию о нём'.format(info[0]['first_name']),
                                        random_id=get_random_id())
            return

        if aim_link is None:
            s='#Новая_бесплатная_завяка\n#Клиент{}\nСсылка на клиента: https://vk.com/id{}'.format(client_id, client_id)
        else:
            s='#Новая_платная_заявка\n#Клиент{}\n#Цель{}\nСсылка на клиента: https://vk.com/id{}\nПол поиска: {}'.format(client_id,aim_id,client_id,gender)

        #Если заявка платная!
        if aim_link is not None:
            keyboard = VkKeyboard(one_time=False)
            keyboard.add_button('📋Главное меню')
            #Сообщение для платной функции
            # api_community.messages.send(peer_id=client_id,
            #                             message='Заявка создана и находится в обработке.\nМаксимальное время ожидания - 18 часов.\nЧтобы получить результат, приобретите товар: https://vk.com/revakoreva?w=product-178533511_3176004%2Fquery\n1 - 📋Вернуться в главное меню',
            #                             random_id=get_random_id())

            #Выводим то же сообщение, что и для бесплатного, т.к. теперь все бесплатно
            api_community.messages.send(peer_id=client_id,
                                        message='Заявка создана и находится в обработке.\nМы отправим вам результат по завершении процесса анализа.\nМаксимальное время ожидания - 18 часов.\n1 - 📋Вернуться в главное меню',
                                        keyboard=keyboard.get_keyboard(),
                                        random_id=get_random_id())

            #Платные заявки тоже теперь бесплатные. Захочешь сделать платными, меняй что-то с этим
            if gender=='жен':
                gender='female'
            elif gender=='муж':
                gender='male'
            else:
                gender = None
            self.queue.put({'aim_id': aim_id, 'client_id': client_id, 'gender': gender})

        else:
            keyboard= VkKeyboard(one_time=False)
            keyboard.add_button('📋Главное меню')
            api_community.messages.send(peer_id=client_id,
                                        message='Заявка создана и находится в обработке.\nМы отправим вам результат по завершении процесса анализа.\nМаксимальное время ожидания - 18 часов.\n1 - 📋Вернуться в главное меню',
                                        keyboard=keyboard.get_keyboard(),
                                        random_id=get_random_id())
            if info[0]['sex']==1: #Ставим пол, противоположный полу клиента
                gender='male'
            else: gender='female'

            self.queue.put({'client_id': client_id, 'aim_id': aim_id, 'gender': gender})

        for admin in self.admins:
            try:
                api_community.messages.send(peer_id=admin,
                                    message=s,
                                    random_id=get_random_id())
            except:
                print('Не удалось отправить сообщение админу {}'.format(admin))
                continue

        return True


    def __send_payed_order_to_admins(self, client_id):
        for admin in self.admins:
            try:
                api_community.messages.send(peer_id=admin,
                                    message='#Оплата\nЗаказ либо оплачен, либо нас читерят!\nСсылка на клиента: https://vk.com/id{}'.format(client_id),
                                    random_id=get_random_id())
            except:
                print('Не удалось отправить сообщение админу {}'.format(admin))
                continue


    def __get_common_friends(self, links, count):
        r = links.find('vk.com')

        space = links.find(' ')
        if space == -1:
            space = links.find('\n')

        aim_id1 = links[r + 7:space].lstrip()

        links=links[space:]
        r = links.find('vk.com')
        aim_id2 = links[r + 7:].lstrip()

        try:
            aim_id1 = self.api_service.utils.resolveScreenName(screen_name=aim_id1, v='5.92')['object_id']
        except (TypeError, vk.exceptions.VkAPIError) as e:

            return 'Пользователя {} не существует. Повторите ввод'.format(links[:links.find(' ')])

        try:
            aim_id2 = self.api_service.utils.resolveScreenName(screen_name=aim_id2, v='5.92')['object_id']
        except (TypeError, vk.exceptions.VkAPIError) as e:
            return 'Пользователя {} не существует. Повторите ввод'.format(links [links.find(' '):])

        info1 = self.api_service.users.get(user_ids=aim_id1, lang='ru', v='5.92')
        if info1[0]['is_closed'] is True:
            return 'К сожалению, профиль пользователя {} закрыт. Мы не можем вам предоставить информацию о нём'.format(info1[0]['first_name'])

        info2 = self.api_service.users.get(user_ids=aim_id2, lang='ru', v='5.92')
        if info2[0]['is_closed'] is True:
            return 'К сожалению, профиль пользователя {} закрыт. Мы не можем вам предоставить информацию о нём'.format(
                info2[0]['first_name'])

        try:
            friends1 = self.api_service.friends.get(user_id=aim_id1, count=count, order='name', v='5.92')
        except vk.exceptions.VkAPIError as e:
            return "К сожалению, профиль пользователя {}. Мы не можем вам предоставить информацию о нём".format(info1[0]['first_name'])
        try:
            friends2 = self.api_service.friends.get(user_id=aim_id2, count=count, v='5.92')
        except vk.exceptions.VkAPIError as e:
            return "К сожалению, профиль пользователя {} закрыт. Мы не можем вам предоставить информацию о нём".format(info2[0]['first_name'])

        common_friends= [friend for friend in friends1['items'] if friend in friends2['items']]

        friends_with_info=self.api_service.users.get(user_ids=common_friends, lang='ru', v='5.92')

        str='Общие друзья между двумя пользователями:\n'
        i=1
        for friend in friends_with_info:
            str+=('{}) {} {} https://vk.com/id{}\n'.format(i,friend['first_name'], friend['last_name'], friend['id']))
            i+=1
        if i==1:
            str='У пользователей нет общих друзей'


        return str




