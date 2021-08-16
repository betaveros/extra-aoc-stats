import re, bs4, json
from bs4 import BeautifulSoup

def parse_position_span(span):
	s = span.string
	assert s[3:] == ')'
	return int(s[:3])

def parse_time_span(span, day):
	s = span.string
	m = re.match(r'Dec (\d\d)  (\d\d):(\d\d):(\d\d)', s)
	assert m
	assert int(m.group(1)) == day
	return int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))

def parse_rest(rest):
	ret = dict()
	name_parts = []
	supporter = False
	sponsor = False
	for x in rest:
		# ??? not pythonic
		if isinstance(x, bs4.element.NavigableString):
			name_parts.append(x)
		else:
			for img in x.find_all('img'):
				ret['i'] = img['src']

			classes = x.get('class', [])
			if 'supporter' in classes or 'supporter-badge' in classes:
				ret['s'] = True
			elif 'sponsor-badge' in classes:
				ret['p'] = x['href']
			else:
				if x.name == 'a':
					ret['h'] = x['href']

				name_parts.extend(x.strings)
	ret['n'] = ''.join(name_parts).strip()
	return ret

def parse_entry(entry, day, part):
	position_span, _1, time_span, _2, *rest = list(entry.children)
	assert _1 == _2 == ' '
	position = parse_position_span(position_span)
	seconds = parse_time_span(time_span, day)
	return {
		'p': part,
		'n': position,
		's': seconds,
		'u': parse_rest(rest),
	}

def parse(infile, day):
	soup = BeautifulSoup(infile, 'html.parser')
	entries = list(soup.find_all('div', class_='leaderboard-entry'))
	assert len(entries) == 200
	return [parse_entry(entry, day, 2 if i < 100 else 1) for i, entry in enumerate(entries)]

def get_day(year, day):
	with open('{}_day_{}.html'.format(year, day)) as infile:
		return parse(infile, day)

for year in range(2020, 2021):
	with open('{}.json'.format(year), 'w') as outfile:
		outfile.write(json.dumps([{
			'd': i,
			'l': get_day(year, i),
		} for i in range(1, 26)]))

"""
array of {
	d: day,
	l: array of {
		p: part,
		n: position,
		s: seconds,
		u: {
			n: name,
			i?: image source,
			h?: link href,
			s?: true if supporter,
			p?: sponsor link href if sponsor,
		}
	}
}
"""
