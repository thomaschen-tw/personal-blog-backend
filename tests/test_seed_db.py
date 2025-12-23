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
            namespace = {}
            exec("\n".join(func_lines), namespace)
            return namespace["generate_slug"]

    pytest.skip("generate_slug not defined in scripts/seed_db.py")


generate_slug = _load_generate_slug()


@pytest.mark.parametrize(
    "title,index,expected",
    [
        ("article1", 1, "article-1"),
        ("Article 1", 2, "article-2"),
        ("My -- Title!!", 3, "article-3"),
        ("  Leading and trailing  ", 4, "article-4"),
        ("multiple   spaces", 5, "article-5"),
        ("special_chars*&^%$", 6, "article-6"),
        ("---already--dashed---", 7, "article-7"),
        ("Title With NUMBERS 123", 8, "article-8"),
    ],
)
def test_generate_slug_various(title, index, expected):
    """Test that generate_slug returns article-{index} format regardless of title."""
    assert generate_slug(title, index) == expected


def test_generate_slug_format():
    """Test that generate_slug always returns article-{index} format."""
    # The function should always return article-{index} regardless of title
    s1 = generate_slug("Any Title", 1)
    assert s1 == "article-1"
    
    s2 = generate_slug("  ---A   B---  ", 42)
    assert s2 == "article-42"
    
    # Verify format consistency
    assert s1.startswith("article-")
    assert s2.startswith("article-")
