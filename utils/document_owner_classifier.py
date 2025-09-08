import re

def get_patient_name_from_test_report(text):
    """
    Extracts the patient's name from a medical test report using regex.
    Prioritized patterns: "Patient Name:", "Name:", followed by the patient's name.
    """
    patterns = [
        r"Patient Name\n(.*?)\n",
        r"Patient Name(?:\s*:,|\s*:\s)(.*?)\n",
        r"Name(?:\s*:,|\s*:\s)(.*?)\n",
        r"Name\s*:\s*(.*?)\n"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ''

def get_patient_name_from_invoice(text):
    """
    Extracts the patient's name from an invoice using regex.
    Prioritized patterns: "Patient Name:", "Patient:", followed by the patient's name.
    """
    patterns = [
        r"Patient Name(?:\s*:,|\s*:\s)(.*?)\n",
        r"Patient(?:\s*:,|\s*:\s)(.*?)\n",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    # Special case for "M" on the invoice
    match = re.search(r"M\s*([A-Z][a-z]+ [A-Z][a-z]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ''

def get_patient_name_from_insurance(text):
    """
    Extracts the insured person's name from an insurance document using regex.
    Prioritized patterns: "Insured Person:", "Name:", "Patient Name:", followed by the name.
    """
    patterns = [
        r"Insured Person(?:\s*:,|\s*:\s)(.*?)\n",
        r"Name(?:\s*:,|\s*:\s)(.*?)\n",
        r"Patient Name(?:\s*:,|\s*:\s)(.*?)\n",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ''

def get_patient_name_from_discharge_summary(text):
    """
    Extracts the patient's name from a discharge summary using regex.
    Prioritized patterns: "Patient Name:", "Name:", followed by the patient's name.
    """
    patterns = [
        r"Patient Name(?:\s*:,|\s*:\s)(.*?)\n",
        r"Name(?:\s*:,|\s*:\s)(.*?)\n"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ''

def get_patient_name_from_other_document(text):
    """
    Extracts a name from a general document. This is a fallback function.
    It looks for patterns like "Patient Name:", "Insured Person:", "Name:", etc.
    """
    patterns = [
        r"Patient Name(?:\s*:,|\s*:\s)(.*?)\n",
        r"Insured Person(?:\s*:,|\s*:\s)(.*?)\n",
        r"Name(?:\s*:,|\s*:\s)(.*?)\n",
        r"Patient(?:\s*:,|\s*:\s)(.*?)\n"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ''
