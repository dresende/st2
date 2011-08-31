#!/bin/sh
FOUND=`grep 'application/x-extension-sublime-project' /etc/mime.types`
if [ -z "$FOUND" ]; then
	echo "Registering MIME.."
	echo 'application/x-extension-sublime-project              sublime-project' >> /etc/mime.types
	mkdir -p /usr/share/icons/gnome/scalable/mimetypes/
	ln -s `pwd`/sublime-project-mime-icon.svg /usr/share/icons/gnome/scalable/mimetypes/application-x-extension-sublime-project.svg
	ln -s `pwd`/sublime-project-mime-icon.png /usr/share/icons/gnome/48x48/mimetypes/application-x-extension-sublime-project.png
	ln -s `pwd`/sublime_text.desktop /usr/share/applications/sublime_text.desktop
else
	echo "MIME already registed"
fi
