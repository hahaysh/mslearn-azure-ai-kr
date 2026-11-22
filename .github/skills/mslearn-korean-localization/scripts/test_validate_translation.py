import tempfile
import unittest
from pathlib import Path

import validate_translation as validator


def shell_examples(
    bash_language: str = "bash", powershell_label: str = "PowerShell"
) -> tuple[str, str]:
    bash = (
        "    **Bash**\n"
        f"    ```{bash_language}\n"
        '    echo "$NAME"\n'
        "    ```\n"
    )
    powershell = (
        f"    **{powershell_label}**\n"
        "    ```powershell\n"
        "    Write-Output $env:NAME\n"
        "    ```\n"
    )
    return bash, powershell


class ShellOrderingTests(unittest.TestCase):
    def test_shell_labels_determine_order_without_changing_commands(self) -> None:
        for language in ("bash", "azurecli"):
            for label in ("PowerShell", "Powershell"):
                for newline in ("\n", "\r\n"):
                    with self.subTest(language=language, label=label, newline=newline):
                        bash, powershell = shell_examples(language, label)
                        source = (bash + "\n" + powershell).replace("\n", newline)
                        expected = (powershell + "\n" + bash).replace("\n", newline)
                        reordered = validator.powershell_first(source)
                        self.assertEqual(expected, reordered)
                        self.assertEqual(reordered, validator.powershell_first(reordered))

    def test_shell_pairs_do_not_move_across_steps_or_inside_code_and_comments(
        self,
    ) -> None:
        bash, powershell = shell_examples("azurecli", "Powershell")
        pair = bash + "\n" + powershell
        examples = (
            bash + "\n1. Another step.\n\n" + powershell,
            "````markdown\n" + pair + "````\n",
            "{% comment %}\n" + pair + "{% endcomment %}\n",
            "<!--\n" + pair + "-->\n",
        )
        for text in examples:
            with self.subTest(text=text):
                self.assertEqual(text, validator.powershell_first(text))


class TranslationValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.source_root = self.repo / "Instructions"
        self.target_root = self.repo / "Instructions-kr"
        self.source_root.mkdir()
        self.target_root.mkdir()
        self.readme = self.target_root / "README.md"
        self.readme.write_text("# Translation\n", encoding="utf-8")

    def validate_documents(
        self,
        source: str,
        target: str,
        relative: Path = Path("example.md"),
        *,
        prefer_powershell: bool = True,
    ) -> list[str]:
        for root, text in ((self.source_root, source), (self.target_root, target)):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return validator.validate(
            self.repo,
            self.source_root,
            self.target_root,
            self.readme,
            prefer_powershell=prefer_powershell,
        )

    def management_documents(self) -> tuple[Path, str, str]:
        repo = Path(__file__).resolve().parents[4]
        relative = Path("azure-container-apps") / "02-aca-manage-containers.md"
        source = (repo / "Instructions" / relative).read_text(encoding="utf-8")
        target = (repo / "Instructions-kr" / relative).read_text(encoding="utf-8")
        return relative, source, target

    def test_azurecli_reordering_is_opt_in_and_command_changes_still_fail(self) -> None:
        header = "---\nlab:\n    title: 'Lab'\n---\n# \uc2e4\uc2b5\n\n"
        bash, powershell = shell_examples("azurecli", "Powershell")
        source = header + "1. Run the command.\n\n" + bash + "\n" + powershell
        target = header + "1. Run the command.\n\n" + powershell + "\n" + bash
        self.assertEqual([], self.validate_documents(source, target))
        strict_errors = self.validate_documents(
            source, target, prefer_powershell=False
        )
        self.assertTrue(
            any("fenced block changed or moved" in error for error in strict_errors)
        )
        changed = target.replace("Write-Output $env:NAME", "Write-Output $env:OTHER")
        errors = self.validate_documents(source, changed)
        self.assertTrue(
            any("fenced block changed or moved" in error for error in errors)
        )

    def test_bash_first_azurecli_pair_is_rejected(self) -> None:
        header = "---\nlab:\n    title: 'Lab'\n---\n# \uc2e4\uc2b5\n\n"
        bash, powershell = shell_examples("azurecli", "Powershell")
        text = header + "1. Run the command.\n\n" + bash + "\n" + powershell
        errors = self.validate_documents(text, text)
        self.assertTrue(any("not PowerShell first" in error for error in errors))

    def test_known_source_fence_and_visible_steps_validate(self) -> None:
        relative, source, target = self.management_documents()
        self.assertEqual([], self.validate_documents(source, target, relative))

    def test_preserved_source_comment_cannot_hide_a_changed_visible_command(self) -> None:
        relative, source, target = self.management_documents()
        changed = target.replace(
            '(Invoke-RestMethod -Uri "https://$FQDN/").model',
            '(Invoke-RestMethod -Uri "https://$FQDN/").other',
            1,
        )
        errors = self.validate_documents(source, changed, relative)
        self.assertTrue(
            any("fenced block changed or moved" in error for error in errors)
        )

    def test_changed_source_preservation_comment_is_rejected(self) -> None:
        relative, source, target = self.management_documents()
        comment = validator.COMMENTS.search(target)
        self.assertIsNotNone(comment)
        if comment is None:
            self.fail("Expected the exercise's source preservation comment")
        changed_comment = comment[0].replace(".model", ".other", 1)
        changed = target.replace(comment[0], changed_comment, 1)
        errors = self.validate_documents(source, changed, relative)
        self.assertTrue(any("preservation comment" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
