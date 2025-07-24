#!/usr/bin/env python3
"""
TradingView Pine Script Documentation Scraper and PDF Converter
This script scrapes the Pine Script documentation and converts it to PDF files.
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import weasyprint
from PyPDF2 import PdfMerger, PdfReader
import json
from collections import defaultdict

class PineDocsScraper:
    def __init__(self, base_url="https://www.tradingview.com/pine-script-docs/"):
        self.base_url = base_url
        self.visited_urls = set()
        self.pages_data = []
        self.output_dir = "pine_script_docs"
        self.temp_dir = os.path.join(self.output_dir, "temp")
        self.final_dir = os.path.join(self.output_dir, "final")
        
        # Create directories
        for dir_path in [self.output_dir, self.temp_dir, self.final_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Setup Selenium
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Falling back to requests-based scraping")
            self.driver = None
    
    def get_page_content(self, url):
        """Get page content using Selenium or requests"""
        if self.driver:
            try:
                self.driver.get(url)
                # Wait for content to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
                time.sleep(2)  # Additional wait for dynamic content
                return self.driver.page_source
            except Exception as e:
                print(f"Selenium error for {url}: {e}")
                # Fall back to requests
        
        # Use requests as fallback
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_navigation_links(self, soup, current_url):
        """Extract navigation links from the page"""
        links = []
        
        # Look for navigation menu
        nav_selectors = [
            'nav', 
            '.navigation', 
            '.sidebar', 
            '[role="navigation"]',
            '.docs-sidebar',
            '.menu',
            'aside'
        ]
        
        for selector in nav_selectors:
            nav_elements = soup.select(selector)
            for nav in nav_elements:
                for link in nav.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    
                    # Only include Pine Script docs links
                    if 'pine-script-docs' in full_url and full_url not in self.visited_urls:
                        links.append({
                            'url': full_url,
                            'text': link.get_text(strip=True)
                        })
        
        # Also look for links in the main content
        content_selectors = ['main', 'article', '.content', '.docs-content']
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                for link in content.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    
                    if 'pine-script-docs' in full_url and full_url not in self.visited_urls:
                        links.append({
                            'url': full_url,
                            'text': link.get_text(strip=True)
                        })
        
        # Remove duplicates
        seen = set()
        unique_links = []
        for link in links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)
        
        return unique_links
    
    def clean_html_for_pdf(self, soup):
        """Clean HTML content for PDF conversion"""
        # Remove unnecessary elements
        for element in soup.select('script, style, nav, header, footer, .navigation, .sidebar'):
            element.decompose()
        
        # Add custom CSS for better PDF rendering
        style = soup.new_tag('style')
        style.string = """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 40px;
            font-size: 12pt;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 20px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }
        h1 { font-size: 24pt; }
        h2 { font-size: 20pt; }
        h3 { font-size: 16pt; }
        pre, code {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            overflow-wrap: break-word;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        @page {
            size: A4;
            margin: 2cm;
        }
        """
        
        if soup.head:
            soup.head.append(style)
        else:
            head = soup.new_tag('head')
            head.append(style)
            soup.insert(0, head)
        
        return soup
    
    def save_page_as_pdf(self, url, content, title):
        """Save a single page as PDF"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract main content
        main_content = None
        content_selectors = ['main', 'article', '.content', '.docs-content', '[role="main"]']
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body if soup.body else soup
        
        # Create new HTML with just the main content
        new_soup = BeautifulSoup('<html><head><meta charset="utf-8"></head><body></body></html>', 'html.parser')
        
        # Add title
        title_tag = new_soup.new_tag('h1')
        title_tag.string = title
        new_soup.body.append(title_tag)
        
        # Add URL reference
        url_tag = new_soup.new_tag('p')
        url_tag.string = f"Source: {url}"
        url_tag['style'] = "font-size: 10pt; color: #666; margin-bottom: 20px;"
        new_soup.body.append(url_tag)
        
        # Add main content
        new_soup.body.append(main_content)
        
        # Clean and style
        new_soup = self.clean_html_for_pdf(new_soup)
        
        # Generate filename
        filename = re.sub(r'[^\w\s-]', '', title)
        filename = re.sub(r'[-\s]+', '-', filename)
        filename = filename[:100]  # Limit length
        pdf_path = os.path.join(self.temp_dir, f"{filename}.pdf")
        
        try:
            # Convert to PDF using WeasyPrint
            html_string = str(new_soup)
            weasyprint.HTML(string=html_string, base_url=url).write_pdf(pdf_path)
            
            # Check file size
            file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # Size in MB
            
            return {
                'url': url,
                'title': title,
                'pdf_path': pdf_path,
                'file_size': file_size
            }
        except Exception as e:
            print(f"Error converting {url} to PDF: {e}")
            return None
    
    def scrape_all_pages(self):
        """Scrape all pages from the documentation"""
        print(f"Starting scrape from: {self.base_url}")
        
        # Start with the base URL
        urls_to_visit = [{'url': self.base_url, 'text': 'Home'}]
        
        while urls_to_visit:
            current = urls_to_visit.pop(0)
            url = current['url']
            
            if url in self.visited_urls:
                continue
            
            print(f"Scraping: {url}")
            self.visited_urls.add(url)
            
            content = self.get_page_content(url)
            if not content:
                continue
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else current['text']
            
            # Save as PDF
            pdf_data = self.save_page_as_pdf(url, content, title_text)
            if pdf_data:
                self.pages_data.append(pdf_data)
            
            # Extract more links
            new_links = self.extract_navigation_links(soup, url)
            urls_to_visit.extend(new_links)
            
            # Be respectful to the server
            time.sleep(1)
    
    def organize_pdfs_by_size(self):
        """Organize PDFs into files smaller than 15MB"""
        # Group pages by category (based on URL structure)
        categories = defaultdict(list)
        
        for page in self.pages_data:
            # Extract category from URL
            url_parts = urlparse(page['url']).path.split('/')
            category = 'general'
            
            if len(url_parts) > 2:
                # Try to identify category from URL
                if 'primer' in page['url']:
                    category = '01_primer'
                elif 'language' in page['url']:
                    category = '02_language'
                elif 'concepts' in page['url']:
                    category = '03_concepts'
                elif 'writing' in page['url']:
                    category = '04_writing_scripts'
                elif 'faq' in page['url']:
                    category = '05_faq'
                elif 'error' in page['url']:
                    category = '06_errors'
                elif 'migration' in page['url']:
                    category = '07_migration'
                else:
                    # Use the first meaningful part of the URL
                    for part in url_parts:
                        if part and part != 'pine-script-docs':
                            category = part
                            break
            
            categories[category].append(page)
        
        # Create PDFs for each category, splitting if necessary
        final_pdfs = []
        
        for category, pages in categories.items():
            current_size = 0
            current_pages = []
            part_number = 1
            
            for page in pages:
                if current_size + page['file_size'] > 14:  # Leave some margin under 15MB
                    # Save current batch
                    if current_pages:
                        self.merge_pdfs(current_pages, category, part_number)
                        part_number += 1
                        current_pages = []
                        current_size = 0
                
                current_pages.append(page)
                current_size += page['file_size']
            
            # Save remaining pages
            if current_pages:
                self.merge_pdfs(current_pages, category, part_number)
    
    def merge_pdfs(self, pages, category, part_number):
        """Merge multiple PDFs into one"""
        if not pages:
            return
        
        merger = PdfMerger()
        
        # Sort pages by title for better organization
        pages.sort(key=lambda x: x['title'])
        
        # Add cover page
        cover_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding-top: 200px;
                }}
                h1 {{
                    font-size: 36pt;
                    margin-bottom: 20px;
                }}
                h2 {{
                    font-size: 24pt;
                    color: #666;
                    margin-bottom: 40px;
                }}
                .toc {{
                    text-align: left;
                    margin: 0 auto;
                    max-width: 600px;
                }}
                .toc-item {{
                    margin: 10px 0;
                    font-size: 14pt;
                }}
            </style>
        </head>
        <body>
            <h1>Pine Script Documentation</h1>
            <h2>{category.replace('_', ' ').title()} - Part {part_number}</h2>
            <div class="toc">
                <h3>Table of Contents:</h3>
        """
        
        for i, page in enumerate(pages, 1):
            cover_html += f'<div class="toc-item">{i}. {page["title"]}</div>'
        
        cover_html += """
            </div>
        </body>
        </html>
        """
        
        # Create cover PDF
        cover_path = os.path.join(self.temp_dir, f"cover_{category}_{part_number}.pdf")
        weasyprint.HTML(string=cover_html).write_pdf(cover_path)
        
        # Add cover to merger
        merger.append(cover_path)
        
        # Add all pages
        for page in pages:
            try:
                merger.append(page['pdf_path'])
            except Exception as e:
                print(f"Error adding {page['pdf_path']} to merger: {e}")
        
        # Save merged PDF
        output_filename = f"pine_script_docs_{category}_part{part_number}.pdf"
        output_path = os.path.join(self.final_dir, output_filename)
        
        try:
            merger.write(output_path)
            merger.close()
            
            # Check final size
            final_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"Created: {output_filename} ({final_size:.2f} MB)")
            
            # Clean up cover
            os.remove(cover_path)
            
        except Exception as e:
            print(f"Error creating merged PDF: {e}")
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        if self.driver:
            self.driver.quit()
    
    def run(self):
        """Main execution method"""
        try:
            print("Starting Pine Script documentation scraper...")
            
            # Scrape all pages
            self.scrape_all_pages()
            
            print(f"\nScraped {len(self.pages_data)} pages")
            
            # Organize into PDFs
            print("\nOrganizing PDFs...")
            self.organize_pdfs_by_size()
            
            # Save metadata
            metadata = {
                'total_pages': len(self.pages_data),
                'pages': [
                    {
                        'url': page['url'],
                        'title': page['title'],
                        'size_mb': page['file_size']
                    }
                    for page in self.pages_data
                ]
            }
            
            with open(os.path.join(self.output_dir, 'metadata.json'), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"\nCompleted! PDFs saved in: {self.final_dir}")
            
        except Exception as e:
            print(f"Error during execution: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()


if __name__ == "__main__":
    scraper = PineDocsScraper()
    scraper.run()