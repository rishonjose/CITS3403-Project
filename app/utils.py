import re
from pdfminer.high_level import extract_text

def parse_pdf_bill(path):
    """
    Returns a dict with keys: category, units, cost, start_date, end_date.
    Adjust the regexes to match your bill’s layout!
    """
    text = extract_text(path)

    # crude examples—tweak to your PDFs
    units_match = re.search(r"Consumed[:\s]+([\d,\.]+)", text)
    cost_match  = re.search(r"Cost[:\s]+\$?([\d,\.]+)", text)
    period_match = re.search(
        r"Period\s+(\d{4}-\d{2}-\d{2})\s*to\s*(\d{4}-\d{2}-\d{2})",
        text
    )

    return {
        "units":       float(units_match.group(1).replace(',','')) if units_match else None,
        "cost":        float(cost_match.group(1))                        if cost_match  else None,
        "start_date":  period_match.group(1)                             if period_match else None,
        "end_date":    period_match.group(2)                             if period_match else None,
    }
