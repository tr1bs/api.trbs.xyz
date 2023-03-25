import requests
from bs4 import BeautifulSoup
import random 
import json
 
user_agents = [ 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
	'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
	'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
] 
user_agent = random.choice(user_agents)
headers = {'User-Agent': user_agent} 

url = 'https://www.ssense.com/en-us/women/product/see-by-chloe/indigo-flared-emily-jeans/10049711'
html = requests.get(url, headers=headers)


# with open('test.txt', 'w') as file:
#     file.write(html.text)

soup = BeautifulSoup(html.text, 'html.parser')
data = json.loads(soup.find('script', type='application/ld+json').text)
#print(data)

print(data['offers']['availability'].split('/')[3])


#print(soup.prettify())
 

'''
# title: <title>
# meta name:author content
# meta description:content
# meta name twitter:description content


#class:  
# s-buybox__size-selector
	contains what sizes are there and what is sold out
	do not include in v1 but this will be great for scraping for db purposes in the future


# product-price__price s-text
	# maybe get an autoconverter to eth api at some point lol


anything under the below section is underneath: pdp-product-description
	should probably loop through the divs in the div
	that way you can make sure youre not getting nulls in the data side


# pdpProductDescriptionContainerText
	

'''