import json
import jsonschema
import yaml
import click
import pprint

import os
from . import util

SCHEMA_DIR = util.from_scriptroot('schema')
print SCHEMA_DIR

SCHEMAS = {}

def load_schema(key, filename):
    SCHEMAS[key] = yaml.load(open(
            os.path.join(SCHEMA_DIR, filename)))

load_schema('main', 'main.yml')
load_schema('builders', 'builders.yml')
load_schema('files', 'files.yml')
load_schema('platforms', 'platforms.yml')
load_schema('packagers', 'packagers.yml')
load_schema('sources', 'sources.yml')
load_schema('mimetypes', 'mimetypes.yml')

def force_list(config):
    if isinstance(config, dict):
        return [config]
    else:
        return config

def validate(schema, config, name="", verbose=False):
    print "SCHEMA", schema, name
#    print SCHEMAS[schema]
#    print config['platforms']['linux']

    try:
        jsonschema.validate(config, SCHEMAS[schema])
    except jsonschema.exceptions.ValidationError as e:
        print e.message
        return None
    except ScannerError as e:
        print e.message
        return None

    return config

def validate_sources(config):
    for source in config.keys():
        validate('sources', config[source])

        for builder in force_list(config[source]['builders']):
            validate('builders', builder)

        if 'files' in config[source]:
            for builder in force_list(config[source]['files']):
                validate('files', config[source]['files'], source)
    return True
    
def validate_packfile(packfile):
    config = {}
    try:
        config = yaml.load(open(packfile))
    except yaml.scanner.ScannerError as e:
        print __name__+":", e.problem,"\n",e.problem_mark
        return False

    validate('main', config)
    validate('platforms', config['platforms'])
    validate('packagers', config['packagers'])

    validate_sources(config['sources'])

    for mimetype in force_list(config['mimetypes']):
        validate('mimetypes', mimetype)
