from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import json
def create_pdf(departments,type,laboratory_examination="result",image_examination="findings"):
    report_type=f"{laboratory_examination}_{image_examination}"
    for department in departments:
        with open(f"{department}_{type}_{report_type}.json", "r") as file:
            data = json.load(file)
            
            print(data)
            pdf_file = f"{department}_{type}_{report_type}.pdf"
            doc = SimpleDocTemplate(pdf_file, pagesize=A4)

            # Define a style for the document
            styles = getSampleStyleSheet()
            style_normal = styles["Normal"]

            # Container for the 'Flowable' objects (Paragraphs, Spacers, etc.)
            content = []

            # Loop through the dictionary and add content to the PDF
            for key, sub_dict in data.items():
                # Add the main key
                content.append(Paragraph(f"Key: {key}", style_normal))
                content.append(Spacer(1, 0.2 * inch))  # Add some space

                # Add each sub-key and its corresponding text
                for sub_key, text in sub_dict.items():
                    content.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{sub_key}: {text}", style_normal))
                    content.append(Spacer(1, 0.1 * inch))  # Add some space

                # Add a page break after each key
                content.append(PageBreak())

            # Build the PDF
            doc.build(content)

            print(f"PDF generated successfully at {pdf_file}!")