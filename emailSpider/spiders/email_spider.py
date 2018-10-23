import pkgutil

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
from scrapy.http import Request
from w3lib.url import safe_url_string
from emailSpider import settings


URL_RESOURCE_NAME = 'data/input/data-brokers4.csv'
EMAIL_WRONG_SUFFIXES = ('png', 'jpg')
HTTP_PREFIX = 'http://'
LUA_SOURCE = pkgutil.get_data('emailSpider', 'scripts/crawlera.lua').decode('utf-8')


def make_request(url, callback):
	if settings.SPLASH:
		return SplashRequest(
			url, 
			callback,
			endpoint='render.html',
			args={
				'viewport':'full',
				'render_all': 1,
				'lua_source': LUA_SOURCE,
				'crawlera_user': settings.CRAWLERA_APIKEY,
				'wait': .5,
				},
			cache_args=['lua_source']
			)
	else:
		return Request(url=url, callback=callback)


class EmailItem(scrapy.Item):
	domain = scrapy.Field() 
	email = scrapy.Field()
	source = scrapy.Field()
	page_type = scrapy.Field()


class EmailSpider(CrawlSpider):
	name = 'email_spider'
	http_user = 'e56a3bc2612e408b803a9c9df6fd0d24'

	domainfile = pkgutil.get_data('emailSpider', URL_RESOURCE_NAME)
	allowed_domains = [domain.decode('utf-8').strip() for domain in domainfile.splitlines()]
	start_urls = ['{0}{1}'.format(HTTP_PREFIX, domain) for domain in allowed_domains]

	def start_requests(self):
		for url in self.start_urls:
			request = make_request(url, self.parse)
			request.meta['domain'] =  url[len(HTTP_PREFIX):]
			self.logger.info('Start Requests %s' % request.url)
			yield request

	def parse(self, response):
		expressons = {
			'[Pp]rivacy': 'Privacy policy',
			'[Cc]ontact': 'Contact',
			'[Tt]erms|T&C|T&c|t&c': 'T&Cs'
		}
		for expresson, page_type in expressons.items():
			le = LinkExtractor(allow=(expresson), unique=True)
			links = le.extract_links(response)
			for link in links:
				self.logger.info('--> {0} link: {1}'.format(page_type, safe_url_string(link.url)))
				request = make_request(link.url, self.parse_page_for_emails)
				request.meta['domain'] = response.meta['domain']
				request.meta['page_type'] = page_type
				yield request		

	def parse_page_for_emails(self, response):
		self.logger.info('--> Crawled {0} page! {1}'.format(response.meta['page_type'], response.url))
		selector = scrapy.Selector(response)
		emails = list(set(selector.xpath('//body').re('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')))
		emailitems = []
		for email in emails:
			email = email.lower()
			if not email.endswith(EMAIL_WRONG_SUFFIXES):
				if email.endswith('.'):
					email = email[:-1]
				self.logger.info('--> Email: {0}'.format(email))
				emailitem = EmailItem()
				emailitem["domain"] = response.meta['domain']
				emailitem["email"] = email
				emailitem["source"] = response.url
				emailitem["page_type"] = response.meta['page_type']
				emailitems.append(emailitem)
		return emailitems

