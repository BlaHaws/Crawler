import scrapy
from bs4 import BeautifulSoup
import pdfplumber
import tabula
import pandas as pd
import os
import tempfile


class PdfSpider(scrapy.Spider):
    name = "pdf_spider"
    start_urls = ['https://www.ncdazqr.com/']

    def parse(self, response):
        # Use BeautifulSoup to parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find product category links with BeautifulSoup
        category_links = soup.select('div nav div a[href]')
        for link in category_links:
            yield response.follow(link.get('href'),
                                  callback=self.parse_category,
                                  dont_filter=True)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find product links
        product_links = soup.select('a.blog-more-link')
        for link in product_links:
            yield response.follow(link.get('href'),
                                  callback=self.parse_product)

        # Find next page link
        next_page = soup.select_one('div a[href]')
        if next_page:
            yield response.follow(next_page.get('href'),
                                  callback=self.parse_category)

    def parse_product(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find Google Drive link
        drive_link = soup.select_one('p a(href)')
        if drive_link:
            yield response.follow(drive_link.get('href'),
                                  callback=self.parse_pdf)

    download_count = 0  # Class variable to track downloads

    def parse_pdf(self, response):
        if self.download_count > 0:  # Skip if we already downloaded one
            return
        # Download the PDF
        pdf_bytes = response.body
        self.download_count += 1  # Increment counter
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
                            df = pd.DataFrame(table)
                            df.to_csv('extracted_data.csv',
                                      mode='a',
                                      header=False,
                                      index=False)
                        elif "Terpenes" in header_text:
                            df = pd.DataFrame(table)
                            df.to_csv('extracted_data.csv',
                                      mode='a',
                                      header=False,
                                      index=False)
        # Delete the temporary file
        os.remove(temp_file_path)
