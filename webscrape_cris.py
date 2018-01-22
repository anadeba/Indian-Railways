from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import pandas as pd
import datetime
import numpy as np
import os


def scrape_modal_window():
    browser.find_element_by_xpath('//*[(@id = "viaStnRefreshBtn")]').click()
    time.sleep(10)
    return browser.find_element_by_css_selector('.ui-dialog-content div .allTrainsViaStn').text

def text_to_frame(text):
    df2 = pd.DataFrame(columns = ['Train_Number', 'Train_Name', 'Source', 'Destination', 'Expected_Arrival', 'Delay_in_Arrival', 'Expected_Departure', 'Delay_in_Departure', 'Expected_Platform', 'Recorded_On'])
    lst = text.splitlines()
    if lst[0].strip() == 'No record found':
        return df2
    for line in lst:
        line = line.split(' ')
        if line[-1] == '':
            line.remove(line[-1])


        s = set(line) & set(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        if bool(s):
            remove_index_from_line = [i for i, item in enumerate(line) if item in s]
            remove_addtnl_index_from_line = []
            [remove_addtnl_index_from_line.append(item - 1) for item in remove_index_from_line]
            remove_index_from_line = sorted(remove_index_from_line + remove_addtnl_index_from_line)
            line = list(np.delete(line, remove_index_from_line))


        expected_platform = line[-1]
        delay_in_departure = line[-2]
        expected_departure = line[-3]
        delay_in_arrival = line[-4]
        expected_arrival= line[-5]
        destination = line[-6]
        source = line[-7]
        train_no = line[1]
        train_name = ' '.join(line[2:-7])
        recorded_on = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df1 = pd.DataFrame([[train_no, train_name, source, destination, expected_arrival, delay_in_arrival, expected_departure, delay_in_departure, expected_platform, recorded_on]], columns = ['Train_Number', 'Train_Name', 'Source', 'Destination', 'Expected_Arrival', 'Delay_in_Arrival', 'Expected_Departure', 'Delay_in_Departure', 'Expected_Platform','Recorded_On'])
        df2 = df2.append(df1)
    #df2.set_index('Train_Number')
    return df2

def open_website():
    url = "https://enquiry.indianrail.gov.in/ntes/"
    try:
        browser.get(url)  # navigate to the page
    except:
        time.sleep(60)
        print('Website down ..... waiting for 1 minute')
        open_website()
    time.sleep(3)
    browser.find_element_by_link_text("Live Station").click()
    time.sleep(3)
    browser.find_element_by_id('viaStation').send_keys(division)
    time.sleep(3)
    button_element = browser.find_element_by_id('viaStnGoBtn')
    button_element.click()
    time.sleep(8)
    browser.switch_to.alert

### Program execution flow starts here ===>>>
#browser = webdriver.Chrome(r'C:\Users\debanjan\Documents\indian_railways\chromedriver_win32/chromedriver.exe')
binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
browser = webdriver.Firefox( firefox_binary=binary )
division = 'SEALDAH [SDAH]'
path = 'C:\Users\debanjan\Documents\indian_railways\data\Eastern Railway\Sealdah Division'
#division = 'HOWRAH JN [HWH]'
#path = 'C:\Users\debanjan\Documents\indian_railways\data\Eastern Railway\Howrah Division'
file_list = os.listdir(path)
label = datetime.datetime.now().strftime("%Y-%m-%d")
file = 'data_' + label + '.csv'
path1 = os.path.join(path, file)

if file in file_list:
    base_table = pd.read_csv(path1, index_col = False, usecols = ['Train_Number', 'Train_Name', 'Source', 'Destination', 'Expected_Arrival', 'Delay_in_Arrival', 'Expected_Departure', 'Delay_in_Departure', 'Expected_Platform', 'Recorded_On'])
    base_table.set_index('Train_Number', inplace = True)
else:
    base_table = pd.DataFrame(columns = ['Train_Name', 'Source', 'Destination', 'Expected_Arrival', 'Delay_in_Arrival', 'Expected_Departure', 'Delay_in_Departure', 'Expected_Platform', 'Recorded_On'])

open_website()

refresh_memory_counter = 1

while 1:

    try:
        scrapped_text = scrape_modal_window()
    except:
        print('Error occured, waiting for 10 seconds .....')
        time.sleep(10)
        browser.refresh()
        time.sleep(30)
        open_website()
        continue
    print(scrapped_text)
    new_table = text_to_frame(scrapped_text)
    try:
        if not new_table.empty:
            base_table = new_table.set_index('Train_Number').combine_first(base_table)
    except:
        continue
    print(base_table)
    print('new_table shape: ', new_table.shape)
    print('base_table shape after update', base_table.shape)
    print(division)
    label = datetime.datetime.now().strftime("%Y-%m-%d")
    file = 'data_' + label + '.csv'
    path2 = os.path.join(path, file)
    base_table.to_csv(path2, index = True)
    print('Refresh memory counter: ', refresh_memory_counter)
    refresh_memory_counter = refresh_memory_counter + 1
    if refresh_memory_counter == 500:
        browser.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ui-dialog-titlebar-close", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "ui-icon-closethick", " " ))]').click()
        refresh_memory_counter = 1
