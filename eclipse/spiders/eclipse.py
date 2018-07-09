import re
from scrapy import Spider, Item, Field
from scrapy.http.request import Request
from scrapy_splash.request import SplashRequest

class EclipseItem(Item):
	pluginName = Field()
	publisher = Field()
	downloads = Field()
	shortDesc = Field()S
	partner = Field()
	price = Field()
	capabilities = Field()
	categories = Field()
	tags = Field()

class EclipseSider(Spider):

	name = 'eclipse'

	base = 'https://marketplace.visualstudio.com'

	def start_requests(self):
		with open('/home/aleksey/Downloads/vsm_links.txt') as handle:
			for url in handle:
				req = SplashRequest(self.base + url[:-1])
				req.meta['splash'].setdefault('args', {})['timeout'] = 220
				req.meta['splash']['endpoint'] = 'render.html'
				yield req
				# break


	def parse(self, response):
		item = EclipseItem()
		item['pluginName'] = response.css('div.item-header-content > h1 > span.ux-item-name::text').extract_first()
		item['publisher'] = response.css('div.ux-item-publisher > h2 > a::text').extract_first()
		item['downloads'] = response.css('div.ux-item-rating > span::text').extract_first()
		item['shortDesc'] = response.css('div.ux-item-shortdesc::text').extract_first()

		display = response.css('div.ux-vsippartner::attr(style)').extract_first()
		item['partner'] = not bool(display and u'display: none' in display) 

		paid = response.css('span.ux-item-titleTag.light::text').extract_first()
		if paid:
			item['price'] = paid.lower()
		else:
			item['price'] = 'free' 

		item['capabilities'] = ' '.join(response.css('div.ux-section-capabilities *::text').extract())
		
		cats_and_tags = response.css('div.meta-data-list-container > div.ux-section-meta-data-list')
		for meta in cats_and_tags:
			header = meta.css('h3.ux-section-header::text').extract_first().lower()
			data = meta.css('.meta-data-list-link::text').extract()
			if header == 'tags':
				item['tags'] = data
			elif header == 'categories':
				item['categories'] = data
			else:
				print('ERROR: {} {}'.format(header, response.url))
		if not item.get('tags'):
			item['tags'] = []
		if not item.get('categories'):
			item['categories'] = []
		yield item
