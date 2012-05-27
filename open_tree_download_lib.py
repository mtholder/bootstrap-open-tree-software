#!/usr/bin/env python
'''This is a quick and dirty way to provide developers a way to download
resources needed to build and test components of the open tree software.

environmental variables:
    OPEN_TREE_DOWNLOAD_DEV_RESOURCE_LOGGING_LEVEL=debug for more info
    
    OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG or OPEN_TREE_USER_SETTINGS_DIR to change the 
        default location for config file that stores local filepaths

'''
import os
import sys
import logging
from os.path import basename
from urlparse import urlsplit
import urllib2
import urllib
import shutil
import subprocess
import zipfile
from open_tree_env import get_otol_build_env, put_otol_build_env_into_env, abbreviate_path



# Global dictionary of resources grouped by 'category' Note that dict is filled
#   as a side effect of creating an OpenTreeResource
ALL_RESOURCES = {}
RESOURCE_CATEGORIES = {'taxonomy' : 'OPEN_TREE_TAXONOMY_DIR',
                       'dependency' : 'OPEN_TREE_DEPENDENCY_DIR'
                       }
for key in RESOURCE_CATEGORIES.keys():
    ALL_RESOURCES[key] = []
SUPPORTED_PROTOCOLS = ['http', 'svn']

# global config file parser
_CFG_PARSER = None
_ACTION_LOG_FILE = None
_LAST_LOGGED_DIR = None
def _get_action_log_file():
    global _ACTION_LOG_FILE
    if _ACTION_LOG_FILE is None:
        fp = os.path.join(get_otol_build_env('OPEN_TREE_DEPENDENCY_DIR'), 'log-bootstrap.txt')
        _LOG.debug('Opening "%s" as action log' % fp)
        fo = open(fp, 'a')
        _ACTION_LOG_FILE = fo
    return _ACTION_LOG_FILE
        
def log_action(message):
    global _LAST_LOGGED_DIR
    op = os.path.abspath(os.curdir)
    action_log_file = _get_action_log_file()
    if (_LAST_LOGGED_DIR is None) or (_LAST_LOGGED_DIR != op):
        _LAST_LOGGED_DIR = op
        abbrev = abbreviate_path(op)
        action_log_file.write('cd "%s"\n' % abbrev)        
    action_log_file.write(message + '\n')
    action_log_file.flush()
    _LOG.debug("ACTION: " + message)
    

################################################################################
# The following is from http://stackoverflow.com/questions/862173/how-to-download-a-file-using-python-in-a-smarter-way
############################

def url2name(url):
    return basename(urllib.unquote(urlsplit(url)[2]))

def download_http(url, localFileName=None):
    localName = url2name(url)
    req = urllib2.Request(url)
    r = urllib2.urlopen(req)
    if r.info().has_key('Content-Disposition'):
        # If the response has Content-Disposition, we take file name from it
        localName = r.info()['Content-Disposition'].split('filename=')[1]
        dq = (localName[0] == '"' and localName[-1] == '"')
        sq = (localName[0] == "'" and localName[-1] == "'")
        if sq or dq:
            localName = localName[1:-1]
    elif r.url != url: 
        # if we were redirected, the real file name we take from the final URL
        localName = url2name(r.url)
    if localFileName: 
        # we can force to save the file as specified name
        localName = localFileName
    f = open(localName, 'wb')
    d = os.path.abspath(os.curdir)
    _LOG.info('Downloading "%s" to "%s"...\n' % (localName, d))
    shutil.copyfileobj(r, f)
    f.close()
    r.close()
    log_action('wget "%s"' % (url))
    return localName

def _my_makedirs(dir):
    '''Calls os.makedirs (if needed), and logs the action.'''
    if not os.path.exists(dir):
        os.makedirs(dir)
        log_action('mkdir -p "%s"' % os.path.abspath(dir))
def _my_chdir(dir):
    '''Calls os.chdir, and logs the action.'''
    if not os.path.exists(dir):
        _my_makedirs(dir)
    os.chdir(dir)


############################
# End code snippet from stackoverflow
################################################################################
## The following is modified from: http://code.activestate.com/recipes/252508/ (r2)
# unzip.py
#     Version: 1.1
# 
#     Extract a zipfile to the directory provided
#     It first creates the directory structure to house the files
#     then it extracts the files to it.
#     
# 
#     By Doug Tolton


