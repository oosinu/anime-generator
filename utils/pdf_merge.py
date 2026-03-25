#!/usr/bin/env python3
"""
PDF Merger for anime Generator
Combine generated images into a single PDF file
"""

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pathlib import Path
from typing import List

def images_to_pdf(image_dir: Path, output_pdf: Path, aspect_ratio: str = "3:4") -> None:
    """Combine all images in directory to a single PDF"""
    
    # Get all PNG files sorted numerically
    image_files = sorted(list(image_dir.glob('*.png')))
    
    if not image_files:
        raise ValueError("No PNG images found in directory")
    
    # Page size based on aspect ratio
    if aspect_ratio == "3:4":
        page_width, page_height = A4[1] * 3/4, A4[1]
    elif aspect_ratio == "4:3":
        page_width, page_height = A4[0], A4[0] * 3/4
    elif aspect_ratio == "16:9":
        page_width, page_height = A4[0], A4[0] * 9/16
    else:
        page_width, page_height = A4[1] * 3/4, A4[1]
    
    c = canvas.Canvas(str(output_pdf), pagesize=(page_width, page_height))
    
    for img_path in image_files:
        img = Image.open(img_path)
        img_width, img_height = img.size
        
        # Scale image to fit page
        scale = min(page_width / img_width, page_height / img_height)
        new_width = img_width * scale
        new_height = img_height * scale
        
        # Center image
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2
        
        c.drawImage(str(img_path), x, y, new_width, new_height)
        c.showPage()
    
    c.save()
    print(f"PDF created: {output_pdf}")
    print(f"   Total pages: {len(image_files)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python pdf_merge.py <image_directory> <output_pdf>")
        sys.exit(1)
    
    image_dir = Path(sys.argv[1])
    output_pdf = Path(sys.argv[2])
    images_to_pdf(image_dir, output_pdf)
