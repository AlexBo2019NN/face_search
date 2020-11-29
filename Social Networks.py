#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import vk_api
import urllib.request
import json
import getpass

LOGIN = input("VK username/email:")
PASSWORD = getpass.getpass("Password for " + LOGIN + ":")

def main():
    # ======= Открываем сессию  с VK =======
    vk_session = vk_api.VkApi(LOGIN, PASSWORD)
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk = vk_session.get_api()
    
    # ======= считываем список пользователей =======
    file_id = open(os.path.join(sys.path[0],'id_users.txt'), 'r')
    data_list = file_id.readlines()
    id_list = []
    users_detail = []
    
    for line in data_list:
        id_new = line.strip().replace('https://vk.com/','')
        #Для лучшей масштабируемости (>1000 клиентов) детали профиля считываем отдельно
        #Отобрали для примера некоторые релевантные поля для сегментаци клиента
        try:
            id_new = vk.utils.resolveScreenName(screen_name=id_new)['object_id']
        except:
            pass
        user_info = vk.users.get(user_ids = [id_new], fields = ['about','bdate','books','career','city', 'country','connections','contacts','domain','education','exports','interests','sex'])[0]
        
        id_list.append(user_info['id'])
        users_detail.append(user_info)
        
        #Запись детальной информации о клиентах в файл
        text_file = open("users_detail.json", "w")
        json.dump(users_detail, text_file)
        text_file.close()    
        
        text_file = open("users_detail.txt", "w")
        text_file.write(str(users_detail))
        text_file.close()    
        
    print(users_detail)
       
    # ======= начинаем перебирать каждого пользователя =======
    for id_user in id_list:
        
        # создаем директорию с именем пользователя, если нет
        newpath = os.path.join(sys.path[0], str(id_user))
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        
        # посылаем запрос к VK API, count свой, но не более 200
        response = vk.photos.getAll(owner_id = id_user, count = 30)
        
        # работаем с каждой полученной фотографией
        for i in range(len(response["items"])):
            
            # берём ссылку на максимальный размер фотографии
            photo_url = str(response["items"][i]["sizes"][len(response["items"][i]["sizes"])-1]["url"])
            
            # скачиваем фото в папку с ID пользователя
            urllib.request.urlretrieve(photo_url, newpath + '/' + str(response["items"][i]['id']) + '.jpg')

if __name__ == "__main__":
    main()