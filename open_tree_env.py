#!/usr/bin/env python
'''Wraps common operations on settings and environmental variables needed
during build.
'''
import os
_DEF_OPEN_TREE_VERSION = '0.0.1'
_build_env_var_list = ['OPEN_TREE_USER_SETTINGS_DIR',
                      'OPEN_TREE_INSTALL_DIR',
                      'OPEN_TREE_VERSION',
                      'OPEN_TREE_BIN_DIR',
                      'OPEN_TREE_LIB_DIR',
                      'OPEN_TREE_PKG_SHARE',
                      'OPEN_TREE_TAXONOMY_DIR',
                      'OPEN_TREE_SOURCE_DIR',
                      'OPEN_TREE_DEPENDENCY_DIR',
                      'OPEN_TREE_BUILD_TOOL_PREFIX',
                      'OPEN_TREE_BUILD_TOOL_BIN_DIR',
                      'OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG',
                      'OPEN_TREE_BUILD_TAG',
                      ]

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
    if var == 'OPEN_TREE_BIN_DIR':
        install_dir = get_otol_build_env('OPEN_TREE_INSTALL_DIR')
        return os.path.join(install_dir, 'bin')
    if var == 'OPEN_TREE_LIB_DIR':
        install_dir = get_otol_build_env('OPEN_TREE_INSTALL_DIR')
        return os.path.join(install_dir, 'lib')
    if var == 'OPEN_TREE_VERSION':
        return _DEF_OPEN_TREE_VERSION
    if var == 'OPEN_TREE_PKG_SHARE':
        install_dir = get_otol_build_env('OPEN_TREE_INSTALL_DIR')
        version_str = get_otol_build_env('OPEN_TREE_VERSION')
        return os.path.join(install_dir, 'share', 'open-tree-' + version_str)
    if var == 'OPEN_TREE_TAXONOMY_DIR':
        share_dir = get_otol_build_env('OPEN_TREE_PKG_SHARE')
        return os.path.join(share_dir, 'taxonomy')
    if var == 'OPEN_TREE_SOURCE_DIR':
        d = os.path.abspath(get_otol_build_env('OPEN_TREE_DEPENDENCY_DIR'))
        p = os.path.dirname(d)
        if p:
            return os.path.abspath(p)
        return d
    if var == 'OPEN_TREE_DEPENDENCY_DIR':
        p = os.path.dirname(__file__)
        return os.path.abspath(p)
    if var == 'OPEN_TREE_BUILD_TOOL_PREFIX':
        p = get_otol_build_env('OPEN_TREE_DEPENDENCY_DIR')
        return os.path.join(p, 'tools')
    if var == 'OPEN_TREE_BUILD_TOOL_BIN_DIR':
        dep_dir = get_otol_build_env('OPEN_TREE_BUILD_TOOL_PREFIX')
        return os.path.join(dep_dir, 'bin')
    if var == 'OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG':
        p = get_otol_build_env('OPEN_TREE_USER_SETTINGS_DIR')
        return os.path.join(p, 'download-dev-resource.cfg')
    if var == 'OPEN_TREE_BUILD_TAG':
        return 'release'
    return None

def put_otol_build_env_into_env():
    '''Assures that all of the OPEN_TREE_... variables are in the os.environ.'''
    for k in _build_env_var_list:
        v = get_otol_build_env(k)
        os.environ[k] = v

def abbreviate_path(p):
    var_list = []
    for a in _build_env_var_list:
        v = get_otol_build_env(a)
        var_list.append([a, v])
    longest_prefix = ''
    longest_prefix_key = ''
    for s_el in var_list:
        s_v = s_el[1]
        if p.startswith(s_v) and len(s_v) > len(longest_prefix):
            longest_prefix = s_v
            longest_prefix_key = s_el[0]
    if longest_prefix:
        pref = longest_prefix_key
        suff = p[len(longest_prefix):]
        return '${%s}%s' % (pref, suff)
    return p

if __name__ == '__main__':
    import sys
    v_list = sys.argv[1:]
    no_args = False
    if not v_list:
        no_args = True
        v_list = _build_env_var_list
    var_list = []
    for a in _build_env_var_list:
        v = get_otol_build_env(a)
        var_list.append([a, v, []])
    # attempt to find the tersest abbreviations
    if no_args:
        for n, el in enumerate(var_list):
            value = el[1]
            subst = el[2]
            longest_prefix = ''
            longest_prefix_key = ''
            for s_el in var_list[:n]:
                s_v = s_el[1]
                if value.startswith(s_v) and len(s_v) > len(longest_prefix):
                    longest_prefix = s_v
                    longest_prefix_key = s_el[0]
            if longest_prefix:
                subst = el[2]
                del subst[:]
                subst.append(longest_prefix_key)
                subst.append(value[len(longest_prefix):])
    for var_entry in var_list:
        a, v = var_entry[:2]
        if v is None:
            sys.stdout.write('unset %s\n' % a )
        else:
            subst = var_entry[2]
            if subst:
                v = '${%s}%s' % (subst[0], subst[1])
            sys.stdout.write('export %s="%s"\n' % (a, v))
    if no_args:
        sys.stdout.write('export PATH="${OPEN_TREE_BIN_DIR}:${OPEN_TREE_BUILD_TOOL_BIN_DIR}:${PATH}"\n')
        import platform
        if platform.system().lower() == 'darwin':
            lib_var = 'DYLD_LIBRARY_PATH'
        else:
            lib_var = 'LD_LIBRARY_PATH'
        sys.stdout.write('export %s="${OPEN_TREE_LIB_DIR}:${%s}"\n' % (lib_var, lib_var))
