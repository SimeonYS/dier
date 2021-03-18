import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import DierItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class DierSpider(scrapy.Spider):
	name = 'dier'
	start_urls = ['https://blog.dierickxleys.be/']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="button dark empty"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="row-fluid-wrapper row-depth-2 row-number-4 "]//div[@class="span12 widget-span widget-type-raw_jinja "]/text()').get().strip()
		title = response.xpath('//h1/span/text()').get()
		content = response.xpath('//span[@id="hs_cos_wrapper_post_body"]//text()[not (ancestor::script)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=DierItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
