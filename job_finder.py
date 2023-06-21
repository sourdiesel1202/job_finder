# This is a sample Python script.

# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from selenium.common.exceptions import TimeoutException
# "strain_keywords": ["haze", "skywalker", "sky walker", "afghan","pakistan", "hindu", "maui","afgoo" ,"hindi","diesel","crack", "cheese","dixie","khalifa", "syrup" ]
import csv
import itertools
import multiprocessing
import os
import traceback
import re

import cx_Oracle, json, pprint, sys, time
from datetime import datetime
import pandas as pd
from pandas import ExcelWriter
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from functions import  load_module_config,strip_special_chars,strip_alphabetic_chars,read_csv, write_csv as _write_csv
from tabulate import tabulate
# from ready_up import  initialize
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
module_config = load_module_config(__file__.split("/")[-1].split(".py")[0])
file_suffix = f"{datetime.now().strftime('%m-%d-%Y')}"
class Workbook:
    def __init__(self, name):
        self.sheets =[]
        self.workbook_name=f'{name}'
    def write_workbook(self):

        writer = ExcelWriter(self.workbook_name)

        for filename in self.sheets:
            df_csv = pd.read_csv(filename)

            (_, f_name) = os.path.split(filename)
            (f_shortname, _) = os.path.splitext(f_name)
            df_csv.to_excel(writer,filename.split('/')[-1].split('__')[0], index=False)
        writer.save()
global_workbook = Workbook(module_config['report_file'].replace('{date}', file_suffix))
def combine_outputs(pids, type):
    '''
    This function combines a series of output csvs into a single file. This is required as this script is multi-processed and issues can occur writing to the same file
    :param pids: the list of child processes that have written files
    :param environment: the environment the files are written in. this corresponds to a directory name in extracts/
    :return:
    '''
    print(f"Combining {len(pids)} .csv files from child processes into a singular extract")
    pass
    rows = []
    for i in range(0, len(pids)):
        print(f"Processing {type}{pids[i]}.csv")
        if i==0:
            #base case
            if f"{type}{pids[i]}.csv" in os.listdir():
                rows=read_csv(f"{type}{pids[i]}.csv")
        else:
            print(f"reading from temp file {type}{pids[i]}.csv")
            if f"{type}{pids[i]}.csv" in os.listdir():
                tmp_rows = read_csv(f"{type}{pids[i]}.csv")
                for i in range(1, len(tmp_rows)):
                    rows.append(tmp_rows[i])


    print(f"writing extraction file to {type}.csv")
    write_csv(f'{type}.csv',rows)
def build_webdriver():
    CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    CHROMEDRIVER_PATH ='../chromedriver'
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    # chrome_options.headless=True
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--start-minimized")
    chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

    driver = webdriver.Chrome(executable_path='../chromedriver', chrome_options=chrome_options)
    # driver = webdriver.Chrome('../chromedriver')
    driver.get(module_config['url']) #get auth first
    wait = WebDriverWait(driver, 180)

    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))).send_keys(module_config['username'])
    # username_field.send_keys(module_config['username'])
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="current-password"]'))).send_keys(module_config['password'])
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'button[data-id="sign-in-form__submit-btn"]'))).click()
    # password_field.
    # username_input = driver.find_element(By.CSS_SELECTOR, 'button[data-test="age-restriction-yes"]')
    # age_restriction_btn.click()
    return driver

def load_search_pages(driver, search_query):
    driver.get(f"{module_config['url']}/{module_config['jobs_endpoint']}/search/?keywords={search_query}&refresh=true")
    wait = WebDriverWait(driver, 60)

    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Show all filters. Clicking this button displays all available filter options."]'))).click()
    #ok so set our filter options
    #date posted
    for option in wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'input[name="date-posted-filter-value"]'))):
        label = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'label[for="{option.get_attribute("id")}"]')))
        if label.text.split("\n")[0].lower() == module_config['date_posted'].lower():
            label.click()
            break

    #experience level
    for option in wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'input[name="experience-level-filter-value"]'))):
        label = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'label[for="{option.get_attribute("id")}"]')))
        if label.text.split("\n")[0].lower() in [ x.lower() for x in module_config['experience_levels']]:
            label.click()
    #job_type
    for option in wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'input[name="job-type-filter-value"]'))):
        label = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'label[for="{option.get_attribute("id")}"]')))
        if label.text.split("\n")[0].lower() in [ x.lower() for x in module_config['job_types']]:
            label.click()
    #onsite/remote
    for option in wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'input[name="on-site/remote-filter-value"]'))):
        label = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'label[for="{option.get_attribute("id")}"]')))
        if label.text.split("\n")[0].lower() in [ x.lower() for x in module_config['onsite_remote']]:
            label.click()
    # easy_apply
    # if module_config['easy_apply']:
    #     easy_apply_btn = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'input[data-artdeco-toggle-button="true"]')))
    #     print(f'label[for="{easy_apply_btn.get_attribute("id")}"]')
    #     wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'span[class="artdeco-toggle__text"]'))).click()
    #industry
    for option in wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'input[name="industry-filter-value"]'))):
        label = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'label[for="{option.get_attribute("id")}"]')))
        if label.text.split("\n")[0].lower() in [ x.lower() for x in module_config['industries']]:
            label.click()
    #under 10 applicants
    # if module_config['under_10_applicants']:
        # easy_apply_btn = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'input[data-artdeco-toggle-button="true"]')))
    #process the boolean switches
    for option in wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'input[role="switch"]'))):
        label = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'label[for="{option.get_attribute("id")}"]')))
        print(label.text.split("\n")[0])
        #under 10 applicants
        if module_config['under_10_applicants'] and label.text.split("\n")[0].lower() =='toggle under 10 applicants filter':
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'div[id="{option.get_attribute("id").split("_")[1]}"]'))).click()
            # print("um not sure from here")
            # parent_div
        #in your network
        if module_config['in_your_network'] and label.text.split("\n")[0].lower() =='toggle in your network filter':
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'div[id="{option.get_attribute("id").split("_")[1]}"]'))).click()
        #easy apply
        if module_config['easy_apply'] and label.text.split("\n")[0].lower() =='toggle easy apply filter':
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'div[id="{option.get_attribute("id").split("_")[1]}"]'))).click()
        #fair chance
        if module_config['fair_chance_employee'] and label.text.split("\n")[0].lower() == 'toggle fair chance employer filter':
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'div[id="{option.get_attribute("id").split("_")[1]}"]'))).click()

        # if label.text.split("\n")[0].lower() in [ x.lower() for x in module_config['onsite_remote']]:

        # print(f'label[for="{easy_apply_btn.get_attribute("id")}"]')
        # wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'span[class="artdeco-toggle__text"]'))).click()
    #once we get here click show results

    wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, f'button[class="reusable-search-filters-buttons search-reusables__secondary-filters-show-results-button artdeco-button artdeco-button--2 artdeco-button--primary ember-view"]'))).click()
    print("fuckery duckery")
    #ok so here is the first bit
    # now we need to figure out how many pages there are
    # driver.find_elements()
    #add a manuel wait
    time.sleep(5)
    ul = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'ul[class="artdeco-pagination__pages artdeco-pagination__pages--number"]')))
    lis = ul.find_elements(By.CSS_SELECTOR, 'li')
    return [x.text for x in lis][-1]

    print('hmm')


