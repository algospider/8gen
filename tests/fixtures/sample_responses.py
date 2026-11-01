"""Sample LLM test responses."""

SAMPLE_LLM_OUTPUT_WITH_MARKDOWN = """
Here is your retro arcade game:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Sample Asteroids</title>
</head>
<body>
  <canvas id="c" width="400" height="400"></canvas>
  <script>
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');
    function draw() {
      ctx.fillStyle = '#fff';
      ctx.fillRect(10, 10, 50, 50);
      requestAnimationFrame(draw);
    }
    draw();
  </script>
</body>
</html>
```
Enjoy playing!
"""
