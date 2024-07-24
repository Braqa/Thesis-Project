import scrapy
import re
from scrapy.utils.response import open_in_browser


class GetdatafromlinkSpider(scrapy.Spider):
    name = 'getDataFromLink'
    #allowed_domains = ['www.merrjep.com']
    start_urls = ['https://www.merrjep.com/']


    def __init__(self):
        self.parcells = {str(x).strip() for x in open('parcellID.txt', 'rt', encoding="utf-8")}
        self.inserted = {str(x).strip() for x in open('inserted.txt', 'rt')}


    # Metoda per ruajtjen e linqeve te procesuara
    def saveParcels(self, i):
        try:
            with open('inserted.txt', 'at') as p:
                p.write(f'{i}\n')
                p.close()
        except Exception as e:
            raise e
        return

    # Metoda per parsimin e responsit (kontentit), menjanimit te duplove dhe dergimi i kerkesave te reja
    def parse(self, response):
        if response.status == 200:
            for parcel in self.parcells:
                if parcel not in self.inserted:
                    yield scrapy.Request(
                        url=f'https://www.merrjep.com/shpallja/vendbanime/{parcel}',
                        meta={
                          'parcel': parcel
                        },
                        dont_filter=True,
                        callback=self.getItemsFromDeepLink
                    )
                else:
                    print(f'Already Saved {parcel}')

    # Metoda për nxjerrjen e të dhënave
    def getItemsFromDeepLink(self, response):
        if response.status == 200:
            parcel = response.meta['parcel']
            self.saveParcels(parcel)
            print(f'Saved Links: {parcel}')
            # open_in_browser(response)
            content = response.text
            publishDate = re.search(r'Publikuar:<[^>]*>\s*<bdi[^>]*>([^<]*)<', content, re.S | re.I)
            publishDate = publishDate.group(1).strip()
            publishTime = re.search(r'Publikuar:<[^>]*>\s*<bdi[^>]*>[^<]*<[^>]*>\s*<bdi[^>]*>([^<]*)<', content, re.S | re.I)
            publishTime = publishTime.group(1).strip()
            views = re.search(r'<span[^>]*>Shikime:<[^>]*>\s*<span[^>]*>([^<]*)<', content, re.S | re.I)
            views = views.group(1).strip()
            title = re.search(r'<h1\s*class="ci-text-base">([^<]*)<', content, re.S | re.I)
            title = title.group(1).strip().replace("&#203;", "Ë").replace("&#235;", "ë").replace("&#178", "²")
            telephone = re.search(r'Telefon:<[^>]*>\s*<p><bdi>([^<]*)<', content, re.S | re.I)
            if telephone:
                telephone = telephone.group(1).strip()
            else:
                telephone = '00-000-000'
            viber = re.search(r'Viber:<[^>]*>\s*<p><bdi>([^<]*)<', content, re.S | re.I)
            if viber:
                viber = viber.group(1).strip()
            else:
                viber = '00-000-000'
            price = re.search(r'class="new-price">\s*<[^>]*>([^<]*)<[^>]*><span>[^<]*<', content, re.S | re.I)
            if price:
                price = price.group(1).strip()
            else:
                price = ''
            valute = re.search(r'class="new-price">\s*<[^>]*>[^<]*<[^>]*><span>([^<]*)<', content, re.S | re.I)
            if valute:
                valute = valute.group(1).strip()
            else:
                valute = ''
            period = re.search(r'<\/h4>\s*<span\s*class="ci-text-ghost">\/\s*([^<]*)<', content, re.S | re.I)
            if period:
                period = period.group(1).strip()
            else:
                period = ''
            nrRooms = re.search(r'Numri\s*i\s*dhomave:<[^>]*>\s*<bdi>([^<]*)<', content, re.S | re.I)
            if nrRooms:
                nrRooms = nrRooms.group(1).strip()
            else:
                nrRooms = ''
            address = re.search(r'<span>Adresa\/Rruga:<[^>]*>\s*<bdi>([^<]*)<', content, re.S | re.I)
            if address:
                address = address.group(1).strip().replace("&#203;", "Ë").replace("&#235;", "ë")
            else:
                address = ''
            space = re.search(r'<span>[^r]*rfaqe:<[^>]*>\s*<bdi>\s*(\d{1,6})\s*([^<]*)\s*<', content, re.S | re.I) #rishiqim i regex paternit per grupacione si dhe output per csv
            if space:
                space = space.groups(1)
            else:
                space = ''
            description = re.search(r'<span>[^.]*vendbanimin:<[^>]*>\s*<bdi>\s*([^<]*)<', content, re.S | re.I)
            if description:
                description = description.group(1).strip().replace("&#203;", "Ë").replace("&#235;", "ë")
            else:
                description = ''
            description2 = re.search(r'description-area">\s*<span>([^<]*)<', content, re.S | re.I)
            if description2:
                description2 = description2.group(1).strip().replace("&#203;", "Ë").replace("&#235;", "ë")
            else:
                description2 = ''
            rentOrsell = re.search(r'<span>Lloji\s*i\s*shpalljes:<[^>]*>\s*<bdi>\s*([^<]*)<', content, re.S | re.I)
            if rentOrsell:
                rentOrsell = rentOrsell.group(1).strip()
            else:
                rentOrsell = ''
            publishedFrom = re.search(r'<span>Publikuar\s*nga:<[^>]*>\s*<bdi>\s*([^<]*)<', content, re.S | re.I)
            if publishedFrom:
                publishedFrom = publishedFrom.group(1).strip()
            else:
                publishedFrom = ''
            gender = re.search(r'Gjinia:<[^<]*<bdi>([^<]*)<', content, re.S | re.I)
            if gender:
                gender = gender.group(1).strip()
            else:
                gender = ''
            roomMateGender = re.search(r'Shokut\s*të\s*Dhomës:<[^<]*<bdi>([^<]*)<', content, re.S | re.I)
            if roomMateGender:
                roomMateGender = roomMateGender.group(1).strip()
            else:
                roomMateGender = ''
            municipality = re.search(r'<span>Komuna:<[^>]*>\s*<bdi>\s*([^<]*)<', content, re.S | re.I)
            if municipality:
                municipality = municipality.group(1).strip()
            else:
                municipality = ''


            yield {
                'publishDate': publishDate,
                'publishTime': publishTime,
                'views': views,
                'title': title,
                'telephone': telephone,
                'viber': viber,
                'price': price,
                'valute': valute,
                'period': period,
                'nrRooms': nrRooms,
                'address': address,
                'description': description,
                'description2': description2,
                'rentOrsell': rentOrsell,
                'gender': gender,
                'roomMateGender': roomMateGender,
                'publishedFrom': publishedFrom,
                'municipality': municipality,
                'space': space,
            }

