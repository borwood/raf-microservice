import os, sys

# Add /vendor to sys.path
# This project is currently using a slightly modified version of HCCinFHIR (enabling heart failure and specified arrhythmia interaction), located in /vendor/hccinfhir
current_dir = os.path.dirname(os.path.abspath(__file__))
vendor_dir = os.path.join(current_dir, "vendor")
sys.path.insert(0, vendor_dir)
