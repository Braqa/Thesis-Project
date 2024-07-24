import scrapy
import re
from scrapy.utils.response import open_in_browser

# Klasa e gjeneruar per Spider
class GetofkerlinksSpider(scrapy.Spider):
    name = 'getOfKerLinks'
    allowed_domains = ['www.ofertasuksesi.com']
    start_urls = ['https://www.ofertasuksesi.com/']


    def __init__(self):
        self.page = 2
        self.inserted = {str(x).strip() for x in open('parcellID.txt', 'rt')}


    # Metoda per ruajtjen e linqeve ne text file
    def saveLink(self, i):
        try:
            with open('parcellID.txt', 'at', encoding="utf-8") as p:
                p.write(f'{i}\n')
                p.close()
        except Exception as e:
            raise e
        return


    # Metoda e parsimit te response (kontentit) dhe targetimi i linkut te patundshmerive
    def parse(self, response):
        # open_in_browser(response)
        if response.status == 200:
            RealEstLink = re.search(r'<a\s*href="([^"]*)">[^>]*>[^<]*<span>Patundshm', response.text, re.S | re.I)
            if RealEstLink:
                RealEstLink = RealEstLink.group(1)
                yield scrapy.Request(
                    url=f'{RealEstLink}',
                    meta={
                      'RealEstLink': RealEstLink
                    },
                    dont_filter=True,
                    callback=self.getRealEstateTab
                )

    # Metoda e parsimit te response (kontentit) dhe targetimi i linkut te patundshmerive per nje kategori me specifike
    def getRealEstateTab(self, response):
        if response.status == 200:
            RealEstLink = response.meta['RealEstLink']
            yield scrapy.Request(
                url=f'{RealEstLink}?keyword=&category=&city=&subcategory[]=13&subcategory[]=14',
                dont_filter=False,
                callback=self.getRealEstateSubCategories
            )

    # Metoda per nxerrjen dhe ruajtjen e te gjitha linqeve nga cdo faqe deri ne fund
    def getRealEstateSubCategories(self, response):
        if response.status == 200:
            # open_in_browser(response)
            ListOfLinks = re.findall(r'<a\s*href="https:\/\/www\.ofertasuksesi\.com\/shpalljet\/([^"]*)"\s*class=[^>]*>Lexo', response.text, re.S | re.I)
            for link in ListOfLinks:
                if link not in self.inserted:
                    self.saveLink(link)
                    print(f'Saved Links: {link}')
                else:
                    print(f'Already Saved {link}')

            # Kalimi neper faqet tjera (pagination)
            if 'next' in response.text:
                yield scrapy.Request(
                    url=f'https://www.ofertasuksesi.com/kategorite/1-patundshmeri?keyword=&category=&city=&subcategory%5B0%5D=13&subcategory%5B1%5D=14&page={self.page}',
                    dont_filter=True,
                    callback=self.getRealEstateSubCategories
                )
                self.page = self.page + 1