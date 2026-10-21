import markdown
import os

with open('VISTA_Final_Document.md', 'r', encoding='utf-8') as f:
    text = f.read()

html_content = markdown.markdown(text, extensions=['tables'])

full_html = f"""<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
        img {{ max-width: 100%; height: auto; }}
        h1, h2, h3 {{ color: #333; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

with open('VISTA_Final_Document.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("HTML generated successfully.")
