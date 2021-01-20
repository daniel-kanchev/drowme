import scrapy
from datetime import datetime
import sqlite3


class DrowSpider(scrapy.Spider):
    name = 'drow'
    allowed_domains = ['drowme.wordpress.com']
    start_urls = ['https://drowme.wordpress.com/']
    conn = sqlite3.connect('drowme.db')
    c = conn.cursor()

    def parse(self, response):
        self.c.execute(""" CREATE TABLE IF NOT EXISTS articles 
                (title text, date text, author text, category text, link text, content text) """)

        article_link = response.xpath("//article//h1/a/@href").get()
        yield response.follow(article_link, self.parse_article)

    def parse_article(self, response):
        previous_page = response.xpath("//a[@rel='prev']/@href").get()
        if previous_page:
            self.parse_item(response)
            yield response.follow(previous_page, self.parse_article)

    def parse_item(self, response):
        title = response.xpath("//article//h1/descendant-or-self::*/text()").getall()
        title = title[0]

        category = response.xpath("(//div[@class='entry-meta'])[1]/descendant-or-self::*/text()").getall()
        category = [item for item in category if item.strip()]
        category = category[0]

        info = response.xpath("(//div[@class='entry-meta'])[2]/descendant-or-self::*/text()").getall()
        info = [item for item in info if item.strip()]
        date = info[0]
        date_time_obj = datetime.strptime(date, '%B %d, %Y')
        date = date_time_obj.strftime("%Y/%m/%d")

        author = info[1]

        content = []
        paragraphs = response.xpath("//div[@class='entry-content']//p")
        for p in paragraphs:
            text = p.xpath(".//descendant-or-self::*/text()").getall()
            text = [item for item in text if item.strip()]
            text = "".join(text)
            content.append(text)

        content = [item for item in content if item.strip()]
        content = "\n".join(content)

        self.c.execute("""SELECT * FROM articles WHERE title = ? AND date = ?""",
                       (title, date,))
        duplicate = self.c.fetchall()
        if len(duplicate):
            return

        # Insert values
        self.c.execute("INSERT INTO articles (title, date, author, category, link, content)"
                       " VALUES (?,?,?,?,?,?)", (title, date, author, category, response.url, content))
        self.conn.commit()  # commit after every entry
