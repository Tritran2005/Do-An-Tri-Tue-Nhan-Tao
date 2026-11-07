import re, os, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image

def main():
    md_path = r'd:\DDTTNT\NEWS_SYSTEM_DIAGRAMS.md'
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    blocks = re.findall(r'```mermaid\n(.*?)\n```', text, re.DOTALL)
    print(f"Loaded {len(blocks)} diagrams from {md_path}")

    assets_dir = r'd:\DDTTNT\report_assets'
    os.makedirs(assets_dir, exist_ok=True)
    temp_html = os.path.join(assets_dir, 'render_temp.html')
    js_url = f"file:///{os.path.join(assets_dir, 'mermaid.min.js').replace(os.sep, '/')}"

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=2600,2000')
    chrome_options.add_argument('--force-device-scale-factor=2')

    driver = webdriver.Chrome(options=chrome_options)

    # Filenames and widths
    diagram_configs = [
        (0, "hinh_3_1_use_case.png", 1200),
        # 1 is BFD, already rendered as high-res from redesigned HTML
        (2, "hinh_3_3_ifd_nop_cv.png", 1200),
        (3, "hinh_3_4_ifd_quan_ly_tin.png", 1200),
        (4, "hinh_3_5_ifd_quan_tri.png", 1100),
        (5, "hinh_3_6_context_dfd.png", 1100),
        (6, "hinh_3_7_dfd_muc_0.png", 1200),
        (7, "hinh_3_8_dfd_muc_1_ai.png", 1200),
        (8, "hinh_3_9_dfd_muc_1_ranking.png", 1100),
        (9, "hinh_3_10_dfd_muc_1_auth.png", 1100),
        (10, "hinh_3_11_erd.png", 1300),
        (11, "hinh_3_12_relational_schema.png", 1300),
        (12, "hinh_3_13_class_diagram.png", 1300),
    ]

    for block_idx, fname, width in diagram_configs:
        code = blocks[block_idx].strip()
        print(f"Rendering {fname} (width={width}px)...")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="{js_url}"></script>
    <style>
        body {{
            margin: 0;
            padding: 25px;
            background: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        #diagram {{
            width: {width}px;
            background: #ffffff;
            padding: 15px;
            box-sizing: border-box;
        }}
        svg {{
            width: 100% !important;
            height: auto !important;
        }}
    </style>
</head>
<body>
    <div id="diagram" class="mermaid">
{code}
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                fontFamily: 'Segoe UI, Arial, sans-serif',
                fontSize: '14px',
                primaryColor: '#e8f0fe',
                primaryBorderColor: '#1a73e8',
                primaryTextColor: '#174ea6',
                lineColor: '#5f6368',
                secondaryColor: '#f1f3f4',
                tertiaryColor: '#ffffff'
            }}
        }});
    </script>
</body>
</html>"""
        with open(temp_html, 'w', encoding='utf-8') as hf:
            hf.write(html)

        driver.get(f"file:///{temp_html.replace(os.sep, '/')}")
        time.sleep(2.0)

        out_path = os.path.join(assets_dir, fname)
        try:
            elem = driver.find_element(By.ID, 'diagram')
            elem.screenshot(out_path)
            img = Image.open(out_path)
            print(f"   -> Success: {fname} ({img.size[0]}x{img.size[1]})")
        except Exception as e:
            print(f"   -> Error: {fname}: {e}")

    driver.quit()
    print("All HD diagrams rendered successfully!")

if __name__ == '__main__':
    main()
