#!/usr/bin/env python3
"""
Pine Script v6 Documentation to PDF Converter
Scrapes and converts the latest Pine Script documentation to PDF files
"""

import os
import time
import requests
from bs4 import BeautifulSoup
import weasyprint
from PyPDF2 import PdfReader, PdfWriter
from urllib.parse import urljoin, urlparse
import re

class PineScriptV6Scraper:
    def __init__(self):
        self.base_url = "https://www.tradingview.com/pine-script-docs/"
        self.output_dir = "pine_script_v6_documentation"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Documentation structure based on the v6 documentation
        self.doc_structure = {
            "1_Welcome_and_Primer": [
                "welcome/",
                "primer/",
                "primer/first-steps/",
                "primer/first-indicator/",
                "primer/next-steps/"
            ],
            "2_Language": [
                "language/",
                "language/execution-model/",
                "language/type-system/",
                "language/script-structure/",
                "language/identifiers/",
                "language/variable-declarations/",
                "language/operators/",
                "language/conditional-structures/",
                "language/loops/",
                "language/built-ins/",
                "language/user-defined-functions/",
                "language/objects/",
                "language/enums/",
                "language/methods/",
                "language/arrays/",
                "language/matrices/",
                "language/maps/"
            ],
            "3_Concepts_Part1": [
                "concepts/",
                "concepts/alerts/",
                "concepts/backgrounds/",
                "concepts/bar-coloring/",
                "concepts/bar-plotting/",
                "concepts/bar-states/",
                "concepts/chart-information/",
                "concepts/colors/",
                "concepts/fills/",
                "concepts/inputs/",
                "concepts/levels/",
                "concepts/libraries/"
            ],
            "3_Concepts_Part2": [
                "concepts/lines-and-boxes/",
                "concepts/non-standard-charts-data/",
                "concepts/other-timeframes-and-data/",
                "concepts/plots/",
                "concepts/repainting/",
                "concepts/sessions/",
                "concepts/strategies/",
                "concepts/strings/",
                "concepts/tables/",
                "concepts/text-and-shapes/",
                "concepts/time/",
                "concepts/timeframes/"
            ],
            "4_Writing_Scripts": [
                "writing/",
                "writing/style-guide/",
                "writing/debugging/",
                "writing/profiling-and-optimization/",
                "writing/publishing-scripts/",
                "writing/limitations/"
            ],
            "5_FAQ": [
                "faq/",
                "faq/general/",
                "faq/alerts/",
                "faq/data-structures/",
                "faq/functions/",
                "faq/indicators/",
                "faq/other-data-and-timeframes/",
                "faq/programming/",
                "faq/strategies/",
                "faq/strings-and-formatting/",
                "faq/techniques/",
                "faq/times-dates-and-sessions/",
                "faq/variables-and-operators/",
                "faq/visuals/"
            ],
            "6_Errors_and_Release_Notes": [
                "errors/",
                "release-notes/"
            ],
            "7_Migration_Guides": [
                "migration-guides/",
                "migration-guides/overview/",
                "migration-guides/to-pine-script-v6/",
                "migration-guides/to-pine-script-v5/",
                "migration-guides/to-pine-script-v4/",
                "migration-guides/to-pine-script-v3/",
                "migration-guides/to-pine-script-v2/"
            ]
        }
    
    def fetch_page(self, relative_url):
        """Fetch a documentation page"""
        url = urljoin(self.base_url, relative_url)
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text, url
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None, url
    
    def clean_html_content(self, html_content, url):
        """Clean and prepare HTML for PDF conversion"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'noscript', 'header', 'footer', 'nav', 'aside']):
            element.decompose()
        
        # Remove navigation elements
        for element in soup.find_all(class_=re.compile(r'(nav|navigation|sidebar|menu|header|footer)')):
            element.decompose()
        
        # Find main content - Pine Script docs use specific content containers
        main_content = None
        
        # Try different selectors
        selectors = [
            'main',
            'article',
            '.content',
            '.documentation-content',
            '[role="main"]',
            '.doc-content',
            '.main-content'
        ]
        
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            # Fallback to body content
            main_content = soup.body or soup
        
        # Get title
        title = soup.find('h1')
        if not title:
            title = soup.find('title')
        title_text = title.text.strip() if title else relative_url.strip('/')
        
        # Create clean HTML with styling
        clean_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title_text}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 100%;
                    margin: 0;
                    padding: 0;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #2962ff;
                    margin-top: 24px;
                    margin-bottom: 16px;
                    page-break-after: avoid;
                }}
                h1 {{
                    font-size: 2.5em;
                    border-bottom: 3px solid #2962ff;
                    padding-bottom: 10px;
                }}
                h2 {{ font-size: 2em; }}
                h3 {{ font-size: 1.5em; }}
                h4 {{ font-size: 1.25em; }}
                p {{
                    margin: 12px 0;
                    text-align: justify;
                }}
                code {{
                    background-color: #f5f5f5;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 0.9em;
                    color: #d73a49;
                }}
                pre {{
                    background-color: #f8f8f8;
                    border: 1px solid #e1e4e8;
                    border-radius: 6px;
                    padding: 16px;
                    overflow-x: auto;
                    line-height: 1.45;
                    page-break-inside: avoid;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                    color: inherit;
                }}
                blockquote {{
                    border-left: 4px solid #2962ff;
                    margin: 16px 0;
                    padding-left: 16px;
                    color: #666;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                    page-break-inside: avoid;
                }}
                th, td {{
                    border: 1px solid #e1e4e8;
                    padding: 8px 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f6f8fa;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    page-break-inside: avoid;
                }}
                ul, ol {{
                    margin: 12px 0;
                    padding-left: 30px;
                }}
                li {{
                    margin: 6px 0;
                }}
                a {{
                    color: #2962ff;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .note, .warning, .tip {{
                    padding: 12px;
                    margin: 16px 0;
                    border-radius: 6px;
                    page-break-inside: avoid;
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
                .page-header {{
                    text-align: center;
                    margin-bottom: 40px;
                    page-break-after: avoid;
                }}
                .page-break {{
                    page-break-after: always;
                }}
            </style>
        </head>
        <body>
            <div class="page-header">
                <h1>{title_text}</h1>
                <p style="color: #666; font-size: 0.9em;">Pine Script® v6 Documentation</p>
            </div>
            {str(main_content)}
        </body>
        </html>
        """
        
        return clean_html, title_text
    
    def create_section_pdf(self, section_name, urls):
        """Create a PDF for a section"""
        print(f"\n--- Processing section: {section_name.replace('_', ' ')} ---")
        
        pages_content = []
        
        # Fetch all pages
        for relative_url in urls:
            html_content, full_url = self.fetch_page(relative_url)
            if html_content:
                clean_html, title = self.clean_html_content(html_content, full_url)
                pages_content.append((clean_html, title, full_url))
                time.sleep(0.5)  # Be polite
        
        if not pages_content:
            print(f"No content fetched for section {section_name}")
            return []
        
        # Create combined HTML
        combined_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Pine Script v6 - {section_name.replace('_', ' ')}</title>
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
                .cover-page {{
                    text-align: center;
                    padding: 100px 20px;
                    page-break-after: always;
                }}
                .cover-page h1 {{
                    color: #2962ff;
                    font-size: 3em;
                    margin-bottom: 20px;
                }}
                .cover-page h2 {{
                    color: #666;
                    font-size: 1.5em;
                }}
                .toc {{
                    margin: 40px 0;
                    padding: 20px;
                    background-color: #f8f8f8;
                    border-radius: 8px;
                    page-break-after: always;
                }}
                .toc h2 {{
                    color: #2962ff;
                    margin-top: 0;
                }}
                .toc ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                .toc li {{
                    margin: 10px 0;
                    padding-left: 20px;
                    border-left: 3px solid #2962ff;
                }}
                .page-break {{
                    page-break-after: always;
                }}
            </style>
        </head>
        <body>
            <div class="cover-page">
                <h1>Pine Script® v6 Documentation</h1>
                <h2>{section_name.replace('_', ' ')}</h2>
                <p>TradingView Pine Script Programming Language</p>
            </div>
            
            <div class="toc">
                <h2>Table of Contents</h2>
                <ul>
        """
        
        # Add TOC entries
        for i, (_, title, _) in enumerate(pages_content):
            combined_html += f'<li>{i+1}. {title}</li>\n'
        
        combined_html += """
                </ul>
            </div>
        """
        
        # Add all pages
        for i, (html, title, url) in enumerate(pages_content):
            if i > 0:
                combined_html += '<div class="page-break"></div>\n'
            
            # Extract body content
            soup = BeautifulSoup(html, 'html.parser')
            body_content = soup.find('body')
            if body_content:
                combined_html += str(body_content.decode_contents())
        
        combined_html += "</body></html>"
        
        # Save and convert to PDF
        temp_html = os.path.join(self.output_dir, f"temp_{section_name}.html")
        output_pdf = os.path.join(self.output_dir, f"PineScript_v6_{section_name}.pdf")
        
        try:
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(combined_html)
            
            print(f"Converting to PDF: {output_pdf}")
            pdf = weasyprint.HTML(filename=temp_html).write_pdf()
            
            with open(output_pdf, 'wb') as f:
                f.write(pdf)
            
            # Check size and split if needed
            file_size_mb = os.path.getsize(output_pdf) / (1024 * 1024)
            
            if file_size_mb > 15:
                print(f"PDF is {file_size_mb:.2f} MB, splitting...")
                return self.split_pdf(output_pdf, section_name)
            else:
                print(f"Created: {os.path.basename(output_pdf)} ({file_size_mb:.2f} MB)")
                return [output_pdf]
                
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return []
        finally:
            # Clean up temp file
            if os.path.exists(temp_html):
                os.remove(temp_html)
    
    def split_pdf(self, pdf_file, section_name):
        """Split large PDF into smaller parts"""
        try:
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
            
            pages_per_part = max(1, int(total_pages * 14 / file_size_mb))
            
            part_files = []
            part_num = 1
            
            for start in range(0, total_pages, pages_per_part):
                writer = PdfWriter()
                end = min(start + pages_per_part, total_pages)
                
                for i in range(start, end):
                    writer.add_page(reader.pages[i])
                
                part_file = os.path.join(self.output_dir, f"PineScript_v6_{section_name}_part{part_num}.pdf")
                
                with open(part_file, 'wb') as f:
                    writer.write(f)
                
                size_mb = os.path.getsize(part_file) / (1024 * 1024)
                print(f"Created: {os.path.basename(part_file)} ({size_mb:.2f} MB)")
                part_files.append(part_file)
                part_num += 1
            
            os.remove(pdf_file)
            return part_files
            
        except Exception as e:
            print(f"Error splitting PDF: {e}")
            return [pdf_file]
    
    def run(self):
        """Main execution"""
        print("="*60)
        print("Pine Script® v6 Documentation to PDF Converter")
        print("="*60)
        print("\nStarting documentation download and conversion...")
        print("Each PDF will be kept under 15 MB as requested.\n")
        
        all_pdfs = []
        
        # Process each section
        for section_name, urls in self.doc_structure.items():
            pdf_files = self.create_section_pdf(section_name, urls)
            all_pdfs.extend(pdf_files)
        
        # Final summary
        print("\n" + "="*60)
        print("✅ Conversion completed!")
        print(f"📁 PDF files saved in: {self.output_dir}/")
        print(f"\n📚 Created {len(all_pdfs)} PDF files:")
        
        total_size = 0
        for pdf in sorted(all_pdfs):
            if os.path.exists(pdf):
                size_mb = os.path.getsize(pdf) / (1024 * 1024)
                total_size += size_mb
                print(f"   📄 {os.path.basename(pdf)} ({size_mb:.2f} MB)")
        
        print(f"\n💾 Total size: {total_size:.2f} MB")
        print("="*60)

if __name__ == "__main__":
    scraper = PineScriptV6Scraper()
    scraper.run()