# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 10:32:36 2017

@author: HP

"""

from selenium import webdriver

#from selenium.webdriver.common.keys import keys
from pyvirtualdisplay import Display

import lxml.html
from lxml import html
from lxml import etree
import urllib
import time




#br = webdriver.Chrome()

#display = Display(visible=0, size=(800,600))
#display.start()

def search_DHL_site(source,destination):

	br = webdriver.Firefox()
	url = ""
	br.get('http://dct.dhl.com/input.jsp?langId=en')



	flag = False

	origin_country_val = 'INDIA (IN)'
	origin_zip_val = source
	#origin_zip_val = '560071'
	#origin_city_val = 'BANGALORE'

	destination_country_val = 'INDIA (IN)'
	destination_zip_val = destination
	#destination_zip_val = '741235'
	#destination_city_val = 'BARRACKPORE'

	origin_country = br.find_element_by_name('orgCtry')
	origin_zip = br.find_element_by_name('orgZip')
	#origin_city = br.find_element_by_name('orgCity')

	destination_country = br.find_element_by_name('dstCtry')
	destination_zip = br.find_element_by_name('dstZip')
	#destination_city = br.find_element_by_name('dstCity')

	#origin_country.send_keys('INDIA (IN)')
	#origin_zip.send_keys('560071')
	#origin_city.send_keys('BANGALORE')
	#time.sleep(1)
	#
	#destination_country.send_keys('INDIA (IN)')
	#destination_zip.send_keys('741235')
	#destination_city.send_keys('BARRACKPORE')

	origin_country.send_keys(origin_country_val)
	origin_zip.send_keys(origin_zip_val)
	#origin_city.send_keys(origin_city_val)
	time.sleep(1)

	destination_country.send_keys(destination_country_val)
	destination_zip.send_keys(destination_zip_val)
	#destination_city.send_keys(destination_city_val)

	time.sleep(1)
	search_button = br.find_element_by_name('calculate')

	print(type(origin_country.get_attribute('value')))
	print(type(origin_zip.get_attribute('value')))
	#print(type(origin_city.get_attribute('value')))
	print(type(destination_country.get_attribute('value')))
	print(type(destination_zip.get_attribute('value')))
	#print(type(destination_city.get_attribute('value')))

	while(flag == False):
		if(origin_country.get_attribute('value') != origin_country_val):
			print("Inside 1")
			origin_country.send_keys(origin_country_val)
			continue;
		elif(origin_zip.get_attribute('value') != origin_zip_val):
			print("Inside 1")
			origin_zip.send_keys(origin_zip_val)
			continue;
	#    elif(origin_city.get_attribute('value') != origin_city_val):
	#        print("Inside 1")
	#        origin_city.send_keys(origin_city_val)
			continue;
		elif(destination_country.get_attribute('value') != destination_country_val):
			print("Inside 1")
			destination_country.send_keys(destination_country_val)
			continue;
		elif(destination_zip.get_attribute('value') != destination_zip_val):
			print("Inside 2")
			destination_zip.send_keys(destination_zip_val)
			continue;
	#    elif(destination_city.get_attribute('value') != destination_city_val):
	#        print("Inside 3")
	#        destination_city.send_keys(destination_city_val)
	#        continue;
		else:
			print("Inside 4")
			flag = True
			continue
		

	search_button.click()
	time.sleep(2)

	table_element = br.find_element_by_id("search_result_table")

	print(table_element)

	ele = br.find_elements_by_xpath("//table[@id='search_result_table']/tbody/tr")
	for e in ele:
		for td in e.find_elements_by_xpath(".//td"):
			print td.text



    
