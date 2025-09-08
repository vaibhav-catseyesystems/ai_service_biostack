from utils.gemini_utils import get_gemini_model, generate_content_with_file
from utils.GeminiPrompts import GEMINI_EXTRACT_DETAILS_PROMPT_TEMPLATE, GEMINI_EXTRACT_TEST_REPORT_DETAILS_PROMPT_TEMPLATE, GEMINI_EXTRACT_INVOICE_DETAILS_PROMPT_TEMPLATE
import logging

logger = logging.getLogger(__name__)

def process_document(file_bytes, mime_type, relatives_string):
    full_prompt = GEMINI_EXTRACT_DETAILS_PROMPT_TEMPLATE.format(relatives_string=relatives_string)
    model = get_gemini_model()
    raw_response_text = generate_content_with_file(model, str(full_prompt), file_bytes, mime_type)
    try:
        json_start = raw_response_text.find('```json') + len('```json')
        json_end = raw_response_text.rfind('```')
        json_string = raw_response_text[json_start:json_end].strip()        
        return json_string
    except ValueError as e:
        raise RuntimeError(f"Failed to decode JSON from Gemini response: {e}. Raw content: {raw_response_text}")

def extract_document_details(file_bytes, mime_type, relatives_string, document_type):
  if document_type == "test_report":
      prompt_template = GEMINI_EXTRACT_TEST_REPORT_DETAILS_PROMPT_TEMPLATE
  elif document_type == "invoice":
      prompt_template = GEMINI_EXTRACT_INVOICE_DETAILS_PROMPT_TEMPLATE
  else:
      raise RuntimeError("Report digitization for this record type not setup yet")
  
  full_prompt = prompt_template.format(relatives_string=relatives_string)
  model = get_gemini_model()
  raw_response_text = generate_content_with_file(model, str(full_prompt), file_bytes, mime_type)
  json_start = raw_response_text.find('```json') + len('```json')
  json_end = raw_response_text.rfind('```')
  if json_start != -1 and json_end != -1 and json_end > json_start:
      json_string = raw_response_text[json_start:json_end].strip() 
  else:
      json_string = raw_response_text.strip()        
  return json_string

