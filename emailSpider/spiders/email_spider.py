import pkgutil

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
from scrapy.http import Request
from w3lib.url import safe_url_string


URL_RESOURCE_NAME = 'error-domains.csv'
EMAIL_WRONG_SUFFIXES = ('png', 'jpg')


class EmailItem(scrapy.Item):
    domain = scrapy.Field() 
    email = scrapy.Field()
    source = scrapy.Field()


class EmailSpider(CrawlSpider):
    name = 'email_spider'
    http_user = 'e56a3bc2612e408b803a9c9df6fd0d24'

    domainfile = pkgutil.get_data('emailSpider', URL_RESOURCE_NAME)
    allowed_domains = [domain.decode('utf-8').strip() for domain in domainfile.splitlines()]
    start_urls = ['http://{0}'.format(domain) for domain in allowed_domains]

    def start_requests(self):
        for url in self.start_urls:
            request = SplashRequest(
    			url, 
    			self.parse,
    			endpoint='render.html',
    			args={
    				'viewport':'full',
    				'render_all': 1,
    				'wait': 5,
    				},
    			)
            self.logger.info('Start Requests %s' % request.url)
            yield request

    def parse(self, response):
    	le = LinkExtractor(allow=('[Pp]rivacy.*',), unique=True)
    	links = le.extract_links(response)
    	for link in links:
    		self.logger.info('--> Link: {0}'.format(safe_url_string(link.url)))
    		request = Request(url=link.url, callback=self.parse_privacy_policy)
            request.meta['domain'] = response.url[len('http://'):]
            yield request

    def parse_privacy_policy(self, response):
        self.logger.info('--> Privacy policy page! {0}'.format(response.url))
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
	        	emailitems.append(emailitem)
        return emailitems
