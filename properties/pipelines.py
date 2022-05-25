# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re
import locale
from geopy.geocoders import Nominatim
import json
from itemadapter import ItemAdapter
import time

geolocator = Nominatim(user_agent='hh')


class PropertiesPipeline(object):
    """{"size": "111 m\u00b2", "price": "2\u00a0900\u00a0000 kr"}"""
    def process_item(self, item, spider):

        if item.get('finn_code'):
            location_ = geolocator.geocode(item["address"])
            if location_:
                a_ = location_.address
                a_ = a_.split(',')
            
                if a_[-1] == ' Norge':
                    item['district'] = a_[-4]
                    item['lat'] =location_.latitude
                    item['lon'] =location_.longitude
            time.sleep(1)

            #size\price\price per suqre meter

            # ['68 m²', '2\xa0390\xa0000', '\xa0', 'kr']
                     
            for a_ in item['size_string']:
                if re.search(r'(\d+)\D?-\D?(\d+).?m',a_):
                    obj = re.search(r'(\d+)\D?-\D?(\d+).?m',a_)
                    item['size_min'] = int(obj[1])
                    item['size_max'] = int(obj[2])
                    item['size'] = (item['size_min'] + item['size_max'])/2

                elif re.search(r'(\d+).?m',a_):
                    obj = re.search(r'(\d+).?m',a_)
                    item['size'] = int(obj[1])
                else:
                    pass
                     

            for a_ in item['price_type_string']:

            # 1.0)['Totalpris: 3\xa0283\xa0021 kr • Fellesutg.: 5\xa0832 kr']
            # 1.1)['Totalpris: 3\xa0283\xa0021 kr]
            # 1.2)['Totalpris: 3\xa0283\xa0021 - 12312323 kr]
            # 1.3)['Totalpris: 3\xa0283\xa0021 - 12312323 kr • Fellesutg.: 5\xa0832 - 3432 kr']
            # 2# ['Andel • Leilighet • 2 soverom']
     
                a_ = a_.replace(u'\xa0', u'')

                if re.search(r'\d.kr',a_): # 1
                    
                    if re.search(r'\d+\D?-\D?\d+',a_):   # 1.2 and 1.3    -
                        obj = re.search(r'(Totalpris:(?P<t>.*\d+.?)kr.*Fellesutg.:(?P<f>.*\d+.?)kr)|(Totalpris:(?P<tt>.*\d+.?)kr)',a_,re.M|re.I)

                        t_ = obj.group('t') if obj.group('t') else obj.group('tt')
                        f_ = obj.group('f')
                        if f_:
                            item['mmd'] = f_.split("-")  # ['4533640', '14933640']
                            item['mmd'] = (int(item['mmd'][0]) + int(item['mmd'][1])) /2
                        if t_:
                            item['price'] = t_.split("-")  # ['4533640', '14933640']
                            item['price_min'] = min(int(item['price'][0]),int(item['price'][1]))
                            item['price_max'] = max(int(item['price'][0]),int(item['price'][1]))
                            item['price'] = (int(item['price'][0]) + int(item['price'][1])) /2
                    else: # 1.0 and 1.1)
                        obj = re.search(r'(Totalpris:(?P<t>\D*\d+.?)kr.*Fellesutg.:(?P<f>\D*\d+.?)kr)|(Totalpris:(?P<tt>\D*\d+.?)kr)',a_,re.M|re.I)
                        item['price'] = int(obj.group('t')) if obj.group('t') else int(obj.group('tt'))
                        item['mmd'] = obj.group('f')

                else: # 2
                    item['type'] = a_
                 
            

        return item


class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('items_pp.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item  

