from utils.document_type_classifier import classify_document
from utils.document_owner_classifier import get_patient_name_from_test_report,get_patient_name_from_invoice, get_patient_name_from_discharge_summary,get_patient_name_from_other_document,get_patient_name_from_insurance
import logging
logger = logging.getLogger(__name__)

def check_document_type_programatic(file_content):
    try:
        classification, reason = classify_document(file_content)
        return {
            "classification": classification,
            "reason": reason
        }
    except Exception as e:
        print(f"[ERROR] check_document_type failed: {str(e)}")
        raise

def check_document_owner_name_programatic(file_content, document_type):
    try:
        if document_type=='test_report':
            return get_patient_name_from_test_report(text=file_content)
        elif document_type=="invoice":
            return get_patient_name_from_invoice(text=file_content)
        elif document_type=="insurance":
            return get_patient_name_from_insurance(text=file_content)
        elif document_type=="discharge_summary":
            return get_patient_name_from_discharge_summary(text=file_content)
        else:
            return get_patient_name_from_other_document(text=file_content)            
    except Exception as e:
        logger.error(f"Exception at check_document_owner_name_programatic {str(e)}")
        raise