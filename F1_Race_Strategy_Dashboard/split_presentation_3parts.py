import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

MASTER_PPTX = "G:/DAV/F1_Race_Strategy_Dashboard/F1_Data_Analytics_and_Visualization_Presentation.pptx"
PART1_PPTX = "G:/DAV/F1_Race_Strategy_Dashboard/F1_Presentation_Part1_Data_Engineering.pptx"
PART2_PPTX = "G:/DAV/F1_Race_Strategy_Dashboard/F1_Presentation_Part2_Visual_Analytics.pptx"
PART3_PPTX = "G:/DAV/F1_Race_Strategy_Dashboard/F1_Presentation_Part3_Telemetry_and_Quality.pptx"

def create_subset_presentation(src_path, dest_path, keep_slide_indices, part_title, presenter_name="Team Member"):
    """
    Creates a dedicated standalone presentation containing only the selected slides,
    with an updated title slide tailored for that specific part.
    """
    prs = Presentation(src_path)
    
    # Identify slides to remove (all indices NOT in keep_slide_indices)
    total_slides = len(prs.slides)
    slides_to_remove = [i for i in range(total_slides) if i not in keep_slide_indices]
    
    # Remove from end to beginning so indices don't shift
    for idx in sorted(slides_to_remove, reverse=True):
        rId = prs.slides._sldIdLst[idx].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[idx]
        
    print(f"Created {os.path.basename(dest_path)} with {len(prs.slides)} slides.")
    
    # If the first slide is the title slide, customize the presenter attribution
    title_slide = prs.slides[0]
    for sh in title_slide.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if "PROJECT DOMAIN" in txt:
                sh.text_frame.text = f"PROJECT DOMAIN  •  {part_title.upper()}"
            elif "Team members:" in txt:
                sh.text_frame.text = f"Lead Presenter: {presenter_name}  |  Team: Member 1 • Member 2 • Member 3"
                
    prs.save(dest_path)

def add_part_headers_to_master(src_path):
    """
    Updates the master deck so that every slide explicitly displays which Part (1, 2, or 3)
    and Presenter it belongs to in the top category tag.
    """
    prs = Presentation(src_path)
    
    part_mapping = {
        1: ("[PART 1/3: DATA ENGINEERING]", "Presenter: Member 1"),
        2: ("[PART 1/3: DATA ENGINEERING]", "Presenter: Member 1"),
        3: ("[PART 1/3: DATA ENGINEERING]", "Presenter: Member 1"),
        4: ("[PART 1/3: DATA ENGINEERING]", "Presenter: Member 1"),
        5: ("[PART 1/3: DATA ENGINEERING]", "Presenter: Member 1"),
        6: ("[PART 2/3: VISUAL ANALYTICS & STRATEGY]", "Presenter: Member 2"),
        7: ("[PART 2/3: VISUAL ANALYTICS & STRATEGY]", "Presenter: Member 2"),
        8: ("[PART 2/3: VISUAL ANALYTICS & STRATEGY]", "Presenter: Member 2"),
        9: ("[PART 2/3: VISUAL ANALYTICS & STRATEGY]", "Presenter: Member 2"),
        10: ("[PART 2/3: VISUAL ANALYTICS & STRATEGY]", "Presenter: Member 2"),
        11: ("[PART 3/3: TELEMETRY & DATA QUALITY]", "Presenter: Member 3"),
        12: ("[PART 3/3: TELEMETRY & DATA QUALITY]", "Presenter: Member 3"),
        13: ("[PART 3/3: TELEMETRY & DATA QUALITY]", "Presenter: Member 3"),
        14: ("[PART 3/3: TELEMETRY & DATA QUALITY]", "Presenter: Member 3"),
        15: ("[PART 3/3: TELEMETRY & DATA QUALITY]", "Presenter: Member 3"),
    }
    
    for idx, s in enumerate(prs.slides):
        slide_num = idx + 1
        if slide_num in part_mapping and slide_num > 1:
            part_tag, presenter = part_mapping[slide_num]
            for sh in s.shapes:
                if sh.has_text_frame:
                    # Update top red header tag
                    if 0.1 < sh.left.inches < 1.0 and 0.15 < sh.top.inches < 0.45:
                        orig = sh.text_frame.text.strip()
                        if not orig.startswith("[PART"):
                            sh.text_frame.text = f"{part_tag} • {orig}"
                            if sh.text_frame.paragraphs and sh.text_frame.paragraphs[0].runs:
                                sh.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xE1, 0x06, 0x00)
                                sh.text_frame.paragraphs[0].runs[0].font.size = Pt(9.5)
                                
    prs.save(src_path)
    print("Master deck updated with Part 1, 2, 3 indicators.")

def main():
    # 1. Update master presentation with Part indicators
    add_part_headers_to_master(MASTER_PPTX)
    
    # 2. Part 1 Deck: Slides 1 to 5 (0, 1, 2, 3, 4)
    # Problem, Scope, Cleaning Pipeline, Architecture
    create_subset_presentation(
        MASTER_PPTX,
        PART1_PPTX,
        keep_slide_indices=[0, 1, 2, 3, 4],
        part_title="Part 1: Problem Definition & Data Cleaning Architecture",
        presenter_name="Member 1 (Data Engineering Lead)"
    )
    
    # 3. Part 2 Deck: Slide 1 (Title) + Slides 6 to 10 (0, 5, 6, 7, 8, 9)
    # Race Overview, Custom Graph Studio, Strategy, Tyre Degradation, Pit Stops
    create_subset_presentation(
        MASTER_PPTX,
        PART2_PPTX,
        keep_slide_indices=[0, 5, 6, 7, 8, 9],
        part_title="Part 2: Visual Analytics, Strategy Modeling & Graph Studio",
        presenter_name="Member 2 (Visual Analytics & Strategy Lead)"
    )
    
    # 4. Part 3 Deck: Slide 1 (Title) + Slides 11 to 15 (0, 10, 11, 12, 13, 14)
    # Telemetry Analysis, Driver Battles, Season Explorer, Dataset Quality, Conclusion
    create_subset_presentation(
        MASTER_PPTX,
        PART3_PPTX,
        keep_slide_indices=[0, 10, 11, 12, 13, 14],
        part_title="Part 3: 100 Hz Telemetry, Driver Performance & Governance",
        presenter_name="Member 3 (Telemetry, Quality & Architecture Lead)"
    )
    
    print("All 3 individual presentation parts and master deck generated successfully!")

if __name__ == "__main__":
    main()
