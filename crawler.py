import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

BASE_URL = "https://muqawil.org/en/contractors"

def fetch_content(url):
    # chrome setup 
    driver = webdriver.Chrome()  
    driver.get(url)

    # wait for all card to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "section-card"))
    )
    # pass html to BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    return soup

def fetch_data(page_url):
    # fetch data from each page
    data = fetch_content(page_url)

    companies = []
    # loop for each card to fetch data
    for card in data.select(".section-card"):  # Contractor card
        company_info = {}

        # extract Company Name
        company_name = card.find("h3", class_="card-title")
        company_info["Company Name"] = company_name.text.strip() if company_name else "N/A"

        # extract Membership Number and City
        for info_box in card.select(".col-md-6"):
            label = info_box.find("div", class_="info-name")
            value = info_box.find("div", class_="info-value")
            if label and value:
                field_name = label.text.strip()
                if field_name == "Membership Number" or field_name == "City":  
                    company_info[field_name] = value.text.strip()

        # extract Activities
        activities = card.select("ul.list.list-numerical > li.list-item")
        company_info["Activities"] = ", ".join([activity.text.strip() for activity in activities])

        # extract Email
        company_email = card.find("a", href=lambda href: href and "mailto:" in href)
        company_info["Email"] = company_email['href'].replace("mailto:", "").strip() if company_email else "N/A"

        companies.append(company_info)
    return companies

def crawl_pages(pages=10):
    # loop through pages to get data
    info = []
    for page in range(1, pages + 1):
        print(f"Crawling page {page}...")
        page_url = f"{BASE_URL}?page={page}"
        info.extend(fetch_data(page_url))
    return info

if __name__ == "__main__":
    # Crawl 10 pages
    data = crawl_pages(10) 
    
    # Create an excel file to store data
    df = pd.DataFrame(data)
    df.to_excel("contractors.xlsx", index=False)
    print("Data successfully saved to contractors.xlsx")
