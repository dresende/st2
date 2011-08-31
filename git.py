import sublime, sublime_plugin
import os, subprocess
import time
from threading import Timer

'''
  Show git command in a quick panel

  Key binding: ["ctrl+super+g"]
  Command: "git_commands"
'''
class GitCommandsCommand(sublime_plugin.WindowCommand):
	commands = {
		"git_log"   : "Show log",
		"git_diff"  : "Show stage diff",
		"git_status": "Show stage status",
		"git_commit": "Add current file and commit stage",
		"git_push"  : "Push master to remote origin"
	}
	def run(self):
		self.window.show_quick_panel(self.commands.values(), self.runCommand)
	
	def runCommand(self, index):
		if index == -1:
			return
		
		i = 0
		for k in self.commands:
			if i == index:
				return self.window.run_command(k)
			i += 1

'''
  Ask Git to show a diff of the current active view (it will save the file first)

  Key binding: ["ctrl+super+g", "ctrl+super+d"]
  Command: "git_diff"
'''
class GitDiffCommand(sublime_plugin.WindowCommand):
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
  Add current file to stage and commit

  Key binding: ["ctrl+super+g", "ctrl+super+c"]
  Command: "git_commit"
'''
class GitCommitCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		if view.file_name() == None:
			return

		view.run_command("save")
		view.window().show_input_panel("Message:", "", self.onCommitDone, None, None)

	def onCommitDone(self, msg):
		if len(msg) == 0:
			return

		self.view = self.window.active_view()
		filename = self.view.file_name()

		self.setFinalCommitStatus("Adding '" + os.path.basename(filename) + "'")

		p = subprocess.Popen([ "git", "add", filename ],
							cwd = os.path.dirname(filename),
							bufsize = 4096,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
		stdout, stderr = p.communicate()

		if len(stderr) > 0:
			print stderr
			return self.setFinalCommitStatus("Error adding file...")
		
		self.setCommitStatus("Committing '" + msg + "'")

		p = subprocess.Popen([ "git", "commit", "-m", msg ],
							cwd = os.path.dirname(filename),
							bufsize = 4096,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
		stdout, stderr = p.communicate()

		if len(stderr) > 0:
			print stderr
			return self.setFinalCommitStatus("Error committing...")

		self.setFinalCommitStatus("Committed")

	def setCommitStatus(self, msg):
		self.view.set_status("git-status", msg)

	def setFinalCommitStatus(self, msg):
		self.view.set_status("git-status", msg)
		Timer(3, self.clearCommitStatus, ()).start()

	def clearCommitStatus(self):
		self.view.erase_status("git-status")

'''
  Push master to origin

  Key binding: ["ctrl+super+g", "ctrl+super+p"]
  Command: "git_push"
'''
class GitPushCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.view = self.window.active_view()
		self.filename = self.view.file_name()
		if self.filename == None:
			return

		self.setPushStatus("Pushing...")
		Timer(1, self.gitPush, ()).start()
	
	def gitPush(self):
		p = subprocess.Popen([ "git", "push", "origin", "master" ],
							cwd = os.path.dirname(self.filename),
							bufsize = 4096,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
		stdout, stderr = p.communicate()

		output = stdout
		if stderr != "":
			output = stderr
		output = output.splitlines()

		# this is very bad... but it works!
		if len(output) == 0:
			return self.setFinalPushStatus("Error pushing")

		if output[0] == "Everything up-to-date":
			return self.setFinalPushStatus("Push is up-to-date")
		
		return self.setFinalPushStatus("Pushed:" + output[1])
		print output

	def setPushStatus(self, msg):
		self.view.set_status("git-status", msg)

	def setFinalPushStatus(self, msg):
		self.view.set_status("git-status", msg)
		Timer(3, self.clearPushStatus, ()).start()

	def clearPushStatus(self):
		self.view.erase_status("git-status")

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

'''
  Ask Git to show the log of the current active view repository

  Key binding: ["ctrl+super+g", "ctrl+super+l"]
  Command: "git_log"
'''
class GitLogCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		if view.file_name() == None:
			return

		status_title = get_git_remote_url(view.file_name())
		if status_title == False:
			status_title = os.path.basename(view.file_name())

		p = subprocess.Popen([ "git", "log", "--no-color", "-30" ],
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
			if output[line][0:7] == "commit ":
				output[line] = "+++ Commit: " + output[line][7:].strip()
			elif output[line][0:7] == "Author:":
				output[line] = "+   Author: " + output[line][7:].strip()
			elif output[line][0:5] == "Date:":
				output[line] = "-     Date: " + output[line][5:].strip()

		output = "\n".join(map(str, output))
		show_in_new_view(self.window, output, "(git log) " + status_title, "Diff")

class GitEvents(sublime_plugin.EventListener):
	# when loading a file...
	def on_load(self, view):
		# show remote url if found on status bar
		url = get_git_remote_url(view.file_name())
		branch = get_git_branch(view.file_name())

		# zinfo is just to put this info after the other git status messages
		view.set_status("git-zinfo", url + " (" + branch + ")")

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

# get the git branch for a given path
def get_git_branch(path):
	p = subprocess.Popen([ "git", "branch", "--no-color" ],
							cwd = os.path.dirname(path),
							bufsize = 4096,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
	stdout, stderr = p.communicate()
	stdout = stdout.splitlines()

	for line in stdout:
		if line[0:2] == "* ":
			return line[2:].strip()

	return "?"