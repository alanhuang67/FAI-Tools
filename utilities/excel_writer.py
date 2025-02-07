from openpyxl.styles import Alignment

def set_wrap_text(writer, align_top=True):
    for sheet_name in writer.sheets:
        ws = writer.sheets[sheet_name]
        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrapText=True, vertical="top" if align_top else "center")
