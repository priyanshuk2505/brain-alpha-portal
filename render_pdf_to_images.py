import os
import Quartz
from Quartz import PDFDocument
from Foundation import NSURL
import AppKit

os.makedirs('rendered_slides', exist_ok=True)
pdf_path = 'SIH_2026_MARIS_TRACER_PS26143.pdf'

doc = PDFDocument.alloc().initWithURL_(NSURL.fileURLWithPath_(pdf_path))
num_pages = doc.pageCount()
print(f"Total pages in PDF: {num_pages}")

for i in range(num_pages):
    page = doc.pageAtIndex_(i)
    bounds = page.boundsForBox_(Quartz.kPDFDisplayBoxMediaBox)
    scale = 2.0 # 2x resolution for high quality
    width, height = int(bounds.size.width * scale), int(bounds.size.height * scale)

    img = AppKit.NSImage.alloc().initWithSize_((width, height))
    img.lockFocus()
    ctx = AppKit.NSGraphicsContext.currentContext().CGContext()
    
    # Fill white background
    Quartz.CGContextSetRGBFillColor(ctx, 1, 1, 1, 1)
    Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, width, height))
    
    # Scale CTM
    Quartz.CGContextScaleCTM(ctx, scale, scale)
    page.drawWithBox_(Quartz.kPDFDisplayBoxMediaBox)
    img.unlockFocus()

    tiff = img.TIFFRepresentation()
    bitmap = AppKit.NSBitmapImageRep.imageRepWithData_(tiff)
    png = bitmap.representationUsingType_properties_(AppKit.NSPNGFileType, None)
    
    out_img = f"rendered_slides/slide_{i+1}.png"
    png.writeToFile_atomically_(out_img, True)
    print(f"Rendered Slide {i+1} -> {out_img}")

print("All slides rendered to PNG successfully.")
