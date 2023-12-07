import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime

# function definition for getting the page
def get_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    return soup


@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


def get_company_names(file_name: str):
    company_stock = []
    with open(file_name, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace("\n", '')
            company_stock.append(line)
    return company_stock


def web_scrap_DSE_stocks(company_stock):
    main_url = "https://www.dsebd.org/displayCompany.php?name="

    # set up empty lists to catch each value
    closing_price = list()
    days_value_mn = list()
    days_volume = list()
    market_cap = list()
    paidup_cap = list()
    face_par_value = list()
    outstanding_securities = list()
    sect_lst = list()
    price_earnings_ratio = list()
    spons_dir_lst = list()
    govt = list()
    institute_lst = list()
    foreign_lst = list()
    public_lst = list()

    count = 0
    container = st.empty()

    for company_tckr in company_stock:
        count += 1
        url_to_scrap = main_url + company_tckr
        soup = get_page(url_to_scrap)

        # scrap each value to their own list
        closing_price.append(soup.find_all("table", class_="table table-bordered background-white")[0].find_all("td")[1].text)
        days_value_mn.append(soup.find_all("table", class_="table table-bordered background-white")[0].find_all("tr")[2].find_all("td")[1].text)
        days_volume.append(soup.find_all("table", class_="table table-bordered background-white")[0].find_all("tr")[4].find_all("td")[1].text)
        market_cap.append(soup.find_all("table", class_="table table-bordered background-white")[0].find_all("tr")[6].find_all("td")[1].text)
        paidup_cap.append(soup.find_all("table", class_="table table-bordered background-white")[1].find_all("tr")[1].find_all("td")[0].text)
        face_par_value.append(soup.find_all("table", class_="table table-bordered background-white")[1].find_all("tr")[2].find_all("td")[0].text)
        outstanding_securities.append(soup.find_all("table", class_="table table-bordered background-white")[1].find_all("tr")[3].find_all("td")[0].text)
        sect_lst.append(soup.find_all("table", class_="table table-bordered background-white")[1].find_all("tr")[3].find_all("td")[1].text)
        price_earnings_ratio.append(soup.find_all("table", class_="table table-bordered background-white")[4].find_all("tr")[1].find_all("td")[-1].text)
        spons_dir_lst.append(soup.find_all("table", class_="table table-bordered background-white")[9] \
        .find_all("tr", class_="alt")[-1] \
        .find_all("td")[2].text.split()[-1])
        govt.append(soup.find_all("table", class_="table table-bordered background-white")[9] \
        .find_all("tr", class_="alt")[-1] \
        .find_all("td")[3].text.split()[-1])
        institute_lst.append(soup.find_all("table", class_="table table-bordered background-white")[9] \
        .find_all("tr", class_="alt")[-1] \
        .find_all("td")[4].text.split()[-1])
        foreign_lst.append(soup.find_all("table", class_="table table-bordered background-white")[9] \
        .find_all("tr", class_="alt")[-1] \
        .find_all("td")[5].text.split()[-1])
        public_lst.append(soup.find_all("table", class_="table table-bordered background-white")[9] \
        .find_all("tr", class_="alt")[-1] \
        .find_all("td")[6].text.split()[-1])
        # give the user an update on percentage
        calc_perc = float(count/len(company_stock)) * 100
        container.write(f"{calc_perc:.02f}% Done")

    data_dict = {
        "tckr": company_stock,
        "close_price": closing_price,
        "days_value_mn": days_value_mn,
        "days_volumn": days_volume,
        "market_cap": market_cap,
        "paidup_cap": paidup_cap,
        "face_par_value": face_par_value,
        "outstanding_sec": outstanding_securities,
        "sector": sect_lst,
        "price_earnings_ratio": price_earnings_ratio,
        "sponsor_director": spons_dir_lst,
        "govt": govt,
        "institute": institute_lst,
        "foreign": foreign_lst,
        "public": public_lst
    }

    dataf = pd.DataFrame(data=data_dict)

    return dataf


current_date = datetime.date.today()
company_stock = get_company_names("tckr_lst.txt")

st.title("Dhaka Stock Exchange (DSE) Daily Web Scraper")
st.markdown("""
By: [Tahsin Jahin Khalid](https://tahsinjahinkhalid.github.io/)
""")
st.write(f"Today is {current_date}")

button_start = st.button("Begin Web Scraping", type="primary")
if button_start:
    df = web_scrap_DSE_stocks(company_stock)
    st.dataframe(df)

    # prep into CSV file
    csv = convert_df(df)

    st.download_button(
        "Press to Download",
        csv,
        f"dse_daily_tckr_data_{current_date}.csv",
        "text/csv",
        key='download-csv')
