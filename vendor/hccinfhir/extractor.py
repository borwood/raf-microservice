from typing import Union, List, Literal
from hccinfhir.datamodels import ServiceLevelData
from hccinfhir.extractor_837 import extract_sld_837
from hccinfhir.extractor_fhir import extract_sld_fhir

def extract_sld(
    data: Union[str, dict], 
    format: Literal["837", "fhir"] = "fhir"
) -> List[ServiceLevelData]:
    """
    Unified entry point for SLD extraction with explicit format specification
    
    Args:
        data: Input data - string for 837, dict for FHIR
        format: Data format - either "837" or "fhir"
        
    Returns:
        List of ServiceLevelData
        
    Raises:
        ValueError: If format and data type don't match or format is invalid
        TypeError: If data is None or wrong type
    """
    if data is None:
        raise TypeError("Input data cannot be None")
        
    if format == "837":
        if not isinstance(data, str) or data == "":
            raise TypeError(f"837 format requires string input, got {type(data)}")
        return extract_sld_837(data)
    elif format == "fhir":
        if not isinstance(data, dict) or data == {}:
            raise TypeError(f"FHIR format requires dict input, got {type(data)}")   
        return extract_sld_fhir(data)
    else:
        raise ValueError(f'Format must be either "837" or "fhir", got {format}')


def extract_sld_list(data: Union[List[str], List[dict]], format: Literal["837", "fhir"] = "fhir") -> List[ServiceLevelData]:
    """Extract SLDs from a list of FHIR EOBs"""
    output = []
    for item in data:

        try:
            output.extend(extract_sld(item, format))
        except TypeError as e:
            print(f"Warning: Skipping invalid types: {str(e)}")
        except ValueError as e:
            print(f"Warning: Skipping invalid values: {str(e)}")
    return output

