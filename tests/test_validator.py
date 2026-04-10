import unittest

from tools.validator import find_missing_features, validate_cognitive_rules


FEATURES = {
    "behavioral_markers": {
        "interruption": {
            "per_1k": 1.5,
            "detail": {"你先别说": 2},
        }
    },
    "structural_features": {
        "top_enders": [{"suffix": "对吧", "count": 6}],
    },
    "scene_modes": [
        {
            "scene_label": "控场定调",
            "behavior_chain": ["打断截流", "直接定性", "结论先行"],
        }
    ],
    "cognitive_proxies": {
        "decision_rules": [
            {
                "rule": "先下判断，再补论据",
                "confidence": 0.82,
                "evidence": ["我觉得这个方向不对，因为投入产出不成立。"],
            }
        ],
        "value_hierarchy": [
            {
                "value": "控制与责任",
                "score": 4,
                "evidence": ["谁负责、什么时候交付先讲清楚。"],
            }
        ],
        "bias_signals": [
            {
                "bias": "诉诸经验",
                "confidence": 0.75,
                "evidence": ["我年轻的时候也是这么干的。"],
            }
        ],
    },
}


class ValidatorTests(unittest.TestCase):
    def test_validate_cognitive_rules_detects_missing_deep_rules(self):
        skill_text = """
        ## Layer 2：思维模型
        这个人很强势。
        """

        result = validate_cognitive_rules(skill_text, FEATURES)

        self.assertLess(result["score"], 100)
        self.assertIn("先下判断，再补论据", result["missing_rules"])
        self.assertIn("控制与责任", result["missing_values"])

    def test_find_missing_features_detects_scene_behavior_chain(self):
        skill_text = """
        ## Layer 3：话术系统
        会打断别人，也会说教。
        """

        result = find_missing_features(skill_text, FEATURES)

        issues = [item["issue"] for item in result]
        self.assertTrue(any("行为链" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
