from __future__ import annotations

import copy
import hashlib
import hmac

from pydicom.uid import UID

from api.privacy import SENSITIVE_DICOM_KEYWORDS


UID_KEYWORDS = (
    "StudyInstanceUID",
    "SeriesInstanceUID",
    "SOPInstanceUID",
    "FrameOfReferenceUID",
)


def pseudonymous_uid(value: str, secret: str) -> UID:
    digest = hmac.new(secret.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).digest()
    # 2.25 UIDs encode a UUID-sized integer and remain below DICOM's 64-char limit.
    return UID(f"2.25.{int.from_bytes(digest[:16], byteorder='big')}")


def anonymize_dicom(dataset, secret: str):
    if len(secret) < 16:
        raise ValueError("DICOM_PSEUDONYM_SECRET debe tener al menos 16 caracteres")

    burned_in = str(getattr(dataset, "BurnedInAnnotation", "UNKNOWN")).upper()
    if burned_in != "NO":
        raise ValueError(
            "BurnedInAnnotation no confirma NO; se requiere OCR/redaccion de pixeles antes de exportar"
        )

    result = copy.deepcopy(dataset)
    result.remove_private_tags()
    for keyword in SENSITIVE_DICOM_KEYWORDS:
        if keyword in result:
            result.data_element(keyword).value = ""

    uid_map = {}
    for keyword in UID_KEYWORDS:
        value = getattr(result, keyword, None)
        if value:
            replacement = pseudonymous_uid(str(value), secret)
            uid_map[keyword] = str(replacement)
            setattr(result, keyword, replacement)

    if getattr(result, "file_meta", None) and getattr(result, "SOPInstanceUID", None):
        result.file_meta.MediaStorageSOPInstanceUID = result.SOPInstanceUID

    result.PatientIdentityRemoved = "YES"
    result.DeidentificationMethod = "IPRE research-basic-v1"
    return result, {
        "profile": "research-basic-v1",
        "uids_remapped": sorted(uid_map),
        "pixel_data_modified": False,
        "warning": "Perfil experimental; requiere validacion institucional contra DICOM PS3.15.",
    }
