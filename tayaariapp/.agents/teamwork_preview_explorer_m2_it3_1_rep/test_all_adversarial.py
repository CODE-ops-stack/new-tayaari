import sys, os
sys.path.insert(0, os.path.abspath("."))
import unittest
from test_proposed_patterns import extract_simulated

class TestAllAdversarialSentences(unittest.TestCase):
    def test_adversarial_m2_all(self):
        # 1. Entity integrity
        sentences_entity = [
            ("Atmosphere is divided into five layers.", "Atmosphere", "classification"),
            ("Antarctica is covered by permanent ice sheets.", "Antarctica", None),
            ("Andesite is an extrusive volcanic rock with intermediate composition.", "Andesite", "definition"),
            ("Thermosphere is the layer of the atmosphere above the mesosphere.", "Thermosphere", "part-of"), # or definition
            ("Alluvial soils are deposited by the Himalayan river systems.", "Alluvial soils", "process"),
            ("Precipitation falls to the ground in the form of rain or snow.", "Precipitation", None),
            ("Primary seismic waves are followed by secondary waves.", "Primary seismic waves", "sequence"),
        ]
        for s, exp_ent, exp_intent in sentences_entity:
            intent, ent, pred = extract_simulated(s)
            self.assertIsNotNone(intent, f"Failed on '{s}'")
            self.assertIn(exp_ent.lower(), ent.lower(), f"Entity mismatch on '{s}': expected {exp_ent}, got {ent}")
            if exp_intent:
                self.assertEqual(intent, exp_intent, f"Intent mismatch on '{s}': expected {exp_intent}, got {intent}")

        # 2. Syntactic inversions
        s_multi = "In the northern plains of India, during the summer monsoon season, heavy rainfall causes extensive riverine flooding."
        intent, ent, pred = extract_simulated(s_multi)
        self.assertEqual(intent, "cause/effect")
        self.assertIn("rainfall", ent.lower())

        s_loc = "Under the Trans-Himalayan range lies the Indus-Tsangpo Suture Zone."
        intent, ent, pred = extract_simulated(s_loc)
        self.assertEqual(intent, "spatial")
        self.assertIn("indus-tsangpo", ent.lower())

        s_exc1 = "Except for Mercury and Venus, all planets in the solar system have natural satellites."
        intent, ent, pred = extract_simulated(s_exc1)
        self.assertEqual(intent, "exception")

        s_exc2 = "With the exception of Venus and Uranus, all planets rotate from west to east."
        intent, ent, pred = extract_simulated(s_exc2)
        self.assertEqual(intent, "exception")

        s_pass_ce = "Extensive riverine flooding is caused by heavy monsoon rainfall."
        intent, ent, pred = extract_simulated(s_pass_ce)
        self.assertEqual(intent, "cause/effect")

        # 3. Comparisons
        comparisons = [
            "Continental crust is thicker than oceanic crust.",
            "Mercury is smaller than Earth.",
            "The density of continental crust is lower than that of oceanic crust.",
        ]
        for c in comparisons:
            intent, ent, pred = extract_simulated(c)
            self.assertEqual(intent, "comparison", f"Failed comparison on '{c}': got {intent}")

        # 4. Classifications
        classifications = [
            "The crust is divided into oceanic and continental crust.",
            "Earth atmosphere is divided into troposphere, stratosphere, mesosphere, thermosphere, and exosphere."
        ]
        for c in classifications:
            intent, ent, pred = extract_simulated(c)
            self.assertEqual(intent, "classification", f"Failed classification on '{c}': got {intent}")

        # 5. Scientific process
        processes = [
            "Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
            "Condensation transforms water vapor into liquid water droplets.",
            "Evaporation turns liquid water into water vapor."
        ]
        for p in processes:
            intent, ent, pred = extract_simulated(p)
            self.assertEqual(intent, "process", f"Failed process on '{p}': got {intent}")

        # 6. Quantities
        quantities = [
            "The Earth has an equatorial radius of 6378 kilometers.",
            "The core extends to a depth of 2900 kilometers.",
            "Mount Everest has an elevation of 8848 meters."
        ]
        for q in quantities:
            intent, ent, pred = extract_simulated(q)
            self.assertEqual(intent, "quantity", f"Failed quantity on '{q}': got {intent}")

        # 7. Complex Indian geographic entities (challenge 05)
        samples = [
            ("The Indo-Gangetic plain constitutes the most fertile agricultural region of Northern India.", "Indo-Gangetic"),
            ("The Trans-Himalayan zone contains the Karakoram, Ladakh, and Zaskar ranges.", "Trans-Himalayan"),
            ("The Great Rann of Kutch is a vast salt marsh situated in the Thar Desert.", "Great Rann of Kutch"),
            ("The Chota Nagpur Plateau comprises rich deposits of iron ore, coal, and bauxite.", "Chota Nagpur Plateau"),
            ("The Andaman and Nicobar Islands are separated by the Ten Degree Channel.", "Andaman and Nicobar Islands"),
            ("The Deccan Traps were formed through massive basaltic fissure eruptions.", "Deccan Traps"),
        ]
        for text, entity in samples:
            intent, ent, pred = extract_simulated(text)
            self.assertIsNotNone(intent, f"Dropped: {entity} ('{text}')")
            self.assertIn(entity.lower(), ent.lower(), f"Entity mismatch: expected '{entity}', got '{ent}'")

        # 8. Challenge 03 passive def
        text_pass = "The Western Ghats are known as Sahyadri in Maharashtra."
        intent, ent, pred = extract_simulated(text_pass)
        self.assertIn("western ghats", ent.lower())

        # 9. Challenge 04 prefix
        text_prefix = "Along the Malabar Coast, during the southwest monsoon, heavy precipitation occurs regularly."
        intent, ent, pred = extract_simulated(text_prefix)
        self.assertFalse(ent.startswith("long the"))

if __name__ == "__main__":
    unittest.main()
