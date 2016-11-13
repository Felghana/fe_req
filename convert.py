#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import re
import sys

from pathlib import Path

import requests
from bs4 import BeautifulSoup

page2 = Path(
    "/Users/bilalh/Projects/_Programming/fe_link/fe_requests_cleaned.html").read_text()
soup2 = BeautifulSoup(page2, "html5lib")

table = []
by_chapters = [dict(start=[],
                    intermission=[],
                    main=[],
                    ng_start=[],
                    ng_intermission=[],
                    ng_main=[]) for i in range(0, 6 + 1)]

chapter_re = re.compile(
    '(?P<start>Start of )?Chapter (?P<num>\d+)(?P<intermission> Intermission)?(?P<ng> \(NG\+\))?')

i = 0
for p in soup2.select('h4 + p'):
  h4 = p.find_previous('h4')
  id = h4.a['id']
  text = p.contents[0].strip()
  match = chapter_re.match(text)
  data = match.groupdict()
  data['num'] = int(data['num'])
  data['main'] = not data['start'] and not data['intermission']

  i += 1
  for key in ['start', 'intermission', 'main']:
    if (data[key]):
      if data['ng']:
        key = "ng_" + key
      by_chapters[data['num']][key].append(id)

  table.append((text, id, data))

print(i)

top = soup2.new_tag('div')

h2 = soup2.new_tag('h2')
h2.string = "By Chapter"
top.append(h2)

by_chapters[6]['main'].append('')

for (ix, ele) in enumerate(by_chapters):
  if (ix == 0):
    continue

  for (title, key) in [('Start of Chapter {}', 'start'), ('Chapter {}', 'main'),
                       ('Chapter {} intermission', 'intermission'),
                       ('(NG+) Start of Chapter {}', 'ng_start'),
                       ('(NG+) Chapter {}', 'ng_main'),
                       ('(NG+) Chapter {} intermission', 'ng_intermission')]:

    if not key.startswith('ng_') or len(ele[key]) > 0:
      h3 = soup2.new_tag('h3')
      h3.string = title.format(ix)
      top.append(h3)

    for id in ele[key]:
      a = soup2.new_tag('a')
      a['class'] = 'chap_link'
      a['href'] = '#' + id
      a.string = id
      top.append(a)
      top.append(soup2.new_tag('br'))

soup2.select_one('h2').insert_before(top)

Path("/Users/bilalh/Projects/_Programming/fe_link/out0.html").write_text(soup2.prettify())

page = Path("/Users/bilalh/Projects/_Programming/fe_link/out0.html").read_text()
soup = BeautifulSoup(page, "html5lib")


def add_structure(h, *, stop=None, div_class=None):
  """ Put the elements inside of a div """
  if not stop:
    stop = {h.name}

  div = soup2.new_tag("div")
  if div_class:
    div['class'] = div_class
  h.wrap(div)
  div = h.parent

  last = None
  i = 0
  for ele in div.next_elements:
    last = ele
    if i <= 2:
      i += 1
      continue

    if ele.name in stop:
      break
    else:
      i += 1
      div.append(ele)

  return last


h = soup.select('h2')[1]
while h.name == 'h2':
  h = add_structure(h)

for h in soup.select('h2')[1:]:
  cur = h.parent.select('h4')
  if len(cur) == 0:
    continue
  cur = cur[0]
  while cur.name == 'h4':
    cur = add_structure(cur, stop={"h2", "h4"}, div_class="entry")

for h4 in soup.select('h4'):
  t_elem = h4.next_sibling.next_sibling
  h4.insert(0, t_elem)

Path("/Users/bilalh/Projects/_Programming/fe_link/out.html").write_text(soup.prettify())
