import scrapy
import re
from ..constants import LOCATIONS

# https://www.finn.no/realestate/homes/search.html?filters=&location=0.20061

class PropertiesSpider(scrapy.Spider):
    """Run 'scrapy crawl properties' in virtualenv"""
    name = 'properties'
    allowed_domains = ['finn.no']
    start_urls = ['https://www.finn.no/realestate/homes/search.html?filters=' + parameter for parameter in LOCATIONS]

    def parse(self, response):
        parameter = response.request.url.split("filters=")[1][:17]
        location = LOCATIONS[parameter]

        for unit in response.xpath('/html/body/div[2]/main/div[2]/div/section[1]/div[2]/article'):
            item = dict()
            
            item['finn_code'] = unit.css('h2 a').attrib['id']
            if unit.attrib['class'] == 'ads__unit':
                item['size_string'] =unit.css("div.ads__unit__content__keys ::text").getall()
                item['price_type_string'] = unit.css("div.ads__unit__content__list ::text").getall()
                item['address'] = unit.css("div.ads__unit__content__details ::text").getall()[0]
            else:
                item['size_string'] = unit.css("div.flex.flex-wrap.justify-between.font-bold.mb-8 ::text").getall() #  ['68 m²', '2\xa0390\xa0000', '\xa0', 'kr']
                item['price_type_string'] = unit.css("div.text-14.text-gray-500 ::text").getall()
                item['address'] = unit.css("span.text-14.text-gray-500::text").getall()[0]

            
            item['unit_title'] = unit.css('h2 a::text').get()
            item['unit_link'] = unit.css('h2 a').attrib['href']
            item['unit_pic'] = unit.css('img').attrib['src']
            item['location'] = location
            
            yield item

        for a in response.css('a.button--icon-right'):
            print('RESPONSE: ', a)
            yield response.follow(a, callback=self.parse)
