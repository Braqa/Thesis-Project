import scrapy
import re
from scrapy.utils.response import open_in_browser

# Klasa e gjeneruar per Spider
class GetgjirafalinksSpider(scrapy.Spider):
    name = 'getGjirafaLinks'
    #allowed_domains = ['gjirafa.com']
    start_urls = ['https://gjirafa.com/Top/Patundshmeri?f=0&r=Prishtine']

    def __init__(self):
        self.count = 0
        self.end = 4551
        self.inserted = {str(x).strip() for x in open('parcelID.txt', 'rt')}

    # Metoda per ruajtjen e linqeve ne text file
    def saveParcels(self, i):
        try:
            with open('parcelID.txt', 'at') as p:
                p.write(f'{i}\n')
                p.close()
        except Exception as e:
            raise e
        return


    # Metoda per nxerrjen dhe ruajtjen e te gjitha linqeve nga cdo faqe deri ne fund
    def parse(self, response):
        # open_in_browser(response)
        if response.status == 200:
            parcelList = re.findall(r'<a target="_blank"\s*id="http://gjirafa.com/Shpallje/Patundshmeri/([^"]*)"\s*class="[^"]*"\s*href="http://gjirafa\.com/Shpallje/Patundshmeri[^"]*"', response.text, re.S)
            for parcel in parcelList:
                if parcel not in self.inserted:
                    self.saveParcels(parcel)
                    print(f'Link ADDED {parcel}')
                else:
                    print(f'This LINK is COPY {parcel}')

            # Kalimi neper faqet tjera (pagination)
            # if self.count <= self.end:
            if 'para' in response.text:
                if self.count <= self.end:
                    yield scrapy.Request(
                        url=f'https://gjirafa.com/Top/Patundshmeri?f={self.count}&r=Prishtine',
                        dont_filter=False,
                        callback=self.parse
                    )
                    self.count = self.count + 1
                else:
                    print('End of crawling')


#ka pas ka fundi i linqeve 4500+ linqe te patundshmerive te gjirafes po qe permbajne linqe ose patundeshmeri ne faqe tjera si mirlire.com etj (injorohen keto)