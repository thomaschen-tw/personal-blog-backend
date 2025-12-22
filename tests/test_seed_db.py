import ast
from pathlib import Path
import pytest


def _load_generate_slug():
    # Locate the seed_db.py relative to this test file
    seed_path = Path(__file__).resolve().parents[1] / "scripts" / "seed_db.py"
    if not seed_path.exists():
        pytest.skip("scripts/seed_db.py not found; skipping generate_slug tests")

    source = seed_path.read_text(encoding="utf-8")
    module = ast.parse(source)

    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == "generate_slug":
            # extract the exact source lines for the function
            lines = source.splitlines()
            func_lines = lines[node.lineno - 1 : node.end_lineno]
            namespace = {"re": __import__("re")}
            exec("\n".join(func_lines), namespace)
            return namespace["generate_slug"]

    pytest.skip("generate_slug not defined in scripts/seed_db.py")


generate_slug = _load_generate_slug()


@pytest.mark.parametrize(
    "title,expected",
    [
        ("article1", "article1"),
        ("Article 1", "article-1"),
        ("My -- Title!!", "my-title"),
        ("  Leading and trailing  ", "leading-and-trailing"),
        ("multiple   spaces", "multiple-spaces"),
        ("special_chars*&^%$", "specialchars"),
        ("---already--dashed---", "already-dashed"),
        ("Title With NUMBERS 123", "title-with-numbers-123"),
    ],
)
def test_generate_slug_various(title, expected):
    assert generate_slug(title) == expected


def test_generate_slug_no_leading_trailing_or_double_hyphens():
	import ast
	from pathlib import Path
	import pytest


	def _load_generate_slug():
		# Locate the seed_db.py relative to this test file
		seed_path = Path(__file__).resolve().parents[1] / "scripts" / "seed_db.py"
		if not seed_path.exists():
			pytest.skip("scripts/seed_db.py not found; skipping generate_slug tests")

		source = seed_path.read_text(encoding="utf-8")
		module = ast.parse(source)

		for node in module.body:
			if isinstance(node, ast.FunctionDef) and node.name == "generate_slug":
				# extract the exact source lines for the function
				lines = source.splitlines()
				func_lines = lines[node.lineno - 1 : node.end_lineno]
				# ensure regex support is available when the function runs
				code = "import re\n" + "\n".join(func_lines)
				namespace = {}
				exec(code, namespace)
				return namespace["generate_slug"]

		pytest.skip("generate_slug not defined in scripts/seed_db.py")


	generate_slug = _load_generate_slug()


	@pytest.mark.parametrize(
		"title,expected",
		[
			("article1", "article1"),
			("Article 1", "article-1"),
			("My -- Title!!", "my-title"),
			("  Leading and trailing  ", "leading-and-trailing"),
			("multiple   spaces", "multiple-spaces"),
			("special_chars*&^%$", "specialchars"),
			("---already--dashed---", "already-dashed"),
			("Title With NUMBERS 123", "title-with-numbers-123"),
		],
	)
	def test_generate_slug_various(title, expected):
		assert generate_slug(title) == expected


	def test_generate_slug_no_leading_trailing_or_double_hyphens():
		s = generate_slug("  ---A   B---  ")
		assert not s.startswith("-")
		assert not s.endswith("-")
		assert "--" not in s
