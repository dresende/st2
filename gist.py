import sublime, sublime_plugin
import os, subprocess
import tempfile
from threading import Timer

class GistCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.view = self.window.active_view()

		tmp_gist = tempfile.TemporaryFile()
		tmp_gist.write(self.view.substr(sublime.Region(0, self.view.size())))
		tmp_gist.seek(0)

		self.showMsg("Creating gist...")

		p = subprocess.Popen([ "gist", "--no-open" ],
							bufsize = 4096,
							stdin = tmp_gist,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
		stdout, stderr = p.communicate()

		output = stdout
		if stderr != "":
			output = stderr

		output = output.splitlines()

		sublime.set_clipboard(output[0])

		print "URL", output[0]

		tmp_gist.close()

		self.clearTemporaryMsg()
		self.window.show_input_panel("Gist:", output[0], None, None, None)

	def showMsg(self, msg):
		self.view.set_status("gist", msg)

	def showTemporaryMsg(self, msg):
		self.view.set_status("gist", msg)
		Timer(3, self.clearTemporaryMsg, ()).start()

	def clearTemporaryMsg(self):
		self.view.erase_status("gist")