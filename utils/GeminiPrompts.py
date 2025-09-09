
GEMINI_EXTRACT_DETAILS_PROMPT_TEMPLATE = """
You are an expert medical document analyzer
Your task has two steps:
### 1. Domain Check (MANDATORY and STRICT):
- First decide if the document is related to the healthcare/medical domain.  
- A document is **medical** if it relates to: hospitals, doctors, prescriptions, medications, lab tests, diagnostic scans, discharge summaries, vaccinations, medical invoices, or health/medical insurance.  
- A document is **non_medical** if it relates to: restaurants, shopping, travel, vehicle/home insurance, bank statements, retail receipts, utility bills, or anything outside healthcare.  
- Returning "unknown" or "unidentified" is **not allowed**.  
- If the document is medical, go to Step 2. If not, classify as `"non_medical"`.

### 2. Bucket Classification (STRICT):
If the document is medical, classify it into exactly **one** of these buckets:  
["test_report","medications","insurance","invoice","vaccinations","discharge_summary","scans","other"]

#### Explicit Rules:  
- **test_report** → Pathology and functional tests: blood, urine, stool, biopsy, histopathology, ECG, Echo, TMT, Holter, lab reports.   
- **medications** → Prescriptions or medicine lists (look for Rx, prescribed by, dosage, tablet, syrup, capsule).   
- **insurance** → Health/medical insurance documents (policy no, insured person, insurance company).  
- **invoice** → Any billing, receipt, payment record from hospital, clinic, pharmacy, or lab (look for words like "Bill No", "Invoice", "Receipt", "Gross Total", "Grand Total", "Amount").
- **vaccinations** → Immunization records (vaccine name, dose, booster, immunization card).  
- **discharge_summary** → Hospital discharge documents (look for "Admission Date", "Discharge Date", hospital name, diagnosis on discharge).
- **scans** → Imaging/radiology: MRI, CT, X-ray, PET, Ultrasound, Doppler, Mammogram.
- **other** → Only use if the document is medical but does not fit any above (e.g., admission notes, consent forms, procedure preparation sheets).

**Strict rule:**  
The `"document_bucket"` must always be one of:  
["test_report","medications","insurance","invoice","vaccinations","discharge_summary","scans","other","non_medical"]  
Do not output `"unknown"`, `"unidentified"`, or any other label.


Based on the bucket, I want to extract its details as follows in the given JSON format:
test_report:
{{
  "report_details": {{
    "patient_name": "string",
    "patient_age": "string",
    "patient_gender": "string",
    "report_name": "string",
    "report_date": "string (format: DD-MMM-YY HH24:mm:ss)",
    "collection_date": "string (format: DD-MMM-YY HH24:mm:ss)",
    "lab_name": "string",
    "lab_id": "string",
    "lab_location": "string",
    "lab_contact_number": "string"
  }},
  "tests": [
    {{
      "test_name": "string",
      "interpretation": "string or null",
      "components": [
        {{
          "test_component_name": "string",
          "result_value": "string",
          "units": "string or null",
          "reference_range": {{ "min": "string or 0", "max": "string or 0" }},
          "biological_reference_description": "string",
          "status": "high / low / normal / null"
        }}
      ]
    }}
  ]
}}
- If `reference_range` is missing or not present, do not return `null`. Instead, return:
`"reference_range": {{ "min": "0", "max": "0" }}`
- The "result_value" and "reference_range" can also be a word instead of a number — identify and extract accordingly. Try to populate the "reference_range" in such cases, but default to min/max 0/0 if not available.
- Additional instructions for computing "status":
    - If reference range is of format `> X`, set `"min": X`, `"max": null`. If result < X, status = "low". If result ≥ X, status = "normal".
    - If reference range is `< X`, set `"min": null`, `"max": X`. If result > X, status = "high". If result ≤ X, status = "normal".
    - If range is like `X - Y`, split it and compare accordingly.
    - If any value is non-numeric (e.g., "Normal", "Absent", "Occasional"), retain it as is and set `"status": null`.
    - If comparison isn't possible due to missing or incompatible values, set `"status": null".
    - If result_value, min, and max are numeric and comparable, compare result_value with min and max.
    - If result_value is greater than max, status is "high".
    - If result_value is less than min, status is "low".
    - If result_value is between min and max, status is "normal".
    - If result_value, min, or max are missing or non-numeric, status is null.
    - If a test has multiple reference values for different conditions or populations (e.g., Normal, Therapy, High Dose), return the entire text block as a **string** under "biological_reference_description".
    - "%" should be considered as Unit if present.

medications:
{{
  "prescribed_by": "string",
  "clinic_address":"string",
  "email_id":"string",
  "contact_number":"string",
  "prescription_name": "string",
  "description": "string",
  "prescription_date": "string (format: DD-MMM-YY HH24:mm:ss)",
  "prescription_attachment_url": "string (leave empty if not provided)",
  "patient_name": "string",
  "prescription_details": [
    {{
      "medicine_name": "string",
      "prescription_type": "string (Tablet/Syrup etc)",
      "dose_quantity": "number",
      "duration": "number (days)",
      "unit_value": "number",
      "unit_type": "string (mg/ml etc)",
      "frequency": "number (times per day)",
      "times_per_day": "number",
      "interval_hour": "number",
      "instruction": "string"
    }}
  ]
}}

insurance:
{{
  "policy_no": "string",
  "insured_person":"string",
  "insurance_company":"string"
}}

invoice:
{{
  "invoice_no": "string",
  "billing_date":"string",
  "biller_name":"string",
  "final_payable_amt":"string"
}}

discharge_summary:
{{
  "hospital_name":"string",
  "admission_date":"string",
  "discharge_date":"string"
}}

scans:
{{
  "scan_type":"string"
}}

Also, my family members are: {relatives_string}
So based on the document owner you identified, do a near match to know whose document this is.
When determining "near_matched_with":
- A near match means the document owner's name and a family member's name
  clearly refer to the same person, even if written differently.
  Valid differences include:
  • Use of initials instead of full names
  • Spelling variations
  • Missing or additional middle names
  • Presence or absence of honorifics/titles (Mr., Mrs., Dr., etc.)
- A near match is NOT valid if the overlap is only partial
  (e.g., only the first name matches, or only the last name matches,
  or a middle name coincidentally overlaps).
  Different individuals who merely share part of their names
  must NOT be considered a near match.
- To be considered a near match, both the first and last components
  (allowing for initials/abbreviations/spelling variants) must align
  strongly enough to indicate the same identity.
- If no family member meets this stricter criterion,
  return `"near_matched_with": null`.

### Output Format
At the end, I want everything returned in the following JSON format:
{{
  "document_bucket":"string", // document type you identified, must be one of the allowed values
  "document_owner":"string", // name of person to whom this document belongs, otherwise null
  "document_details": {{...}}, // here goes the details you extracted based on the document bucket. `null` in case no details were extracted
  "near_matched_with": {{
    "name":"string",
    "user_id":"number"
  }} // name of family member that near matched with. In case it's not matching with any family member, return null.
  "summary":"string" // this will contain reason for choosing specific bucket, why chosen document owner and reason for near match
}}
Strict Rules
 Do not return anything extra and make sure you return valid json.
 Choose exactly one bucket from this list: ["test_report", "medications", "insurance", "invoice", "vaccinations", "discharge_summary", "scans", "other", "non_medical"]
 Do not return "unknown", "unidentified", or any custom category outside this list.
"""

