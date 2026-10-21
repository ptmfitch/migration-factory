import unittest

from gen_coverage import render_coverage


class RenderCoverageTest(unittest.TestCase):
    def test_renders_operator_progress_before_inventory_context(self) -> None:
        manifest = {
            "app_id": "example",
            "scanned_seeds": [],
            "unscanned_hints": [],
            "surfaces": [],
            "behaviours": [
                {
                    "behaviour_id": "done",
                    "name": "Done behaviour",
                    "status": "converted",
                    "impl_in_modern": "full",
                },
                {
                    "behaviour_id": "partial",
                    "status": "documented",
                    "impl_in_modern": "partial",
                    "notes": "One material gap remains.",
                },
                {
                    "behaviour_id": "remaining",
                    "status": "documented",
                    "slice_id": "example-slice",
                    "legacy_green": True,
                },
                {
                    "behaviour_id": "out",
                    "status": "deferred",
                    "impl_in_modern": "none",
                },
            ],
        }

        output = render_coverage(manifest)

        self.assertLess(
            output.index("## Operator progress (modern implementation)"),
            output.index("## Inventory context"),
        )
        self.assertIn("| none | 1 | Not started in modern |", output)
        self.assertIn("| partial | 1 | Some modern execution; gaps in notes |", output)
        self.assertIn("| full (converted) | 1 | Done in modern;", output)
        self.assertIn("| deferred / rejected | 1 | Explicitly out |", output)
        self.assertIn("- partial — One material gap remains.", output)
        self.assertIn("- remaining — example-slice — legacy_green yes", output)
        self.assertNotIn("%", output)

    def test_rejects_converted_without_full_implementation(self) -> None:
        manifest = {
            "app_id": "example",
            "behaviours": [
                {
                    "behaviour_id": "dishonest",
                    "status": "converted",
                    "impl_in_modern": "partial",
                    "notes": "Still incomplete.",
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "requires impl_in_modern: full"):
            render_coverage(manifest)

    def test_rejects_partial_without_gap_notes(self) -> None:
        manifest = {
            "app_id": "example",
            "behaviours": [
                {
                    "behaviour_id": "partial",
                    "status": "documented",
                    "impl_in_modern": "partial",
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "requires gap notes"):
            render_coverage(manifest)


if __name__ == "__main__":
    unittest.main()
