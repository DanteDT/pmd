# Test 01 - Test utils/utilities.py function titlecase
import os
import sys
import unittest
from utils.utilities import titlecase
import utils.config as config

input_strs =   ["the dog's adventure AND IN THE \"big\" city",
                "the dog\"s adventure in the \"big\" city",
                "DaVinci shouldn't (definitely not) journey through The children's museum",
                "J.R.R. TolKein shouldn't either.",
                "learning from A [i mean *you're*] teacher's guide",
                "it's a beautiful <a href=\"https://wikipedia.com/Day\">day</a> in the neighborhood",
                "MIDNIGHT ALOFT—THUNDER AND LIGHTNING.",
                "DOES THE WHALE'S MAGNITUDE DIMINISH?–WILL HE PERISH?."]

expect_strs =  ["The Dog's Adventure and in the \"Big\" City",
                "The Dog\"s Adventure in the \"Big\" City",
                "DaVinci Shouldn't (Definitely Not) Journey Through the Children's Museum",
                "J.R.R. TolKein Shouldn't Either.",
                "Learning From a [I Mean *You're*] Teacher's Guide",
                "It's a Beautiful <a href=\"https://wikipedia.com/Day\">day</a> in the Neighborhood",
                "Midnight Aloft—Thunder and Lightning.",
                "Does the Whale's Magnitude Diminish?–Will He Perish?."]

config_data = config.load_config()
ttl_lower = config_data["proj_dirs"]["ttl_lower"]

ignore_list = ttl_lower

class TestTitleCase(unittest.TestCase):
    def test_titlecase(self):
        for i in range(len(input_strs)):
            actual_str = titlecase(input_strs[i], ignore_list)
            expected_str = expect_strs[i]
            print(f"Input:    {input_strs[i]}")
            print(f"Actual:   {actual_str}")
            print(f"Expected: {expected_str}")
            self.assertEqual(actual_str, expected_str)

if __name__ == "__main__":
    unittest.main()
