import requests
import pandas as pd
import time

# ---- 1. Load Medicare file ----
medicare = pd.read_csv("medicare_drug_spending.csv")

# unique generic names
generics = (
    medicare["Gnrc_Name"]
    .dropna()
    .drop_duplicates()
    .sort_values()
)

print("Unique generic names:", len(generics))

# ---- 2. Disease → ATC prefix mapping ----
DISEASE_PREFIXES = {
    "Hypertension": ("C02", "C03", "C07", "C08", "C09"),
    "High Cholesterol": ("C10",),
    "Diabetes": ("A10",),
    "Obesity": ("A08",),
    "Arthritis": ("M01", "M02", "M04", "L04"),
}

def get_atc_codes_for_name(drug_name: str):
    """
    Call RxClass getClassByRxNormDrugName to get ATC codes for a generic name.
    Returns a list of ATC codes like ['C09AA03', 'C09AA'].
    """
    url = "https://rxnav.nlm.nih.gov/REST/rxclass/class/byDrugName.json"
    params = {
        "drugName": drug_name,
        "relaSource": "ATC",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
    except Exception as e:
        print(f"[ERROR] Request failed for {drug_name}: {e}")
        return []

    if not resp.ok:
        print(f"[ERROR] HTTP {resp.status_code} for {drug_name}")
        return []

    try:
        data = resp.json()
    except Exception as e:
        # If RxNav ever returns HTML instead of JSON, avoid crashing
        print(f"[ERROR] JSON decode failed for {drug_name}: {e}")
        return []

    infos = data.get("rxclassDrugInfoList", {}).get("rxclassDrugInfo", [])
    codes = set()

    for info in infos:
        cls = info.get("rxclassMinConceptItem", {})
        code = cls.get("classId")
        if code:
            codes.add(code)

    return sorted(codes)


def classify_from_atc_codes(codes):
    """
    Given a list of ATC codes, return a semicolon-separated list
    of disease categories based on prefixes.
    """
    diseases = set()

    for code in codes:
        for disease, prefixes in DISEASE_PREFIXES.items():
            if any(code.startswith(p) for p in prefixes):
                diseases.add(disease)

    return ";".join(sorted(diseases)) if diseases else ""


rows = []
for i, name in enumerate(generics, start=1):
    print(f"{i}/{len(generics)}: {name}")

    codes = get_atc_codes_for_name(name)
    disease_label = classify_from_atc_codes(codes)

    rows.append(
        {
            "Gnrc_Name": name,
            "ATC_Codes": "|".join(codes),
            "Disease_Category": disease_label,
        }
    )

    # be polite to the API
    time.sleep(0.2)

mapping = pd.DataFrame(rows)
mapping.to_csv("atc_disease_mapping.csv", index=False)

print("Saved atc_disease_mapping.csv with", len(mapping), "rows")
print(mapping.head())
