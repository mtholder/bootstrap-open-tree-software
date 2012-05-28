bootstrap-open-tree-software
============================
This repo will house scripts and utilities that help developers get a new
development machine ready to build and test the software tools associated with
the Open Tree of Life project.

Each software tool will be fairly self contained, but this repository should
help with obtaining dependencies and keeping track of links to large artifacts
(e.g. taxonomies) which are not currently under version control.


Environmental Variables
-----------------------
You can put variables in your environment to override the default location for
resources.

<table border="1">
<tr>
    <th>Env. variable</th>
    <th width="25%">Purpose</th>
    <th>Default</th>
</tr>
<tr>
    <td>OPEN_TREE_USER_SETTINGS_DIR</td>
    <td>Directory containing config files to be read at runtime</td>
    <td><pre>${HOME}/.open_tree</pre></td>
</tr>
<tr>
    <td>OPEN_TREE_INSTALL_DIR</td>
    <td>The top level (prefix) directory of the installed version of the software</td>
    <td><pre>${HOME}/open_tree_install</pre></td>
</tr>
<tr>
    <td>OPEN_TREE_BIN_DIR</td>
    <td>The location of installed Open Tree of Life executables (put on PATH to run)</td>
    <td><pre>${OPEN_TREE_INSTALL_DIR}/bin</pre></td>
</tr>
<tr>
    <td>OPEN_TREE_LIB_DIR</td>
    <td>The location of installed Open Tree of Life libraries (may need to be on load path at runtime)</td>
    <td><pre>${OPEN_TREE_INSTALL_DIR}/lib</pre></td>
</tr>
<tr>
    <td>OPEN_TREE_PKG_SHARE</td>
    <td>Default directory to data related to the package</td>
    <td><pre>${OPEN_TREE_INSTALL_DIR}/share/open-tree-#.#.#</pre></td>
</tr>
<tr>
    <td>OPEN_TREE_TAXONOMY_DIR</td>
    <td>Default directory to search for taxonomy files</td>
    <td><pre>${OPEN_TREE_PKG_SHARE}/taxonomy</pre></td>
</tr>
<tr>
    <td>OPEN_TREE_DEPENDENCY_DIR</td>
    <td>Parent of the directories containing dependencies</td>
    <td>The top level of the bootstrap-open-tree-software repository</td>
</tr>
<tr>
    <td>OPEN_TREE_SOURCE_DIR</td>
    <td>Parent directory into which Open Tree of Life git repos are checked out by default</td>
    <td><pre>${OPEN_TREE_DEPENDENCY_DIR}/..</td>
</tr>
<tr>
    <td>OPEN_TREE_BUILD_TOOL_PREFIX</td>
    <td>Prefix argument given to build tools (resulting in bin, lib, ... subdirectories). Required for building, but not running. Make, gcc, javac, etc are condsidered to be prerequisites. This is intended for small and more obscure build tools (e.g. autoconf)</td>
    <td><pre>${OPEN_TREE_DEPENDENCY_DIR}/tools</td>
</tr>
<tr>
    <td>OPEN_TREE_BUILD_TOOL_BIN_DIR</td>
    <td>Directory that should be on your PATH so you can find build tools</td>
    <td><pre>${OPEN_TREE_BUILD_TOOL_PREFIX}/bin</td>
</tr>
<tr>
    <td>OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG</td>
    <td>Config file that stores the location of local versions of the resources you have downloaded</td>
    <td><pre>${OPEN_TREE_USER_SETTINGS_DIR}/download-dev-resource.cfg</pre></td>
</tr>
<tr>
    <td>OPEN_TREE_BUILD_TAG</td>
    <td>A simple string (no spaces or shell token breakers) used to tag this build variant</td>
    <td><pre>release</pre></td>
</tr>
<tr>
    <td>OPEN_TREE_VERSION</td>
    <td>tag used in package install</td>
    <td><pre>0.0.1</pre></td>
</tr>
</table>

Example Usage
=============
<pre>
./open_tree_env.py > open_tree_env.sh
[tweak open_tree_env.sh for your preferences ]
source open_tree_env.sh
python download-dev-resource.py install taxa_allCoL.tre
python download-dev-resource.py install ncl
python download-dev-resource.py status
</pre>
