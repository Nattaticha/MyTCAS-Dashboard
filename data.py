from playwright.sync_api import sync_playwright
import pandas as pd
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.mytcas.com/search")

    # ค้นหา
    page.fill("input[placeholder='พิมพ์ชื่อมหาวิทยาลัย คณะ หรือหลักสูตร']", "วิศวกรรมคอมพิวเตอร์")
    page.keyboard.press("Enter")

    # ✅ รอผลลัพธ์โหลด (ตรง class ที่เจอ)
    page.wait_for_selector(".t-sec.p-0", timeout=60000)

    # ✅ ดึง element หลัก
    results = page.query_selector_all(".t-sec.p-0")

    data = []

    for result in results:
        name_el = result.query_selector(".program-name")  # ตรวจว่า class นี้มีจริงหรือไม่
        uni_el = result.query_selector(".university-name")

        name = name_el.inner_text().strip() if name_el else "-"
        uni = uni_el.inner_text().strip() if uni_el else "-"

        # ดึงค่าใช้จ่ายจาก <dt> ค่าใช้จ่าย <dd>
        fee = "-"
        dts = result.query_selector_all("dt")
        dds = result.query_selector_all("dd")
        for dt, dd in zip(dts, dds):
            if "ค่าใช้จ่าย" in dt.inner_text():
                fee = dd.inner_text().replace("== $0", "").strip()
                break

        data.append({
            "คณะ": name,
            "มหาวิทยาลัย": uni,
            "ค่าเทอม": fee
        })

    df = pd.DataFrame(data)
    df.to_excel("tcas_search.xlsx", index=False)
    print("✅ บันทึกข้อมูลแล้วเป็น tcas_search.xlsx")
    browser.close()
