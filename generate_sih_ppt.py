import os
import sys
from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Color Palette Definitions
NAVY = (10, 25, 47)          # #0A192F - Primary Dark Navy
DARK_BLUE = (15, 23, 42)     # #0F172A - Primary Text Dark
SLATE_BG = (30, 41, 59)      # #1E293B
TEAL_ACCENT = (13, 148, 136) # #0D9488 - Teal
CYAN_ACCENT = (2, 132, 199)  # #0284C7 - Cyan
GREEN_MVP = (22, 101, 52)    # #166534 - Emerald Green
AMBER_WARN = (217, 119, 6)   # #D97706 - Warning Amber
BG_LIGHT = (248, 250, 252)   # #F8FAFC - Slide Background
CARD_BG = (255, 255, 255)    # #FFFFFF - Card Background
BORDER_GRAY = (203, 213, 225)# #CBD5E1
TEXT_MUTED = (71, 85, 105)   # #475569

class SIH_PDF_Generator(FPDF):
    def __init__(self):
        # Widescreen 16:9 Presentation Dimensions: 297mm x 167mm
        super().__init__(orientation='L', unit='mm', format=(167, 297))
        self.set_auto_page_break(auto=False)
        self.set_margins(0, 0, 0)

    def build_title_slide(self):
        self.add_page()
        # Slide Background
        self.set_fill_color(*BG_LIGHT)
        self.rect(0, 0, 297, 167, 'F')

        # Header Bar
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 297, 22, 'F')

        # SIH Header Text
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.set_xy(15, 6)
        self.cell(180, 10, 'SMART INDIA HACKATHON 2026', 0, 0, 'L')

        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(56, 189, 248) # Sky Blue
        self.set_xy(200, 6)
        self.cell(82, 10, 'HARDWARE & SOFTWARE EDITION', 0, 0, 'R')

        # Title Page Card
        self.set_fill_color(*CARD_BG)
        self.set_draw_color(*BORDER_GRAY)
        self.rect(12, 26, 273, 134, 'DF')

        # Inner Header for Title Page
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(*NAVY)
        self.set_xy(20, 31)
        self.cell(200, 10, 'TITLE PAGE', 0, 0, 'L')

        # Decorative Horizontal Bar
        self.set_fill_color(*CYAN_ACCENT)
        self.rect(20, 42, 257, 1.5, 'F')

        # Problem Details - Left Column Card
        self.set_fill_color(241, 245, 249)
        self.rect(20, 47, 175, 106, 'F')
        self.set_draw_color(*BORDER_GRAY)
        self.rect(20, 47, 175, 106, 'D')

        details = [
            ("Problem Statement ID:", "26143"),
            ("Problem Statement Title:", "Leveraging satellite imagery to determine Oil spills at sea along with AIS data correlations to identify vessel responsible for the spill."),
            ("Theme:", "Disaster Management"),
            ("PS Category:", "Software"),
            ("Project Name:", "MARIS-TRACER (Multi-Modal Oil Spill Source Attribution)"),
            ("Organization / Ministry:", "National Technical Research Organisation (NTRO)"),
            ("Team ID:", "________________________  (Left blank as per SIH guidelines)"),
            ("Team Name:", "Team MARIS")
        ]

        y_offset = 51
        for label, val in details:
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(*NAVY)
            self.set_xy(24, y_offset)
            self.cell(50, 5, f"• {label}", 0, 0, 'L')

            self.set_font('Helvetica', '', 8.5 if len(val) > 60 else 9)
            self.set_text_color(*DARK_BLUE)
            self.set_xy(74, y_offset)
            if len(val) > 60:
                self.multi_cell(118, 4.5, val)
                y_offset += (len(val) // 60 + 1) * 4.5 + 2.5
            else:
                self.cell(118, 5, val, 0, 0, 'L')
                y_offset += 6.5

        # Right Column - Core Architecture Highlights Card
        self.set_fill_color(*NAVY)
        self.rect(200, 47, 77, 106, 'F')

        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(56, 189, 248) # Cyan text
        self.set_xy(204, 52)
        self.cell(69, 6, 'MARIS-TRACER', 0, 0, 'C')

        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(255, 255, 255)
        self.set_xy(204, 58)
        self.cell(69, 5, 'Decision Support Framework', 0, 0, 'C')

        self.set_fill_color(*CYAN_ACCENT)
        self.rect(210, 65, 57, 0.8, 'F')

        highlights = [
            "1. Deep SAR Vision",
            "U-Net capillary wave dampening segmentation on Sentinel-1 SAR.",
            "2. 4D Hydrodynamics",
            "Backward particle tracking (OpenDrift) under wind & currents.",
            "3. AIS Correlation",
            "Spatiotemporal vessel trajectory query & candidate ranking.",
            "4. Decision Support",
            "Evidence-backed report generation for Coast Guard / NTRO."
        ]

        hy = 70
        for i in range(0, len(highlights), 2):
            self.set_font('Helvetica', 'B', 8.5)
            self.set_text_color(56, 189, 248)
            self.set_xy(204, hy)
            self.cell(69, 4.5, highlights[i], 0, 0, 'L')

            self.set_font('Helvetica', '', 7.5)
            self.set_text_color(226, 232, 240)
            self.set_xy(204, hy + 4.5)
            self.multi_cell(69, 3.8, highlights[i+1])
            hy += 19

    def build_slide(self, title_text, diagram_path, slide_num):
        self.add_page()
        # Slide Background
        self.set_fill_color(*BG_LIGHT)
        self.rect(0, 0, 297, 167, 'F')

        # Top Banner
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 297, 18, 'F')

        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(255, 255, 255)
        self.set_xy(12, 4.5)
        self.cell(150, 9, 'SMART INDIA HACKATHON 2026', 0, 0, 'L')

        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(56, 189, 248)
        self.set_xy(180, 4.5)
        self.cell(105, 9, 'PS ID: 26143 | Software Category | NTRO', 0, 0, 'R')

        # Slide Title Bar Card
        self.set_fill_color(*CARD_BG)
        self.rect(10, 21, 277, 12, 'F')
        self.set_draw_color(*BORDER_GRAY)
        self.rect(10, 21, 277, 12, 'D')

        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*NAVY)
        self.set_xy(14, 22.5)
        self.cell(180, 9, title_text.upper(), 0, 0, 'L')

        self.set_font('Helvetica', 'B', 9.5)
        self.set_text_color(*TEAL_ACCENT)
        self.set_xy(210, 22.5)
        self.cell(72, 9, 'Idea Title: MARIS-TRACER', 0, 0, 'R')

        # Diagram Image Placement
        if os.path.exists(diagram_path):
            self.image(diagram_path, x=10, y=35, w=277)

        # Footer
        self.set_draw_color(*BORDER_GRAY)
        self.line(10, 159, 287, 159)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(*TEXT_MUTED)
        self.set_xy(10, 160)
        self.cell(180, 5, 'MARIS-TRACER: Multi-Modal Oil Spill Source Attribution (Decision Support System)', 0, 0, 'L')
        self.set_xy(240, 160)
        self.cell(47, 5, f'Slide {slide_num} of 6', 0, 0, 'R')

def main():
    pdf = SIH_PDF_Generator()
    
    # Slide 1: Title Page
    pdf.build_title_slide()
    
    # Slide 2: Proposed Solution
    pdf.build_slide("Proposed Solution — From Detection to Source Attribution", "slide_assets/slide2_diagram.png", 2)
    
    # Slide 3: Technical Approach
    pdf.build_slide("Technical Approach — System Architecture & Scope", "slide_assets/slide3_diagram.png", 3)
    
    # Slide 4: Feasibility & Viability
    pdf.build_slide("Feasibility & Viability — Data Strategy & Risk Mitigation", "slide_assets/slide4_diagram.png", 4)
    
    # Slide 5: Impact & Benefits
    pdf.build_slide("Impact & Benefits — Evaluation Plan & Strategic Value", "slide_assets/slide5_diagram.png", 5)
    
    # Slide 6: Research & References
    pdf.build_slide("Research & References — Scientific & Governance Foundations", "slide_assets/slide6_diagram.png", 6)
    
    output_filename = "SIH_2026_MARIS_TRACER_PS26143.pdf"
    pdf.output(output_filename)
    print(f"Presentation PDF successfully created: {output_filename}")

if __name__ == "__main__":
    main()
