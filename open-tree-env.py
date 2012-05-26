#!/usr/bin/env python
'''Wraps common operations on settings and environmental variables needed
during build.
'''
import os
_DEF_OPEN_TREE_VERSION = '0.0.1'
build_env_var_list = ['OPEN_TREE_USER_SETTINGS_DIR', 
                      'OPEN_TREE_INSTALL_DIR',
                      'OPEN_TREE_VERSION',
                      'OPEN_TREE_PKG_SHARE',
                      'OPEN_TREE_TAXONOMY_DIR',
                      'OPEN_TREE_DEPENDENCY_DIR',
                      'OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG']

def get_otol_build_env(var):
    '''Checks the environment for `var` and substitutes an appropriate default
    value if it is not found (or None if `var` is not recognized)
    '''
    val = os.environ.get(var)
    if val is not None:
        return val
    if var == 'OPEN_TREE_USER_SETTINGS_DIR':
        return os.path.expanduser(os.path.join('~', '.open_tree'))
    if var == 'OPEN_TREE_INSTALL_DIR':
        return os.path.expanduser(os.path.join('~', 'open_tree_install'))
    if var == 'OPEN_TREE_VERSION':
        return _DEF_OPEN_TREE_VERSION
    if var == 'OPEN_TREE_PKG_SHARE':
        install_dir = get_otol_build_env('OPEN_TREE_INSTALL_DIR')
        version_str = get_otol_build_env('OPEN_TREE_VERSION')
        return os.path.join(install_dir, 'share', 'open-tree-' + version_str)
    if var == 'OPEN_TREE_TAXONOMY_DIR':
        share_dir = get_otol_build_env('OPEN_TREE_PKG_SHARE')
        return os.path.join(share_dir, 'taxonomy')
    if var == 'OPEN_TREE_DEPENDENCY_DIR':
        p = os.path.dirname(__file__)
        return os.path.abspath(p)
    if var == 'OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG':
        p = get_otol_build_env('OPEN_TREE_USER_SETTINGS_DIR')
        return os.path.join(p, 'download-dev-resource.cfg')

    return None    

if __name__ == '__main__':
    import sys
    v_list = sys.argv[1:]
    if not v_list:
        v_list = build_env_var_list
    for a in build_env_var_list:
        v = get_otol_build_env(a)
        if v is None:
            sys.stdout.write('unset %s\n' % a )
        else:
            sys.stdout.write('export %s="%s"\n' % (a, v))
