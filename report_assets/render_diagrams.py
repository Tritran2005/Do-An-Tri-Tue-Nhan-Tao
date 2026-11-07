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
    chrome_options.add_argument('--window-size=2400,1600')
    chrome_options.add_argument('--force-device-scale-factor=2')

    driver = webdriver.Chrome(options=chrome_options)

    filenames = [
        "hinh_3_1_use_case.png",
        "hinh_3_2_bfd.png",
        "hinh_3_3_ifd_nop_cv.png",
        "hinh_3_4_ifd_quan_ly_tin.png",
        "hinh_3_5_ifd_quan_tri.png",
        "hinh_3_6_context_dfd.png",
        "hinh_3_7_dfd_muc_0.png",
        "hinh_3_8_dfd_muc_1_ai.png",
        "hinh_3_9_dfd_muc_1_ranking.png",
        "hinh_3_10_dfd_muc_1_auth.png",
        "hinh_3_11_erd.png",
        "hinh_3_12_relational_schema.png",
        "hinh_3_13_class_diagram.png"
    ]

    for idx, (code, fname) in enumerate(zip(blocks, filenames)):
        print(f"[{idx+1}/{len(blocks)}] Rendering {fname}...")
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
            display: inline-block;
        }}
        #diagram {{
            background: #ffffff;
            padding: 20px;
        }}
        svg {{
            max-width: none !important;
        }}
    </style>
</head>
<body>
    <div id="diagram" class="mermaid">
{code.strip()}
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                fontFamily: 'Segoe UI, Arial, sans-serif',
                fontSize: '15px',
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
            
            # verify image
            img = Image.open(out_path)
            print(f"   -> Success: {out_path} ({img.size[0]}x{img.size[1]})")
        except Exception as e:
            print(f"   -> Error rendering {fname}: {e}")

    driver.quit()
    print("All diagrams rendered successfully!")

if __name__ == '__main__':
    main()
