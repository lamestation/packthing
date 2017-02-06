#!/usr/bin/env python

import sys

import json
import yaml

import textwrap

#if len(sys.argv) < 2:
#    sys.exit(1)
#

def get_key(yml, key, required=True):
    if not key in yml:
        print "Missing required key '"+key+"'; exiting"
        sys.exit(1)

    return yml[key]

def header(text, level=1):
    return "#"*level + " " + text + "\n\n"

def style(text, bold=False, italic=False):
    if bold:
        text = "**"+text+"**"
    if italic:
        text = "*"+text+"*"
    return text

#def bullet(text, level=1, ch='-'):
#    ch = ch*level

def process_header(yml, level=1, key=None):
    get_key(yml, 'title')

    title = ""
    if isinstance(key, str):
        title += key + ": "
    title += yml['title']

    return header(title, level)

def process_property(yml, key):
    get_key(yml, 'title')

    output = "-   " + style(key, bold=True, italic=True) + "\n\n"

    description = process_description(yml, key=key)
    description = textwrap.wrap(description,
            width=80,
            initial_indent='    ',
            subsequent_indent='    ',
            break_long_words=False)
    description = "\n".join(description)

    print type(output), type(description)
    output += description+"\n\n"

    return output

def process_description(yml, level=1, key=None):
    get_key(yml, 'description')

    try:
        return yml['description']+"\n\n"
    except:
        return ""

def process_yaml(yml, level=1, key=None):
    output = process_header(yml, level, key=key)
    output += process_description(yml, key=key)

    if 'properties' in yml:
        for p in yml['properties']:
            #output += process_property(yml['properties'][p], level+1, key=p)
            output += process_property(yml['properties'][p], key=p)

    return output

def process_schema(filename):
    y = yaml.load(open(filename))
    return process_yaml(y, level=2)

print header("Packfile Configuration")
print process_schema('packthing/schema/main.yml')
print process_schema('packthing/schema/platforms.yml')
print process_schema('packthing/schema/sources.yml')
print process_schema('packthing/schema/builders.yml')
print process_schema('packthing/schema/files.yml')
print process_schema('packthing/schema/packagers.yml')
print process_schema('packthing/schema/mimetypes.yml')

