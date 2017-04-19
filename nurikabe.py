#!/usr/bin/python2
# -*- encoding: utf-8 -*-
#
# Author: Peter Schüller (2014)
# Adapted from a script posted by Adam Marshall Smith on the potassco mailing list (2014)
#

import sys
import re
import json
import subprocess
import collections
import traceback

def extractExtensions(answerset):
  #print(repr(answer_set))
  field_pattern = re.compile(r'(\w+)\(f\((\d+),(\d+)\)(?:,([0-9]+|[a-z][a-zA-Z0-9]*|"[^"]*"))?\)')
  extensions = collections.defaultdict(lambda: set())
  for l in answerset:
    try:
      args = field_pattern.match(l).groups()
      #print "for {} got field pattern match {}".format(l, repr(args))
      # first arg = predicate
      # second/third arg = coordinates
      # rest is taken as string if not None but " are stripped
      head = args[0]
      rest = [int(args[1]), int(args[2])]
      if args[3]:
        rest.append(str(args[3]).strip('"'))
      #sys.stderr.write(
      #  "got head {} and rest {}\n".format(repr(head), repr(rest)))
      extensions[head].add(tuple(rest))
    except:
      #sys.stderr.write("exception ignored: "+traceback.format_exc())
      pass
  return extensions

def render_svg(literals,size=40):
    import xmlbuilder

    answer_set = extractExtensions(literals)
    maxx = max(map(lambda x: x[0], answer_set['field']))
    maxy = max(map(lambda x: x[1], answer_set['field']))

    svg = xmlbuilder.XMLBuilder(
        'svg',
        viewBox="0 0 %d %d"%(10*(maxx+1),10*(maxy+1)),
        xmlns="http://www.w3.org/2000/svg",
        **{'xmlns:xlink':"http://www.w3.org/1999/xlink"})

    #with svg.linearGradient(id="grad"):
    #    svg.stop(offset="0", **{'stop-color': "#f00"})
    #    svg.stop(offset="1", **{'stop-color': "#ff0"})

    #with svg.g():
    #    for (x,y) in room.values():
    #        svg.circle(cx=str(5+10*x),cy=str(5+10*y),r="2")

    with svg.g():
        for (x, y) in answer_set['field']:
            x = int(x)
            y = int(y)
            svg.rect(x=str(10*x - 5),
                     y=str(10*y - 5),
                     width=str(10),
                     height=str(10),
                     style="stroke: black; stroke-width: 1px; fill:white;")
        for (x, y) in answer_set['wall']:
            x = int(x)
            y = int(y)
            svg.rect(x=str(10*x - 5),
                     y=str(10*y - 5),
                     width=str(10),
                     height=str(10),
                     style="stroke: black; stroke-width: 1px; fill:black;")
        for (x, y) in answer_set['exit']:
            x = int(x)
            y = int(y)
            svg.circle(cx=str(10*x), cy=str(10*y), r=str(3), style="stroke: red; fill:red; ")
        for (x, y) in answer_set['mark']:
            x = int(x)
            y = int(y)
            svg.circle(cx=str(10*x), cy=str(10*y), r=str(2), style="stroke: blue; fill:blue; ")
        for (x, y, text) in answer_set['text']:
            x = int(x)
            y = int(y)
            text = str(text)
            print("SVG %d %d %s" % (x, y, text))
            svg.text(text, x=str(10*x-3), y=str(10*y+3), style="stroke: green; font-size: 9px; ")

    #return IPython.display.SVG(data=str(svg))
    with file("out.svg","w+") as f:
      f.write(str(svg))

import Tkinter as tk
class Window:
  def __init__(self,answersets):
    self.answersets = answersets
    self.selections = range(0,len(self.answersets))
    self.selected = 0
    self.root = tk.Tk()
    self.main = tk.Frame(self.root)
    self.main.pack(fill=tk.BOTH, expand=1)
    self.canvas = tk.Canvas(self.main, bg="white")
    self.canvas.pack(fill=tk.BOTH, expand=1, side=tk.TOP)
    self.selector = tk.Scale(self.main, orient=tk.HORIZONTAL, showvalue=0, command=self.select)
    self.selector.pack(side=tk.BOTTOM,fill=tk.X)
    self.root.bind("<Right>", lambda x:self.go(+1))
    self.root.bind("<Left>", lambda x:self.go(-1))
    self.root.bind("q", exit) # TODO more graceful quitting

    self.items = []
    self.updateView()

  def select(self,which):
    self.selected = int(which)
    self.updateView()

  def go(self,direction):
    self.selected = (self.selected + direction) % len(self.answersets)
    self.updateView()

  def updateView(self):
    self.selector.config(from_=0, to=len(self.answersets)-1)

    SIZE=40
    FIELD_FILL='#FFF'
    WALL_FILL='#444'
    MARK_FILL='#A77'
    TEXT_FILL='#000'

    def fieldRect(x,y,offset=SIZE):
      x, y = int(x), int(y)
      return (x*SIZE-offset/2, y*SIZE-offset/2, x*SIZE+offset/2, y*SIZE+offset/2)

    # delete old items
    for i in self.items:
      self.canvas.delete(i)
    # create new items
    self.items = []

    ext = extractExtensions(self.answersets[self.selected])
    #print repr(ext)
    maxx = max(map(lambda x: x[0], ext['field']))
    maxy = max(map(lambda x: x[1], ext['field']))
    self.root.geometry("{}x{}+0+0".format((maxx+1)*SIZE, (maxy+2)*SIZE))

    for (x, y) in ext['field']:
      self.items.append( self.canvas.create_rectangle( * fieldRect(x,y), fill=FIELD_FILL) )
    for (x, y) in ext['wall']:
      self.items.append( self.canvas.create_rectangle( * fieldRect(x,y), fill=WALL_FILL) )
    for (x, y) in ext['mark']:
      self.items.append( self.canvas.create_oval( *fieldRect(x,y,10), fill=MARK_FILL) )
    for (x, y, text) in ext['text']:
      fr = fieldRect(x,y)
      #print("TK %d %d %s" % (x, y, repr(text)))
      self.items.append( self.canvas.create_text( (fr[0]+fr[2])/2, (fr[1]+fr[3])/2, text=str(text), fill=TEXT_FILL) )

def display_tk(answersets):
  w = Window(answersets)

MAXANS=100
clingo = subprocess.Popen(
  "clingo --outf=2 nurikabe.lp {maxans}".format(maxans=MAXANS),
  shell=True, stdout=subprocess.PIPE)
clingoout, clingoerr = clingo.communicate()
del clingo
clingoout = json.loads(clingoout)
#print(repr(clingoout))
#print(repr(clingoout['Call'][0]['Witnesses']))
#print(repr(clingoout['Call'][0]['Witnesses'][0]['Value']))
witnesses = clingoout['Call'][0]['Witnesses']

import random
#render_svg(random.choice(witn)['Value'])
display_tk(map(lambda witness: witness['Value'], witnesses))

tk.mainloop()