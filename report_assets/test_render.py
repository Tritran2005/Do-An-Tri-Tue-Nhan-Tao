import re, os, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image

def test():
    md_path = r'd:\DDTTNT\NEWS_SYSTEM_DIAGRAMS.md'
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    blocks = re.findall(r'```mermaid\n(.*?)\n```', text, re.DOTALL)
    assets_dir = r'd:\DDTTNT\report_assets'
    temp_html = os.path.join(assets_dir, 'render_temp.html')
    js_url = f"file:///{os.path.join(assets_dir, 'mermaid.min.js').replace(os.sep, '/')}"

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=2400,1800')
    chrome_options.add_argument('--force-device-scale-factor=2')

    driver = webdriver.Chrome(options=chrome_options)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="{js_url}"></script>
    <style>
        body {{
            margin: 0;
            padding: 30px;
            background: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        #diagram {{
            width: 1200px;
            background: #ffffff;
            padding: 20px;
        }}
        svg {{
            width: 100% !important;
            height: auto !important;
        }}
    </style>
</head>
<body>
    <div id="diagram" class="mermaid">
{blocks[0].strip()}
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default'
        }});
    </script>
</body>
</html>"""
    with open(temp_html, 'w', encoding='utf-8') as hf:
        hf.write(html)

    driver.get(f"file:///{temp_html.replace(os.sep, '/')}")
    time.sleep(2.0)

    elem = driver.find_element(By.ID, 'diagram')
    out_p = os.path.join(assets_dir, 'hinh_3_1_use_case.png')
    elem.screenshot(out_p)
    driver.quit()

    print("Rendered hinh_3_1_use_case:", Image.open(out_p).size)

if __name__ == '__main__':
    test()
