#!/usr/bin/env python3
"""
Download TradingView Pine Script Documentation and Convert to PDFs
Uses wget to mirror the website and then converts HTML files to PDFs
"""

import os
import subprocess
import re
from pathlib import Path
from bs4 import BeautifulSoup
import weasyprint
from PyPDF2 import PdfReader, PdfWriter
import shutil

class PineDocsDownloader:
    def __init__(self):
        self.base_url = "https://www.tradingview.com/pine-script-docs/"
        self.download_dir = "pine_docs_download"
        self.output_dir = "pine_docs_pdfs"
        self.temp_dir = "pine_docs_temp"
        
        # Create directories
        for dir_path in [self.download_dir, self.output_dir, self.temp_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def download_documentation(self):
        """Download the entire documentation using wget"""
        print("Downloading TradingView Pine Script documentation...")
        
        wget_cmd = [
            "wget",
            "--recursive",
            "--no-clobber",
            "--page-requisites",
            "--html-extension",
            "--convert-links",
            "--restrict-file-names=windows",
            "--domains", "tradingview.com",
            "--no-parent",
            "--directory-prefix=" + self.download_dir,
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            self.base_url
        ]
        
        try:
            subprocess.run(wget_cmd, check=True)
            print("Download completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error downloading documentation: {e}")
            return False
    
    def find_html_files(self):
        """Find all HTML files in the downloaded directory"""
        html_files = []
        for root, dirs, files in os.walk(self.download_dir):
            for file in files:
                if file.endswith(('.html', '.htm')):
                    html_files.append(os.path.join(root, file))
        return html_files
    
    def clean_html_for_pdf(self, html_content):
        """Clean HTML content for better PDF conversion"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script tags
        for script in soup.find_all('script'):
            script.decompose()
        
        # Remove style tags that might cause issues
        for style in soup.find_all('style'):
            style.decompose()
        
        # Add basic styling for better PDF output
        style_tag = soup.new_tag('style')
        style_tag.string = """
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            max-width: 800px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #333;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        pre, code {
            background-color: #f4f4f4;
            padding: 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }
        pre {
            padding: 10px;
            margin: 10px 0;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        """
        
        if soup.head:
            soup.head.append(style_tag)
        else:
            head_tag = soup.new_tag('head')
            head_tag.append(style_tag)
            soup.insert(0, head_tag)
        
        return str(soup)
    
    def convert_html_to_pdf(self, html_file, output_pdf):
        """Convert a single HTML file to PDF"""
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # Clean the HTML
            cleaned_html = self.clean_html_for_pdf(html_content)
            
            # Convert to PDF using WeasyPrint
            pdf = weasyprint.HTML(string=cleaned_html, base_url=os.path.dirname(html_file)).write_pdf()
            
            with open(output_pdf, 'wb') as f:
                f.write(pdf)
            
            return True
        except Exception as e:
            print(f"Error converting {html_file} to PDF: {e}")
            return False
    
    def organize_and_convert_to_pdfs(self):
        """Organize HTML files and convert them to PDFs"""
        html_files = self.find_html_files()
        
        if not html_files:
            print("No HTML files found!")
            return
        
        print(f"Found {len(html_files)} HTML files")
        
        # Group files by directory structure
        file_groups = {}
        for html_file in html_files:
            # Get relative path from download directory
            rel_path = os.path.relpath(html_file, self.download_dir)
            dir_path = os.path.dirname(rel_path)
            
            if dir_path not in file_groups:
                file_groups[dir_path] = []
            file_groups[dir_path].append(html_file)
        
        # Convert each group to a PDF
        pdf_count = 0
        for group_name, files in file_groups.items():
            # Create a meaningful PDF name
            if group_name == '' or group_name == '.':
                pdf_name = "pine_script_docs_main.pdf"
            else:
                # Clean the group name for filename
                clean_name = re.sub(r'[^\w\s-]', '_', group_name)
                clean_name = re.sub(r'[-\s]+', '_', clean_name)
                pdf_name = f"pine_script_docs_{clean_name}.pdf"
            
            output_pdf = os.path.join(self.output_dir, pdf_name)
            
            # Convert each HTML file in the group
            temp_pdfs = []
            for i, html_file in enumerate(files):
                temp_pdf = os.path.join(self.temp_dir, f"temp_{pdf_count}_{i}.pdf")
                if self.convert_html_to_pdf(html_file, temp_pdf):
                    temp_pdfs.append(temp_pdf)
                    print(f"Converted: {os.path.basename(html_file)}")
            
            # Merge PDFs if multiple files
            if temp_pdfs:
                if len(temp_pdfs) == 1:
                    shutil.copy(temp_pdfs[0], output_pdf)
                else:
                    self.merge_pdfs(temp_pdfs, output_pdf)
                
                # Check file size
                file_size = os.path.getsize(output_pdf) / (1024 * 1024)  # MB
                if file_size > 15:
                    # Split the PDF if it's too large
                    self.split_large_pdf(output_pdf, 15)
                
                pdf_count += 1
                print(f"Created: {pdf_name} ({file_size:.2f} MB)")
            
            # Clean up temp files
            for temp_pdf in temp_pdfs:
                if os.path.exists(temp_pdf):
                    os.remove(temp_pdf)
    
    def merge_pdfs(self, pdf_files, output_file):
        """Merge multiple PDF files into one"""
        pdf_writer = PdfWriter()
        
        for pdf_file in pdf_files:
            try:
                pdf_reader = PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
            except Exception as e:
                print(f"Error reading {pdf_file}: {e}")
        
        with open(output_file, 'wb') as output:
            pdf_writer.write(output)
    
    def split_large_pdf(self, pdf_file, max_size_mb):
        """Split a large PDF into smaller parts"""
        try:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            
            # Estimate pages per part
            file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
            pages_per_part = int(total_pages * max_size_mb / file_size_mb * 0.9)  # 90% to be safe
            
            if pages_per_part < 1:
                pages_per_part = 1
            
            # Split the PDF
            base_name = os.path.splitext(pdf_file)[0]
            part_num = 1
            
            for i in range(0, total_pages, pages_per_part):
                pdf_writer = PdfWriter()
                
                for j in range(i, min(i + pages_per_part, total_pages)):
                    pdf_writer.add_page(pdf_reader.pages[j])
                
                part_filename = f"{base_name}_part{part_num}.pdf"
                with open(part_filename, 'wb') as output:
                    pdf_writer.write(output)
                
                part_size = os.path.getsize(part_filename) / (1024 * 1024)
                print(f"Created: {os.path.basename(part_filename)} ({part_size:.2f} MB)")
                part_num += 1
            
            # Remove the original large file
            os.remove(pdf_file)
            
        except Exception as e:
            print(f"Error splitting PDF {pdf_file}: {e}")
    
    def run(self):
        """Main execution method"""
        print("Starting Pine Script documentation download and conversion...")
        
        # Download documentation
        if self.download_documentation():
            # Convert to PDFs
            self.organize_and_convert_to_pdfs()
            
            # Clean up
            print("\nCleaning up temporary files...")
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            print("\nConversion completed!")
            print(f"PDF files are saved in: {self.output_dir}")
            
            # List created PDFs
            pdf_files = [f for f in os.listdir(self.output_dir) if f.endswith('.pdf')]
            print(f"\nCreated {len(pdf_files)} PDF files:")
            for pdf in sorted(pdf_files):
                size = os.path.getsize(os.path.join(self.output_dir, pdf)) / (1024 * 1024)
                print(f"  - {pdf} ({size:.2f} MB)")

if __name__ == "__main__":
    downloader = PineDocsDownloader()
    downloader.run()