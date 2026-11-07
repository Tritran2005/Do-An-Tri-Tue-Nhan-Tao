import os, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image

def capture_ui():
    assets_dir = r'd:\DDTTNT\report_assets'
    os.makedirs(assets_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1400,900')
    chrome_options.add_argument('--force-device-scale-factor=1.5')

    driver = webdriver.Chrome(options=chrome_options)

    # 1. Hình 3.14: Job Board
    print("Capturing Hình 3.14: Job Board...")
    driver.get("http://127.0.0.1:8000/jobs/")
    time.sleep(2)
    p_3_14 = os.path.join(assets_dir, 'hinh_3_14_job_board.png')
    driver.save_screenshot(p_3_14)
    print(f"Saved {p_3_14}: {Image.open(p_3_14).size}")

    # 2. Hình 3.15: Job Detail
    print("Capturing Hình 3.15: Job Detail...")
    driver.get("http://127.0.0.1:8000/jobs/1/")
    time.sleep(2)
    p_3_15 = os.path.join(assets_dir, 'hinh_3_15_job_detail.png')
    driver.save_screenshot(p_3_15)
    print(f"Saved {p_3_15}: {Image.open(p_3_15).size}")

    # 3. Hình 3.16: Apply Form
    print("Capturing Hình 3.16: Apply Form...")
    # Scroll down to apply form or take screenshot of form container
    driver.execute_script("window.scrollTo(0, 600);")
    time.sleep(1)
    p_3_16 = os.path.join(assets_dir, 'hinh_3_16_apply_form.png')
    driver.save_screenshot(p_3_16)
    print(f"Saved {p_3_16}: {Image.open(p_3_16).size}")

    # 4. Hình 3.17: Login
    print("Capturing Hình 3.17: Login...")
    driver.get("http://127.0.0.1:8000/accounts/login/")
    time.sleep(2)
    p_3_17 = os.path.join(assets_dir, 'hinh_3_17_login.png')
    driver.save_screenshot(p_3_17)
    print(f"Saved {p_3_17}: {Image.open(p_3_17).size}")

    # 5. Hình 3.18: Register
    print("Capturing Hình 3.18: Register...")
    driver.get("http://127.0.0.1:8000/accounts/register/")
    time.sleep(2)
    p_3_18 = os.path.join(assets_dir, 'hinh_3_18_register.png')
    driver.save_screenshot(p_3_18)
    print(f"Saved {p_3_18}: {Image.open(p_3_18).size}")

    # Now Login as HR
    print("Logging in as hr_demo...")
    driver.get("http://127.0.0.1:8000/accounts/login/")
    time.sleep(1)
    try:
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("hr_demo")
        password_input.send_keys("123456")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        time.sleep(2)
        print("Logged in, current URL:", driver.current_url)
    except Exception as e:
        print("Login error:", e)

    # 6. Hình 3.19: HR Dashboard
    print("Capturing Hình 3.19: HR Dashboard...")
    driver.get("http://127.0.0.1:8000/jobs/hr/dashboard/")
    time.sleep(2)
    p_3_19 = os.path.join(assets_dir, 'hinh_3_19_hr_dashboard.png')
    driver.save_screenshot(p_3_19)
    print(f"Saved {p_3_19}: {Image.open(p_3_19).size}")

    # 7. Hình 3.20: Candidate Ranking
    print("Capturing Hình 3.20: Candidate Ranking...")
    driver.get("http://127.0.0.1:8000/jobs/hr/job/1/ranking/")
    time.sleep(2)
    p_3_20 = os.path.join(assets_dir, 'hinh_3_20_candidate_ranking.png')
    driver.save_screenshot(p_3_20)
    print(f"Saved {p_3_20}: {Image.open(p_3_20).size}")

    # 8. Hình 3.21: AI Analysis Detail
    print("Capturing Hình 3.21: AI Analysis Detail...")
    driver.get("http://127.0.0.1:8000/jobs/hr/application/3/detail/")
    time.sleep(2)
    p_3_21 = os.path.join(assets_dir, 'hinh_3_21_ai_analysis_detail.png')
    driver.save_screenshot(p_3_21)
    print(f"Saved {p_3_21}: {Image.open(p_3_21).size}")

    driver.quit()
    print("All UI screenshots captured successfully!")

if __name__ == '__main__':
    capture_ui()
