from typing import Set, Dict, Tuple
import importlib.resources
from hccinfhir.datamodels import ModelName, ProcFilteringFilename, DxCCMappingFilename

def load_is_chronic(filename: str) -> Dict[Tuple[str, ModelName], bool]:
    """
    Load a CSV file into a dictionary mapping (cc, model_name) to a boolean value indicating whether the HCC is chronic.
    """
    mapping: Dict[Tuple[str, ModelName], bool] = {}
    try:
        with importlib.resources.open_text('hccinfhir.data', filename) as f:
            for line in f.readlines()[1:]:  # Skip header
                try:
                    hcc, is_chronic, model_version, model_domain = line.strip().split(',')
                    cc = hcc.replace('HCC', '')
                    model_name = f"{model_domain} Model {model_version}"
                    key = (cc, model_name)
                    if key not in mapping:
                        mapping[key] = (is_chronic == 'Y')
                except ValueError:
                    continue  # Skip malformed lines
    except Exception as e:
        print(f"Error loading mapping file: {e}")
        return {}
    
    return mapping 

def load_proc_filtering(filename: ProcFilteringFilename) -> Set[str]:
    """
    Load a single-column CSV file into a set of strings.
    
    Args:
        filename: Name of the CSV file in the hccinfhir.data package
        
    Returns:
        Set of strings from the CSV file
    """
    try:
        with importlib.resources.open_text('hccinfhir.data', filename) as f:
            return set(f.read().splitlines())
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return set()

def load_dx_to_cc_mapping(filename: DxCCMappingFilename) -> Dict[Tuple[str, ModelName], Set[str]]:
    """
    Load diagnosis to CC mapping from a CSV file.
    Expected format: diagnosis_code,cc,model_name
    
    Args:
        filename: Name of the CSV file in the hccinfhir.data package
        
    Returns:
        Dictionary mapping (diagnosis_code, model_name) to a set of CC codes
    """
    mapping: Dict[Tuple[str, ModelName], Set[str]] = {}
    
    try:
        with importlib.resources.open_text('hccinfhir.data', filename) as f:
            for line in f.readlines()[1:]:  # Skip header
                try:
                    diagnosis_code, cc, model_name = line.strip().split(',')
                    key = (diagnosis_code, model_name)
                    if key not in mapping:
                        mapping[key] = {cc}
                    else:
                        mapping[key].add(cc)
                except ValueError:
                    continue  # Skip malformed lines
    except Exception as e:
        print(f"Error loading mapping file: {e}")
        return {}
    
    return mapping 