import os
import sys
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create output folder for slide diagrams
os.makedirs('slide_assets', exist_ok=True)

# Set global styles for matplotlib diagrams
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# Color Definitions
NAVY = '#0A192F'
SLATE = '#1E293B'
TEAL = '#0D9488'
CYAN = '#0284C7'
GREEN_MVP = '#15803D'
AMBER = '#D97706'
BG_LIGHT = '#F8FAFC'
CARD_BG = '#FFFFFF'
BORDER_GRAY = '#CBD5E1'
TEXT_DARK = '#0F172A'
TEXT_MUTED = '#475569'

def generate_slide2_diagram():
    fig, ax = plt.subplots(figsize=(12, 5.2), dpi=200)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_facecolor(BG_LIGHT)
    ax.axis('off')

    # Top Section: 3-Stage Pipeline
    ax.text(0.02, 0.94, "PROPOSED 3-STAGE ATTRIBUTION PIPELINE", fontsize=11, fontweight='bold', color=NAVY)
    
    stages = [
        ("STAGE 1: DETECT", "Sentinel-1 SAR Imagery\nDeep U-Net Slick Segmentation\nDual-Pol VV/VH Ratio Dampening", CYAN),
        ("STAGE 2: RECONSTRUCT", "4D Backward Drift (OpenDrift)\nERA5 Winds + INCOIS Currents\n95% Probable Origin Region", TEAL),
        ("STAGE 3: CORRELATE & RANK", "Spatiotemporal AIS Trajectory Query\nHeading, Time & Distance Matching\nRanked Candidate Attribution List", GREEN_MVP)
    ]
    
    for i, (title, text, color) in enumerate(stages):
        x = 0.02 + i * 0.325
        y = 0.65
        w = 0.30
        h = 0.24
        
        # Main Card
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor=CARD_BG, edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        
        # Header Badge
        header_rect = patches.FancyBboxPatch((x, y + h - 0.06), w, 0.06, boxstyle="round,pad=0,rounding_size=0.01",
                                             facecolor=color, edgecolor='none')
        ax.add_patch(header_rect)
        ax.text(x + w/2, y + h - 0.03, title, fontsize=9.5, fontweight='bold', color='white', ha='center', va='center')
        
        # Content Text
        ax.text(x + 0.015, y + 0.09, text, fontsize=8.5, color=TEXT_DARK, va='center', linespacing=1.35)
        
        # Arrow connecting stages
        if i < 2:
            ax.annotate("", xy=(x + w + 0.022, y + h/2), xytext=(x + w + 0.003, y + h/2),
                        arrowprops=dict(arrowstyle="->", color=NAVY, lw=2.5))

    # Bottom Left: False Positive Gating Flow
    ax.text(0.02, 0.58, "FALSE-POSITIVE LOOK-ALIKE REJECTION GATING", fontsize=10, fontweight='bold', color=NAVY)
    
    gating_box = patches.FancyBboxPatch((0.02, 0.04), 0.46, 0.50, boxstyle="round,pad=0.01,rounding_size=0.02",
                                         facecolor=CARD_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(gating_box)
    
    ax.text(0.04, 0.46, "SAR Input  -->  Candidate Slick (U-Net)", fontsize=8.5, fontweight='bold', color=NAVY)
    ax.annotate("", xy=(0.20, 0.38), xytext=(0.20, 0.44), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.5))
    
    gate_card = patches.Rectangle((0.04, 0.20), 0.42, 0.18, facecolor='#F1F5F9', edgecolor=BORDER_GRAY)
    ax.add_patch(gate_card)
    ax.text(0.05, 0.34, "[ Look-Alike Feature & MetOcean Gating ]", fontsize=8, fontweight='bold', color=CYAN)
    ax.text(0.05, 0.26, "* Dual-Pol VV/VH Ratio (Bragg damping)\n* GLCM Texture Entropy & Homogeneity\n* Wind Speed Thresholding (> 2 m/s)", fontsize=7.5, color=TEXT_DARK, linespacing=1.3)
    
    ax.annotate("", xy=(0.14, 0.12), xytext=(0.14, 0.20), arrowprops=dict(arrowstyle="->", color=GREEN_MVP, lw=1.5))
    ax.annotate("", xy=(0.36, 0.12), xytext=(0.36, 0.20), arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.5))
    
    ax.text(0.14, 0.08, "Oil Slick\n(Confidence: 0.92)", fontsize=7.5, fontweight='bold', color=GREEN_MVP, ha='center', va='center')
    ax.text(0.36, 0.08, "Biogenic Film\n(Rejected)", fontsize=7.5, fontweight='bold', color=AMBER, ha='center', va='center')

    # Bottom Right: Workflow Evolution
    ax.text(0.51, 0.58, "WORKFLOW COMPARISON: CURRENT VS MARIS-TRACER", fontsize=10, fontweight='bold', color=NAVY)
    
    wf_box = patches.FancyBboxPatch((0.51, 0.04), 0.47, 0.50, boxstyle="round,pad=0.01,rounding_size=0.02",
                                     facecolor=CARD_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(wf_box)
    
    curr_wf = (
        "CURRENT WORKFLOW (Analyst-Driven Screening):\n"
        "  Satellite Alert  -->  Manual Triage  -->  Unlinked AIS\n"
        "  - High manual delay (hours to days)\n"
        "  - Detection completely isolated from attribution\n\n"
        "MARIS-TRACER (Decision Support Framework):\n"
        "  SAR Ingest  -->  U-Net  -->  4D Drift  -->  AIS Match\n"
        "  - Automated end-to-end processing pipeline\n"
        "  - Output: Ranked Vessel Candidates with Score %"
    )
    ax.text(0.53, 0.28, curr_wf, fontsize=8.2, color=TEXT_DARK, va='center', linespacing=1.35)

    plt.tight_layout()
    plt.savefig('slide_assets/slide2_diagram.png', bbox_inches='tight', facecolor=BG_LIGHT)
    plt.close()

def generate_slide3_diagram():
    fig, ax = plt.subplots(figsize=(12, 5.2), dpi=200)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_facecolor(BG_LIGHT)
    ax.axis('off')

    # Top Section: Hackathon MVP vs Advanced Scope
    ax.text(0.02, 0.94, "SYSTEM SCOPE: HACKATHON MVP VS ADVANCED PHASE", fontsize=11, fontweight='bold', color=NAVY)
    
    # MVP Box (Green)
    mvp_box = patches.FancyBboxPatch((0.02, 0.50), 0.46, 0.40, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#F0FDF4', edgecolor=GREEN_MVP, linewidth=2)
    ax.add_patch(mvp_box)
    ax.text(0.04, 0.85, "HACKATHON MVP (36-Hour Core - MUST WORK)", fontsize=9.5, fontweight='bold', color=GREEN_MVP)
    mvp_items = (
        "- Sentinel-1 GRD SAR Ingestion + SNAP Speckle Filter\n"
        "- PyTorch U-Net Deep Learning Slick Segmentation\n"
        "- 2D/3D Backward Particle Drift (ERA5 + INCOIS Currents)\n"
        "- Spatiotemporal AIS Trajectory Bounding Query (PostGIS)\n"
        "- Explainable Proximity Ranking + Interactive GIS Dashboard"
    )
    ax.text(0.04, 0.67, mvp_items, fontsize=8.2, color=TEXT_DARK, va='center', linespacing=1.35)
    
    # Advanced Box (Amber/Slate)
    adv_box = patches.FancyBboxPatch((0.51, 0.50), 0.47, 0.40, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#FFFBEB', edgecolor=AMBER, linewidth=1.5)
    ax.add_patch(adv_box)
    ax.text(0.53, 0.85, "ADVANCED PHASE (Post-Hackathon / If Time Permits)", fontsize=9.5, fontweight='bold', color=AMBER)
    adv_items = (
        "- Bi-Temporal OSCD Change Detection & Multi-sensor Fusion\n"
        "- 10,000 Particle Monte Carlo Ensemble Dispersion\n"
        "- Dark-Ship Kinematic Dead Reckoning & Wake Detection\n"
        "- Automated PDF Forensic Evidence Report Generation\n"
        "- Real-Time Live NMEA/AIS Stream Parser Integration"
    )
    ax.text(0.53, 0.67, adv_items, fontsize=8.2, color=TEXT_DARK, va='center', linespacing=1.35)

    # Bottom Section: Team Expertise & Role Allocation Matrix
    ax.text(0.02, 0.44, "TEAM EXPERTISE & MODULE OWNERSHIP MATRIX", fontsize=10, fontweight='bold', color=NAVY)
    
    table_box = patches.FancyBboxPatch((0.02, 0.04), 0.96, 0.37, boxstyle="round,pad=0.01,rounding_size=0.02",
                                        facecolor=CARD_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(table_box)
    
    # Header Row
    ax.fill_between([0.02, 0.98], [0.34, 0.34], [0.40, 0.40], color=NAVY)
    ax.text(0.04, 0.37, "Role / Expertise", fontsize=8.5, fontweight='bold', color='white', va='center')
    ax.text(0.25, 0.37, "Primary Responsibility", fontsize=8.5, fontweight='bold', color='white', va='center')
    ax.text(0.58, 0.37, "Tech Stack & Core Deliverable", fontsize=8.5, fontweight='bold', color='white', va='center')
    ax.text(0.85, 0.37, "Hackathon Owner", fontsize=8.5, fontweight='bold', color='white', va='center')
    
    rows = [
        ("ML / CV Lead", "SAR Preprocessing & U-Net Slick Segmentation", "PyTorch, OpenCV, GDAL, Albumentations", "Member 1"),
        ("Hydrodynamics Lead", "Ocean Current Forcing & Particle Backtracking", "OpenDrift, PyGNOME, NetCDF4, SciPy", "Member 2"),
        ("Maritime GIS Lead", "AIS Trajectory Indexing & Spatial Queries", "PostgreSQL/PostGIS, GeoPandas, H3", "Member 3"),
        ("Full-Stack Lead", "Backend API, Interactive Map UI & Report Engine", "FastAPI, React, Mapbox GL JS, Leaflet", "Member 4 & 5")
    ]
    
    for i, (role, resp, stack, owner) in enumerate(rows):
        y_pos = 0.28 - i * 0.075
        bg_c = '#F8FAFC' if i % 2 == 0 else CARD_BG
        rect = patches.Rectangle((0.025, y_pos - 0.025), 0.95, 0.065, facecolor=bg_c, edgecolor='none')
        ax.add_patch(rect)
        ax.text(0.04, y_pos, role, fontsize=8, fontweight='bold', color=TEXT_DARK, va='center')
        ax.text(0.25, y_pos, resp, fontsize=8, color=TEXT_DARK, va='center')
        ax.text(0.58, y_pos, stack, fontsize=8, color=TEXT_MUTED, va='center')
        ax.text(0.85, y_pos, owner, fontsize=8, fontweight='bold', color=CYAN, va='center')

    plt.tight_layout()
    plt.savefig('slide_assets/slide3_diagram.png', bbox_inches='tight', facecolor=BG_LIGHT)
    plt.close()

def generate_slide4_diagram():
    fig, ax = plt.subplots(figsize=(12, 5.2), dpi=200)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_facecolor(BG_LIGHT)
    ax.axis('off')

    # Top Left: Data Strategy Box
    ax.text(0.02, 0.94, "DATA VIABILITY: DEMONSTRATION-FEASIBLE", fontsize=11, fontweight='bold', color=NAVY)
    
    data_box = patches.FancyBboxPatch((0.02, 0.50), 0.46, 0.40, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=CYAN, linewidth=1.5)
    ax.add_patch(data_box)
    
    data_content = (
        "REAL / PUBLIC OPEN-ACCESS FEEDS:\n"
        "- Sentinel-1 SAR GRD (ESA Copernicus API)\n"
        "- ERA5 Hourly 10m Surface Winds (ECMWF CDS)\n"
        "- INCOIS OSFS Daily Surface Current Velocity Grids\n\n"
        "DEMONSTRATION FALLBACK STRATEGY:\n"
        "- Public/Historical AIS Datasets (NOAA MarineCadastre / GFW)\n"
        "- Synthetic AIS Vessel Trajectory Generator (for live testing)\n"
        "- Ensures 100% reliable 36-hr hackathon prototype demo."
    )
    ax.text(0.04, 0.70, data_content, fontsize=8.2, color=TEXT_DARK, va='center', linespacing=1.35)

    # Top Right: Deployment Strategy Box
    ax.text(0.51, 0.94, "DEPLOYMENT & HARDWARE REQUIREMENTS", fontsize=11, fontweight='bold', color=NAVY)
    
    deploy_box = patches.FancyBboxPatch((0.51, 0.50), 0.47, 0.40, boxstyle="round,pad=0.01,rounding_size=0.02",
                                         facecolor=CARD_BG, edgecolor=TEAL, linewidth=1.5)
    ax.add_patch(deploy_box)
    
    deploy_content = (
        "ZERO VESSEL HARDWARE REQUIRED:\n"
        "- Operates entirely via remote satellite sensing and AIS.\n"
        "- No physical sensors or equipment installed on vessels.\n\n"
        "COMPUTE & HOSTING STACK:\n"
        "- Single workstation / cloud instance with NVIDIA GPU.\n"
        "- 1-Click Docker Compose deployment containerizing:\n"
        "  FastAPI Backend + PostgreSQL/PostGIS + React WebGIS UI."
    )
    ax.text(0.53, 0.70, deploy_content, fontsize=8.2, color=TEXT_DARK, va='center', linespacing=1.35)

    # Bottom: Risk & Mitigation Cards
    ax.text(0.02, 0.44, "KEY TECHNICAL RISKS & PRACTICAL MITIGATION STRATEGIES", fontsize=10, fontweight='bold', color=NAVY)
    
    risks = [
        ("RISK 1: Look-Alike Slicks", 
         "Algae, biogenic films & calm waters dampen radar waves like oil slicks.", 
         "Dual-Pol VV/VH ratio + GLCM texture + wind thresholding (> 2 m/s).", AMBER),
        ("RISK 2: Dark Ships (No AIS)", 
         "Perpetrators disable AIS transponders (~6% of global fleet).", 
         "Kinematic dead reckoning from past waypoints + SAR target detection.", AMBER),
        ("RISK 3: Hydrodynamic Drift Error", 
         "Ocean current turbulence & wind gust forecasting uncertainties.", 
         "Monte Carlo ensemble deriving probabilistic 95% origin region.", TEAL)
    ]
    
    for i, (title, desc, mit, color) in enumerate(risks):
        x = 0.02 + i * 0.325
        y = 0.04
        w = 0.30
        h = 0.36
        
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=color, linewidth=1.5)
        ax.add_patch(card)
        
        ax.text(x + 0.015, y + h - 0.04, title, fontsize=8.5, fontweight='bold', color=color)
        
        wrapped_desc = textwrap.fill(desc, width=34)
        ax.text(x + 0.015, y + h - 0.15, f"Challenge:\n{wrapped_desc}", fontsize=7.2, color=TEXT_DARK, va='top', linespacing=1.2)
        
        mit_rect = patches.Rectangle((x + 0.01, y + 0.015), w - 0.02, 0.13, facecolor='#F1F5F9', edgecolor='none')
        ax.add_patch(mit_rect)
        wrapped_mit = textwrap.fill(mit, width=32)
        ax.text(x + 0.015, y + 0.08, f"Mitigation:\n{wrapped_mit}", fontsize=7.0, fontweight='bold', color=NAVY, va='center', linespacing=1.2)

    plt.tight_layout()
    plt.savefig('slide_assets/slide4_diagram.png', bbox_inches='tight', facecolor=BG_LIGHT)
    plt.close()

def generate_slide5_diagram():
    fig, ax = plt.subplots(figsize=(12, 5.2), dpi=200)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_facecolor(BG_LIGHT)
    ax.axis('off')

    # Top Left: 6-Step Hackathon Demo Scenario
    ax.text(0.02, 0.94, "END-TO-END 6-STEP HACKATHON DEMO FLOW", fontsize=11, fontweight='bold', color=NAVY)
    
    demo_box = patches.FancyBboxPatch((0.02, 0.44), 0.51, 0.46, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=CYAN, linewidth=1.5)
    ax.add_patch(demo_box)
    
    steps = [
        "1. Ingest Sentinel-1 SAR Scene",
        "2. U-Net Segmentation (Slick Mask)",
        "3. 4D Backward Particle Drift",
        "4. 95% Origin Region Boundary",
        "5. Spatiotemporal AIS Search",
        "6. Ranked Candidates & Report"
    ]
    
    for i, step in enumerate(steps):
        col = i % 2
        row = i // 2
        sx = 0.04 + col * 0.24
        sy = 0.75 - row * 0.12
        
        sbox = patches.FancyBboxPatch((sx, sy), 0.22, 0.09, boxstyle="round,pad=0.005,rounding_size=0.01",
                                       facecolor='#F0F9FF', edgecolor=CYAN, linewidth=1)
        ax.add_patch(sbox)
        ax.text(sx + 0.11, sy + 0.045, step, fontsize=7.5, fontweight='bold', color=NAVY, ha='center', va='center')

    # Top Right: Target Evaluation Metrics Table
    ax.text(0.55, 0.94, "EVALUATION PLAN & TARGET METRICS", fontsize=11, fontweight='bold', color=NAVY)
    
    eval_box = patches.FancyBboxPatch((0.55, 0.44), 0.43, 0.46, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=GREEN_MVP, linewidth=1.5)
    ax.add_patch(eval_box)
    
    ax.fill_between([0.555, 0.975], [0.82, 0.82], [0.87, 0.87], color=GREEN_MVP)
    ax.text(0.57, 0.845, "Module", fontsize=8.5, fontweight='bold', color='white', va='center')
    ax.text(0.76, 0.845, "Target Metric", fontsize=8.5, fontweight='bold', color='white', va='center')
    ax.text(0.90, 0.845, "Target Goal", fontsize=8.5, fontweight='bold', color='white', va='center')
    
    metrics = [
        ("Slick Segmentation", "Dice / mIoU", ">= 0.78"),
        ("Look-Alike Rejection", "False Positive Rate", "<= 12%"),
        ("Origin Drift Error", "Median Error Distance", "<= 4.5 km"),
        ("Vessel Attribution", "Top-3 Recall", ">= 85%")
    ]
    for i, (mod, met, val) in enumerate(metrics):
        y_p = 0.75 - i * 0.075
        ax.text(0.57, y_p, mod, fontsize=8, color=TEXT_DARK, va='center')
        ax.text(0.76, y_p, met, fontsize=8, color=TEXT_MUTED, va='center')
        ax.text(0.90, y_p, val, fontsize=8, fontweight='bold', color=GREEN_MVP, va='center')

    # Bottom: Multi-Dimensional Benefits
    ax.text(0.02, 0.38, "MULTI-DIMENSIONAL STRATEGIC BENEFITS", fontsize=10, fontweight='bold', color=NAVY)
    
    benefits = [
        ("ENVIRONMENTAL IMPACT", "Accelerates spill containment boom deployment, protecting sensitive coastal ecosystems & mangroves.", GREEN_MVP),
        ("OPERATIONAL EFFICIENCY", "Replaces hours of manual screening with automated candidate ranking in under 3 minutes.", CYAN),
        ("ENFORCEMENT PRIORITIZATION", "Provides decision support for Coast Guard / NTRO to prioritize vessel inspections.", TEAL)
    ]
    
    for i, (title, desc, color) in enumerate(benefits):
        x = 0.02 + i * 0.325
        y = 0.04
        w = 0.30
        h = 0.28
        
        bcard = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                        facecolor=CARD_BG, edgecolor=color, linewidth=1.5)
        ax.add_patch(bcard)
        ax.text(x + 0.012, y + h - 0.05, title, fontsize=8, fontweight='bold', color=color)
        
        wrapped_desc = textwrap.fill(desc, width=34)
        ax.text(x + 0.012, y + 0.14, wrapped_desc, fontsize=7.2, color=TEXT_DARK, va='top', linespacing=1.25)

    plt.tight_layout()
    plt.savefig('slide_assets/slide5_diagram.png', bbox_inches='tight', facecolor=BG_LIGHT)
    plt.close()

def generate_slide6_diagram():
    fig, ax = plt.subplots(figsize=(12, 5.2), dpi=200)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_facecolor(BG_LIGHT)
    ax.axis('off')

    ax.text(0.02, 0.94, "SCIENTIFIC & GOVERNANCE REFERENCE FOUNDATIONS", fontsize=11, fontweight='bold', color=NAVY)
    
    ref_cats = [
        ("1. SAR AI & DEEP LEARNING PAPERS", [
            "- Lai et al. (2024). Deep Learning for SAR Oil Spill Segmentation & OSCD. IEEE TGRS.",
            "- Chen et al. (2023). DGNet: Distribution-Guided SAR Feature Extraction. IEEE TGRS.",
            "- Moon et al. (2024). DAKTer Diffusion Augmentation for SAR Segmentation. arXiv:2412.08116."
        ], CYAN),
        ("2. HYDRODYNAMICS & LAGRANGIAN DRIFT", [
            "- Dagestad et al. (2018). OpenDrift: Open-source Trajectory Framework. Geosci. Model Dev.",
            "- NOAA OR&R (2023). PyGNOME: Operational Oil Spill Modeling Environment.",
            "- Stokes Drift & Wind Leeway Formulations for Surface Pollutant Backtracking."
        ], TEAL),
        ("3. MARITIME LAW & GOVERNANCE", [
            "- IMO (2024). MARPOL Annex I: Regulations for Prevention of Pollution by Oil.",
            "- UNCLOS Part XII (1982). Protection and Preservation of Marine Environment. UN.",
            "- EMSA (2023). CleanSeaNet Satellite Monitoring Service in European Waters."
        ], AMBER),
        ("4. NATIONAL DATA & STRATEGIC ASSETS", [
            "- INCOIS (MoES, Govt. of India). Ocean State Forecast System (OSFS) High-Res Currents.",
            "- ESA Copernicus Hub. Sentinel-1 Synthetic Aperture Radar (SAR) Level-1 GRD.",
            "- NOAA MarineCadastre & Global Fishing Watch. Historic AIS Vessel Tracking Datasets."
        ], GREEN_MVP)
    ]
    
    for i, (title, points, color) in enumerate(ref_cats):
        col = i % 2
        row = i // 2
        x = 0.02 + col * 0.49
        y = 0.48 - row * 0.43
        w = 0.47
        h = 0.40
        
        rcard = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=color, linewidth=1.5)
        ax.add_patch(rcard)
        
        # Title bar
        rtitle = patches.FancyBboxPatch((x, y + h - 0.07), w, 0.07, boxstyle="round,pad=0,rounding_size=0.01",
                                         facecolor=color, edgecolor='none')
        ax.add_patch(rtitle)
        ax.text(x + 0.02, y + h - 0.035, title, fontsize=8.5, fontweight='bold', color='white', va='center')
        
        # Content points with textwrap
        wrapped_points = [textwrap.fill(pt, width=54) for pt in points]
        p_text = "\n".join(wrapped_points)
        ax.text(x + 0.015, y + 0.16, p_text, fontsize=7.0, color=TEXT_DARK, va='center', linespacing=1.3)

    plt.tight_layout()
    plt.savefig('slide_assets/slide6_diagram.png', bbox_inches='tight', facecolor=BG_LIGHT)
    plt.close()

# Generate all 5 slide diagrams
generate_slide2_diagram()
generate_slide3_diagram()
generate_slide4_diagram()
generate_slide5_diagram()
generate_slide6_diagram()

print("All slide diagrams regenerated cleanly with text wrapping!")