GEMINI_EXTRACT_TEST_REPORT_DETAILS_PROMPT_TEMPLATE = """
You are an expert medical document analyzer
I have shared test report with you, I want to extract its details as follows in the given JSON format:

{{
  "report_details": {{
    "patient_name": "string",
    "patient_age": "string",
    "patient_gender": "string",
    "report_name": "string",
    "report_date": "string (format: DD-MMM-YY HH24:mm:ss)",
    "collection_date": "string (format: DD-MMM-YY HH24:mm:ss)",
    "lab_name": "string",
    "lab_id": "string",
    "lab_location": "string",
    "lab_contact_number": "string"
  }},
  "tests": [
    {{
      "test_name": "string",
      "interpretation": "string or null",
      "components": [
        {{
          "test_component_name": "string",
          "result_value": "string",
          "units": "string or null",
          "reference_range": {{ "min": "string or 0", "max": "string or 0" }},
          "biological_reference_description": "string",
          "status": "high / low / normal / null"
        }}
      ]
    }}
  ]
}}
- If `reference_range` is missing or not present, do not return `null`. Instead, return:
`"reference_range": {{ "min": "0", "max": "0" }}`
- The "result_value" and "reference_range" can also be a word instead of a number — identify and extract accordingly. Try to populate the "reference_range" in such cases, but default to min/max 0/0 if not available.
- Additional instructions for computing "status":
    - If reference range is of format `> X`, set `"min": X`, `"max": null`. If result < X, status = "low". If result ≥ X, status = "normal".
    - If reference range is `< X`, set `"min": null`, `"max": X`. If result > X, status = "high". If result ≤ X, status = "normal".
    - If range is like `X - Y`, split it and compare accordingly.
    - If any value is non-numeric (e.g., "Normal", "Absent", "Occasional"), retain it as is and set `"status": null`.
    - If comparison isn't possible due to missing or incompatible values, set `"status": null".
    - If result_value, min, and max are numeric and comparable, compare result_value with min and max.
    - If result_value is greater than max, status is "high".
    - If result_value is less than min, status is "low".
    - If result_value is between min and max, status is "normal".
    - If result_value, min, or max are missing or non-numeric, status is null.
    - If a test has multiple reference values for different conditions or populations (e.g., Normal, Therapy, High Dose), return the entire text block as a **string** under "biological_reference_description".
    - "%" should be considered as Unit if present.

Also, my family members are: {relatives_string}
So based on the document owner you identified, do a near match to know whose document this is.
When determining "near_matched_with":
- A near match means the document owner's name and a family member's name
  clearly refer to the same person, even if written differently.
  Valid differences include:
  • Use of initials instead of full names
  • Spelling variations
  • Missing or additional middle names
  • Presence or absence of honorifics/titles (Mr., Mrs., Dr., etc.)
- A near match is NOT valid if the overlap is only partial
  (e.g., only the first name matches, or only the last name matches,
  or a middle name coincidentally overlaps).
  Different individuals who merely share part of their names
  must NOT be considered a near match.
- To be considered a near match, both the first and last components
  (allowing for initials/abbreviations/spelling variants) must align
  strongly enough to indicate the same identity.
- If no family member meets this stricter criterion,
  return `"near_matched_with": null`.

At the end, I want everything returned in the following JSON format:
{{
  "document_owner":"string", // name of person to whom this document belongs
  "document_details": {{...}}, // here goes the details you extracted. `null` in case no details were extracted
  "near_matched_with": {{
    "name":"string",
    "user_id":"number"
  }} // name of family member that near matched with. In case it's not matching with any family member, return null.
  "summary":"string" // this will contain reason for choosing document owner and reason for near match
}}
Do not return anything extra and make sure you return valid json.
"""