class unzip:
        
    def extract(self, file, dir):
        if not dir.endswith(':'):
            _my_makedirs(dir)
    
        zf = zipfile.ZipFile(file)

        # create directory structure to house files
        self._createstructure(file, dir)

        # extract files to directory structure
        for i, name in enumerate(zf.namelist()):
            if not name.endswith('/'):
                outfile = open(os.path.join(dir, name), 'wb')
                outfile.write(zf.read(name))
                outfile.flush()
                outfile.close()
        log_action('unzip "%s"' % (file))

    def _createstructure(self, file, dir):
        self._makedirs(self._listdirs(file), dir)


    def _makedirs(self, directories, basedir):
        """ Create any directories that don't currently exist """
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            _my_makedirs(curdir)

    def _listdirs(self, file):
        """ Grabs all the directories in the zip structure
        This is necessary to create the structure before trying
        to extract the file to it. """
        zf = zipfile.ZipFile(file)

        dirs = []

        for name in zf.namelist():
            if name.endswith('/'):
                dirs.append(name)

        dirs.sort()
        return dirs

def unzip_file(file, dest_parent):
    u = unzip()
    u.extract(file, dest_parent)
## end of http://code.activestate.com/recipes/252508/ }}}

def untar_gz(file, dest_parent):
    system_call(['tar', 'xfvz', os.path.abspath(file)], wd=dest_parent)

class RESOURCE_STATUS_CODE:
    SKIPPED, MISSING, DOWNLOADED, INSTALLED = range(4)


