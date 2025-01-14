import scrapy
import pdfplumber
import tabula
import pandas as pd
import os
import tempfile


class PdfSpider(scrapy.Spider):
    name = "pdf_spider"
    start_urls = ['https://www.ncdazqr.com/']

    def parse(self, response):
        # Find product category links
        for category_link in response.css(
                'a.preFade.fadeIn::attr(href)').getall():
            yield response.follow(category_link, callback=self.parse_category, dont_filter=True)

    def parse_category(self, response):
        # Find product links and next page link
        for product_link in response.css(
                'a.blog-more-link.preFade.fadeIn::attr(href)').getall():
            yield response.follow(product_link,
                                  callback=self.parse_product)
        next_page_link = response.css('div.older > a::attr(href)').get()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse_category)

    def parse_product(self, response):
        # Find Google Drive link
        google_drive_link = response.css(
            'p.preFade.fadeIn > a::attr(href)').get()
        if google_drive_link:
            yield response.follow(google_drive_link, callback=self.parse_pdf)

    def parse_pdf(self, response):
        # Download the PDF
        pdf_bytes = response.body
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_file_path = temp_file.name
            # Parse PDF content
            with pdfplumber.open(temp_file_path) as pdf:
                for page in pdf.pages:
                    # Extract tables
                    tables = tabula.read_pdf(temp_file_path,
                                             pages=page.page_number,
                                             multiple_tables=True)
                    for table in tables:
                        # Extract table header text
                        header_text = table.df.columns.tolist()[0]
                        # Check if header contains "Cannabinoids" or "Terpenes"
                        if "Cannabinoids" in header_text:
                            # Process table data using pandas
                            df = pd.DataFrame(table)
                            # Append data to CSV
                            df.to_csv('extracted_data.csv',
                                      mode='a',
                                      header=False,
                                      index=False)
                        elif "Terpenes" in header_text:
                            # Process table data using pandas
                            df = pd.DataFrame(table)
                            # Append data to CSV
                            df.to_csv('extracted_data.csv',
                                      mode='a',
                                      header=False,
                                      index=False)
        # Delete the temporary file
        os.remove(temp_file_path)
