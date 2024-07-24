import scrapy
import re
import os.path
import csv
import time
from textwrap import wrap


class GetgjirafacontentSpider(scrapy.Spider):
    name = 'getGjirafaContent'
    # allowed_domains = ['gjirafa.com']
    start_urls = ['https://gjirafa.com/Top/Patundshmeri']

    def __init__(self):
        self.lineCount = 0
        self.fileExist = os.path.isfile('RealEstateOffers.csv')
        self.parcells = {str(x).strip() for x in open('parcelID.txt', 'rt')}
        self.inserted = {str(x).strip() for x in open('inserted.txt', 'rt')}
        super().__init__()

    # Metoda per ruajtjen e parcelave
    def saveParcels(self, i):
        try:
            with open('inserted.txt', 'at') as p:
                p.write(f'{i}\n')
                p.close()
        except Exception as e:
            raise e
        return

    # Metoda per dekodimin e te dhenave te enkriptuara (email)
    def DecodeData(self, parameter):
        res = ''
        key = int(parameter[:2], 16)
        for v in wrap(parameter[2:], 2):
            res += chr(int(v, 16) ^ key)
        return res

    # Metoda per parsimin e responsit (kontentit), menjanimit te duplove dhe dergimi i kerkesave te reja
    def parse(self, response):
        if response.status == 200:
            for parcel in self.parcells:
                time.sleep(2)
                if parcel not in self.inserted:
                    yield scrapy.Request(
                        url=f'https://gjirafa.com/Shpallje/Patundshmeri/{parcel}',
                        meta={
                            'parcel': parcel,
                            'cookiejar': parcel
                        },
                        dont_filter=False,
                        callback=self.getPageData
                    )
                else:
                    print(f'Already Saved {parcel}')

    # Metoda per parsimin e responsit (kontentit) dhe dhe thirrja e metodes per krijimin e CSV file
    def getPageData(self, response):
        # print(response.text)
        if response.status == 200:
            parcel = response.meta['parcel']
            content = response.text
            self.saveParcels(parcel)
            print(f'Saved Links: {parcel}')
            self.WriteInCSV(content)

    # Metoda per nxerrjen e te dhenave dhe ruajtjen e tyre ne CSV file
    def WriteInCSV(self, content):
        try:
            title = re.search(r'<title>(.*?)</title>', content, re.S | re.I)
            if title:
                title = title.group(1).strip()
                category = re.search(r'Kategoria.*?<h3>(.*?)</h3', content, re.S | re.I)
                category = category.group(1).strip()
                typeOffer = re.search(r'Lloji i shpalljes.*?<h3>(.*?)<', content, re.S | re.I)
                typeOffer = typeOffer.group(1).strip()
                squareFeet = re.search(r'Kuadratura.*?<h3>(.*?)<', content, re.S | re.I)
                squareFeet = squareFeet.group(1).strip()
                rooms = re.search(r'Numri i dhomave.*?<h3>(.*?)<', content, re.S | re.I)
                rooms = rooms.group(1).strip()
                price = re.search(r'Detajet.*?<strong>(.*?)<', content, re.S | re.I)
                price = price.group(1).strip()
                date = re.search(r'Data[^class]*class="display-field">(.*?)</div>', content, re.S | re.I)
                date = date.group(1).strip()
                zone = re.search(r'Rajoni[^class]*class="display-field">(.*?)</div>', content, re.S | re.I)
                zone = zone.group(1).strip()
                state = re.search(r'Shteti[^class]*class="display-field">(.*?)</div>', content, re.S | re.I)
                state = state.group(1).strip()
                describe = re.search(r'class="gjcs1 gjcm3-4 description">(.*?)</div>', content, re.S | re.I)
                describe = describe.group(1).strip()
                describe = describe.replace('<br />', '')
                picture = re.search(r'class="slides".*?<li class="bgcover" style="width:.*?data-thumb="(.*?)">',
                                    content, re.S | re.I)
                picture = picture.group(1).strip()

                encodedEmail = re.search(r'class="v-sect-header">Kontakt</h3>.*?data-cfemail="(.*?)"', content,
                                         re.S | re.I)
                if encodedEmail:
                    encodedEmail = encodedEmail.group(1)
                    decoded_email = self.DecodeData(encodedEmail)
                else:
                    decoded_email = 'Nuk ka email'

                phone = re.search(r'class="clickCall">([^<]*)</a>', content, re.S | re.I)
                if phone:
                    phone = phone.group(1)
                    phone = phone.strip()
                else:
                    phone = 'Nuk ka telefon'

            print(
                f"================================================\nTitulli: {title}\nKategoria: {category}\nLloji "
                f"Shpalljes: {typeOffer}\nSiperfaqja: {squareFeet}\nDhomat: {rooms}\nCmimi: {price}\nData: {date}\nRajoni: "
                f"{zone}\nShteti: {state}\nPershkrimi: {describe}\nFotot: {picture}\nTelefoni: {phone}")

            with open('RealEstateOffers.csv', 'a', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',')

                if self.lineCount == 0 and not self.fileExist:
                    csv_writer.writerow(
                        ['Titulli', 'Kategoria', 'Lloji Shpalljes', 'Siperfaqja', 'Dhomat', 'Cmimi', 'Data', 'Rajoni',
                         'Shteti', 'Pershkrimi', 'Fotot', 'Email', 'Telefoni'])
                    self.lineCount += 1
                else:
                    # Fushat te cilat integrohen ne csv
                    csv_writer.writerow(
                        [title, category, typeOffer, squareFeet, rooms, price, date, zone, state, describe, picture,
                         decoded_email, phone])
                    self.lineCount += 1
                print(f'Processed {self.lineCount} lines.')
        except e:
            print(e)