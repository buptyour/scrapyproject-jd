# -*- coding: utf-8 -*-
import scrapy
import urllib
from copy import deepcopy


class JdspiderSpider(scrapy.Spider):
    name = 'jdspider'
    allowed_domains = ['jd.com']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        # 分组
        dt_list = response.xpath('.//div[@class="mc"]/dl/dt')  # 大分类列表
        for dt in dt_list:
            item = {}
            item['b_cate'] = dt.xpath('./a/text()').extract_first()
            em_list = dt.xpath('./following-sibling::dd[1]/em')  # 小分类列表
            for em in em_list:
                item['s_href'] = em.xpath('./a/@href').extract_first()
                item['s_cate'] = em.xpath('./a/text()').extract_first()

                if item['s_href'] is not None:
                    item['s_href'] = "https:" + item['s_href']  # 补充url地址
                    yield scrapy.Request(
                        item['s_href'],
                        callback=self.parse_book_list,
                        meta={"item": deepcopy(item)}
                    )

    # 解析书的列表页
    def parse_book_list(self, response):
        item = response.meta["item"]
        # 分组
        li_list = response.xpath('//div[@id="plist"]/ul/li')
        for li in li_list:
            item['book_name'] = li.xpath('.//div[@class="p-name"]/a/em/text()').extract_first().strip()
            item['book_author'] = li.xpath('.//span[@class="author_type_1"]/a/@title').extract()
            item['book_date'] = li.xpath('.//span[@class="p-bi-date"]/text()').extract_first().strip()
            item['book_date'] = item['book_date'].split("-")[0]
            yield item

        # 翻页
        next_url = response.xpath('//a[@class="pn-next"]/@href').extract_first()
        if next_url is not None:
            # 补充下一页的url地址
            next_url = urllib.parse.urljoin(response.url, next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse,
                meta={"item": item}
            )
