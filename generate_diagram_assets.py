import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Create output folder for slide diagrams
os.makedirs('slide_assets', exist_ok=True)

# Set global styles for matplotlib diagrams
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']

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
    ax.text(0.02, 0.94, "PROPOSED 3-STAGE ATTRIPUTION PIPELINE", fontsize=11, fontweight='bold', color=NAVY)
    
    stages = [
        ("STAGE 1: DETECT", "Sentinel-1 SAR Imagery\nDeep U-Net Slick Segmentation\nDual-Pol VV/VH Ratio Dampening", CYAN),
        ("STAGE 2: RECONSTRUCT", "4D Backward Drift (OpenDrift)\nERA5 Winds + INCOIS Currents\n95% Probable Origin Region", TEAL),
        ("STAGE 3: CORRELATE & RANK", "Spatiotemporal AIS Trajectory Query\nHeading, Time & Distance Matching\nRanked Attribution Candidate List", GREEN_MVP)
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
        ax.text(x + w/2, y + h - 0.03, title, fontsize=10, fontweight='bold', color='white', ha='center', va='center')
        
        # Content Text
        ax.text(x + 0.015, y + 0.09, text, fontsize=8.5, color=TEXT_DARK, va='center', linespacing=1.4)
        
        # Arrow connecting stages
        if i < 2:
            ax.annotate("", xy=(x + w + 0.02, y + h/2), xytext=(x + w + 0.005, y + h/2),
                        arrowprops=dict(arrowstyle="->", color=NAVY, lw=2.5))

    # Bottom Left: False Positive Gating Flow
    ax.text(0.02, 0.58, "FALSE-POSITIVE LOOK-ALIKE REJECTION GATING", fontsize=10, fontweight='bold', color=NAVY)
    
    gating_box = patches.FancyBboxPatch((0.02, 0.05), 0.46, 0.48, boxstyle="round,pad=0.01,rounding_size=0.02",
                                         facecolor=CARD_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(gating_box)
    
    # Gating steps text
    gate_text = (
        "SAR Input  ─►  Candidate Slick (U-Net)\n"
        "                     │\n"
        "                     ▼\n"
        "     [ Look-Alike Feature Gating ]\n"
        "     • Dual-Pol VV/VH Ratio (Bragg damping)\n"
        "     • GLCM Texture Entropy & Homogeneity\n"
        "     • MetOcean Wind Speed Thresholding (> 2 m/s)\n"
        "                     │\n"
        "         ┌───────────┴───────────┐\n"
        "         ▼                       ▼\n"
        "  Oil Slick (Score: 0.92)   Biogenic Film (Rejected)"
    )
    ax.text(0.04, 0.29, gate_text, fontsize=8, family='monospace', color=TEXT_DARK, va='center')

    # Bottom Right: Workflow Evolution (Current vs MARIS-TRACER)
    ax.text(0.51, 0.58, "WORKFLOW COMPARISON: CURRENT VS MARIS-TRACER", fontsize=10, fontweight='bold', color=NAVY)
    
    wf_box = patches.FancyBboxPatch((0.51, 0.05), 0.47, 0.48, boxstyle="round,pad=0.01,rounding_size=0.02",
                                     facecolor=CARD_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(wf_box)
    
    curr_wf = (
        "CURRENT WORKFLOW (Analyst-Driven Manual Screening):\n"
        "  Satellite Alert ──► Manual Slick Screening ──► Unlinked AIS Data\n"
        "  • High manual delay (hours to days) | Detection isolated from attribution\n\n"
        "MARIS-TRACER (Decision Support System):\n"
        "  SAR Ingestion ──► Deep U-Net ──► 4D Drift ──► AIS Spatiotemporal Match\n"
        "  • Automated pipeline | Output: Ranked Vessel Candidates with Score %"
    )
    ax.text(0.53, 0.28, curr_wf, fontsize=8.5, color=TEXT_DARK, va='center', linespacing=1.35)

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
    mvp_box = patches.FancyBboxPatch((0.02, 0.52), 0.46, 0.38, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#F0FDF4', edgecolor=GREEN_MVP, linewidth=2)
    ax.add_patch(mvp_box)
    ax.text(0.04, 0.85, "HACKATHON MVP (36-Hour Core - MUST WORK)", fontsize=10, fontweight='bold', color=GREEN_MVP)
    mvp_items = (
        "• Sentinel-1 GRD SAR Ingestion + SNAP Speckle Filter\n"
        "• PyTorch U-Net Deep Learning Slick Segmentation\n"
        "• 2D/3D Backward Particle Drift (ERA5 + INCOIS Currents)\n"
        "• Spatiotemporal AIS Trajectory Bounding Query (PostGIS)\n"
        "• Explainable Proximity Ranking + Interactive GIS Dashboard"
    )
    ax.text(0.04, 0.67, mvp_items, fontsize=8.5, color=TEXT_DARK, va='center', linespacing=1.35)
    
    # Advanced Box (Amber/Slate)
    adv_box = patches.FancyBboxPatch((0.51, 0.52), 0.47, 0.38, boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#FFFBEB', edgecolor=AMBER, linewidth=1.5)
    ax.add_patch(adv_box)
    ax.text(0.53, 0.85, "ADVANCED PHASE (Post-Hackathon / If Time Permits)", fontsize=10, fontweight='bold', color=AMBER)
    adv_items = (
        "• Bi-Temporal OSCD Change Detection & Multi-sensor Fusion\n"
        "• 10,000 Particle Monte Carlo Ensemble Dispersion\n"
        "• Dark-Ship Kinematic Dead Reckoning & Wake Detection\n"
        "• Automated PDF Forensic Evidence Report Generation\n"
        "• Real-Time Live NMEA/AIS Stream Parser Integration"
    )
    ax.text(0.53, 0.67, adv_items, fontsize=8.5, color=TEXT_DARK, va='center', linespacing=1.35)

    # Bottom Section: Team Expertise & Role Allocation Matrix
    ax.text(0.02, 0.45, "TEAM EXPERTISE & MODULE OWNERSHIP MATRIX", fontsize=10, fontweight='bold', color=NAVY)
    
    table_box = patches.FancyBboxPatch((0.02, 0.05), 0.96, 0.36, boxstyle="round,pad=0.01,rounding_size=0.02",
                                        facecolor=CARD_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(table_box)
    
    # Header Row
    ax.fill_between([0.02, 0.98], [0.35, 0.35], [0.41, 0.41], color=NAVY)
    ax.text(0.04, 0.38, "Role / Expertise", fontsize=9, fontweight='bold', color='white', va='center')
    ax.text(0.25, 0.38, "Primary Responsibility", fontsize=9, fontweight='bold', color='white', va='center')
    ax.text(0.58, 0.38, "Tech Stack & Core Deliverable", fontsize=9, fontweight='bold', color='white', va='center')
    ax.text(0.85, 0.38, "Hackathon Owner", fontsize=9, fontweight='bold', color='white', va='center')
    
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
    
    data_box = patches.FancyBboxPatch((0.02, 0.52), 0.46, 0.38, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=CYAN, linewidth=1.5)
    ax.add_patch(data_box)
    
    data_content = (
        "REAL / PUBLIC OPEN-ACCESS FEEDS:\n"
        "• Sentinel-1 SAR GRD (ESA Copernicus API)\n"
        "• ERA5 Hourly 10m Surface Winds (ECMWF CDS)\n"
        "• INCOIS OSFS Daily Surface Current Velocity Grids\n\n"
        "DEMONSTRATION FALLBACK STRATEGY:\n"
        "• Public/Historical AIS Datasets (NOAA MarineCadastre / GFW)\n"
        "• Synthetic AIS Vessel Trajectory Generator (for live testing)\n"
        "► Ensures 100% reliable 36-hr hackathon prototype demo."
    )
    ax.text(0.04, 0.70, data_content, fontsize=8.5, color=TEXT_DARK, va='center', linespacing=1.35)

    # Top Right: Deployment Strategy Box
    ax.text(0.51, 0.94, "DEPLOYMENT & HARDWARE REQUIREMENTS", fontsize=11, fontweight='bold', color=NAVY)
    
    deploy_box = patches.FancyBboxPatch((0.51, 0.52), 0.47, 0.38, boxstyle="round,pad=0.01,rounding_size=0.02",
                                         facecolor=CARD_BG, edgecolor=TEAL, linewidth=1.5)
    ax.add_patch(deploy_box)
    
    deploy_content = (
        "ZERO VESSEL HARDWARE REQUIRED:\n"
        "• Operates entirely via remote satellite sensing and AIS.\n"
        "• No physical sensors or equipment installed on vessels.\n\n"
        "COMPUTE & HOSTING STACK:\n"
        "• Single workstation / cloud instance with NVIDIA GPU.\n"
        "• 1-Click Docker Compose deployment containerizing:\n"
        "  FastAPI Backend + PostgreSQL/PostGIS + React WebGIS UI."
    )
    ax.text(0.53, 0.70, deploy_content, fontsize=8.5, color=TEXT_DARK, va='center', linespacing=1.35)

    # Bottom: Risk & Mitigation Cards
    ax.text(0.02, 0.45, "KEY TECHNICAL RISKS & PRACTICAL MITIGATION STRATEGIES", fontsize=10, fontweight='bold', color=NAVY)
    
    risks = [
        ("RISK 1: Look-Alike Slicks", "Algae, biogenic films, and low-wind areas dampen radar waves like oil.", "Dual-Pol VV/VH ratio + GLCM texture entropy + ERA5 wind speed gating (> 2 m/s).", AMBER),
        ("RISK 2: Dark Ships (No AIS)", "Perpetrators disable AIS transponders (~6% of global fleet).", "Kinematic dead reckoning from past waypoints + SAR vessel target detection.", AMBER),
        ("RISK 3: Hydrodynamic Drift Error", "Ocean current turbulence and wind gust forecasting inaccuracies.", "Multi-particle Monte Carlo ensemble deriving a probabilistic 95% origin region.", TEAL)
    ]
    
    for i, (title, desc, mit, color) in enumerate(risks):
        x = 0.02 + i * 0.325
        y = 0.05
        w = 0.30
        h = 0.36
        
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=color, linewidth=1.5)
        ax.add_patch(card)
        
        ax.text(x + 0.015, y + h - 0.04, title, fontsize=9, fontweight='bold', color=color)
        ax.text(x + 0.015, y + h - 0.12, f"Challenge: {desc}", fontsize=7.5, color=TEXT_DARK, va='top', wrap=True)
        
        mit_rect = patches.Rectangle((x + 0.01, y + 0.015), w - 0.02, 0.14, facecolor='#F1F5F9', edgecolor='none')
        ax.add_patch(mit_rect)
        ax.text(x + 0.02, y + 0.08, f"Mitigation: {mit}", fontsize=7.5, fontweight='bold', color=NAVY, va='center')

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
    
    demo_box = patches.FancyBboxPatch((0.02, 0.44), 0.52, 0.46, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=CYAN, linewidth=1.5)
    ax.add_patch(demo_box)
    
    steps = [
        "1. Ingest Sentinel-1 SAR Scene",
        "2. U-Net Segmentation (Slick Mask)",
        "3. 4D Backward Particle Drift",
        "4. 95% Origin Region Boundary",
        "5. Spatiotemporal AIS Candidate Search",
        "6. Ranked Vessel List + Evidence Report"
    ]
    
    for i, step in enumerate(steps):
        col = i % 2
        row = i // 2
        sx = 0.04 + col * 0.24
        sy = 0.76 - row * 0.12
        
        sbox = patches.FancyBboxPatch((sx, sy), 0.22, 0.09, boxstyle="round,pad=0.005,rounding_size=0.01",
                                       facecolor='#F0F9FF', edgecolor=CYAN, linewidth=1)
        ax.add_patch(sbox)
        ax.text(sx + 0.11, sy + 0.045, step, fontsize=7.5, fontweight='bold', color=NAVY, ha='center', va='center')

    # Top Right: Target Evaluation Metrics Table
    ax.text(0.56, 0.94, "EVALUATION PLAN & TARGET METRICS", fontsize=11, fontweight='bold', color=NAVY)
    
    eval_box = patches.FancyBboxPatch((0.56, 0.44), 0.42, 0.46, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=GREEN_MVP, linewidth=1.5)
    ax.add_patch(eval_box)
    
    ax.fill_between([0.565, 0.975], [0.82, 0.82], [0.87, 0.87], color=GREEN_MVP)
    ax.text(0.58, 0.845, "Module", fontsize=8.5, fontweight='bold', color='white', va='center')
    ax.text(0.76, 0.845, "Target Metric", fontsize=8.5, fontweight='bold', color='white', va='center')
    ax.text(0.89, 0.845, "Target Goal", fontsize=8.5, fontweight='bold', color='white', va='center')
    
    metrics = [
        ("Slick Segmentation", "Dice / mIoU", "≥ 0.78"),
        ("Look-Alike Rejection", "False Positive Rate", "≤ 12%"),
        ("Origin Drift Error", "Median Error Distance", "≤ 4.5 km"),
        ("Vessel Attribution", "Top-3 Recall", "≥ 85%")
    ]
    for i, (mod, met, val) in enumerate(metrics):
        y_p = 0.76 - i * 0.075
        ax.text(0.58, y_p, mod, fontsize=8, color=TEXT_DARK, va='center')
        ax.text(0.76, y_p, met, fontsize=8, color=TEXT_MUTED, va='center')
        ax.text(0.89, y_p, val, fontsize=8, fontweight='bold', color=GREEN_MVP, va='center')

    # Bottom: Multi-Dimensional Benefits
    ax.text(0.02, 0.38, "MULTI-DIMENSIONAL STRATEGIC BENEFITS", fontsize=10, fontweight='bold', color=NAVY)
    
    benefits = [
        ("ENVIRONMENTAL IMPACT", "Accelerates spill containment boom deployment, protecting sensitive coastal ecosystems & mangroves.", GREEN_MVP),
        ("OPERATIONAL EFFICIENCY", "Replaces hours of manual screening with automated candidate ranking in under 3 minutes.", CYAN),
        ("ENFORCEMENT PRIORITIZATION", "Provides decision support for Coast Guard / NTRO to prioritize vessel inspections.", TEAL)
    ]
    
    for i, (title, desc, color) in enumerate(benefits):
        x = 0.02 + i * 0.325
        y = 0.05
        w = 0.30
        h = 0.28
        
        bcard = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                        facecolor=CARD_BG, edgecolor=color, linewidth=1.5)
        ax.add_patch(bcard)
        ax.text(x + 0.015, y + h - 0.04, title, fontsize=8.5, fontweight='bold', color=color)
        ax.text(x + 0.015, y + 0.08, desc, fontsize=7.5, color=TEXT_DARK, va='top', wrap=True)

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
            "• Lai et al. (2024). Deep Learning for SAR Oil Spill Segmentation & Bi-Temporal OSCD Change Detection. IEEE TGRS.",
            "• Chen et al. (2023). DGNet: Distribution-Guided SAR Feature Extraction for Marine Pollution. IEEE TGRS.",
            "• Moon et al. (2024). DAKTer Diffusion Augmentation for SAR Slick Segmentation. arXiv:2412.08116."
        ], CYAN),
        ("2. HYDRODYNAMICS & LAGRANGIAN DRIFT", [
            "• Dagestad et al. (2018). OpenDrift: Open-source Python Framework for Ocean Trajectory Modeling. Geoscientific Model Dev.",
            "• NOAA Office of Response & Restoration (2023). PyGNOME: Operational Oil Spill Modeling Environment.",
            "• Stokes Drift & Wind Leeway Formulations for Surface Pollutant Backtracking in Coastal Waters."
        ], TEAL),
        ("3. MARITIME LAW & GOVERNANCE", [
            "• IMO (2024). MARPOL Annex I: Regulations for Prevention of Pollution by Oil. International Maritime Organization.",
            "• UNCLOS Part XII (1982). Protection and Preservation of the Marine Environment. United Nations.",
            "• EMSA (2023). CleanSeaNet Satellite Monitoring Service for Maritime Oil Spill Detection in European Waters."
        ], AMBER),
        ("4. NATIONAL DATA & STRATEGIC ASSETS", [
            "• INCOIS (MoES, Govt. of India). Ocean State Forecast System (OSFS) High-Resolution Ocean Currents.",
            "• ESA Copernicus Open Access Hub. Sentinel-1 Synthetic Aperture Radar (SAR) Level-1 GRD Data.",
            "• NOAA / MarineCadastre & Global Fishing Watch. Historic AIS Vessel Tracking Datasets."
        ], GREEN_MVP)
    ]
    
    for i, (title, points, color) in enumerate(ref_cats):
        col = i % 2
        row = i // 2
        x = 0.02 + col * 0.49
        y = 0.50 - row * 0.44
        w = 0.47
        h = 0.39
        
        rcard = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                       facecolor=CARD_BG, edgecolor=color, linewidth=1.5)
        ax.add_patch(rcard)
        
        # Title bar
        rtitle = patches.FancyBboxPatch((x, y + h - 0.07), w, 0.07, boxstyle="round,pad=0,rounding_size=0.01",
                                         facecolor=color, edgecolor='none')
        ax.add_patch(rtitle)
        ax.text(x + 0.02, y + h - 0.035, title, fontsize=9, fontweight='bold', color='white', va='center')
        
        # Content points
        p_text = "\n".join(points)
        ax.text(x + 0.02, y + 0.14, p_text, fontsize=7.5, color=TEXT_DARK, va='center', linespacing=1.4)

    plt.tight_layout()
    plt.savefig('slide_assets/slide6_diagram.png', bbox_inches='tight', facecolor=BG_LIGHT)
    plt.close()

# Generate all 5 slide diagrams
generate_slide2_diagram()
generate_slide3_diagram()
generate_slide4_diagram()
generate_slide5_diagram()
generate_slide6_diagram()

print("All slide diagrams generated in slide_assets/")
