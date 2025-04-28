import unittest
from content_moderation import ContentModeration

class TestContentModeration(unittest.TestCase):
    def setUp(self):
        # instantiate and clear out whitelist so all PERSON ents are caught
        self.cm = ContentModeration()
        self.cm.whitelist.clear()

    def assertPII(self, query, expected):
        found = set(self.cm.detect_pii(query))
        self.assertEqual(found, set(expected),
                         msg=f"\nQuery: {query!r}\nExpected: {expected}\n  Found: {found}")

    def test_wayne_isham_case_number(self):
        q = (
            "Wayne Isham would like to renew their SNAP benefits. "
            "Can they use their Case number 236473447 to renew using COMPASS?"
        )
        self.assertPII(q, ["Wayne Isham", "236473447"])

    def test_amy_rose_and_janet_morris(self):
        q = (
            "Amy Rose received an eligibility notice for Medical Assistance but it "
            "was for someone who isn't in their household. How did Janet Morris "
            "get included on their notice address at 1 main street, York PA, 17402?"
        )
        self.assertPII(q, ["Amy Rose", "Janet Morris"])

    def test_incorrect_ssn(self):
        q = (
            "A mother was renewing her Medical Assistance benefits through COMPASS "
            "but her son's SSN 278888876 is incorrect within the demographics page. "
            "How do I get that updated?"
        )
        self.assertPII(q, ["278888876"])

    def test_janet_young_mci(self):
        q = (
            "Janet Young with MCI 799994444 has $3,000 in monthly gross income. "
            "Is she eligible for Medical Assistance if her net deductions are $400 per month?"
        )
        self.assertPII(q, ["Janet Young", "799994444"])

    def test_mary_riley_two_case_numbers(self):
        q = (
            "Mary Riley received two different SNAP eligibility notices with two "
            "different case numbers 153456666 and 175444444. She is afraid that she "
            "will be accused of benefit fraud. How do we resolve this issue?"
        )
        self.assertPII(q, ["Mary Riley", "153456666", "175444444"])

    def test_john_and_mary_taylor(self):
        q = (
            "A father applied for Medical Assistance for his Son John Taylor with MCI 222228888 "
            "and daughter Mary Taylor with MCI 444449999 this morning and received case number 545777777. "
            "When can he expect to receive their Medical Assistance notices?"
        )
        self.assertPII(q, [
            "John Taylor",
            "222228888",
            "Mary Taylor",
            "444449999",
            "545777777"
        ])

if __name__ == "__main__":
    unittest.main()