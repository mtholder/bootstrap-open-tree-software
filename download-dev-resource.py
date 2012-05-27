#!/usr/bin/env python
'''This is a quick and dirty way to provide developers a way to download
resources needed to build and test components of the open tree software.

environmental variables:
    OPEN_TREE_DOWNLOAD_DEV_RESOURCE_LOGGING_LEVEL=debug for more info
    
    OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG or OPEN_TREE_USER_SETTINGS_DIR to change the 
        default location for config file that stores local filepaths

'''
from open_tree_download_lib import OpenTreeResource
################################################################################
# Place new resources here
################################################################################
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
                 description='NEXUS class library (C++ library for parsing phylogenetic data)',
                 install_parent='${OPEN_TREE_INSTALL_DIR}',
                 install_sub='lib/ncl',
                 install_steps = [{'commands' : [['sh', 'bootstrap.sh']
                                                ]},
                                  {'wd' : 'build${OPEN_TREE_BUILD_TAG}',
                                   'commands' : [['../configure', '--prefix=${OPEN_TREE_INSTALL_DIR}'],
                                                 ['make'],
                                                 ['make', 'install']
                                                ]
                                  },
                                 ],
                 requires = ['automake-1.11.5', 'libtool-2.4.2'])

OpenTreeResource(name='autoconf-2.69', 
                 url='http://ftp.gnu.org/gnu/autoconf/autoconf-2.69.tar.gz',
                 protocol='http',
                 min_version=(2, 69, 0), # we probably could deal with an earlier automake
                 category='dependency',
                 compression='tar.gz',
                 contact='mtholder',
                 description='tool for creating cross-platform configue scripts',
                 install_parent='${OPEN_TREE_BUILD_TOOL_PREFIX}',
                 install_sub='bin/autoconf',
                 install_steps = [{'commands' : [['./configure', '--prefix=${OPEN_TREE_BUILD_TOOL_PREFIX}'],
                                                 ['make'],
                                                 ['make', 'install']
                                                ]
                                  },
                                 ])
OpenTreeResource(name='automake-1.11.5', 
                 url='http://ftp.gnu.org/gnu/automake/automake-1.11.5.tar.gz',
                 protocol='http',
                 min_version=(1, 11, 5), # we probably could deal with an earlier automake
                 category='dependency',
                 compression='tar.gz',
                 contact='mtholder',
                 description='tool for creating cross-platform Makefile',
                 install_parent='${OPEN_TREE_BUILD_TOOL_PREFIX}',
                 install_sub='bin/automake',
                 install_steps = [{'commands' : [['./configure', '--prefix=${OPEN_TREE_BUILD_TOOL_PREFIX}'],
                                                 ['make'],
                                                 ['make', 'install']
                                                ]
                                  },
                                 ],
                 requires = ['autoconf-2.69'])
OpenTreeResource(name='libtool-2.4.2', 
                 url='http://mirrors.kernel.org/gnu/libtool/libtool-2.4.2.tar.gz',
                 protocol='http',
                 min_version=(2, 4, 2), # we probably could deal with an earlier libtool
                 category='dependency',
                 compression='tar.gz',
                 contact='mtholder',
                 description='tool for creating cross-platform dynamic libraries',
                 install_parent='${OPEN_TREE_BUILD_TOOL_PREFIX}',
                 install_sub='bin/libtool',
                 install_steps = [{'commands' : [['./configure', '--prefix=${OPEN_TREE_BUILD_TOOL_PREFIX}'],
                                                 ['make'],
                                                 ['make', 'install']
                                                ]
                                  },
                                 ],
                 requires = ['automake-1.11.5'])





   
if __name__ == '__main__':
    from open_tree_env import get_otol_build_env, put_otol_build_env_into_env
    from optparse import OptionParser
    import os
    import sys
    from open_tree_download_lib import get_logger, get_flattened_resource_list, \
            list_command, status_command, get_command, install_command
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

    _LOG = get_logger()
    description =  '%s %s %s' % (_program_name, _program_version, _program_subtitle)
    command_width = len('install [resource]') + 1
    command_help = [('list', 'list available resources (no additional resource argument needed)'), 
                    ('status [resource]', 'show the status of the designated resource'),
                    ('get [resource]', 'download (and unpack) the designated resource'),
                    ('install [resource]', 'install the designated resource'),
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

    put_otol_build_env_into_env()

    command = args[0].lower()
    try:
        if command == 'list':
            list_command(opts)
        else:
            if len(args) < 2:
                if command == 'status':
                    res_list = [i.name for i in get_flattened_resource_list()]
                else:
                    sys.exit('Expecting a resource identifier after the "%s" command.' % command)
            else:
                res_list = args[1:]
            for res_id in res_list:
                if command == 'status':
                    status_command(res_id, cfg_path, opts)
                elif command == 'get':
                    get_command(res_id, cfg_path, opts)
                elif command == 'install':
                    install_command(res_id, cfg_path, opts)
                else:
                    sys.exit('command "%s" not recognized. Use -h for help' % command)
    except Exception, e:
        if True:
            raise
        else:
            sys.exit("Failing with an exception:\n    %s\n" % str(e))
        
            

################################################################################
# Script by Mark T. Holder available for use under the terms of either the 
# BSD or GPL (v3) license. (see BSDLicense.txt GPL.txt)
#
################################################################################
