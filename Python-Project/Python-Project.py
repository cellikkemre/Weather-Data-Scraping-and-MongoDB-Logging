import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
import threading

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

client = MongoClient('localhost', 27017)
db = client['emre_celik']
hava_durumu_koleksiyonu = db['hava_durumu_koleksiyonu']


lock = threading.Lock()


class HavaDurumuKaydi:
    def __init__(self, provincial_plate, date, weather):
        self.provincial_plate = provincial_plate
        self.date = date
        self.weather = weather


def hava_durumu_kaydi_ekle(kayit):
    with lock:
        # Koleksiyonda aynı kayıt var mı kontrol et
        existing_record = hava_durumu_koleksiyonu.find_one({
            'provincial_plate': kayit.provincial_plate,
            'date': kayit.date
        })

        # Eğer kayıt yoksa ekle
        if existing_record is None:
            hava_durumu_koleksiyonu.insert_one({
                'provincial_plate': kayit.provincial_plate,
                'date': kayit.date,
                'weather': kayit.weather
            })



def hava_durumu_yazdir(header, il_id, il_ad, url):
    get = requests.get(url, headers=header)
    content = get.content
    soup = BeautifulSoup(content, "html.parser")

    tablo = soup.find('table', id='hor-minimalist-a')
    ilk_yedi_gun = tablo.find_all('tr')[1:8]

    kayitlar = []

    for gun in ilk_yedi_gun:
        tarih_elem = gun.find_all('td', limit=1)
        if tarih_elem:
            tarih = gun.find_all('td')[0].text.split(',')[0]
            gunduz_elem = gun.find_all('td')[2]
            gece_elem = gun.find_all('td')[3]

            if gunduz_elem and gece_elem:
                gunduz = gunduz_elem.text
                gece = gece_elem.text

                gunduz = float(gunduz.replace('°', ''))
                gece = float(gece.replace('°', ''))

                ay_cevirme = {
                    'Ocak': 'January',
                    'Şubat': 'February',
                    'Mart': 'March',
                    'Nisan': 'April',
                    'Mayıs': 'May',
                    'Haziran': 'June',
                    'Temmuz': 'July',
                    'Ağustos': 'August',
                    'Eylül': 'September',
                    'Ekim': 'October',
                    'Kasım': 'November',
                    'Aralık': 'December'
                }

                for tr, en in ay_cevirme.items():
                    tarih = tarih.replace(tr, en)

                kayit = HavaDurumuKaydi(provincial_plate=il_id, date=datetime.strptime(tarih, '%d %B %Y'),
                                        weather={"up": gunduz, "low": gece})

                hava_durumu_kaydi_ekle(kayit)

                kayitlar.append(kayit)
            else:
                print("Gündüz veya gece bulunamadı.")
        else:
            print("Tarih bulunamadı.")

    return kayitlar


def main():
    try:
        with open('plaka_kodlari.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            hava_durumu_kayitlari = []


            threads = []

            for il in data[0].items():
                il_id, il_ad = il
                url = f"https://www.havadurumux.net/{il_ad.lower()}-hava-durumu/"

                
                thread = threading.Thread(target=hava_durumu_yazdir, args=(header, il_id, il_ad, url))
                thread.start()
                threads.append(thread)


            for thread in threads:
                thread.join()

        print("Hava durumu kayıtları MongoDB'ye başarıyla eklendi.")
    except Exception as e:
        print(f'Hata: {e}')


if __name__ == "__main__":
    main()
