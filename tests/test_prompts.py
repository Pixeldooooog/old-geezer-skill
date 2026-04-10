import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PromptContractTests(unittest.TestCase):
    def test_builder_mentions_behavior_chain_and_decision_rules(self):
        text = (ROOT / "prompts" / "geezer_builder.md").read_text(encoding="utf-8")

        self.assertIn("behavior_chain", text)
        self.assertIn("decision_rules", text)
        self.assertIn("value_hierarchy", text)

    def test_analyzer_mentions_behavior_chain_output(self):
        text = (ROOT / "prompts" / "geezer_analyzer.md").read_text(encoding="utf-8")

        self.assertIn("behavior_chain", text)
        self.assertIn("scene_label", text)


if __name__ == "__main__":
    unittest.main()
