import scrapy

#from src.data.preprocessing import preprocess_data  # Import preprocessing function
from spiders.pdf_spider import PdfSpider # Import the spider

if __name__ == '__main__':
    # Create a Scrapy crawler object
    crawler = scrapy.crawler.CrawlerRunner({
        'USER_AGENT': 'Mozilla/5.0',  # Set the user agent for the crawler
    })

    # Add the spider to the crawler
    crawler.crawl(PdfSpider)

    # Start the crawler
    crawler.start()

    # Preprocess the extracted data
    #preprocess_data()  # Call the preprocessing function