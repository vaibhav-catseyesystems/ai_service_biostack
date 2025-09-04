import re

# Weighted medical keywords
MEDICAL_KEYWORDS = {
    "patient": 2, "doctor": 2, "hospital": 1, "clinic": 2, "pathology": 2,
    "report": 3, "test": 2, "blood": 3, "lab": 3, "diagnosis": 3,
    "prescription": 4, "rx": 4, "medication": 3, "tablet": 3, "capsule": 3,
    "discharge": 4, "admission": 3, "summary": 1, 
    "insurance": 3, "policy": 2, "claim": 2, "coverage": 2,
    "vaccine": 3, "vaccination": 3, "immunization": 3, "dose": 2,
}

# Generic finance/non-medical keywords
GENERIC_FINANCE_KEYWORDS = ["bill", "invoice", "receipt", "gst", "tax", "amount"]

MANDATORY_KEYWORD_RULES = {
    "test_report": {
        "required_score": 6,
        "buckets": {
            "patient_info": {
                "keywords": [ "patient name", "patient id", "referred by", "bch.no", "refferral", "bch no"],
                "score": 3
            },
            "collection_date": {
                "keywords": [ "collected", "collection", "sample date", "smpl rcd. dt" ],
                "score": 2
            },
            "report_date": {
                "keywords": [ "reported", "printed", "reported on", "date of report" ],
                "score": 2
            },
            "units": {
                "keywords": ["mg","ml","mmol","g/dl","%","iu"],
                "score": 3
            },
            "other":{
                "keywords":["end of report"],
                "score": 3
            }
        },
    },
    "invoice": {
        "required_score": 5,
        "buckets": {
            "tax_info": {
                "keywords": [ "tax invoice", "tax", ],
                "score": 2
            },
            "amount_info": {
                "keywords": [ "total amount","gross total","grand total", "amount due", "balance", "net payable", "total bill amount" ],
                "score": 3
            },
            "invoice_meta": {
                "keywords": [ "invoice no", "bill no", "receipt no", "bill cum receipt",],
                "score": 2
            },
        },
    },
    "prescription": {
        "required_score": 5,
        "buckets": {
            "doctor_info": {
                "keywords": ["dr.","doctor","physician"],
                "score": 2
            },
            "rx_symbol": {
                "keywords": ["rx","prescription"],
                "score": 3
            },
            "medicines": {
                "keywords": ["tablet","capsule","syrup","dose"],
                "score": 2
            },
        },
    },
    "discharge_summary": {
        "required_score": 5,
        "buckets": {
            "admission": {
                "keywords": [ "admission date", "date of admission", "admitted on" ],
                "score": 2
            },
            "discharge": {
                "keywords": [ "discharge summary", "discharge date", "date of discharge", "condition on discharge", "discharged on" ],
                "score": 3
            },
            "diagnosis": {
                "keywords": [ "diagnosis", "final diagnosis", "reason for admission" ],
                "score": 2
            },
            "hospital_course": {
                "keywords": ["hospital course", "course in hospital", "treatment given"],
                "score": 2
            },
            "summary": {
                "keywords": [ "hospital stay", "course in hospital", "summary" ],
                "score": 1
            },
        },
    },
    "insurance": {
        "required_score": 5,
        "buckets": {
            "policy_info": {
                "keywords": [ "policy no", "policy number", "policy schedule", "insurance policy", "mediclaim", "health insurance", "life insurance", "sum insured", "premium certificate", "certificate of insurance" ],
                "score": 3
            },
            "claim_info": {
                "keywords": [ "claim", "claim number", "settlement", "approval", "cashless", "mediclaim" ],
                "score": 2
            },
            "premium_info": {
                "keywords": [ "premium", "renewal", "premium amount", "stamp duty" ],
                "score": 2
            },
            "company_info": {
                "keywords": [ "insurance company", "insurer", "policyholder", "insured person", "nominee details", "tpa details", "ombudsman" ],
                "score": 2
            },
        }
    }
}


def check_mandatory_rules(text: str, category: str):
    rules = MANDATORY_KEYWORD_RULES.get(category)
    if not rules:
        return True, 0, {}
    
    total_score = 0
    bucket_hits = {}
    for bucket, cfg in rules["buckets"].items():
        found = any(re.search(rf"\b{kw}\b", text) for kw in cfg["keywords"])
        matches = [kw for kw in cfg["keywords"] if re.search(rf"\b{kw}\b", text)]
        if matches:
            total_score += cfg["score"]
            bucket_hits[bucket] = cfg["score"]
            bucket_hits[bucket] = {"score": cfg["score"], "matches": matches}
        else:
            bucket_hits[bucket] = {"score": 0, "matches": []}
    return total_score >= rules["required_score"], total_score, bucket_hits



def classify_document(text: str) -> tuple[str, str]:
    text_lower = text.lower() if text else ""
    logs = []

    if not text_lower.strip():
        logs.append("[RESULT] No text extracted → UNKNOWN")
        return "unknown", "\n".join(logs)
    print("Checking for: ",text)
    # Step 1: Medical vs Non-medical
    medical_matches = [kw for kw in MEDICAL_KEYWORDS if re.search(rf"\b{kw}\b", text_lower)]
    finance_matches = [kw for kw in GENERIC_FINANCE_KEYWORDS if re.search(rf"\b{kw}\b", text_lower)]
    medical_score = sum(MEDICAL_KEYWORDS[kw] for kw in medical_matches)
    finance_score = len(finance_matches)

    logs.append(f"[CHECK] Medical matches={medical_matches}, score={medical_score}")
    logs.append(f"[CHECK] Finance matches={finance_matches}, score={finance_score}")

    if medical_score < 5 or medical_score < finance_score:
        logs.append("[RESULT] Classified as NON_MEDICAL")
        return "non_medical", "\n".join(logs)

    # Step 2: Try each medical category’s mandatory rules
    category_results = {}
    for category in MANDATORY_KEYWORD_RULES.keys():
        passed, score, hits = check_mandatory_rules(text_lower, category)
        category_results[category] = (passed, score, hits)
        logs.append(f"[CHECK] {category.upper()} total={score}, passed={passed}")
        for bucket, details in hits.items():
            logs.append(f"   - {bucket}: score={details['score']}, matches={details['matches']}")

    valid_categories = {cat: data for cat, data in category_results.items() if data[0]}
    if valid_categories:
        best_category = max(valid_categories, key=lambda c: valid_categories[c][1])
        logs.append(f"[RESULT] Classified as {best_category} ✅")
        return best_category, "\n".join(logs)

    # Step 3: Medical but no category → OTHER
    logs.append("[RESULT] Classified as OTHER (medical but no category matched mandatory rules)")
    return "other", "\n".join(logs)
