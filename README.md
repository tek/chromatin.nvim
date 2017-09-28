# Chromatin

This **neovim** python remote plugin provides management for plugins built with [ribosome] and distributed over
**pypi**.

Each plugin is installed with `pip` into a separate virtualenv and loaded automatically, without the need for
`UpdateRemotePlugins`, allowing runtime reloading of the complete plugin package.

# Install

`Plug tek/chromatin.nvim`

The nvim plugin is just a bootstrap stub that installs **chromatin** itself into a virtualenv and starts its host.
No dependencies have to be installed as a prerequisite; if a python 3.6 interpreter is available, everything should be
automatically set up.

On the first start, it takes about 10 seconds for bootstrapping to complete, after which **chromatin** begins to install
your plugins.

**Note**: The plugin has a hard dep on **pyuv** at the moment, because the bootstrapping process hangs with the
**asyncio** main loop.

# Usage

## Declare
When starting, **chromatin** reads plugin configuration from `g:chromating_rplugins`:

```viml
let g:chromatin_rplugins = [
  \ { 'name': 'myo' },
  \ { 'name': 'proteome', 'spec': '/home/tek/path/to/proteome' },
  \ ]
```

To add a plugin at runtime, use the command `Cram`:

```
Cram myo
Cram /home/tek/path/to/proteome { 'name': 'proteome' }
```

Any string that `pip` can understand will work as a spec, but the name has to be supplied in the options for nontrivial
requirements.

## Install

If the variable `g:chromatin_autostart` is unset or `1`, all plugins will be installed and activated on neovim startup
or after they have been added.

To manually trigger installation, execute `CrmSetupPlugins`.

Virtualenvs are stored in `g:chromatin_venv_dir`, defaulting to `~/.cache/chromatin/venvs`.

## Activate

Each plugin gets its own plugin host, allowing differing library dependency versions.

In order to manually trigger the activation of plugins, execute `CrmActivate [plugin_names]`.

## Update

The command `CrmUpdate [plugin_names]` runs `pip install --upgrade` for the specified or all plugins.
This includes **chromatin** itself, but you will have to restart vim for the changes to take effect.

## Deactivate

Plugins hosts can be shut down with the command `CrmDeactivate [plugins]`, removing all request handlers. The command
`CrmReboot [plugins]` combines deactivating and reactivating plugins, allowing plugins to be updated at runtime.

By default, plugins are rebooted after an update unless the variable `g:chromatin_autoreboot` is set to `0`.

## Configure

After a plugin has been loaded, files matching `{runtimepath}/chromatin/<plugin_name>/*.vim` are sourced to allow for
post-load configuration.

[ribosome]: https://github.com/tek/ribosome
