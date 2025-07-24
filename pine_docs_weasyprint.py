#!/usr/bin/env python3
"""
Pine Script Documentation to PDF Converter using WeasyPrint
Downloads and converts Pine Script documentation pages to PDF
"""

import os
import time
import requests
from bs4 import BeautifulSoup
import weasyprint
from PyPDF2 import PdfReader, PdfWriter
from urllib.parse import urljoin

class PineDocsWeasyPrint:
    def __init__(self):
        self.output_dir = "pine_script_documentation"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Main documentation URLs organized by section
        self.doc_sections = {
            "1_Welcome_Introduction": [
                "https://www.tradingview.com/pine-script-docs/welcome/",
                "https://www.tradingview.com/pine-script-docs/welcome/Pine_Script_v5_User_Manual/",
                "https://www.tradingview.com/pine-script-docs/welcome/First_steps/",
                "https://www.tradingview.com/pine-script-docs/welcome/Next_steps/",
            ],
            "2_Language_Fundamentals": [
                "https://www.tradingview.com/pine-script-docs/language/",
                "https://www.tradingview.com/pine-script-docs/language/Execution_model/",
                "https://www.tradingview.com/pine-script-docs/language/Time_series/",
                "https://www.tradingview.com/pine-script-docs/language/Script_structure/",
                "https://www.tradingview.com/pine-script-docs/language/Identifiers/",
                "https://www.tradingview.com/pine-script-docs/language/Operators/",
                "https://www.tradingview.com/pine-script-docs/language/Variable_declarations/",
                "https://www.tradingview.com/pine-script-docs/language/Conditional_structures/",
                "https://www.tradingview.com/pine-script-docs/language/Loops/",
                "https://www.tradingview.com/pine-script-docs/language/Type_system/",
                "https://www.tradingview.com/pine-script-docs/language/Built-ins/",
                "https://www.tradingview.com/pine-script-docs/language/User-defined_functions/",
                "https://www.tradingview.com/pine-script-docs/language/Objects/",
                "https://www.tradingview.com/pine-script-docs/language/Methods/",
                "https://www.tradingview.com/pine-script-docs/language/Arrays/",
                "https://www.tradingview.com/pine-script-docs/language/Matrices/",
                "https://www.tradingview.com/pine-script-docs/language/Maps/",
            ],
            "3_Core_Concepts": [
                "https://www.tradingview.com/pine-script-docs/concepts/",
                "https://www.tradingview.com/pine-script-docs/concepts/Alerts/",
                "https://www.tradingview.com/pine-script-docs/concepts/Backgrounds/",
                "https://www.tradingview.com/pine-script-docs/concepts/Bar_plotting/",
                "https://www.tradingview.com/pine-script-docs/concepts/Bar_states/",
                "https://www.tradingview.com/pine-script-docs/concepts/Chart_information/",
                "https://www.tradingview.com/pine-script-docs/concepts/Colors/",
                "https://www.tradingview.com/pine-script-docs/concepts/Fills/",
                "https://www.tradingview.com/pine-script-docs/concepts/Inputs/",
                "https://www.tradingview.com/pine-script-docs/concepts/Levels/",
                "https://www.tradingview.com/pine-script-docs/concepts/Libraries/",
                "https://www.tradingview.com/pine-script-docs/concepts/Lines_and_boxes/",
                "https://www.tradingview.com/pine-script-docs/concepts/Non-standard_charts_data/",
                "https://www.tradingview.com/pine-script-docs/concepts/Other_timeframes_and_data/",
                "https://www.tradingview.com/pine-script-docs/concepts/Plots/",
                "https://www.tradingview.com/pine-script-docs/concepts/Repainting/",
                "https://www.tradingview.com/pine-script-docs/concepts/Sessions/",
                "https://www.tradingview.com/pine-script-docs/concepts/Strategies/",
                "https://www.tradingview.com/pine-script-docs/concepts/Tables/",
                "https://www.tradingview.com/pine-script-docs/concepts/Text_and_shapes/",
                "https://www.tradingview.com/pine-script-docs/concepts/Time/",
                "https://www.tradingview.com/pine-script-docs/concepts/Timeframes/",
            ],
            "4_Writing_Scripts": [
                "https://www.tradingview.com/pine-script-docs/writing/",
                "https://www.tradingview.com/pine-script-docs/writing/Style_guide/",
                "https://www.tradingview.com/pine-script-docs/writing/Debugging/",
                "https://www.tradingview.com/pine-script-docs/writing/Publishing_scripts/",
                "https://www.tradingview.com/pine-script-docs/writing/Limitations/",
            ],
            "5_FAQ_Migration": [
                "https://www.tradingview.com/pine-script-docs/faq/",
                "https://www.tradingview.com/pine-script-docs/migration_guides/",
                "https://www.tradingview.com/pine-script-docs/migration_guides/To_Pine_Script_v5/",
                "https://www.tradingview.com/pine-script-docs/migration_guides/v4_to_v5_migration_guide/",
            ],
            "6_Errors_ReleaseNotes": [
                "https://www.tradingview.com/pine-script-docs/errors/",
                "https://www.tradingview.com/pine-script-docs/release_notes/",
            ]
        }
    
    def fetch_and_clean_page(self, url):
        """Fetch a page and clean it for PDF conversion"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove navigation, scripts, and other non-content elements
            for element in soup.find_all(['script', 'noscript', 'header', 'footer', 'nav']):
                element.decompose()
            
            # Find main content
            main_content = None
            for selector in ['main', 'article', '.content', '#content', '.documentation']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.body or soup
            
            # Get title
            title = soup.find('title')
            title_text = title.text.strip() if title else url.split('/')[-2]
            
            # Create clean HTML with inline CSS
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
                        color: #2c3e50;
                        margin-top: 24px;
                        margin-bottom: 16px;
                        page-break-after: avoid;
                    }}
                    h1 {{
                        font-size: 2em;
                        border-bottom: 2px solid #eee;
                        padding-bottom: 10px;
                    }}
                    h2 {{ font-size: 1.5em; }}
                    h3 {{ font-size: 1.25em; }}
                    p {{
                        margin: 12px 0;
                        text-align: justify;
                    }}
                    code {{
                        background-color: #f4f4f4;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 0.9em;
                    }}
                    pre {{
                        background-color: #f8f8f8;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 12px;
                        overflow-x: auto;
                        line-height: 1.4;
                        page-break-inside: avoid;
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
                        page-break-inside: avoid;
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
                        page-break-inside: avoid;
                    }}
                    ul, ol {{
                        margin: 12px 0;
                        padding-left: 30px;
                    }}
                    li {{
                        margin: 4px 0;
                    }}
                    a {{
                        color: #2196f3;
                        text-decoration: none;
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
                    <p style="color: #666;">Source: {url}</p>
                </div>
                {str(main_content)}
            </body>
            </html>
            """
            
            return clean_html, title_text
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None, None
    
    def create_section_pdf(self, section_name, urls):
        """Create a PDF for a section of documentation"""
        print(f"\n--- Processing section: {section_name.replace('_', ' ')} ---")
        
        temp_dir = os.path.join(self.output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Fetch all pages in the section
        pages_html = []
        for url in urls:
            html_content, title = self.fetch_and_clean_page(url)
            if html_content:
                pages_html.append((html_content, title, url))
                time.sleep(0.5)  # Be polite to the server
        
        if not pages_html:
            print(f"No pages fetched for section {section_name}")
            return []
        
        # Create combined HTML for the section
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
                .toc {{
                    margin: 40px 0;
                    padding: 20px;
                    background-color: #f8f8f8;
                    border-radius: 8px;
                }}
                .toc h2 {{
                    margin-top: 0;
                }}
                .toc ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                .toc li {{
                    margin: 8px 0;
                }}
            </style>
        </head>
        <body>
            <h1>Pine Script Documentation</h1>
            <h2>{}</h2>
            <div class="toc">
                <h2>Table of Contents</h2>
                <ul>
        """.format(
            section_name.replace('_', ' '),
            section_name.replace('_', ' ')
        )
        
        # Add table of contents
        for i, (_, title, _) in enumerate(pages_html):
            combined_html += f'<li>{i+1}. {title}</li>\n'
        
        combined_html += """
                </ul>
            </div>
            <div class="page-break"></div>
        """
        
        # Add all pages
        for i, (html, title, url) in enumerate(pages_html):
            if i > 0:
                combined_html += '<div class="page-break"></div>\n'
            
            # Extract body content from the page HTML
            soup = BeautifulSoup(html, 'html.parser')
            body_content = soup.find('body')
            if body_content:
                combined_html += str(body_content.decode_contents())
        
        combined_html += "</body></html>"
        
        # Save temporary HTML
        temp_html = os.path.join(temp_dir, f"{section_name}.html")
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(combined_html)
        
        # Convert to PDF
        output_pdf = os.path.join(self.output_dir, f"PineScript_{section_name}.pdf")
        try:
            print(f"Converting to PDF: {output_pdf}")
            pdf = weasyprint.HTML(filename=temp_html).write_pdf()
            
            with open(output_pdf, 'wb') as f:
                f.write(pdf)
            
            # Check file size and split if necessary
            file_size_mb = os.path.getsize(output_pdf) / (1024 * 1024)
            
            if file_size_mb > 15:
                print(f"PDF is {file_size_mb:.2f} MB, splitting...")
                return self.split_pdf(output_pdf, section_name)
            else:
                print(f"Created: {os.path.basename(output_pdf)} ({file_size_mb:.2f} MB)")
                return [output_pdf]
                
        except Exception as e:
            print(f"Error creating PDF for {section_name}: {e}")
            return []
        finally:
            # Clean up temp file
            if os.path.exists(temp_html):
                os.remove(temp_html)
            if os.path.exists(temp_dir):
                try:
                    os.rmdir(temp_dir)
                except:
                    pass
    
    def split_pdf(self, pdf_file, section_name):
        """Split a large PDF into smaller parts"""
        try:
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
            
            # Calculate pages per part
            pages_per_part = max(1, int(total_pages * 14 / file_size_mb))
            
            part_files = []
            part_num = 1
            
            for start_page in range(0, total_pages, pages_per_part):
                writer = PdfWriter()
                end_page = min(start_page + pages_per_part, total_pages)
                
                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])
                
                part_filename = os.path.join(self.output_dir, f"PineScript_{section_name}_part{part_num}.pdf")
                
                with open(part_filename, 'wb') as output:
                    writer.write(output)
                
                part_size_mb = os.path.getsize(part_filename) / (1024 * 1024)
                print(f"Created: {os.path.basename(part_filename)} ({part_size_mb:.2f} MB)")
                part_files.append(part_filename)
                part_num += 1
            
            # Remove original large file
            os.remove(pdf_file)
            return part_files
            
        except Exception as e:
            print(f"Error splitting PDF: {e}")
            return [pdf_file]
    
    def run(self):
        """Main execution"""
        print("Starting Pine Script documentation download and PDF conversion...")
        print("This will download the main documentation pages and convert them to PDF files.")
        print("Each PDF will be kept under 15 MB as requested.\n")
        
        all_pdfs = []
        
        # Process each section
        for section_name, urls in self.doc_sections.items():
            pdf_files = self.create_section_pdf(section_name, urls)
            all_pdfs.extend(pdf_files)
        
        # Summary
        print("\n" + "="*60)
        print("Conversion completed!")
        print(f"PDF files are saved in: {self.output_dir}")
        print(f"\nCreated {len(all_pdfs)} PDF files:")
        
        total_size = 0
        for pdf in sorted(all_pdfs):
            if os.path.exists(pdf):
                size_mb = os.path.getsize(pdf) / (1024 * 1024)
                total_size += size_mb
                print(f"  - {os.path.basename(pdf)} ({size_mb:.2f} MB)")
        
        print(f"\nTotal size: {total_size:.2f} MB")
        print("="*60)

if __name__ == "__main__":
    converter = PineDocsWeasyPrint()
    converter.run()