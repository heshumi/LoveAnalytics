from vkService.LikesService import LikesService
import time
from plots.PlotBuilder import PlotBuilder
from vkService.BotService import VkBot
from queue import Queue
from random import randint
import os

queue=Queue() #Объявляем атомарную очередь запросов
likesService = LikesService()
bot= VkBot(likesService, queue)
plt= PlotBuilder()

bot.run()
max=30
while True:
# while True вытаскиваем из очереди айдишники и проверяем каждого по 10 мин
# Результаты сохраняем в папку с <client id>-<aim_id> (учесть, что чел 2 раза может искать 1 тян)
    request=queue.get()
    client_id=request['client_id']
    aim_id=request['aim_id']
    gender=request['gender']

    likesService.recreate_database()
    likesService.fill_fans_by_likes_and_friends(300, 0, 20, 20, 20, aim_id=aim_id, time_in_minutes=5, period_in_days=None)

    likesService.get_fans_info(10)

    fans=likesService.get_fans_with_info(aim_id=aim_id, gender=gender)
    attractives= likesService.get_attractives(aim_id=aim_id, gender=gender)

    crossed_fans= likesService.get_crossed_fans(fans=fans, attractives=attractives)
    crossed_attractives= likesService.get_crossed_attractives(attractives=attractives, fans=fans)

    print('График фанов')
    path='VkLikeBot/Clients_Data/{}'.format(aim_id)
    plt.crossed_fans(crossed_fans, max=max, path=path)

    print('График перекрёстных')
    plt.crossed_attractives(crossed_attractives, path=path, max=max)

    # Кого и как часто, отфильтрованный по времени:
    # print("Кого и как часто по времени")
    # likesService.remove_fans(gen='Year')
    # likesService.fill_fans(0, 20, 20, 20, aim_domain=aim_domain, gen='Year', period_in_days=365)
    # year_fans=likesService.get_fans_with_info(gen='Year', gender=gender)
    #
    # plt.fan_to_aim(fans=year_fans, max=max)

    #Графики и инфу отправляем клиенту.
    #time.sleep(1.5*60+randint(0,60))
    bot.send_respond(client_id,aim_id)

    likesService.close_connection()





#Создать поток, который проверяет готовность результатов и отправляет его клиенту (в отдельном методе)

