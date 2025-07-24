#!/usr/bin/env python3
"""
Simple TradingView Pine Script Documentation Scraper
Uses requests and BeautifulSoup for more reliable scraping
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pdfkit
import json
from collections import defaultdict

class SimplePineScraper:
    def __init__(self):
        self.base_url = "https://www.tradingview.com/pine-script-docs/"
        self.visited_urls = set()
        self.pages_data = []
        self.output_dir = "pine_docs_output"
        self.temp_html_dir = os.path.join(self.output_dir, "html")
        self.pdf_dir = os.path.join(self.output_dir, "pdfs")
        
        # Create directories
        for dir_path in [self.output_dir, self.temp_html_dir, self.pdf_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # PDF options for wkhtmltopdf
        self.pdf_options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
    
    def get_page(self, url):
        """Fetch a page using requests"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, soup, current_url):
        """Extract documentation links from the page"""
        links = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            
            # Filter for Pine Script docs links
            if ('pine-script-docs' in full_url and 
                full_url not in self.visited_urls and
                not full_url.endswith('.png') and
                not full_url.endswith('.jpg') and
                not full_url.endswith('.gif') and
                '#' not in full_url):  # Avoid anchor links
                
                links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True) or 'Untitled'
                })
        
        return links
    
    def clean_content(self, soup, url):
        """Clean and prepare HTML content for PDF conversion"""
        # Create a new clean HTML document
        clean_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #2c3e50;
                    margin-top: 20px;
                    margin-bottom: 10px;
                }
                h1 { font-size: 28px; }
                h2 { font-size: 24px; }
                h3 { font-size: 20px; }
                h4 { font-size: 18px; }
                code {
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }
                pre {
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    line-height: 1.4;
                }
                pre code {
                    background-color: transparent;
                    padding: 0;
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
                    font-weight: bold;
                }
                img {
                    max-width: 100%;
                    height: auto;
                }
                .source-url {
                    font-size: 12px;
                    color: #666;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eee;
                }
            </style>
        </head>
        <body>
        """
        
        # Add source URL
        clean_html += f'<div class="source-url">Source: {url}</div>'
        
        # Extract title
        title = soup.find('title')
        if title:
            clean_html += f'<h1>{title.get_text(strip=True)}</h1>'
        
        # Find main content
        content = None
        content_selectors = [
            'article',
            'main',
            '.content',
            '.documentation-content',
            '.docs-content',
            '[role="main"]',
            '.markdown-body'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            # Try to find the largest div with text
            divs = soup.find_all('div')
            max_text_length = 0
            for div in divs:
                text_length = len(div.get_text(strip=True))
                if text_length > max_text_length:
                    max_text_length = text_length
                    content = div
        
        if content:
            # Remove navigation, headers, footers
            for elem in content.select('nav, header, footer, .navigation, .sidebar, script, style'):
                elem.decompose()
            
            # Convert relative image URLs to absolute
            for img in content.find_all('img'):
                if 'src' in img.attrs:
                    img['src'] = urljoin(url, img['src'])
            
            clean_html += str(content)
        else:
            clean_html += "<p>No content found on this page.</p>"
        
        clean_html += """
        </body>
        </html>
        """
        
        return clean_html
    
    def save_as_pdf(self, url, content, page_num):
        """Save content as PDF using wkhtmltopdf"""
        # Create filename from URL
        url_parts = urlparse(url).path.strip('/').split('/')
        filename = '_'.join(url_parts) if url_parts else 'index'
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = f"{page_num:03d}_{filename[:50]}"
        
        # Save HTML temporarily
        html_path = os.path.join(self.temp_html_dir, f"{filename}.html")
        pdf_path = os.path.join(self.pdf_dir, f"{filename}.pdf")
        
        try:
            # Write HTML
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Convert to PDF
            pdfkit.from_file(html_path, pdf_path, options=self.pdf_options)
            
            # Check file size
            file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
            
            return {
                'url': url,
                'pdf_path': pdf_path,
                'file_size': file_size,
                'page_num': page_num
            }
            
        except Exception as e:
            print(f"Error converting {url} to PDF: {e}")
            return None
    
    def scrape_documentation(self):
        """Main scraping function"""
        print("Starting Pine Script documentation scrape...")
        
        # Start with known documentation sections
        start_urls = [
            "https://www.tradingview.com/pine-script-docs/welcome/",
            "https://www.tradingview.com/pine-script-docs/primer/",
            "https://www.tradingview.com/pine-script-docs/language/",
            "https://www.tradingview.com/pine-script-docs/concepts/",
            "https://www.tradingview.com/pine-script-docs/writing/",
            "https://www.tradingview.com/pine-script-docs/faq/",
            "https://www.tradingview.com/pine-script-docs/error_messages/",
            "https://www.tradingview.com/pine-script-docs/migration_guides/"
        ]
        
        urls_to_visit = []
        for url in start_urls:
            urls_to_visit.append({'url': url, 'text': url.split('/')[-2]})
        
        page_num = 1
        
        while urls_to_visit and len(self.visited_urls) < 200:  # Limit to prevent infinite loops
            current = urls_to_visit.pop(0)
            url = current['url']
            
            if url in self.visited_urls:
                continue
            
            print(f"Processing ({page_num}): {url}")
            self.visited_urls.add(url)
            
            # Get page content
            html_content = self.get_page(url)
            if not html_content:
                continue
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Clean and save as PDF
            clean_content = self.clean_content(soup, url)
            pdf_data = self.save_as_pdf(url, clean_content, page_num)
            
            if pdf_data:
                self.pages_data.append(pdf_data)
                page_num += 1
            
            # Extract more links
            new_links = self.extract_links(soup, url)
            urls_to_visit.extend(new_links)
            
            # Be respectful
            time.sleep(0.5)
        
        print(f"\nScraped {len(self.pages_data)} pages")
    
    def combine_pdfs(self):
        """Combine PDFs into larger files under 15MB"""
        from PyPDF2 import PdfMerger
        
        print("\nCombining PDFs...")
        
        # Sort PDFs by page number
        self.pages_data.sort(key=lambda x: x['page_num'])
        
        current_merger = PdfMerger()
        current_size = 0
        part_num = 1
        pages_in_current = 0
        
        for pdf_data in self.pages_data:
            # Check if adding this PDF would exceed 14MB (leaving margin)
            if current_size + pdf_data['file_size'] > 14 and pages_in_current > 0:
                # Save current merger
                output_path = os.path.join(self.output_dir, f"pine_script_docs_part_{part_num:02d}.pdf")
                current_merger.write(output_path)
                current_merger.close()
                print(f"Created: pine_script_docs_part_{part_num:02d}.pdf ({current_size:.2f} MB)")
                
                # Start new merger
                current_merger = PdfMerger()
                current_size = 0
                pages_in_current = 0
                part_num += 1
            
            # Add PDF to merger
            try:
                current_merger.append(pdf_data['pdf_path'])
                current_size += pdf_data['file_size']
                pages_in_current += 1
            except Exception as e:
                print(f"Error adding {pdf_data['pdf_path']}: {e}")
        
        # Save last merger if it has content
        if pages_in_current > 0:
            output_path = os.path.join(self.output_dir, f"pine_script_docs_part_{part_num:02d}.pdf")
            current_merger.write(output_path)
            current_merger.close()
            print(f"Created: pine_script_docs_part_{part_num:02d}.pdf ({current_size:.2f} MB)")
        
        # Save metadata
        metadata = {
            'total_pages': len(self.pages_data),
            'total_parts': part_num,
            'pages': [
                {
                    'url': p['url'],
                    'page_num': p['page_num'],
                    'file_size_mb': p['file_size']
                }
                for p in self.pages_data
            ]
        }
        
        with open(os.path.join(self.output_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        
        # Remove individual PDFs and HTML files
        if os.path.exists(self.temp_html_dir):
            shutil.rmtree(self.temp_html_dir)
        if os.path.exists(self.pdf_dir):
            shutil.rmtree(self.pdf_dir)
    
    def run(self):
        """Main execution"""
        try:
            self.scrape_documentation()
            self.combine_pdfs()
            self.cleanup()
            
            print(f"\nCompleted! Combined PDFs are in: {self.output_dir}")
            print("Look for files named: pine_script_docs_part_XX.pdf")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    scraper = SimplePineScraper()
    scraper.run()