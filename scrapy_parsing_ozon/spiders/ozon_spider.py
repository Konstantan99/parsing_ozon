import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import logging
from selenium.webdriver.remote.remote_connection import LOGGER


class BookSpider(scrapy.Spider):

	name = 'ozon_best_phone'
	start_urls = ['https://www.ozon.ru/category/smartfony-15502/?page=1&sorting=rating']

	OS_version_list = []
	page = 1
	LOGGER.setLevel(logging.WARNING)


	options = webdriver.chrome.options.Options()
	options.add_argument("start-maximized")
	options.add_experimental_option("excludeSwitches", ["enable-automation"])
	options.add_experimental_option('useAutomationExtension', False)
	options.add_argument("--disable-blink-features")
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_argument("--headless")
	options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")


	def start_requests(self):
		self.driver = webdriver.Chrome('/Users/derendyaevka/Desktop/parsing_ozon/chromedriver', options=self.options)


		while True:
			self.driver.get(f'https://www.ozon.ru/category/smartfony-15502/?page={self.page}&sorting=rating')
			self.page += 1
			self.wait = WebDriverWait(self.driver, 30)

			# Строка, чтобы проскролить страницу до конца
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")

			links = []

			# Делаем проверку, что на страницу загрузились все 36 товаров со страницы и добавляем их ссылку на в список
			for i in range(36):
				i_xpath = f'//*[@id="layoutPage"]/div/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[{i+1}]/div[2]/div/a'
				try:
					self.wait.until(EC.presence_of_element_located((By.XPATH, i_xpath)))
					elem = self.driver.find_element(By.XPATH, i_xpath)
					link = elem.get_attribute('href') 
					links.append(link)
					print(f'Выполнено - {i+1}')
				except TimeoutException:
					print(f'Вылетело по времени - {i+1}')

			print('Типа собраны все 36 ссылок')
			for link in links:
				yield self.parse_phone(link)

				if len(self.OS_version_list) == 100:
					break

		df = pd.DataFrame(q_list, columns=['q_data'])
		df.to_csv("output.csv", index=False)


	def parse_phone(self, phone_link):
		self.options.add_argument("user-agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1")
		print('начался парсить следующий тельчик')
		self.driver.get(phone_link)
		# self.wait = WebDriverWait(self.driver, 30)
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")

		try:
			self.wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "iOS ")]')) \
				or EC.presence_of_element_located((By.XPATH, '//dd[contains(text(), "Android ")]')))

			# выполняется проверка на версию Айфона
			try:
				elem = self.driver.find_element(By.XPATH, '//a[contains(text(), "iOS ")]')
			except NoSuchElementException:
				pass
				# print('Это не Айфон')

			# выполняется проверка на версию Андроида
			try:
				elem = self.driver.find_element(By.XPATH, '//dd[contains(text(), "Android ")]')
			except NoSuchElementException:
				pass
				# print('это не Андроид')

			self.OS_version_list.append(elem.text)

		except TimeoutException:
			self.OS_version_list.append('Вылетело по времени')
			# print('Вылетело по времени')
