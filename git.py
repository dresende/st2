import sublime, sublime_plugin
import os, subprocess

'''
  Ask Git to show a diff of the current active view (it will save the file first)

  Key binding: ["ctrl+super+g", "ctrl+super+d"]
  Command: "git_diff"
'''
class GitDiffCommand(sublime_plugin.WindowCommand):g
	def run(self):
		view = self.window.active_view()
		if view.file_name() == None:
			return

		view.run_command("save")

		p = subprocess.Popen([ "git", "diff", "-b", "--no-color", view.file_name() ],
							cwd = os.path.dirname(view.file_name()),
							bufsize = 4096,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
		stdout, stderr = p.communicate()

		output = stdout
		if stderr != "":
		 	output = stderr

		show_in_new_view(self.window, output, "(git diff) " + os.path.basename(view.file_name()), "Diff")

'''
  Ask Git to show the status of the current active view repository

  Key binding: ["ctrl+super+g", "ctrl+super+s"]
  Command: "git_status"
'''
class GitStatusCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		if view.file_name() == None:
			return

		status_title = get_git_remote_url(view.file_name())
		if status_title == False:
			status_title = os.path.basename(view.file_name())

		p = subprocess.Popen([ "git", "status", "--porcelain" ],
							cwd = os.path.dirname(view.file_name()),
							bufsize = 4096,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
		stdout, stderr = p.communicate()

		output = stdout
		if stderr != "":
			output = stderr

		output = output.splitlines()
		for line in range(0, len(output)):
			if output[line][0:2] == " M":
				output[line] = "+ " + output[line][2:].strip()
			elif output[line][0:2] == "??":
				output[line] = "+++ " + output[line][2:].strip()

		output = "\n".join(map(str, output))
		show_in_new_view(self.window, output, "(git status) " + status_title, "Diff")

class GitEvents(sublime_plugin.EventListener):
	# when loading a file...
	def on_load(self, view):
		# show remote url if found on status bar
		url = get_git_remote_url(view.file_name())
		if url != False:
			view.set_status("git-remote", url)

# show some text in a new view
def show_in_new_view(window, text, name, syntax = None):
	view = window.new_file()

	edit = view.begin_edit()
	view.insert(edit, view.size(), text)
	view.end_edit(edit)

	view.set_scratch(True)
	view.set_name(name)
	if syntax != None:
		view.set_syntax_file("Packages/" + syntax + "/" + syntax + ".tmLanguage")

# get the git remote url for a given path
def get_git_remote_url(path):
	p = subprocess.Popen([ "git", "config", "remote.origin.url" ],
							cwd = os.path.dirname(path),
							bufsize = 4096,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
	stdout, stderr = p.communicate()
	if len(stdout) > 0:
		return stdout.strip()

	return False