def system_call(invoc, wd=None):
    prev_dir = None
    if wd is not None:
        prev_dir = os.path.abspath(os.curdir)
        wd = os.path.expandvars(wd)
        _my_makedirs(wd)
    else:
        wd = os.curdir
    try:
        wl = []
        for word in invoc:
            if (len(word.split()) > 1) or (len(word.split('$')) > 1):
                wl.append('"%s"' % word)
            else:
                wl.append(word)
        m = ' '.join(wl)
        d = os.path.abspath(wd)
        _my_chdir(d)
        log_action(m)
        rc = subprocess.call(invoc)
        if rc != 0:
            message = 'The command:\n"%s"\nexecuted from %s failed with returncode %d\n' % (m, d, rc)
            raise RuntimeError(message)
    finally:
        if prev_dir is not None:
            _my_chdir(prev_dir)
        
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
        `install_steps` is a list of dicts. each one has a wd key (working directory)
                and a list of commands to be run from that directory
        `install_parent` the parent directory of the installed products
        `install_sub` a path to be joined to `install_parent` to verify that 
                the install step worked.
    '''
    UNPACKING_PROTOCOLS = ['', 'zip', 'tar.gz']
    def __init__(self,
                 name,
                 url,
                 protocol='http',
                 min_version=(0,0,0),
                 category=None,
                 compression='',
                 compressed_name=None,
                 contact='',
                 description='',
                 install_steps=None,
                 install_parent='',
                 install_sub='',
                 requires=None):
        self.name = name
        self.url = url
        self.protocol = protocol.lower()
        if self.protocol not in SUPPORTED_PROTOCOLS:
            raise ValueError('Protocol ' + protocol + ' unrecognized')
        self.category = category.lower()
        if self.category not in RESOURCE_CATEGORIES.keys():
            raise ValueError('Category ' + category + ' unrecognized')
        self.compression = compression.lower()
        if self.compression not in OpenTreeResource.UNPACKING_PROTOCOLS:
            raise ValueError('Compression method ' + compression + ' unrecognized')
        if compressed_name is None:
            if self.compression == '':
                self.compressed_name = self.name
            elif self.compression == 'zip':
                self.compressed_name = self.name + '.zip'
            elif self.compression == 'tar.gz':
                self.compressed_name = self.name + '.tar.gz'
            else:
                assert False
        else:
            self.compressed_name = compressed_name
        self.contact = contact
        self.description = description
        self.path = None
        self.installed_path = None
        self.status = None
        self.install_steps = install_steps
        self.install_parent = install_parent
        self.install_sub = install_sub
        self.requires = requires
        # here is the hack in which we add resource to the global list
        ALL_RESOURCES[self.category].append(self)

    def listing(self, opts):
        return '%s = %s' % (self.name, self.description)

    def do_install(self, cfg_path, opts):
        if self.status < RESOURCE_STATUS_CODE.DOWNLOADED:
            self.do_download()
        if self.install_steps:
            final_path = os.path.join(os.path.expandvars(self.install_parent), 
                                      os.path.expandvars(self.install_sub))
        else:
            final_path = self.path
        if os.path.exists(final_path):
            self.status = RESOURCE_STATUS_CODE.INSTALLED
            self.installed_path = final_path
            return
        if self.requires:
            for requirement in self.requires:
                install_command(requirement, cfg_path, opts)
        cwd = os.path.abspath(os.getcwd())
        try:
            
            parent_var = os.path.expandvars(self.install_parent)
            _my_makedirs(parent_var)
            download_parent = os.path.dirname(os.path.abspath(self.path))
            _my_chdir(self.path)
            for step_dict in self.install_steps:
                wd = step_dict.get('wd')
                cmd_list = step_dict.get('commands')
                for cmd in cmd_list:
                    system_call(cmd, wd)
        finally:
            _my_chdir(cwd)
        if not os.path.exists(final_path):
            raise RuntimeError('Installation steps completed, but installation products were not found at "%s"' % final_path)
        self.status = RESOURCE_STATUS_CODE.INSTALLED
        self.installed_path = final_path
            
    def do_download(self):
        parent_var = RESOURCE_CATEGORIES[self.category]
        parent_dir = get_otol_build_env(parent_var)
        assert parent_dir
        _my_makedirs(parent_dir)
        cwd = os.path.abspath(os.getcwd())
        try:
            parent_dir = os.path.abspath(parent_dir)
            expected_path = os.path.join(parent_dir, self.compressed_name)
            _my_chdir(parent_dir)
            if self.protocol == 'http':
                if os.path.exists(expected_path):
                    _LOG.warn('Path "%s" already exists. It will not be downloaded again...\n' % expected_path)
                    fp = expected_path
                else:
                    p = download_http(self.url)
                    fp = os.path.join(parent_dir, p)
                self.compressed_path = fp

                expected_path = os.path.join(parent_dir, self.name)
                if os.path.exists(expected_path):
                    if expected_path != fp:
                        _LOG.warn('Path "%s" already exists. It will not be unpacked again...\n' % expected_path)
                    fp = expected_path
                else:
                    if self.compression == 'zip':
                        _LOG.info('Unzipping "%s"...\n"' % fp)
                        unzip_file(fp, parent_dir)
                        fp = os.path.join(parent_dir, self.name)
                    elif self.compression == 'tar.gz':
                        _LOG.info('Unpacking "%s"...\n"' % fp)
                        untar_gz(fp, parent_dir)
                        fp = os.path.join(parent_dir, self.name)
                    _LOG.info('Obtained "%s"...\n"' % fp)
                self.path = fp
                return fp
            elif self.protocol == 'svn':
                if os.path.exists(expected_path):
                    _LOG.warn('Path "%s" already exists. It will not be downloaded again...\n' % fp)
                else:
                    system_call(['svn', 'checkout', self.url, self.name])
                self.path = expected_path
                self.compressed_path = self.path
            else:
                assert False
            self.status = RESOURCE_STATUS_CODE.DOWNLOADED

        finally:
            _my_chdir(cwd)

def get_resource_obj(name=''):
    nl = name.lower()
    for row in ALL_RESOURCES.itervalues():
        for resource in row:
            if resource.name.lower() == nl:
                return resource
    return None

def get_flattened_resource_list():
    r = []
    for key in RESOURCE_CATEGORIES.keys():
        r.extend(ALL_RESOURCES[key])
    return r

def list_command(opts):
    '''Lists all the known resources to stdout.'''
    out = sys.stdout
    for resource in get_flattened_resource_list():
        out.write(resource.listing(opts))
        out.write('\n')


def get_cfg_interface(cfg_path):
    global _CFG_PARSER
    if _CFG_PARSER is None:
        from ConfigParser import RawConfigParser
        c = RawConfigParser()
        for resource in get_flattened_resource_list():
            c.add_section(resource.name.lower())
        if cfg_path and os.path.exists(cfg_path):
            co = open(cfg_path)
            c.readfp(co)
            co.close()
        _CFG_PARSER = c
    return _CFG_PARSER
        

def get_resource_status_code(res_id, cfg_path, opts):
    resource = get_resource_obj(name=res_id)
    if resource is None:
        raise ValueError('Resource "%s" not recognized' % res_id)
    resource_path = None
    cfg_interface = get_cfg_interface(cfg_path)
    try:
        p = cfg_interface.get(res_id.lower(), 'path')
    except:
        p = None
    resource.status = RESOURCE_STATUS_CODE.MISSING
    if p and os.path.exists(p):
        resource.path = p
        resource.status = RESOURCE_STATUS_CODE.DOWNLOADED
    try:
        p = cfg_interface.get(res_id.lower(), 'installed_path')
    except:
        p = None
    if p and os.path.exists(p):
        resource.installed_path = p
        resource.status = RESOURCE_STATUS_CODE.INSTALLED
    return resource.status
        
    
    
def status_command(res_id, cfg_path, opts):
    '''Downloads and installs the resource with name `res_id` if it is not 
    already installed.
    '''
    s = get_resource_status_code(res_id, cfg_path, opts)
    resource = get_resource_obj(name=res_id)
    if s == RESOURCE_STATUS_CODE.INSTALLED:
        _LOG.info('"%s" is INSTALLED at "%s"' % (res_id, resource.installed_path))
        return
    if s == RESOURCE_STATUS_CODE.DOWNLOADED:
        _LOG.info('"%s" is DOWNLOADED at "%s"' % (res_id, resource.path))
        return
    if s == RESOURCE_STATUS_CODE.MISSING:
        _LOG.info('"%s" is MISSING' % (res_id))
        return
    if s == RESOURCE_STATUS_CODE.SKIPPED:
        _LOG.info('"%s" is SKIPPED' % (res_id))
        return
    assert False
    
    
def get_command(res_id, cfg_path, opts):
    '''Downloads and installs the resource with name `res_id` if it is not 
    already installed.
    '''
    s = get_resource_status_code(res_id, cfg_path, opts)
    resource = get_resource_obj(name=res_id)
    if s == RESOURCE_STATUS_CODE.INSTALLED:
        _LOG.info('Resource "%s" already installed at "%s"' % (res_id, resource.installed_path))
        return
    if s == RESOURCE_STATUS_CODE.DOWNLOADED:
        _LOG.info('Resource "%s" already obtained at "%s"' % (res_id, resource.path))
        return
    p = resource.do_download()
    cfg_interface = get_cfg_interface(cfg_path)
    cfg_interface.set(res_id.lower(), 'path', resource.path)
    cfg_path_par = os.path.dirname(cfg_path)
    _my_makedirs(cfg_path_par)
    with open(cfg_path, 'wb') as cfg_fileobj:
        cfg_interface.write(cfg_fileobj)

def install_command(res_id, cfg_path, opts):
    '''Downloads and installs the resource with name `res_id` if it is not 
    already installed.
    '''
    s = get_resource_status_code(res_id, cfg_path, opts)
    resource = get_resource_obj(name=res_id)
    if s == RESOURCE_STATUS_CODE.INSTALLED:
        _LOG.info('Resource "%s" already installed at "%s"' % (res_id, resource.installed_path))
        return
    if s != RESOURCE_STATUS_CODE.DOWNLOADED:
        get_command(res_id, cfg_path, opts)
        
    p = resource.do_install(cfg_path, opts)
    cfg_interface = get_cfg_interface(cfg_path)
    cfg_interface.set(res_id.lower(), 'installed_path', resource.installed_path)
    cfg_path_par = os.path.dirname(cfg_path)
    _my_makedirs(cfg_path_par)
    with open(cfg_path, 'wb') as cfg_fileobj:
        cfg_interface.write(cfg_fileobj)
    
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
        
            

################################################################################
# Script by Mark T. Holder available for use under the terms of either the 
# BSD or GPL (v3) license. (see BSDLicense.txt GPL.txt)
#
################################################################################
