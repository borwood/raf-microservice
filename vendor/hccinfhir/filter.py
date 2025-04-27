from typing import List, Set
from hccinfhir.datamodels import ServiceLevelData
from hccinfhir.utils import load_proc_filtering

# use import importlib.resources to load the professional_cpt_fn file as a list of strings
professional_cpt_default_fn = 'ra_eligible_cpt_hcpcs_2023.csv'
professional_cpt_default = load_proc_filtering(professional_cpt_default_fn)

def apply_filter(
    data: List[ServiceLevelData], 
    inpatient_tob: Set[str] = {'11X', '41X'},
    outpatient_tob: Set[str] = {'12X', '13X', '43X', '71X', '73X', '76X', '77X', '85X'},
    professional_cpt: Set[str] = professional_cpt_default
) -> List[ServiceLevelData]:
    # tob (Type of Bill) Filter is based on:
    # https://www.hhs.gov/guidance/sites/default/files/hhs-guidance-documents/2012181486-wq-092916_ra_webinar_slides_5cr_092816.pdf
    # https://www.hhs.gov/guidance/sites/default/files/hhs-guidance-documents/final%20industry%20memo%20medicare%20filtering%20logic%2012%2022%2015_85.pdf

    # Break down the inpatient ToB into facility and service types
    inpatient_facility_types = {tob[0] for tob in inpatient_tob}
    inpatient_service_types = {tob[1] for tob in inpatient_tob}

    # Break down the outpatient ToB into facility and service types
    outpatient_facility_types = {tob[0] for tob in outpatient_tob}
    outpatient_service_types = {tob[1] for tob in outpatient_tob}       

    # If ServiceLevelData has a facility_type and service_type, then filter the data based on the facility_type and service_type
    # If not, then filter the data based on the CPT code
    filtered_data = []
    for item in data:
        if item.facility_type and item.service_type:
            if item.facility_type in inpatient_facility_types and item.service_type in inpatient_service_types:
                filtered_data.append(item)
            elif (item.facility_type in outpatient_facility_types and 
                  item.service_type in outpatient_service_types and
                  item.procedure_code in professional_cpt):
                filtered_data.append(item)
        else:
            if item.procedure_code in professional_cpt:
                filtered_data.append(item)  
    return filtered_data