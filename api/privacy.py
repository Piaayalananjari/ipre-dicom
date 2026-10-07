from __future__ import annotations


SENSITIVE_DICOM_KEYWORDS = (
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "OtherPatientIDs",
    "OtherPatientNames",
    "InstitutionName",
    "InstitutionAddress",
    "ReferringPhysicianName",
    "PerformingPhysicianName",
    "OperatorsName",
    "AccessionNumber",
)


def audit_dicom_privacy(dataset) -> dict:
    """Report PHI-bearing fields without returning their sensitive values."""

    present = []
    for keyword in SENSITIVE_DICOM_KEYWORDS:
        value = getattr(dataset, keyword, None)
        if value not in (None, ""):
            present.append(keyword)

    burned_in = str(getattr(dataset, "BurnedInAnnotation", "UNKNOWN")).upper()
    return {
        "metadata_identifiers_present": present,
        "metadata_identifier_count": len(present),
        "burned_in_annotation": burned_in,
        "pixel_text_review_required": burned_in != "NO",
        "anonymous": len(present) == 0 and burned_in == "NO",
        "warning": (
            "La auditoria no reemplaza un proceso formal de desidentificacion DICOM ni OCR sobre pixeles."
        ),
    }


def non_dicom_privacy_audit() -> dict:
    return {
        "metadata_identifiers_present": [],
        "metadata_identifier_count": 0,
        "burned_in_annotation": "NOT_APPLICABLE",
        "pixel_text_review_required": True,
        "anonymous": False,
        "warning": (
            "Una imagen raster no contiene metadata DICOM evaluable; se requiere OCR para descartar texto identificador."
        ),
    }

