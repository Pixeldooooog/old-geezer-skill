import unittest

from tools.source_parser import preprocess_utterances


class SourceParserPreprocessTests(unittest.TestCase):
    def test_preprocess_normalizes_speakers_filters_noise_and_merges_runs(self):
        utterances = [
            {
                "speaker": "  @张总（iPhone） ",
                "timestamp": "2026-04-08 10:00:00",
                "content": "这个事情我先说两句",
            },
            {
                "speaker": "张总",
                "timestamp": "2026-04-08 10:00:08",
                "content": "你先别说",
            },
            {
                "speaker": "系统消息",
                "timestamp": "2026-04-08 10:00:09",
                "content": "张三撤回了一条消息",
            },
            {
                "speaker": "李四",
                "timestamp": "2026-04-08 10:00:20",
                "content": "收到",
            },
        ]

        result = preprocess_utterances(utterances)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["speaker"], "张总")
        self.assertIn("这个事情我先说两句", result[0]["content"])
        self.assertIn("你先别说", result[0]["content"])


if __name__ == "__main__":
    unittest.main()
