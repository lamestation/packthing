#!/usr/bin/env python

import sys

import json
import yaml

import textwrap

def get_key(yml, key, required=True):
    if not key in yml:
        print "Missing required key '"+key+"'; exiting"
        sys.exit(1)

    return yml[key]

def header(text, level=1):
    return "#"*level + " " + text + "\n\n"

def style(text, bold=False, italic=False, monospace=False):
    if monospace:
        text = "`"+text+"`"
    if bold:
        text = "**"+text+"**"
    if italic:
        text = "*"+text+"*"
    return text

def bullet(text, indent=4, char='-'):
    if indent > len(char):
        return '-' + ' '*(indent-len(char)) + text + "\n"
    else:
        return text

#def bullet(text, level=1, ch='-'):
#    ch = ch*level

def keyvalue(key, val, indent=4):
    output = ""
    output += style(key)
    output += " | "
    output += style(val, monospace=True)
    return output

def keyheader():
    output = ""
    output += "Key | Value\n"
    output += "--- | -----\n"
    return output

def keybool(key, state=False, **kwargs):
    if state:
        return keyvalue(key, "true")
    else:
        return keyvalue(key, "false")

def process_header(yml, level=1, key=None):
    get_key(yml, 'title')

    title = ""
    if isinstance(key, str):
        title += key + ": "
    title += yml['title']

    return header(title, level)

def process_property(yml, key, level=1, required=False):
#    print "Processing!", key
    get_key(yml, 'title')

    output = " *** \n\n"
    #output += "-   " + style(key, bold=True, italic=True)

    output += header(key, level=level)

    output += keyheader()
    output += keybool("required", required)
    output += "\n\n"

    output += process_description(yml, key=key)

    output += process_properties(yml, level+1, key=key)

    return output

def get_description(yml):
    get_key(yml, 'description')

    output = ""
    try:
        output += yml['description']
    except TypeError:
        output += style("TBD", italic=True)

    return output

def process_description(yml, key=None, indent=0):
    output = get_description(yml)
#    output = textwrap.wrap(output,
#            width=80,
#            initial_indent=' '*indent,
#            subsequent_indent=' '*indent,
#            break_long_words=False)
#    output = "\n".join(output)
    output += "\n\n"

    return output

def process_properties(yml, level=1, key=None):
    if not 'properties' in yml:
        return ""

    if not 'required' in yml:
        yml['required'] = []

    properties = yml['properties'].keys()
    properties.sort()

    output = ""
    for p in properties:
        #output += process_property(yml['properties'][p], level+1, key=p)

        required = False
        if p in yml['required']:
            required = True

        output += process_property(yml['properties'][p], key=p, level=level+1, required=required)

    return output

def process_yaml(yml, level=1, key=None):
    output = ""
    output += process_header(yml, level, key=key)
    output += process_description(yml, key=key)

    output += "[TOC]\n\n"

    output += process_properties(yml, level, key=key)

    return output

def process_schema(filename):
    y = yaml.load(open(filename))
    return process_yaml(y, level=1)

if len(sys.argv) < 2:
    print "Usage:",sys.argv[0],"FILE"
    sys.exit(1)

print process_schema(sys.argv[1])
