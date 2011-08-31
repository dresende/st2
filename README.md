# Sublime Text 2

This is a repository with my user preferences and key bindings as well as
my plugins.

## Plugins

### Open Last Closed Files

Binding `Ctrl+Shift+T` to this plugin command ("open_last_closed_file"), the plugin will
behave just like in Firefox, opening the last files. For now, it can open the last 50
closed files (variable at the top of the plugin). Later on, I'll put this on settings.

### Toggle Quotes

Switch from " to ' using `Ctrl+Shift+Q`.

### Increase / Decrease a Number

Put the cursor(s) hover a number in a file. Press `Alt+Up` or `Alt+Down` and see for
yourself.

### Git

This is not a git integration, this plugin will just be a couple of tweaks to make my
life easier. For instance, it displays the remote git repository on the status bar when
you have a git file opened, it will show you a colored diff of the changes of your file
from the last commit and will show you also a colored status of the current repository.
To start press `Ctrl+Super+G` and choose from the list. You better know how to work with
git!

### Diff

Open 2 files, select the first tab and press `Ctrl+Super+D`. The module will add the file
to the queue. Now select the second tab and press again `Ctrl+Super+D`. The module will
pick the file on the queue and add this one, make a diff and opens a new tab with a .diff
file (the queue is then cleared and you can start over again).