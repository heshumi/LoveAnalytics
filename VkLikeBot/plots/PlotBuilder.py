import matplotlib.pyplot as plt
import os

class PlotBuilder:
    def crossed_attractives(self, crossed, max, path):

        print('Количество аттрактивов: {}'.format(crossed['count']))
        if crossed['count'] > max:
            crossed['count'] = max
            crossed['info'] = crossed['info'][:max]
            crossed['aim2fan_count'] = crossed['aim2fan_count'][:max]
            crossed['fan2aim_count'] = crossed['fan2aim_count'][:max]
        plt.figure(figsize=(20, 12))
        plt.tick_params(labelsize=15)

        x = range(1, crossed['count'] + 1)

        y1 = crossed['aim2fan_count']
        y2 = crossed['fan2aim_count']

        plt.xticks(x, ['{}. {} {}'.format(crossed['info'].index(a)+1, a['name'], a['surname']) for a in crossed['info']], rotation=60, ha='right')
        plt.yticks(y1+y2)

        plt.xlabel('Пользователь', fontsize=25)
        plt.ylabel('Коэффициент симпатии', fontsize=25)

        # Построить вторую линию
        plt.plot(x, y2, marker='o', markersize=8,
                 label='Кто лайкает пользователя')

        # Построить первую линию
        plt.grid(color='c', linestyle='--', linewidth=0.8)
        plt.plot(x, y1, marker='o', markersize=8, label='Кого лайкает пользователь', color='r')

        if not os.path.exists(path):
                os.mkdir(path)

        i = 1
        with open(path+'/attractives.txt', 'w') as file:
            for a in crossed['info']:
                file.write('{}) {} {} https://vk.com/id{}\n'.format(i, a['name'], a['surname'], a['id']))
                print('{}) {} {} https://vk.com/id{}'.format(i, a['name'], a['surname'], a['id']))
                i += 1

        plt.tight_layout()
        
        if os.path.exists(path + '/attractives.png'):
            os.remove(path + '/attractives.png')
        plt.savefig(path + '/attractives.png')

    def crossed_fans(self, crossed, max, path):

        print('Количество фанов: {}'.format(crossed['count']))
        if crossed['count'] > max:
            crossed['count'] = max
            crossed['info'] = crossed['info'][:max]
            crossed['aim2fan_count'] = crossed['aim2fan_count'][:max]
            crossed['fan2aim_count'] = crossed['fan2aim_count'][:max]
        for i in range(len(crossed['x'])):
            if crossed['x'][i]>max:
                crossed['x']=crossed['x'][:i]
                break


        plt.figure(figsize=(20, 12))
        plt.tick_params(labelsize=15)

        x1 = range(1, crossed['count'] + 1)

        y1 = crossed['fan2aim_count']
        y2 = [a for a in crossed['aim2fan_count'] if a is not 0]


        plt.xticks(x1, ['{}. {} {}'.format(crossed['info'].index(a)+1, a['name'], a['surname']) for a in crossed['info']], rotation=60, ha='right')
        plt.yticks(y1+y2)

        plt.xlabel('Пользователь', fontsize=25)
        plt.ylabel('Коэффициент симпатии', fontsize=25)




        # Построить вторую линию

        x2 = crossed['x']
        plt.plot(x2, y2 , marker='o', markersize=8,
                 label='Кто лайкает пользователя', color='r')
        # Построить первую линию
        plt.grid(color='c', linestyle='--', linewidth=0.8)
        plt.plot(x1, y1, marker='o', markersize=8, label='Кого лайкает пользователь')


        if not os.path.exists(path):
                os.mkdir(path)

        i = 1
        with open(path + '/fans.txt', 'w') as file:
            for a in crossed['info']:
                print('{}) {} {} https://vk.com/id{}'.format(i, a['name'], a['surname'], a['id']))
                file.write('{}) {} {} https://vk.com/id{}\n'.format(i, a['name'], a['surname'], a['id']))
                i += 1

        plt.tight_layout()
        

        if os.path.exists(path + '/fans.png'):
            os.remove(path + '/fans.png')
        plt.savefig(path + '/fans.png')



    def fan_to_aim(self, fans, max):
        print('Количество фанов: {}'.format(fans['count']))
        if fans['count'] > max:
            fans['count'] = max
            fans['info'] = fans['info'][:max]
            fans['likes_count'] = fans['likes_count'][:max]

        plt.figure(figsize=(20, 12))
        plt.tick_params(labelsize=15)
        x=range(1, fans['count'] + 1)
        y = fans['likes_count']
        plt.xticks(x,
                   ['{}. {} {}'.format(fans['info'].index(a) + 1, a['name'], a['surname']) for a in fans['info']],
                   rotation=70, ha='right')
        plt.yticks(y)
        plt.xlabel('Пользователь', fontsize=25)
        plt.ylabel('Коэффициент симпатии', fontsize=25)
        plt.grid(color='c', linestyle='--', linewidth=0.8)
        plt.plot(x, y, marker='o', markersize=8, label='Кто лайкает пользователя')
        plt.show()
        i = 1
        for a in fans['info']:
            print('{}) {} {} https://vk.com/id{}'.format(i, a['name'], a['surname'], a['id']))
            i += 1
