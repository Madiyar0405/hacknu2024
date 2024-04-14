from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
url = 'https://berekebank.kz/ru/personal/cards/allin'

driver.get(url)

title_bl_element = driver.find_element(By.XPATH, "//div[@class='title_bl' and .//h3[contains(., 'Кешбэк за покупки')]]")
parent_element = title_bl_element.find_element(By.XPATH, "./..")
desc_elements = parent_element.find_elements(By.XPATH, ".//div[@class='desc']//p")

percentages = []
strings = []

percentagesSpecified = []
stringsSpecified = []

for desc_element in desc_elements:
    text = desc_element.text
    if '%' in text:
        percentage_str = text.split('%')[0]
        percentage = float(percentage_str.replace(',', '.'))
        percentages.append(percentage)
        strings.append(text.split('%')[1])
    else:
        strings.append(text)

driver.quit()

print("Percentages:", percentages)
print("Strings:", strings)