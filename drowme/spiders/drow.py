import scrapy


class DrowSpider(scrapy.Spider):
    name = 'drow'
    allowed_domains = ['drowme.wordpress.com']
    start_urls = ['https://drowme.wordpress.com/']

    def parse(self, response):
        pass
