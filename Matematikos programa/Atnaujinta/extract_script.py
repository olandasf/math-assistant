"""Extract text from all curriculum PDF files for analysis."""
import pdfplumber
import os

pdf_dir = r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta"
output_file = r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\extracted_text.txt"

with open(output_file, 'w', encoding='utf-8') as out:
    for pdf_file in sorted(os.listdir(pdf_dir)):
        if not pdf_file.endswith('.pdf'):
            continue
        
        filepath = os.path.join(pdf_dir, pdf_file)
        out.write(f"\n{'='*80}\n")
        out.write(f"FILE: {pdf_file}\n")
        out.write(f"{'='*80}\n")
        
        try:
            with pdfplumber.open(filepath) as pdf:
                out.write(f"Pages: {len(pdf.pages)}\n")
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        out.write(f"\n--- Page {i+1} ---\n")
                        out.write(text[:5000] + "\n")
                    
                    tables = page.extract_tables()
                    if tables:
                        out.write(f"\n  [Tables on page {i+1}: {len(tables)}]\n")
                        for j, table in enumerate(tables):
                            if table:
                                out.write(f"  Table {j+1} ({len(table)} rows):\n")
                                for row_num, row in enumerate(table[:8]):
                                    out.write(f"    R{row_num}: {row}\n")
                                if len(table) > 8:
                                    out.write(f"    ... ({len(table)-8} more rows)\n")
        except Exception as e:
            out.write(f"  ERROR: {e}\n")

print(f"Done. Output: {output_file}")
