from typing import List, Optional, Dict
from pydantic import BaseModel
from hccinfhir.datamodels import ServiceLevelData

CLAIM_TYPES = {
    "005010X222A1": "837P",     # Professional
    "005010X223A2": "837I"      # Institutional
}

class ClaimData(BaseModel):
    """Container for claim-level data"""
    claim_id: Optional[str] = None
    patient_id: Optional[str] = None
    performing_provider_npi: Optional[str] = None
    billing_provider_npi: Optional[str] = None
    provider_specialty: Optional[str] = None
    facility_type: Optional[str] = None
    service_type: Optional[str] = None
    claim_type: str
    dx_lookup: Dict[str, str] = {}

def parse_date(date_str: str) -> Optional[str]:
    """Convert 8-digit date string to ISO format YYYY-MM-DD"""
    if not isinstance(date_str, str) or len(date_str) != 8:
        return None
    try:
        year, month, day = int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8])
        if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
            return None
        return f"{year:04d}-{month:02d}-{day:02d}"
    except ValueError:
        return None

def parse_amount(amount_str: str) -> Optional[float]:
    """Convert string to float, return None if invalid"""
    try:
        return float(amount_str)
    except (ValueError, TypeError):
        return None

def get_segment_value(segment: List[str], index: int) -> Optional[str]:
    """Safely get value from segment at given index"""
    return segment[index] if len(segment) > index else None

def parse_diagnosis_codes(segment: List[str]) -> Dict[str, str]:
    """Extract diagnosis codes from HI segment"""
    dx_lookup = {}
    for pos, element in enumerate(segment[1:], 1):
        if ':' not in element:
            continue
        qualifier, code = element.split(':')[:2]
        if qualifier in ['ABK', 'ABF']:  # ICD-10 qualifiers
            dx_lookup[str(pos)] = code
    return dx_lookup

def process_service_line(segments: List[List[str]], start_index: int) -> tuple[Optional[str], Optional[str]]:
    """Extract NDC and service date from service line segments"""
    ndc = None
    service_date = None
    
    for seg in segments[start_index:]:
        if seg[0] in ['LX', 'CLM', 'SE']:
            break
        if seg[0] == 'LIN' and len(seg) > 3 and seg[2] == 'N4':
            ndc = seg[3]
        elif seg[0] == 'DTP' and seg[1] == '472':
            service_date = parse_date(seg[3])
        if ndc and service_date:
            break
            
    return ndc, service_date

def extract_sld_837(content: str) -> List[ServiceLevelData]:
    """Extract service level data from 837 Professional or Institutional claims"""
    if not content:
        raise ValueError("Input X12 data cannot be empty")
    
    # Split content into segments
    segments = [seg.strip().split('*') for seg in content.split('~') if seg.strip()]
    
    # Detect claim type from GS segment
    claim_type = None
    for segment in segments:
        if segment[0] == 'GS' and len(segment) > 8:
            claim_type = CLAIM_TYPES.get(segment[8])
            break
    
    if not claim_type:
        raise ValueError("Invalid or unsupported 837 format")
    
    encounters = []
    current_data = ClaimData(claim_type=claim_type)
    in_claim_loop = False
    in_rendering_provider_loop = False
    
    for i, segment in enumerate(segments):
        if len(segment) < 2:
            continue
            
        seg_id = segment[0]
        
        # Process NM1 segments (Provider and Patient info)
        if seg_id == 'NM1':
            if segment[1] == 'IL':  # Subscriber/Patient
                current_data.patient_id = get_segment_value(segment, 9)
                in_claim_loop = False
                in_rendering_provider_loop = False
            elif segment[1] == '82' and len(segment) > 8 and segment[8] == 'XX':  # Rendering Provider
                current_data.performing_provider_npi = get_segment_value(segment, 9)
                in_rendering_provider_loop = True
            elif segment[1] == '85' and len(segment) > 8 and segment[8] == 'XX':  # Billing Provider
                current_data.billing_provider_npi = get_segment_value(segment, 9)
                
        # Process Provider Specialty
        elif seg_id == 'PRV' and segment[1] == 'PE' and in_rendering_provider_loop:
            current_data.provider_specialty = get_segment_value(segment, 3)
            
        # Process Claim Information
        elif seg_id == 'CLM':
            in_claim_loop = True
            in_rendering_provider_loop = False
            current_data.claim_id = segment[1] if len(segment) > 1 else None
            
            # Parse facility and service type for institutional claims
            if claim_type == "837I" and len(segment) > 5 and ':' in segment[5]:
                current_data.facility_type = segment[5][0]
                current_data.service_type = segment[5][1] if len(segment[5]) > 1 else None

        # Process Diagnosis Codes
        elif seg_id == 'HI' and in_claim_loop:
            current_data.dx_lookup = parse_diagnosis_codes(segment)
            
        # Process Service Lines
        elif seg_id in ['SV1', 'SV2'] and in_claim_loop:
            # Parse procedure info
            proc_info = segment[1].split(':')
            procedure_code = proc_info[1] if len(proc_info) > 1 else None
            modifiers = proc_info[2:] if len(proc_info) > 2 else []
            
            # Get diagnosis pointers and linked diagnoses
            dx_pointer_pos = 7 if seg_id == 'SV1' else 11
            dx_pointers = get_segment_value(segment, dx_pointer_pos)
            linked_diagnoses = [
                current_data.dx_lookup[pointer]
                for pointer in (dx_pointers.split(',') if dx_pointers else [])
                if pointer in current_data.dx_lookup
            ]
            
            # Get service line details
            ndc, service_date = process_service_line(segments, i)
            
            # Create service level data
            service_data = ServiceLevelData(
                claim_id=current_data.claim_id,
                procedure_code=procedure_code,
                linked_diagnosis_codes=linked_diagnoses,
                claim_diagnosis_codes=list(current_data.dx_lookup.values()),
                claim_type=current_data.claim_type,
                provider_specialty=current_data.provider_specialty,
                performing_provider_npi=current_data.performing_provider_npi,
                billing_provider_npi=current_data.billing_provider_npi,
                patient_id=current_data.patient_id,
                facility_type=current_data.facility_type,
                service_type=current_data.service_type,
                service_date=service_date,
                place_of_service=get_segment_value(segment, 6) if seg_id == 'SV1' else None,
                quantity=parse_amount(get_segment_value(segment, 4)),
                modifiers=modifiers,
                ndc=ndc,
                allowed_amount=None
            )
            encounters.append(service_data)
    
    return encounters