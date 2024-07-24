import scrapy
import re
from scrapy.utils.response import open_in_browser

class GetcontfromlinksSpider(scrapy.Spider):
    name = 'getContFromLinks'
    allowed_domains = ['www.ofertasuksesi.com']
    start_urls = ['https://www.ofertasuksesi.com/kategorite/1-patundshmeri']

    def __init__(self):
        self.parcells = {str(x).strip() for x in open('parcellID.txt', 'rt')}
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
                        url=f'https://www.ofertasuksesi.com/shpalljet/{parcel}',
                        meta={
                            'parcel': parcel
                        },
                        dont_filter=False,
                        callback=self.getDataFromLink
                    )
                else:
                    print(f'Already Saved {parcel}')

    # Metoda per nxjerrjen e te dhënave
    def getDataFromLink(self, response):
        if response.status == 200:
            parcel = response.meta['parcel']
            self.saveParcels(parcel)
            print(f'Saved Links: {parcel}')
            content = response.text
            title = re.search(r'<header>\s*<h1[^>]*>\s*([^<]*)<', content, re.S | re.I)
            if title:
                title = title.group(1).strip()
            else:
                title = ''
            posted = re.search(r'Postuar[^<]*<b>([^<]*)<', content, re.S | re.I)
            posted = posted.group(1).strip()
            category = re.search(r'kategorin[^<]*<a[^>]*>([^<]*)<', content, re.S | re.I)
            category = category.group(1).strip()
            views = re.search(r'class="fa\s*fa-eye">[^<]*<\/i>\s*([^<]*)<', content, re.S | re.I)
            views = views.group(1).strip()
            telephone = re.search(r'INFO:<\/h5>\s*<[^<]*<[^<]*<[^>]*>[^<]*<[^<]*<span><b>([^<]*)<', content, re.S | re.I)
            telephone = telephone.group(1).strip()


            yield {
                'title': title,
                'posted': posted,
                'category': category,
                'views': views,
                'telephone': telephone,
            }
