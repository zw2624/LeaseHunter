# -*- coding: utf-8 -*-
import scrapy
import json
from re import sub
from decimal import Decimal
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_app.items import ScrapyAppItem

CITY = "chicago-il"
#

class IcrawlerSpider(CrawlSpider):
    name = 'icrawler'
    #
    # rules = (
    #     Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    # )
    start_urls = ['https://www.apartments.com/apartments/' + CITY + '/student-housing/']

    def generate_request(self, url, response):
        try:
            return scrapy.Request(url, meta={'dont_redirect': True, "handle_httpstatus_list": [301]}, callback=self.parse)
        except:
            try:
                url = response.urljoin(url)
                return scrapy.Request(url, callback=self.parse)
            except:
                pass


    def parse(self, response):
        if response.xpath("//div[@id='profileHeaderWrapper']") == []:
            if response.xpath("//header[@class='placardHeader']/a/@href").extract() == []:
                ret = response.xpath("//script[@type='application/ld+json']//text()").extract_first()
                data = json.loads(ret)
                for item in data['about']:
                    yield self.generate_request(item['url'], response)
            else:
                for link in response.xpath("//header[@class='placardHeader']/a/@href").extract():
                    yield self.generate_request(link, response)
            next = response.xpath("//div/a[@class='next ']/@href").get()
            if next != None:
                yield self.generate_request(next, response)
        else:
            contact = response.xpath("//span[@class='contactPhone']/text()").extract_first()
            if contact is None:
                contact = "no phone provided"
            full_address = response.xpath("//div[@class='propertyAddress']/h2/span/text()").extract()
            url = response.request.url
            try:
                address = full_address[-4]
            except:
                address = response.xpath("//div[@id='breadcrumbs-container']/span/text()").extract()[-1]
            city = full_address[-3]
            state = full_address[-2]
            postal = full_address[-1]
            name = response.xpath("//h1[@class='propertyName']/text()").get().strip(' \n\r ')
            desciption = response.xpath("//section[@id='descriptionSection']/p/text()").get().strip(' \n\r ')
            tables = response.xpath("//table[contains(@class, 'availabilityTable')]/tbody/tr[contains(@class, 'rentalGridRow')]")
            for table in tables:
                item = ScrapyAppItem()
                beds = table.xpath("td[@class='beds']/span[@class='shortText']/text()").get().strip(' \n\r ')
                baths = table.xpath("td[@class='baths']/span[@class='shortText']/text()").get().strip(' \n\r ')
                rents = table.xpath("td[@class='rent']/text()").get()
                if rents:
                    rents = rents.strip(' \n\r ')
                    if 'Call' in rents:
                        continue
                    rents = int(sub(r'[^\d.]', '', rents))
                deposit = table.xpath("td[@class='deposit']/text()").get()
                if deposit:
                    deposit = deposit.strip(' \n\r ')
                else:
                    deposit = 0
                unit = table.xpath("td[@class='unit']/text()").get()
                if unit:
                    unit = unit.strip(' \n\r ')
                    item['unit'] = unit
                lease_length = table.xpath("td[@class='leaseLength']/text()").get()
                if lease_length:
                    lease_length = lease_length.strip(' \n\r ')
                    item['lease_length'] = lease_length
                available = table.xpath("td[@class='available']/text()").get()
                if available:
                    available = available.strip(' \n\r ')
                    item['available'] = available
                item['contact'] = contact
                item['url'] = url
                item['address'] = address
                item['city'] = city
                item['state'] = state
                item['postal'] = postal
                item['name'] = name
                item['desciption'] = desciption
                item['beds'] = beds
                item['baths'] = baths
                item['rent'] = rents
                item['deposit'] = deposit
                yield item