def write_csv(filename, rows):
    with open(filename  , 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"Wrote file {filename}")
    global_workbook.sheets.append(filename)
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

def scrape_jobs(driver):
    # driver.get(f"{module_config['url']}/{module_config['jobs_endpoint']}/search/?keywords={search_query}&refresh=true")
    #assume url has already been updated

    wait = WebDriverWait(driver, 60)
    ul = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'ul[class="scaffold-layout__list-container"]')))
    # ul = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'div[class="jobs-unified-top-card__content--two-pane"]')))
    # ul =
    lis = ul.find_elements(By.CSS_SELECTOR, 'li')
    #ok so here we'll create our job dict
    job_dict = {}
    for li in lis:
        li_data = li.text.split('\n')
        if len(li_data) < 4:
            continue
        job_dict[li.get_attribute("data-occludable-job-id")]={"id":li.get_attribute("data-occludable-job-id")}
        if li_data[1].lower() in module_config['exclude_companies']:
            print(f"Ignoring jobs from {li_data[1]}")
            continue
        existing=False
        for v in job_dict.values():
            if 'title' in v and 'company' in v:
                if v['title']==li_data[0] and v['company'] == li_data[1]:
                    existing=True
                    break
        if existing:
            break
        # if li_data[0] in [x['title'] for x in job_dict.values()]  li_data[0] in [x['title'] for x in job_dict.values()]
        job_dict[li.get_attribute("data-occludable-job-id")]["title"]=li_data[0]
        job_dict[li.get_attribute("data-occludable-job-id")]["company"]=li_data[1]
        job_dict[li.get_attribute("data-occludable-job-id")]["based_in"]=li_data[2]
        job_dict[li.get_attribute("data-occludable-job-id")]["location"]=li_data[3]

    #ok so once we have our job dict, we need to iterate over each of these and parse the data
    for k,v in job_dict.items():
        try:
            url_data = {x.split('=')[0]: x.split('=')[1] for x in driver.current_url.split('?')[1].split('&')}
            url_data['currentJobId']=k
            new_url = f"{driver.current_url.split('?')[0]}?{'&'.join([k+'='+v for k,v in url_data.items()])}"
            print(new_url)
            driver.get(new_url)
            time.sleep(2)
            top_div = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'div[class="jobs-unified-top-card__content--two-pane"]')))
            description_div = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f'div[id="job-details"]')))
            print("asdf")
            top_div_data = top_div.text.split('\n')

            if 'applicant' in top_div_data[1]:
                job_dict[k]['applicants']=top_div_data[1].split(' ')[2:][0]
            job_dict[k]['employees']=top_div_data[3].split('·')[0].strip()

            job_dict[k]['description']=description_div.text
            job_dict[k]['link']=driver.current_url
        except Exception as e:
            print(f"Unable to load data for job {k}:{v['title']} {str(e)}")
    print("fuckd")

    # class="scaffold - layout__list - container"
def find_jobs(driver):
    for query in module_config['search_queries']:
        # print(f"Found {load_search_pages(driver,query)} pages of jobs")
        total_pages =load_search_pages(driver,query)
        scrape_jobs(driver)
        #ok so iterate over the pages, updating URL accordingly
        # ok so now that we have total pages, we want to get the job data from each page
        #todo add multiprocessing
if __name__ == '__main__':
    driver = build_webdriver()
    # for query in module_config
    find_jobs(driver)
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
