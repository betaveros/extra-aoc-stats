import requests
import time

def scrape(year, day):
	print(year, day)
	with open('{}_day_{}.html'.format(year, day)) as infile:
		s = infile.read().encode('latin1').decode('utf-8')
	with open('{}_day_{}.html'.format(year, day), "w") as outfile:
		outfile.write(s)
for i in range(5, 26):
	scrape(2019, i)
