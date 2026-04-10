import unittest

from tools.feature_extractor import (
    compute_behavioral_markers,
    compute_cognitive_proxies,
    segment_episodes,
)


MARKERS = {
    "dimensions": {
        "interruption": {
            "markers": ["你先别说"],
            "strong_signals": ["等一下", "你先别说"],
            "weak_signals": ["我问一下"],
            "contextual_rules": [
                {
                    "name": "redirect_control",
                    "all_of": ["先不谈", "我关心的是"],
                    "weight": 1.5,
                }
            ],
        },
        "lecturing": {
            "markers": ["我跟你说"],
            "strong_signals": ["我跟你说"],
        },
    }
}


class FeatureExtractorTests(unittest.TestCase):
    def test_behavioral_markers_include_contextual_evidence(self):
        utterances = [
            {
                "speaker": "张总",
                "timestamp": "2026-04-08 10:00:00",
                "content": "等一下，你先别说，这个先不谈，我关心的是谁负责、什么时候交付。",
            }
        ]

        result = compute_behavioral_markers(utterances, "张总", MARKERS)

        interruption = result["interruption"]
        self.assertGreater(interruption["weighted_count"], interruption["total_count"])
        self.assertTrue(interruption["contextual_matches"])
        self.assertEqual(interruption["contextual_matches"][0]["name"], "redirect_control")

    def test_segment_episodes_adds_trigger_based_scene_labels(self):
        utterances = [
            {
                "speaker": "张总",
                "timestamp": "2026-04-08 10:00:00",
                "content": "这个方向不对，你先别说，我先把结论给你。",
            },
            {
                "speaker": "别人",
                "timestamp": "2026-04-08 10:00:10",
                "content": "可是我们想试试看。",
            },
            {
                "speaker": "张总",
                "timestamp": "2026-04-08 10:02:30",
                "content": "我年轻的时候带团队，谁负责、什么时候交付必须先说清楚。",
            },
        ]

        result = segment_episodes(utterances, "张总", gap_seconds=60)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["scene_label"], "控场定调")
        self.assertIn("challenge", result[0]["trigger_signals"])
        self.assertEqual(result[1]["scene_label"], "资历施压")
        self.assertIn("glory_days", result[1]["trigger_signals"])

    def test_segment_episodes_extracts_behavior_chain(self):
        utterances = [
            {
                "speaker": "张总",
                "timestamp": "2026-04-08 10:00:00",
                "content": "等一下，你先别说，这个方向不对。",
            },
            {
                "speaker": "张总",
                "timestamp": "2026-04-08 10:00:12",
                "content": "我先把结论给你，说白了核心问题是没人负责，什么时候交付也没说。",
            },
        ]

        result = segment_episodes(utterances, "张总", gap_seconds=60)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["behavior_chain"],
            ["打断截流", "直接定性", "结论先行", "责任追问"],
        )

    def test_cognitive_proxies_include_evidence_and_confidence(self):
        utterances = [
            {
                "speaker": "张总",
                "timestamp": "2026-04-08 10:00:00",
                "content": "我觉得这个方向不对，因为投入产出根本不成立。",
            },
            {
                "speaker": "张总",
                "timestamp": "2026-04-08 10:00:20",
                "content": "我年轻的时候带团队也是这样，先把结论讲清楚，再看谁负责。",
            },
            {
                "speaker": "张总",
                "timestamp": "2026-04-08 10:00:40",
                "content": "本质上这事不用看那么细，关键是 owner 和时间节点。",
            },
        ]

        result = compute_cognitive_proxies(utterances, "张总")

        self.assertIn("decision_rules", result)
        self.assertGreaterEqual(len(result["decision_rules"]), 2)
        self.assertEqual(result["decision_rules"][0]["rule"], "先下判断，再补论据")
        self.assertTrue(result["decision_rules"][0]["evidence"])
        self.assertIn("confidence", result["decision_rules"][0])
        self.assertIn("value_hierarchy", result)
        self.assertEqual(result["value_hierarchy"][0]["value"], "控制与责任")


if __name__ == "__main__":
    unittest.main()
