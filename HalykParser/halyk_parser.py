import json

from bs4 import BeautifulSoup
from requests_html import HTMLSession

url = "https://halykbank.kz/halykclub"


def parse_halykbank(url):
    k = 0
    data = [
        {
            "city": "Астана",
            "city_code": "1501",
            "cashback_info": []
        },
        {
            "city": "Алматы",
            "city_code": "1802",
            "cashback_info": []
        },
        {
            "city": "Актобе",
            "city_code": "0101",
            "cashback_info": []
        },
        # {
        #     "city": "Атырау",
        #     "city_code": "0601",
        #     "cashback_info": []
        # },
        # {
        #     "city": "Актау",
        #     "city_code": "1402",
        #     "cashback_info": []
        # },
        # {
        #     "city": "Шымкент",
        #     "city_code": "0801",
        #     "cashback_info": []
        # },
        # {
        #     "city": "Туркестан",
        #     "city_code": "0802",
        #     "cashback_info": []
        # },
        # {
        #     "city": "Семей",
        #     "city_code": "0301",
        #     "cashback_info": []
        # },
    ]

    category_params = ["supermarketi",
    "azs", "restorani_kafe", "yuvelirnie_magazini_chasi",
    "odezhda_muzhskaya_zhenskaya_detskaya_obuv_aksessuari", "tabachnie_magazini", "elektronika",
     "tovari_dlya_doma_tekstil_mebel_posuda", "audio_video_knizhnie_kantselyariya",
     "magazini_kosmetiki", "podarki_suveniri_antikvariat", "stroitelnie_magazini",
     "tsvetochnie_magazini", "passazhirskie_perevozki", "transportnie_perevozki_logistika_dostavka",
     "professionalnie_uslugi", "kureri_dostavka_tovara", "kommunalnie_uslugi_televidenie_internet",
     "uslugi_strakhovaniya", "biznes_uslugi", "saloni_krasoti_parikmakherskie",
     "fotosaloni_poligrafiya", "kliringovie_kompanii", "sotovaya_svyaz",
     "detskie_sadi_shkoli_obrazovanie", "detskie_tovari", "meditsinskie_tsentri_kliniki", "apteki",
     "optika", "stomatologii", 'sport', "avtotovari", "avtouslugi", "vetkliniki_i_zoomagazini",
     "internet_magazini", "galerei_vistavki_ekskursii", "kinoteatri", "parki_otdikha_i_razvlechenii",
     "oteli_i_moteli", "turisticheskie_agentstva", "zh_d_kassi"]
    global r
    s = HTMLSession()
    headers = {

    }
    for city_data in data:
        print(city_data)
        for category_param in category_params:
            try:
                params = "?category_code=" + category_param + "&filter"
                r = s.get(url + '#!/' + city_data["city_code"] + "/list" + params, headers=headers)
                r.html.render(sleep=2)
                soup = BeautifulSoup(r.html.html, "lxml")
                info = {}

                content = soup.find("div", class_="px-3 w-8/12 relative <lg:w-full")
                if content is None:
                    continue
                category_name = content.find("div", class_="text-3xl mb-6 font-semibold <lg:text-lg <lg:mb-4")
                if category_name is None:
                    continue

                info["category_name"] = category_name.text
                info["stores"] = []

                stores_block = content.find("div", class_="-mx-3 flex flex-wrap w-full <md:mx-0")
                if stores_block is None:
                    continue
                stores_links = stores_block.find_all("div", class_="w-6/12 px-3 pb-4 <md:w-full <md:px-0")
                if stores_links is None:
                    continue

                for store_link in stores_links:
                    store_link = store_link.find("a")
                    if store_link is None:
                        continue
                    store_link = store_link['href']
                    store = s.get(url + store_link, headers=headers)
                    store.html.render(sleep=2)
                    store_soup = BeautifulSoup(store.html.html, "lxml")
                    store_content = store_soup.find("div", class_="<lg:-mx-4")
                    if store_content is None:
                        continue
                    store_content = store_content.find("div", class_="mb-2 <lg:mx-3")
                    if store_content is None:
                        continue
                    store_content = store_content.find("div", class_='flex flex-wrap -mx-3')
                    if store_content is None:
                        continue
                    store_addresses_block = store_content.find_all("div",
                                                                   class_="border relative border-gray-100 bg-white py-3 px-4 pb-8 rounded-lg null")
                    if store_addresses_block is None:
                        continue
                    for store_address_block in store_addresses_block:
                        store = {}
                        store_name = store_address_block.find("div", class_="text-lg mb-1")
                        if store_name is None:
                            continue
                        store["store_name"] = store_name.text
                        store_address = store_address_block.find("div", class_="text-sm mb-2")
                        if store_address is None:
                            continue
                        store["store_address"] = store_address.text
                        max_cashback = store_address_block.find("div", {'style': "background: rgb(252, 176, 22);"})
                        if max_cashback is not None:
                            max_cashback = max_cashback.text
                        store["max_cashback"] = max_cashback
                        qr_cashback = store_address_block.find("div", {'style': "background: rgb(6, 140, 110);"})
                        if qr_cashback is not None:
                            qr_cashback = qr_cashback.text[1:]
                        store["qr_cashback"] = qr_cashback
                        # print(store)
                        # print()
                        info["stores"].append(store)
                        k += 1
                        print(k)
                city_data["cashback_info"].append(info)
            except Exception as ex:
                print("Error with ", ex)
            finally:
                r.close()
        print(city_data)
    s.close()
    try:
        with open('halykbank.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Failed to write JSON file: {e}")


parse_halykbank(url)
