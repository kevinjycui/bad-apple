from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

import time
import base64
import json
import re


fp = webdriver.FirefoxProfile()

WIDTH = 36
HEIGHT = 28

def data():
    with open('data.json') as f:
        return json.load(f)
    
def convert(grid):
    inputs = []
    for row in range(0, 26, 2):
        eq = ''
        for col in range(0, WIDTH, 2):
            if grid[row][col] == 1:
                eq += '88888+'
            else:
                eq += '0-0-'
        inputs.append(eq[:-1])
    return inputs

def run():

    grids = data()

    driver = webdriver.Firefox(firefox_profile=fp)

    driver.implicitly_wait(5)
    driver.maximize_window()

    driver.get('https://webwork.math.mcgill.ca/webwork2/MATH133_WINTER2021/set2/1/')

    time.sleep(90)
    print('Finished wait')
            
    form = driver.find_elements_by_xpath("//input[@class='codeshard']")
    answers = []
    if len(form) != 13:
        print(len(form))
        return

    for f in form:
        answers.append(f.get_attribute('value'))

    for frame in range(len(grids)):
        while True:
            try:
                inputs = convert(grids[frame])

                form = driver.find_elements_by_xpath("//input[@class='codeshard']")
                preview = driver.find_element_by_xpath("//input[@name='previewAnswers']")

                for i in range(13):
                    form[i].clear()
                    form[i].send_keys(inputs[i])
                preview.click()
                time.sleep(3)
                break
            except:
                driver.get('https://webwork.math.mcgill.ca/webwork2/MATH133_WINTER2021/set2/1/')

    form = driver.find_elements_by_xpath("//input[@class='codeshard']")
    check = driver.find_element_by_xpath("//input[@name='checkAnswers']")

    for i in range(13):
        form[i].clear()
        form[i].send_keys(answers[i])
    check.click()

run()