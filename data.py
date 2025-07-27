from playwright.sync_api import sync_playwright 
import pandas as pd
import time
import re

def scrape_tcas_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print("🔍 เข้าสู่เว็บไซต์ TCAS...")
            page.goto("https://www.mytcas.com/search", wait_until="networkidle")

            print("🔍 ค้นหา 'วิศวกรรมคอมพิวเตอร์'...")
            search_input = page.locator("input[type='text']")
            search_input.fill("วิศวกรรมคอมพิวเตอร์")
            search_input.press("Enter")

            print("⏳ รอผลการค้นหา...")
            try:
                page.wait_for_selector("li, .card, .item, .program-card", timeout=15000)
            except:
                print("⚠️ ไม่พบ selector สำหรับผลการค้นหา กำลังลองใช้เวลารอแทน...")
                time.sleep(10)

            items = page.locator("li, .item, .card, .program-card").all()
            data = []

            print(f"🔍 ตรวจสอบทั้งหมด {len(items)} รายการ")

            for i, item in enumerate(items):
                try:
                    item_text = item.inner_text()
                    if "วิศวกรรมคอมพิวเตอร์" in item_text or "คอมพิวเตอร์" in item_text:
                        program_name = "-"
                        university_name = "-"
                        fee_text = "-"

                        # --- หาชื่อหลักสูตร ---
                        program_selectors = [".program-name", ".course-name", "h3", "h4", ".title"]
                        for sel in program_selectors:
                            if item.locator(sel).count() > 0:
                                program_name = item.locator(sel).first.inner_text()
                                break
                        if program_name == "-":
                            for line in item_text.split('\n'):
                                if "วิศวกรรม" in line or "คอมพิวเตอร์" in line:
                                    program_name = line.strip()
                                    break

                        # --- หาชื่อมหาวิทยาลัย ---
                        uni_selectors = [".university-name", ".school-name", ".institution", ".uni"]
                        for sel in uni_selectors:
                            if item.locator(sel).count() > 0:
                                university_name = item.locator(sel).first.inner_text()
                                break
                        if university_name == "-":
                            for line in item_text.split("\n"):
                                if "มหาวิทยาลัย" in line:
                                    university_name = line.strip()
                                    break

                        # --- ดึงค่าใช้จ่าย ---
                        try:
                            detail_section = item
                            dt_locator = detail_section.locator("xpath=.//dt[normalize-space(text())='ค่าใช้จ่าย']")
                            if dt_locator.count() > 0:
                                fee_text = dt_locator.nth(0).evaluate("""
                                    el => {
                                        const dd = el.nextElementSibling;
                                        if (!dd) return "-";
                                        return dd.innerText || dd.textContent || "-";
                                    }
                                """)
                        except Exception as e:
                            print(f"⚠️ ข้ามรายการ {i+1} (ดึงค่าใช้จ่าย) เนื่องจาก: {e}")

                        # --- เก็บข้อมูล ---
                        if program_name != "-" or university_name != "-":
                            data.append({
                                "หลักสูตร": program_name.strip(),
                                "มหาวิทยาลัย": university_name.strip(),
                                "ค่าเทอม": fee_text.strip()
                            })
                            print(f"📝 [{i+1}] {program_name[:40]} | {university_name[:30]} | {fee_text}")

                except Exception as e:
                    print(f"⚠️ ข้ามรายการ {i+1} เนื่องจากข้อผิดพลาด: {e}")

        finally:
            print("⏳ รอ 3 วินาทีก่อนปิดเบราว์เซอร์...")
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    scrape_tcas_data()
