
import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from spiders.pdf_spider import PdfSpider

if __name__ == '__main__':
    # Configure logging
    configure_logging()
    
    # Create a Scrapy crawler object
    runner = CrawlerRunner({
        'USER_AGENT': 'Mozilla/5.0',
    })

    # Add the spider to the crawler
    d = runner.crawl(PdfSpider)
    
    # Add callback to stop reactor
    d.addBoth(lambda _: reactor.stop())
    
    # Start the crawler
    reactor.run()
