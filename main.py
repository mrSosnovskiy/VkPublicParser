import requests
import json
import datetime
import config_parser

# Ключевое словa, cюда вписать название города.
keyword = "Давлеканово"
# Проверить id городов, сюда id городов
city_id = [2]
count_member = 10000



# Функция для получения групп
def create_json(response, count_member: int):
    data = response.json()
    data_base = {}
    for group in data['response']['items']:
        group_id = group['id']
        response_group = requests.get(
            f'https://api.vk.com/method/groups.getById?group_id={group_id}&fields=members_count,contacts,description&access_token={access_token}&v=5.131')
        data_group = response_group.json()

        if data_group['response'][0]['members_count']:
            members_count = data_group['response'][0]['members_count']
        else:
            members_count = 0

        group_link = f'https://vk.com/{group["screen_name"]}'
        group_name = group['name']
        group_id = group['id']
        group_description = data_group['response'][0]['description']
        if "contacts" in data_group['response'][0].keys():
            group_contacts = data_group['response'][0]["contacts"]
        else:
            group_contacts = 'нет контакта или закрытая группа'

        temp_dict = {"Сообщество": group_name, "Ссылка на сообщество": group_link,
                     "Кол-во подписчиков": members_count, "Контакты": group_contacts, 'Описание': group_description}

        data_base[group_id] = temp_dict

        if members_count < count_member:
            break

    return data_base

def check_city_members(group_id, city_id):
    count_members = 0
    offset = 0
    response_members = requests.get(
        f'https://api.vk.com/method/groups.getMembers?group_id={group_id}&offset={offset}&count_members={1000}&fields=city&access_token=vk1.a.Lpwp8383TgND4rB1mPHWde2y4EE39UPkcpZWUPAevZX8DZCYifg5a6HMzLPeGaNPzb9fBNYyX2UDxq8FvZn7g2zGPprgGehYi_qbPnVeeMRFUda8L6WaVQCGlzCL4FVgKzdLNzcZhZD9-4q1cNuzZK-QnRA50RcFfertv-OrmqM9YR5VegYa6eLPWXxt9FPGGffqV0dCY2CpfBmoscZ8gQ&expires_in=0&user_id=138964205&v=5.131')
    if 'response' in response_members.json().keys():
        # print(response_members.json()['response'].keys())
        if 'count' in response_members.json()['response'].keys():
            group_size = (response_members.json()['response']['count'])
            while True:

                response_members = requests.get(
                    f'https://api.vk.com/method/groups.getMembers?group_id={group_id}&offset={offset}&count_members={1000}&fields=city&access_token={access_token}&v=5.131')
                members = []
                if 'response' in response_members.json().keys():
                    members = response_members.json()['response']['items']


                for member in members:
                    # print(member)
                    if "city" in member.keys() and int(member["city"]['id']) in city_id:
                        count_members += 1
                if offset < group_size:

                    offset += 1000

                else:
                    break

            print(count_members, group_size)
            if count_members / group_size * 100 < 38:
                # print(count_members, group_size)
                return True

    return False


def check_admin(work_dict):
    admin_dict = {}
    for key in work_dict.keys():

        for contact in work_dict[key]['Контакты']:
            # print(contact)
            if int(contact['user_id']):
                if contact['user_id'] not in admin_dict.keys():
                    admin_dict['user_id'] = [work_dict[key]['Ссылка на сообщество']]
                else:
                    admin_dict['user_id'].append(work_dict[key]['Ссылка на сообщество'])
    return admin_dict


def check_competitor(description):
    keyword = ['телеграмм', 'tg', ' https://t.me', 'телега', "Telegram", 't.me']
    for word in keyword:
        if word.lower() in description.lower():
            return True
    return False


start_time = datetime.datetime.now()


access_token = config_parser.access_token


group_count = 1000

# Отправляем запрос к VK API для поиска сообществ
response = requests.get(
    f"https://api.vk.com/method/groups.search?q={keyword}"
    f"&sort=6&count={group_count}&access_token={access_token}&v=5.131"
    )

print(response.json())

# # Создаем json файл для записи результатов
data_base = create_json(response, count_member)
with open(f'group_search_{keyword}.json', 'w', encoding='utf-8') as file:
    json.dump(data_base, file, indent=4)


with open(f"group_search_{keyword}.json", "r") as file:
    data_base = json.load(file)


dict_comperation = {}
dict_nacrutka = {}
dict_donor = {}
work_dict = data_base

for key in work_dict.keys():
    word = key
    if 'Описание' in work_dict[key].keys():
        description = work_dict[key]['Описание']
        if check_competitor(description):
            dict_comperation[word] = work_dict[word]['Ссылка на сообщество']

        elif check_city_members(key, city_id):
            dict_nacrutka[word] = work_dict[word]['Ссылка на сообщество']

        else:
            dict_donor[key] = work_dict[key]['Ссылка на сообщество']

with open("comperation.txt", 'w', encoding='utf-8') as file:
    for key in dict_comperation.keys():
        file.write(f"{dict_comperation[key]}\n")

with open("nacrutca.txt", 'w', encoding='utf-8') as file:
    for key in dict_nacrutka.keys():
        file.write(f"{dict_nacrutka[key]}\n")

with open("donor.txt", 'w', encoding='utf-8') as file:
    for key in dict_donor.keys():
        file.write(f"{dict_donor[key]}\n")

finish_time = datetime.datetime.now() - start_time

print('Время', finish_time)
