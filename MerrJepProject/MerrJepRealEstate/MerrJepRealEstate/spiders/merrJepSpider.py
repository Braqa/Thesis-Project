import scrapy
import re
from scrapy.utils.response import open_in_browser

# Klasa e gjeneruar per Spider
class MerrjepspiderSpider(scrapy.Spider):
    name = 'merrJepSpider'
    #allowed_domains = ['www.merrjep.com']
    start_urls = ['http://www.merrjep.com/']


    def __init__(self):
        self.inserted = {str(x).strip() for x in open('parcellID.txt', 'rt', encoding="utf-8")}


    # Metoda per ruajtjen e linkave
    def saveLink(self, id):
        try:
            with open('parcellID.txt', 'at', encoding="utf-8") as p:
                p.write(f'{id}' + '\n')
        except Exception as e:
            raise e
        return

    # Metoda e parsimit te response (kontentit) dhe targetimi i linkut te patundshmerive
    def parse(self, response):
        if response.status == 200:
            # open_in_browser(response)
            RealEstLink = re.search(r'href="([^"]*)">\s*<i class="groupicon icon-house">', response.text, re.S | re.I)
            if RealEstLink:
                RealEstLink = RealEstLink.group(1)
                yield scrapy.Request(
                    url=f'{RealEstLink}',
                    dont_filter=True,
                    callback=self.GetAllLinksFromRealEst
                )

    # Metoda per nxerrjen dhe ruajtjen e te gjitha linqeve nga cdo faqe deri ne fund
    def GetAllLinksFromRealEst(self, response):
        if response.status == 200:
            ListOfLinks = re.findall(r'<div[^<]*<span[^<]*<a\s*class=[^=]*="\/shpallja\/vendbanime\/([^"]*)"\s*title', response.text, re.S | re.I)
            for link in ListOfLinks:
                if link not in self.inserted:
                    self.saveLink(link)
                    print(f'Saved Links: {link}')
                else:
                    print(f'Already Saved {link}')

            # Kalimi neper faqet tjera (pagination)
            if 'Tjetra' in response.text:
                nextpage = re.search(r'<a\s*class=[^=]*=\s*"([^"]*)">\s*Tjetra', response.text, re.S | re.I)
                if nextpage:
                    nextpage = nextpage.group(1)
                    print(f'Faqja numer: {nextpage}')
                    yield scrapy.Request(
                        nextpage,
                        dont_filter=True,
                        callback=self.GetAllLinksFromRealEst
                        )