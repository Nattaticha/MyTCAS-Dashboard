from playwright.sync_api import sync_playwright
import pandas as pd
import time

def scrape_tcas_to_csv(keywords):
    all_data = []  # รวมข้อมูลทั้งหมด

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.mytcas.com/")  # URL จริงของ TCAS

        for keyword in keywords:
            print(f"\n🔍 Searching for: {keyword}")
            
            page.fill('input#search', '')
            page.fill('input#search', keyword)
            time.sleep(2)

            page.wait_for_selector("ul.t-programs li", timeout=10000)
            results = page.query_selector_all("ul.t-programs li")

            print(f"🧾 Found {len(results)} results for '{keyword}'")

            for i, li in enumerate(results):
                link = li.query_selector("a")
                href = link.get_attribute("href")

                if href:
                    detail_page = browser.new_page()
                    detail_page.goto(href)
                    detail_page.wait_for_load_state("load")

                    print(f"\n📄 [{keyword}] Result {i+1}: {href}")

                    try:
                        # รอ <li id="overview"> ที่อยู่ใน <main>
                        detail_page.wait_for_selector("li#overview dl", timeout=10000)
                        dt_tags = detail_page.query_selector_all("li#overview dl dt")
                        dd_tags = detail_page.query_selector_all("li#overview dl dd")

                        if dt_tags and dd_tags:
                            data = {"Keyword": keyword, "URL": href}
                            for dt, dd in zip(dt_tags, dd_tags):
                                dt_text = dt.inner_text().strip()
                                dd_text = dd.inner_text().strip()
                                data[dt_text] = dd_text
                            all_data.append(data)
                        else:
                            print("⚠️ No data found in detail page.")
                    except Exception as e:
                        print("❌ Error:", e)
                    finally:
                        detail_page.close()

        browser.close()

    # สร้าง DataFrame และบันทึกเป็น CSV
    df = pd.DataFrame(all_data)
    df.to_csv("tcas_data.csv", index=False, encoding="utf-8-sig")
    print("\n✅ Data saved to tcas_data.csv")

if __name__ == "__main__":
    keywords = ["วิศวกรรมคอมพิวเตอร์","วิศวกรรมปัญญาประดิษฐ์"]
    scrape_tcas_to_csv(keywords)
