#!/usr/bin/env python3
"""
Final Pine Script Documentation to PDF Converter
Uses a simple approach to download key documentation pages
"""

import os
import requests
from bs4 import BeautifulSoup
import pdfkit
from PyPDF2 import PdfReader, PdfWriter
import subprocess

class PineDocsFinal:
    def __init__(self):
        self.output_dir = "pine_script_documentation"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Main documentation URLs to download
        self.doc_urls = {
            "Welcome & Introduction": [
                "https://www.tradingview.com/pine-script-docs/welcome/",
                "https://www.tradingview.com/pine-script-docs/welcome/Pine_Script_v5_User_Manual/",
                "https://www.tradingview.com/pine-script-docs/welcome/First_steps/",
                "https://www.tradingview.com/pine-script-docs/welcome/Next_steps/",
            ],
            "Language Fundamentals": [
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
            "Core Concepts": [
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
            "Writing Scripts": [
                "https://www.tradingview.com/pine-script-docs/writing/",
                "https://www.tradingview.com/pine-script-docs/writing/Style_guide/",
                "https://www.tradingview.com/pine-script-docs/writing/Debugging/",
                "https://www.tradingview.com/pine-script-docs/writing/Publishing_scripts/",
                "https://www.tradingview.com/pine-script-docs/writing/Limitations/",
            ],
            "FAQ and Migration": [
                "https://www.tradingview.com/pine-script-docs/faq/",
                "https://www.tradingview.com/pine-script-docs/migration_guides/",
                "https://www.tradingview.com/pine-script-docs/migration_guides/To_Pine_Script_v5/",
                "https://www.tradingview.com/pine-script-docs/migration_guides/v4_to_v5_migration_guide/",
            ],
            "Error Messages": [
                "https://www.tradingview.com/pine-script-docs/errors/",
            ],
            "Release Notes": [
                "https://www.tradingview.com/pine-script-docs/release_notes/",
            ]
        }
    
    def download_page_as_pdf(self, url, output_file):
        """Download a single page and convert it to PDF using wkhtmltopdf"""
        try:
            print(f"Converting {url} to PDF...")
            
            # wkhtmltopdf options for better rendering
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
                'javascript-delay': '2000',  # Wait for JS to load
                'no-stop-slow-scripts': None,
                'load-error-handling': 'ignore',
                'load-media-error-handling': 'ignore'
            }
            
            pdfkit.from_url(url, output_file, options=options)
            return True
        except Exception as e:
            print(f"Error converting {url}: {e}")
            return False
    
    def merge_pdfs(self, pdf_files, output_file):
        """Merge multiple PDFs into one"""
        pdf_writer = PdfWriter()
        
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                try:
                    pdf_reader = PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                except Exception as e:
                    print(f"Error reading {pdf_file}: {e}")
        
        with open(output_file, 'wb') as output:
            pdf_writer.write(output)
    
    def check_and_split_pdf(self, pdf_file):
        """Check PDF size and split if necessary"""
        file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
        
        if file_size_mb > 15:
            print(f"PDF {pdf_file} is {file_size_mb:.2f} MB, splitting...")
            
            try:
                reader = PdfReader(pdf_file)
                total_pages = len(reader.pages)
                pages_per_part = max(1, int(total_pages * 14 / file_size_mb))
                
                base_name = os.path.splitext(pdf_file)[0]
                part_files = []
                
                for part_num, start_page in enumerate(range(0, total_pages, pages_per_part), 1):
                    writer = PdfWriter()
                    end_page = min(start_page + pages_per_part, total_pages)
                    
                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])
                    
                    part_filename = f"{base_name}_part{part_num}.pdf"
                    with open(part_filename, 'wb') as output:
                        writer.write(output)
                    
                    part_size_mb = os.path.getsize(part_filename) / (1024 * 1024)
                    print(f"Created: {os.path.basename(part_filename)} ({part_size_mb:.2f} MB)")
                    part_files.append(part_filename)
                
                # Remove original large file
                os.remove(pdf_file)
                return part_files
            except Exception as e:
                print(f"Error splitting PDF: {e}")
                return [pdf_file]
        else:
            print(f"Created: {os.path.basename(pdf_file)} ({file_size_mb:.2f} MB)")
            return [pdf_file]
    
    def run(self):
        """Main execution"""
        print("Starting Pine Script documentation download...")
        print("This will download and convert the main documentation pages to PDF.")
        
        # First check if wkhtmltopdf is installed
        try:
            subprocess.run(['which', 'wkhtmltopdf'], check=True, capture_output=True)
        except:
            print("Installing wkhtmltopdf...")
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'wkhtmltopdf'], check=True)
        
        all_pdfs = []
        temp_dir = os.path.join(self.output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Process each section
        for section_name, urls in self.doc_urls.items():
            print(f"\n--- Processing section: {section_name} ---")
            
            section_pdfs = []
            for i, url in enumerate(urls):
                temp_pdf = os.path.join(temp_dir, f"{section_name.replace(' ', '_')}_{i}.pdf")
                if self.download_page_as_pdf(url, temp_pdf):
                    section_pdfs.append(temp_pdf)
            
            # Merge section PDFs
            if section_pdfs:
                section_output = os.path.join(self.output_dir, f"PineScript_{section_name.replace(' ', '_')}.pdf")
                self.merge_pdfs(section_pdfs, section_output)
                
                # Check size and split if necessary
                final_files = self.check_and_split_pdf(section_output)
                all_pdfs.extend(final_files)
                
                # Clean up temp files
                for temp_pdf in section_pdfs:
                    if os.path.exists(temp_pdf):
                        os.remove(temp_pdf)
        
        # Clean up temp directory
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        
        print("\n=== Conversion completed! ===")
        print(f"PDF files are saved in: {self.output_dir}")
        print(f"\nCreated {len(all_pdfs)} PDF files:")
        
        total_size = 0
        for pdf in sorted(all_pdfs):
            if os.path.exists(pdf):
                size_mb = os.path.getsize(pdf) / (1024 * 1024)
                total_size += size_mb
                print(f"  - {os.path.basename(pdf)} ({size_mb:.2f} MB)")
        
        print(f"\nTotal size: {total_size:.2f} MB")

if __name__ == "__main__":
    converter = PineDocsFinal()
    converter.run()