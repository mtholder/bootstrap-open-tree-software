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
    <td>OPEN_TREE_PKG_SHARE</td>
    <td>Default directory to search for taxonomy files</td>
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
    <td>OPEN_TREE_DOWNLOAD_DEV_RESOURCE_CFG</td>
    <td>Config file that stores the location of local versions of the resources you have downloaded</td>
    <td><pre>${OPEN_TREE_USER_SETTINGS_DIR}/download-dev-resource.cfg</pre></td>
</tr>
</table>
