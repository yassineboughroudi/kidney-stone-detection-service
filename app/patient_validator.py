import requests
import logging

# The base URL for the patient management service should reflect your Docker network alias or DNS name.
PATIENT_MANAGEMENT_URL = "http://patient-management-service:8082/api/patients"
def get_patient_details(patient_id: str) -> dict:
    """
    Calls the patient management service to retrieve patient details.
    Returns a dictionary with patient data if found; otherwise, returns None.
    """
    url = f"{PATIENT_MANAGEMENT_URL}/{patient_id}"
    try:
        response = requests.get(url, timeout=5)  # Timeout added for robustness
        if response.status_code == 200:
            patient_data = response.json()
            logging.info(f"Patient {patient_id} found: {patient_data}")
            return patient_data
        else:
            logging.warning(f"Patient {patient_id} not found. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error calling Patient Management Service: {e}")
        return None
