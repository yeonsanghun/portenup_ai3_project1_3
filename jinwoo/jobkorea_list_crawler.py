#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🤖 이 소스코드는 100% GitHub Copilot으로 생성되었습니다.
================================================================================

잡코리아 채용 공고 목록 크롤러
- 키워드 검색 기반 채용 공고 제목, 회사명, URL 수집
- Selenium 사용

작성일: 2026-02-02
작성자: GitHub Copilot
================================================================================
"""
import urllib
from base64 import encode

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import pandas as pd
import time

# 크롤링할 페이지 수
MAX_PAGES = 100

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 디버깅을 위해 주석 처리
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

# ChromeDriver 자동 설치 및 실행
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 결과를 저장할 리스트
dict_list = {
    "title": [],
    "company": [],
    "url": []
}

print("="*70)
print("잡코리아 채용 공고 크롤링 시작")
print("="*70)

try:
    for page_no in range(1, MAX_PAGES + 1):
        print(f"\n{'='*70}")
        print(f"페이지 {page_no} 크롤링 시작...")
        print(f"{'='*70}")

        keyword = "AI 에이전트"
        encoded_keyword = urllib.parse.quote(keyword)
        # 페이지별 URL (AI엔지니어 검색)
        url = f"https://www.jobkorea.co.kr/Search/?stext={encoded_keyword}&Page_No={page_no}"
        print(f"URL: {url}")

        driver.get(url)
        time.sleep(5)  # 페이지 로딩 대기

        try:
            title_list = []
            company_list = []
            url_list = []

            print("채용 공고 카드 찾는 중...")

            # 채용 공고 카드 찾기 (Box 컴포넌트)
            cards = driver.find_elements(By.CSS_SELECTOR, "div.dlua7o0")

            if not cards:
                print(f"  [ERROR] 채용 공고 카드를 찾을 수 없습니다")
                break

            print(f"  [OK] {len(cards)}개의 채용 공고 카드 발견")

            # URL 중복 제거를 위한 set
            seen_urls = set()

            # 각 카드에서 정보 추출
            for idx, card in enumerate(cards, 1):
                try:
                    # 카드 내의 모든 링크 찾기
                    links = card.find_elements(By.CSS_SELECTOR, "a[href*='/Recruit/GI_Read/']")

                    if not links:
                        continue

                    # 첫 번째 링크 사용 (제목 링크)
                    link = links[0]
                    href = link.get_attribute('href')

                    # 중복 URL 제거
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    # 제목 추출
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "span.Typography_variant_size18__344nw25")
                        title = title_elem.text.strip()
                    except:
                        title = "제목 미확인"

                    # 회사명 추출
                    try:
                        company_elem = card.find_element(By.CSS_SELECTOR, "span.Typography_variant_size16__344nw26")
                        company = company_elem.text.strip()
                    except:
                        company = "회사명 미확인"

                    if href and title:
                        title_list.append(title)
                        company_list.append(company)
                        url_list.append(href)

                        if idx <= 3:  # 처음 3개만 출력
                            print(f"  [{idx}] {title[:50]}... | {company}")

                except Exception as e:
                    continue

            print(f"\n  추출 완료 - 제목: {len(title_list)}, 회사: {len(company_list)}, URL: {len(url_list)}")

            # 1:1:1 매칭 검증
            if len(title_list) == len(company_list) == len(url_list):
                dict_list["title"].extend(title_list)
                dict_list["company"].extend(company_list)
                dict_list["url"].extend(url_list)
                print(f"  [OK] 데이터 매칭 성공 - {len(title_list)}건 추가")
            else:
                print(f"  [WARN] 데이터 불일치! 제목:{len(title_list)}, 회사:{len(company_list)}, URL:{len(url_list)}")
                min_len = min(len(title_list), len(company_list), len(url_list))
                dict_list["title"].extend(title_list[:min_len])
                dict_list["company"].extend(company_list[:min_len])
                dict_list["url"].extend(url_list[:min_len])
                print(f"  [FIX] {min_len}개만 추가")

        except TimeoutException as te:
            print(f"  [ERROR] 타임아웃 오류: {str(te)[:100]}")
            print(f"  페이지 {page_no}를 건너뜁니다.")
            continue
        except Exception as e:
            print(f"  [ERROR] 페이지 {page_no} 크롤링 오류: {type(e).__name__}")
            print(f"  오류 상세: {str(e)[:200]}")
            import traceback
            traceback.print_exc()
            continue

except KeyboardInterrupt:
    print("\n\n[WARN] 사용자에 의해 중단되었습니다.")
except Exception as e:
    print(f"\n\n[ERROR] 예상치 못한 에러 발생: {type(e).__name__}")
    print(f"에러 상세: {str(e)[:200]}")
    import traceback
    traceback.print_exc()

finally:
    try:
        # 최종 1:1:1 매칭 검증
        print(f"\n{'='*70}")
        print(f"크롤링 완료!")
        print(f"{'='*70}")
        print(f"총 제목: {len(dict_list['title'])}개")
        print(f"총 회사: {len(dict_list['company'])}개")
        print(f"총 URL: {len(dict_list['url'])}개")

        if len(dict_list['title']) == len(dict_list['company']) == len(dict_list['url']):
            print(f"[OK] 1:1:1 매칭 성공!")
        else:
            print(f"[ERROR] 데이터 불일치 발견!")
            min_len = min(len(dict_list['title']), len(dict_list['company']), len(dict_list['url']))
            print(f"[WARN]  {min_len}개만 저장합니다.")
            dict_list['title'] = dict_list['title'][:min_len]
            dict_list['company'] = dict_list['company'][:min_len]
            dict_list['url'] = dict_list['url'][:min_len]

        # DataFrame 생성 및 저장
        df = pd.DataFrame(dict_list)
        df.to_csv('jobkorea_crawler_agent.csv', index=False, encoding='utf-8-sig')

        print(f"\n데이터 저장 완료: jobkorea_crawler_agent.csv")
        print(f"저장된 데이터: {len(df)}건")
        print(f"{'='*70}\n")

    except Exception as save_error:
        print(f"데이터 저장 중 에러 발생: {save_error}")
    finally:
        driver.quit()
