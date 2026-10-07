import unittest

from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

from api.anonymize import anonymize_dicom, pseudonymous_uid


class AnonymizationTests(unittest.TestCase):
    def dataset(self):
        meta = FileMetaDataset()
        meta.TransferSyntaxUID = ExplicitVRLittleEndian
        meta.MediaStorageSOPInstanceUID = generate_uid()
        ds = FileDataset(None, {}, file_meta=meta, preamble=b"\0" * 128)
        ds.PatientName = "Persona^Prueba"
        ds.PatientID = "secret-id"
        ds.PatientBirthDate = "19800101"
        ds.StudyInstanceUID = generate_uid()
        ds.SeriesInstanceUID = generate_uid()
        ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
        ds.BurnedInAnnotation = "NO"
        ds.add_new((0x0011, 0x1010), "LO", "private-value")
        return ds

    def test_uid_mapping_is_deterministic(self):
        original = generate_uid()
        self.assertEqual(
            pseudonymous_uid(original, "a-secret-of-16+chars"),
            pseudonymous_uid(original, "a-secret-of-16+chars"),
        )

    def test_removes_direct_identifiers_and_private_tags(self):
        original = self.dataset()
        old_study_uid = original.StudyInstanceUID
        cleaned, audit = anonymize_dicom(original, "a-secret-of-16+chars")
        self.assertEqual(cleaned.PatientName, "")
        self.assertEqual(cleaned.PatientID, "")
        self.assertEqual(cleaned.PatientBirthDate, "")
        self.assertNotEqual(cleaned.StudyInstanceUID, old_study_uid)
        self.assertEqual(cleaned.PatientIdentityRemoved, "YES")
        self.assertNotIn((0x0011, 0x1010), cleaned)
        self.assertFalse(audit["pixel_data_modified"])

    def test_rejects_unknown_burned_in_annotation(self):
        dataset = self.dataset()
        del dataset.BurnedInAnnotation
        with self.assertRaises(ValueError):
            anonymize_dicom(dataset, "a-secret-of-16+chars")


if __name__ == "__main__":
    unittest.main()
