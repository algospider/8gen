"""Unit tests for HTML extractor."""

from eightgen.core.extractor import HTMLExtractor

SAMPLE_MARKDOWN = """Here is your game!
```html
<!DOCTYPE html>
<html>
<head><title>Test Game</title></head>
<body><canvas id="c"></canvas><script>console.log("running");</script></body>
</html>
```
Enjoy playing!
"""

SAMPLE_RAW_HTML = """
<!DOCTYPE html>
<html>
<head><title>Raw Test</title></head>
<body><canvas id="c"></canvas><script>console.log("running");</script></body>
</html>
"""


def test_extract_from_markdown():
    extracted = HTMLExtractor.extract(SAMPLE_MARKDOWN)
    assert "<!DOCTYPE html>" in extracted
    assert "<canvas id=\"c\">" in extracted
    assert "Here is your game!" not in extracted
    assert "Enjoy playing!" not in extracted


def test_extract_from_raw():
    extracted = HTMLExtractor.extract(SAMPLE_RAW_HTML)
    assert "<!DOCTYPE html>" in extracted
    assert "Raw Test" in extracted


def test_extract_empty():
    assert HTMLExtractor.extract("") == ""
    assert HTMLExtractor.extract("   ") == ""
    assert HTMLExtractor.extract("Just some random conversational text without code.") == ""
