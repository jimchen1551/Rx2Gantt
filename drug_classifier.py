import logging
import requests
from collections import defaultdict

class DrugClassifier:
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"

    def __init__(self):
        self.session = requests.Session()
        self.configure_retry()

    def configure_retry(self):
        """Configures retry settings for API calls."""
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        retry = Retry(
            total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)

    def fetch_rxclass_filtered(self, drug_name, filter_class_types=None):
        """Fetches classifications for a given drug name."""
        try:
            # Step 1: Fetch the RxCUI for the drug
            rxcui = self.get_rxcui(drug_name)
            if not rxcui:
                logging.warning(f"No RxCUI found for drug: {drug_name}")
                return {"MOA": "", "EPC": "", "PE": ""}

            # Step 2: Fetch classifications for the RxCUI
            classifications = self.get_classifications(rxcui, filter_class_types)
            return classifications
        except Exception as e:
            logging.error(f"Error fetching classification for {drug_name}: {e}")
            return {"MOA": "", "EPC": "", "PE": ""}

    def get_rxcui(self, drug_name):
        """Fetches the RxCUI for a drug name."""
        url = f"{self.BASE_URL}/approximateTerm.json?term={drug_name}"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("approximateGroup", {}).get("candidate", [])
            if candidates:
                return candidates[0].get("rxcui")
        return None

    def get_classifications(self, rxcui, filter_class_types=None):
        """Fetches classifications for a given RxCUI."""
        url = f"{self.BASE_URL}/rxclass/class/byRxcui.json?rxcui={rxcui}"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            classifications = data.get("rxclassDrugInfoList", {}).get("rxclassDrugInfo", [])
            grouped_classifications = defaultdict(set)

            for classification in classifications:
                class_type = classification.get("rxclassMinConceptItem", {}).get("classType")
                class_name = classification.get("rxclassMinConceptItem", {}).get("className")
                if class_type and class_name:
                    if not filter_class_types or class_type in filter_class_types:
                        grouped_classifications[class_type].add(class_name)

            return {
                "MOA": "\n".join(sorted(grouped_classifications.get("MOA", []))),
                "EPC": "\n".join(sorted(grouped_classifications.get("EPC", []))),
                "PE": "\n".join(sorted(grouped_classifications.get("PE", []))),
            }
        return {"MOA": "", "EPC": "", "PE": ""}
