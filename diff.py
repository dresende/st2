import sublime, sublime_plugin
import subprocess

diff_files = []

class DiffAddFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		global diff_files

		diff_files.append(self.window.active_view().file_name())

		if len(diff_files) == 2:
			p = subprocess.Popen(["diff", diff_files[0], diff_files[1]], bufsize=4096, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = p.communicate()

			output = stdout
			if stderr != "":
				output = stderr

			diff_view = self.window.new_file()
			diff_view.set_scratch(True)

			diff_edit = diff_view.begin_edit()
			diff_view.insert(diff_edit, diff_view.size(), output)
			diff_view.end_edit(diff_edit)

			diff_view.set_syntax_file("Packages/Diff/Diff.tmLanguage")

			diff_files = []