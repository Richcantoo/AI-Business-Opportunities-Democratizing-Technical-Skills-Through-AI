#!/usr/bin/env python3
"""
TradingView Pine Script Documentation Scraper v2
A more robust approach that handles the documentation structure properly
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import weasyprint
from PyPDF2 import PdfReader, PdfWriter
import re
from collections import OrderedDict

class PineScriptDocsScraper:
    def __init__(self):
        self.base_url = "https://www.tradingview.com/pine-script-docs/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.visited_urls = set()
        self.pages_data = OrderedDict()
        self.output_dir = "pine_script_pdfs"
        self.temp_dir = "temp_html"
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Known sections of Pine Script documentation
        self.known_sections = [
            "welcome",
            "language",
            "concepts",
            "migration_guides",
            "annotations",
            "colors",
            "fills",
            "lines_and_boxes", 
            "tables",
            "plots",
            "text_and_shapes",
            "libraries",
            "indicators",
            "strategies",
            "errors",
            "release_notes",
            "faq"
        ]
    
    def get_page_content(self, url):
        """Fetch page content with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
    
    def extract_documentation_links(self, html_content, current_url):
        """Extract all documentation links from the page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        
        # Look for navigation links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(current_url, href)
            
            # Only include Pine Script documentation links
            if 'pine-script-docs' in absolute_url and absolute_url.startswith('https://www.tradingview.com'):
                links.add(absolute_url)
        
        return links
    
    def clean_html_content(self, html_content, page_url):
        """Clean and prepare HTML content for PDF conversion"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove navigation, headers, footers, and scripts
        for element in soup.find_all(['script', 'noscript', 'header', 'footer', 'nav']):
            element.decompose()
        
        # Remove specific classes that might be problematic
        for class_name in ['sidebar', 'navigation', 'menu', 'header', 'footer']:
            for element in soup.find_all(class_=lambda x: x and class_name in x):
                element.decompose()
        
        # Find the main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and 'content' in x)
        
        if not main_content:
            main_content = soup.body or soup
        
        # Create a new clean HTML document
        clean_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Pine Script Documentation</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #2c3e50;
                    margin-top: 24px;
                    margin-bottom: 16px;
                }}
                h1 {{ font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                h2 {{ font-size: 1.5em; }}
                h3 {{ font-size: 1.25em; }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Monaco', monospace;
                }}
                pre {{
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 12px;
                    overflow-x: auto;
                    line-height: 1.4;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    margin: 0;
                    padding-left: 16px;
                    color: #666;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f4f4f4;
                    font-weight: bold;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                .note, .warning, .tip {{
                    padding: 12px;
                    margin: 16px 0;
                    border-radius: 4px;
                }}
                .note {{
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196f3;
                }}
                .warning {{
                    background-color: #fff3e0;
                    border-left: 4px solid #ff9800;
                }}
                .tip {{
                    background-color: #e8f5e9;
                    border-left: 4px solid #4caf50;
                }}
                a {{
                    color: #2196f3;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .page-break {{
                    page-break-after: always;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                {str(main_content)}
            </div>
        </body>
        </html>
        """
        
        return clean_html
    
    def scrape_documentation(self):
        """Scrape the Pine Script documentation"""
        print("Starting to scrape Pine Script documentation...")
        
        # Start with the main page and known sections
        urls_to_visit = [self.base_url]
        
        # Add known section URLs
        for section in self.known_sections:
            urls_to_visit.append(urljoin(self.base_url, section + "/"))
        
        while urls_to_visit:
            url = urls_to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            print(f"Scraping: {url}")
            self.visited_urls.add(url)
            
            # Get page content
            html_content = self.get_page_content(url)
            if not html_content:
                continue
            
            # Extract title
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('title')
            title_text = title.text.strip() if title else urlparse(url).path.strip('/')
            
            # Clean the HTML
            cleaned_html = self.clean_html_content(html_content, url)
            
            # Store the page data
            self.pages_data[url] = {
                'title': title_text,
                'html': cleaned_html,
                'url': url
            }
            
            # Extract more links
            new_links = self.extract_documentation_links(html_content, url)
            for link in new_links:
                if link not in self.visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)
            
            # Be polite to the server
            time.sleep(0.5)
        
        print(f"Scraped {len(self.pages_data)} pages")
    
    def organize_pages_by_section(self):
        """Organize pages into logical sections"""
        sections = OrderedDict()
        
        for url, page_data in self.pages_data.items():
            # Determine section based on URL
            path = urlparse(url).path
            
            section_name = "main"
            for known_section in self.known_sections:
                if known_section in path:
                    section_name = known_section
                    break
            
            if section_name not in sections:
                sections[section_name] = []
            
            sections[section_name].append(page_data)
        
        return sections
    
    def create_section_pdf(self, section_name, pages, output_filename):
        """Create a PDF for a section"""
        print(f"Creating PDF for section: {section_name}")
        
        # Create a combined HTML file for the section
        combined_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Pine Script Documentation - {}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .page-break {{
                    page-break-after: always;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 10px;
                }}
            </style>
        </head>
        <body>
        """.format(section_name.replace('_', ' ').title())
        
        for i, page in enumerate(pages):
            soup = BeautifulSoup(page['html'], 'html.parser')
            content = soup.find('body') or soup
            
            if i > 0:
                combined_html += '<div class="page-break"></div>\n'
            
            combined_html += f"<h1>{page['title']}</h1>\n"
            combined_html += str(content)
        
        combined_html += "</body></html>"
        
        # Save temporary HTML
        temp_html_file = os.path.join(self.temp_dir, f"{section_name}.html")
        with open(temp_html_file, 'w', encoding='utf-8') as f:
            f.write(combined_html)
        
        # Convert to PDF
        try:
            pdf = weasyprint.HTML(filename=temp_html_file).write_pdf()
            
            with open(output_filename, 'wb') as f:
                f.write(pdf)
            
            # Check file size
            file_size_mb = os.path.getsize(output_filename) / (1024 * 1024)
            
            if file_size_mb > 15:
                print(f"PDF {output_filename} is {file_size_mb:.2f} MB, splitting...")
                self.split_large_pdf(output_filename, section_name)
            else:
                print(f"Created: {output_filename} ({file_size_mb:.2f} MB)")
            
            return True
        except Exception as e:
            print(f"Error creating PDF for {section_name}: {e}")
            return False
    
    def split_large_pdf(self, pdf_file, section_name):
        """Split a large PDF into smaller parts"""
        try:
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            # Calculate pages per part to stay under 15MB
            file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
            pages_per_part = max(1, int(total_pages * 14 / file_size_mb))
            
            part_num = 1
            for start_page in range(0, total_pages, pages_per_part):
                writer = PdfWriter()
                end_page = min(start_page + pages_per_part, total_pages)
                
                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])
                
                part_filename = os.path.join(self.output_dir, f"pine_script_{section_name}_part{part_num}.pdf")
                
                with open(part_filename, 'wb') as output:
                    writer.write(output)
                
                part_size_mb = os.path.getsize(part_filename) / (1024 * 1024)
                print(f"Created: {os.path.basename(part_filename)} ({part_size_mb:.2f} MB)")
                
                part_num += 1
            
            # Remove the original large file
            os.remove(pdf_file)
            
        except Exception as e:
            print(f"Error splitting PDF: {e}")
    
    def convert_to_pdfs(self):
        """Convert scraped content to PDFs"""
        sections = self.organize_pages_by_section()
        
        for section_name, pages in sections.items():
            if not pages:
                continue
            
            output_filename = os.path.join(self.output_dir, f"pine_script_{section_name}.pdf")
            self.create_section_pdf(section_name, pages, output_filename)
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def run(self):
        """Main execution method"""
        self.scrape_documentation()
        self.convert_to_pdfs()
        
        print("\nConversion completed!")
        print(f"PDF files are saved in: {self.output_dir}")
        
        # List all PDFs
        pdf_files = sorted([f for f in os.listdir(self.output_dir) if f.endswith('.pdf')])
        print(f"\nCreated {len(pdf_files)} PDF files:")
        
        total_size = 0
        for pdf in pdf_files:
            file_path = os.path.join(self.output_dir, pdf)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            total_size += size_mb
            print(f"  - {pdf} ({size_mb:.2f} MB)")
        
        print(f"\nTotal size: {total_size:.2f} MB")

if __name__ == "__main__":
    scraper = PineScriptDocsScraper()
    scraper.run()