GEMINI_EXTRACT_INVOICE_DETAILS_PROMPT_TEMPLATE = """
You are an expert medical document analyzer

I have shared test report with you, I want to extract its details as follows in the given JSON format:
invoice:
{{
  "invoice_no": "string",
  "billing_date":"string",
  "biller_name":"string",
  "final_payable_amt":"string"
}}

Also, my family members are: {relatives_string}
So based on the document owner you identified, do a near match to know whose document this is.
When determining "near_matched_with":
- A near match means the document owner's name and a family member's name
  clearly refer to the same person, even if written differently.
  Valid differences include:
  • Use of initials instead of full names
  • Spelling variations
  • Missing or additional middle names
  • Presence or absence of honorifics/titles (Mr., Mrs., Dr., etc.)
- A near match is NOT valid if the overlap is only partial
  (e.g., only the first name matches, or only the last name matches,
  or a middle name coincidentally overlaps).
  Different individuals who merely share part of their names
  must NOT be considered a near match.
- To be considered a near match, both the first and last components
  (allowing for initials/abbreviations/spelling variants) must align
  strongly enough to indicate the same identity.
- If no family member meets this stricter criterion,
  return `"near_matched_with": null`.

At the end, I want everything returned in the following JSON format:
{{
  "document_owner":"string", // name of person to whom this document belongs
  "document_details": {{...}}, // here goes the details you extracted. `null` in case no details were extracted
  "near_matched_with": {{
    "name":"string",
    "user_id":"number"
  }} // name of family member that near matched with. In case it's not matching with any family member, return null.
  "summary":"string" // this will contain reason for choosing document owner and reason for near match
}}
Do not return anything extra and make sure you return valid json.
"""

GEMINI_EXTRACT_PASSWORD_PROMPT_TEMPLATE = """
You are given some text. Your task is to identify a PDF password in it. 
Rules:
- If you find one or more possible passwords, output exactly ONE password (choose the first if multiple).
- Output ONLY the password string, with no quotes, no extra words, no formatting.
- If no password is found, output exactly: NOT_FOUND

Text: {raw_text}

"""