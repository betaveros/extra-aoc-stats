import requests
import time

def scrape(year, day):
	with open('{}_day_{}.html'.format(year, day), "w") as outfile:
		outfile.write(requests.get("https://adventofcode.com/2019/leaderboard/day/{}".format(day)).text)
for i in range(1, 26):
	print(i)
	scrape(2019, i)
	print(i, "done")
	time.sleep(300)
