#!/usr/bin/env python
'''This is a quick and dirty way to provide developers a way to download
resources needed to build and test components of the open tree software.

environmental variables:
    OPEN_TREE_DOWNLOAD_DEV_RESOURCE_LOGGING_LEVEL=debug for more info
    
    OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG or OPEN_TREE_USER_SETTINGS_DIR to change the 
        default location for config file that stores local filepaths

'''

_program_name = 'download-dev-resource'
_program_subtitle = 'OpenTree developer download utility'
_program_date = 'May 25, 2012'
_program_version = 'Version 0.0.1 (%s)' % _program_date
_program_author = 'Mark T. Holder'
_program_contact = 'mtholder@gmail.com'
_program_copyright = 'Copyright (C) 2012 Mark T. Holder.\n' \
                 'License GPLv3+: GNU GPL version 3 or later or BSD.\n' \
                 'This is free software: you are free to change\nand redistribute it. ' \
                 'There is NO WARRANTY,\nto the extent permitted by law.'

from open-tree-env import get_otol_build_env


# Global dictionary of resources grouped by 'category' Note that dict is filled
#   as a side effect of creating an OpenTreeResource
ALL_RESOURCES = {}
RESOURCE_CATEGORIES = {'taxonomy' : 'OPEN_TREE_TAXONOMY_DIR',
                       'dependency' : 
for key in RESOURCE_CATEGORIES:
    ALL_RESOURCES[key] = []
SUPPORTED_PROTOCOLS = ['http', 'svn']


class OpenTreeResource(object):
    '''A bundle of information about a resource. Attributes:
        `name` - name resource when downloaded and unpacked
        `url` - location of the downloadable resource
        `protocol` = http, git, svn
        `compression` - compression protocol (empty or zip)
        `min_version` - tuple of 3 integers (major, minor, revision)
        `category` - name of the type of resource (taxonomy, dependency...)
        `compressed_name` - if different from the default for the compression type.
                should be identical to the file name created
        `description` - string describing the resource
    '''
    UNPACKING_PROTOCOLS = ['', 'zip']
    def __init__(self,
                 name,
                 url,
                 protocol='http',
                 min_version=(0,0,0),
                 category=None,
                 compression='',
                 compressed_name=None,
                 contact='',
                 description=''):
        self.name = name
        self.url = url
        self.protocol = protocol.lower()
        if self.protocol not in SUPPORTED_PROTOCOLS:
            raise ValueError('Protocol ' + protocol + ' unrecognized')
        self.category = category.lower()
        if self.category not in RESOURCE_CATEGORIES:
            raise ValueError('Category ' + category + ' unrecognized')
        self.compression = compression.lower()
        if self.compression not in OpenTreeResource.UNPACKING_PROTOCOLS:
            raise ValueError('Compression method ' + compression + ' unrecognized')
        if compressed_name is None:
            if self.compression == '':
                self.compressed_name = self.name
            elif self.compression == 'zip':
                self.compressed_name = self.name + '.zip'
        else:
            self.compressed_name = self.compressed_name
        self.contact = contact
        self.description = description
        # here is the hack in which we add resource to the global list
        ALL_RESOURCES[self.category].append(self)
    def listing(self, opts):
        return '%s = %s' % (self.name, self.description)





################################################################################
# Place new resources here
################################################################################
#  rough stab CoL in newick
OpenTreeResource(name='taxa_allCoL.tre', 
                 url='https://trello-attachments.s3.amazonaws.com/4fb665cce706648863c3cc90/4fb66a28e706648863c729bf/fxPkDbNwLRGNBnWyNNcAIPFnMpgx/taxa_allCoL.tre.zip',
                 category='taxonomy',
                 compression='zip',
                 contact='blackrim',
                 description='Newick string representation of Catalogue of Life')
OpenTreeResource(name='ncl', 
                 url='https://ncl.svn.sourceforge.net/svnroot/ncl/branches/v2.1',
                 protocol='svn',
                 min_version=(2, 1, 18),
                 category='dependency',
                 compression='',
                 contact='mtholder',
                 description='NEXUS class library (C++ library for parsing phylogenetic data)')










################################################################################

def list_command(opts):
    for key in RESOURCE_CATEGORIES:
        row = ALL_RESOURCES[key]
        out = sys.stdout
        for resource in row:
            out.write(resource.listing(opts))
            out.write('\n')
            
if __name__ == '__main__':
    from optparse import OptionParser
    from ConfigParser import ConfigParser
    import os
    import sys
    import logging
    _LOGGING_LEVEL_ENVAR="OPEN_TREE_DOWNLOAD_DEV_RESOURCE_LOGGING_LEVEL"
    _LOGGING_FORMAT_ENVAR="OPEN_TREE_DOWNLOAD_DEV_RESOURCE_LOGGING_FORMAT"
    
    def get_logging_level():
        if _LOGGING_LEVEL_ENVAR in os.environ:
            if os.environ[_LOGGING_LEVEL_ENVAR].upper() == "NOTSET":
                level = logging.NOTSET
            elif os.environ[_LOGGING_LEVEL_ENVAR].upper() == "DEBUG":
                level = logging.DEBUG
            elif os.environ[_LOGGING_LEVEL_ENVAR].upper() == "INFO":
                level = logging.INFO
            elif os.environ[_LOGGING_LEVEL_ENVAR].upper() == "WARNING":
                level = logging.WARNING
            elif os.environ[_LOGGING_LEVEL_ENVAR].upper() == "ERROR":
                level = logging.ERROR
            elif os.environ[_LOGGING_LEVEL_ENVAR].upper() == "CRITICAL":
                level = logging.CRITICAL
            else:
                level = logging.NOTSET
        else:
            level = logging.INFO
        return level
    
    def get_logger(name="download_dev_resource"):
        """
        Returns a logger with name set as given, and configured
        to the level given by the environment variable _LOGGING_LEVEL_ENVAR.
        """
    
    #     package_dir = os.path.dirname(module_path)
    #     config_filepath = os.path.join(package_dir, _LOGGING_CONFIG_FILE)
    #     if os.path.exists(config_filepath):
    #         try:
    #             logging.config.fileConfig(config_filepath)
    #             logger_set = True
    #         except:
    #             logger_set = False
        logger = logging.getLogger(name)
        if not hasattr(logger, 'is_configured'):
            logger.is_configured = False
        if not logger.is_configured:
            level = get_logging_level()
            rich_formatter = logging.Formatter("[%(asctime)s] %(filename)s (%(lineno)d): %(levelname) 8s: %(message)s")
            simple_formatter = logging.Formatter("%(levelname) 8s: %(message)s")
            raw_formatter = logging.Formatter("%(message)s")
            default_formatter = None
            logging_formatter = default_formatter
            if _LOGGING_FORMAT_ENVAR in os.environ:
                if os.environ[_LOGGING_FORMAT_ENVAR].upper() == "RICH":
                    logging_formatter = rich_formatter
                elif os.environ[_LOGGING_FORMAT_ENVAR].upper() == "SIMPLE":
                    logging_formatter = simple_formatter
                elif os.environ[_LOGGING_FORMAT_ENVAR].upper() == "NONE":
                    logging_formatter = None
                else:
                    logging_formatter = default_formatter
            else:
                logging_formatter = default_formatter
            if logging_formatter is not None:
                logging_formatter.datefmt='%H:%M:%S'
            logger.setLevel(level)
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(logging_formatter)
            logger.addHandler(ch)
            logger.is_configured = True
        return logger
    _LOG = get_logger()
    
    
    
    description =  '%s %s %s' % (_program_name, _program_version, _program_subtitle)
    command_width = len('status [resource]') + 1
    command_help = [('list', 'list available resources (no additional resource argument needed)'), 
                    ('status [resource]', 'show the status of the designated resource'),
                    ('get [resource]', 'download (and unpack) the designated resource'),
                    ]
    fmt_str = '%%%ds  %%s' % command_width
    command_list = '\n'.join([fmt_str % i for i in command_help])
    usage = '%%prog [options] <command> [resource]\nWhere <command> can be:\n%s\n\n' % command_list
    parser = OptionParser(usage=usage, 
                          add_help_option=True,
                          version=_program_version,
                          description=description)
    parser.add_option('--config',
            dest='config',
            default=None,
            metavar='FILEPATH',
            help='if specified, this path will be used to local filesystem paths. If not specified, the fallbacks will be $OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG or ${OPEN_TREE_USER_SETTINGS_DIR}/download-dev-resource.cfg where ~/.open_tree is the default for ${OPEN_TREE_USER_SETTINGS_DIR}')
    (opts, args) = parser.parse_args()
    if len(args) < 1:
        sys.exit('Expecting at least one argument. Use -h for help')
    cfg_path = opts.config
    if not cfg_path:
        cfg_path = get_otol_build_env('OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG')
    _LOG.debug('Config path is %s\n' % cfg_path)

    command = args[0].lower()
    if command == 'list':
        list_command(opts)
    else:
        if len(args) < 2:
            sys.exit('Expecting a resource identifier after the "%s" command.' % command)
        for res_id in args[1:]:
            if command == 'status':
                status_command(res_id, cfg_path, opts)
            elif command == 'get':
                get_command(res_id, cfg_path, opts)
            else:
                sys.exit('command "%s" not recognized. Use -h for help' % command)
    if not os.path.exists(cfg_path):
        _LOG.info('Path "%s" does not exist, creating it...' % cfg_path)
            

################################################################################
# Script by Mark T. Holder available for use under the terms of either the 
# BSD or GPL (v3) license. (see BSDLicense.txt GPL.txt)
#
################################################################################
