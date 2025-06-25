from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "WhatsApp Chat Analysis Report", ln=True, align="C")

    def add_section(self, title):
        self.set_font("Arial", "B", 12)
        self.ln(10)
        self.cell(0, 10, title, ln=True)

    def add_text(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 10, text)

    def add_image(self, path, width=180):
        self.image(path, w=width)

def save_plot_as_image(fig, filename):
    fig.savefig(filename, bbox_inches="tight")

def generate_pdf_report(plots, stats_text, output_path="report.pdf"):
    pdf = PDFReport()
    pdf.add_page()

    pdf.add_section("Summary")
    pdf.add_text(stats_text)

    for title, img in plots:
        pdf.add_section(title)
        pdf.add_image(img)

    pdf.output(output_path)
    return output_path
