import pandas as pd
from selenium.common import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

import time

driver = webdriver.Chrome()  # 크롬 브라우저 실행
driver.maximize_window()  # 창 최대화
wait = WebDriverWait(driver, 10)

url = "https://www.jobkorea.co.kr/"
driver.get(url)

ad_close = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.Modal_close__1qbupvqk")))
ad_close.click()

keyword = "AI엔지니어"
search_bar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='JOB 검색']")))
search_bar.click()
search_bar.clear()
search_bar.send_keys(keyword)
search_bar.send_keys(Keys.ENTER)

# driver.get(f"https://www.jobkorea.co.kr/Search/?stext=AI%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8&Page_No={pageno}")


# titles = wait.until(EC.presence_of_all_elements_located(
#    (By.XPATH, "//span[contains(@class, 'Typography_variant_size18')]/ancestor::a")))
# companies = wait.until(EC.presence_of_all_elements_located(
#    (By.XPATH, "//a[span[contains(@class, 'Typography_variant_size16')]]")))
# recruits = wait.until(EC.presence_of_all_elements_located(
#    (By.XPATH, "//a[contains(@href, '/Recruit/GI_Read')]")))

dict_list = {

}


dict_list["title"] = list()
dict_list["company"] = list()
dict_list["url"] = list()

max_page = 20
try:
    for page_no in range(1, max_page + 1):
        try:
            el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '검색결과가 없습니다.')]")))
        except TimeoutException:
            print(f"{TimeoutException} 터짐")

        title_list = []
        company_list = []
        duplicate_remover = set()

        driver.get(f"https://www.jobkorea.co.kr/Search/?stext={quote(keyword)}&Page_No={page_no}")
        titles = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//span[contains(@class, 'Typography_variant_size18')]/ancestor::a")))
        companies = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//a[span[contains(@class, 'Typography_variant_size16')]]")))
        recruits = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//a[contains(@href, '/Recruit/GI_Read')]")))

        for title in titles:
            str_title = title.text
            if str_title != "":
                title_list.append(str_title)
        dict_list["title"].extend(title_list)
        print(f"타이틀 개수 : {len(title_list)}")

        for company in companies:
            str_company = company.text
            if str_company != "":
                company_list.append(str_company)
        dict_list["company"].extend(company_list)
        print(f"회사이름 개수 : {len(company_list)}")

        for recruit in recruits:
            href = recruit.get_attribute("href")
            duplicate_remover.add(href)
        dict_list["url"].extend(list(duplicate_remover))
        print(f"url 개수 : {len(duplicate_remover)}")
except Exception as e:
    print("에러 발생:", e)

finally:
    try:
        df = pd.DataFrame(dict_list)
        df.to_csv("jobkorea_crawler_engineer.csv", index=False, encoding="utf-8-sig")
        driver.quit()
    except Exception as e:
        print("데이터 저장 중 에러 발생:", e)
    finally:
        print(dict_list.items())
        driver.quit()
