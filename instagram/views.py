import re
from django.shortcuts import render
from subprocess import Popen, PIPE, STDOUT

cracker = None
output = None
exitstatus = None

def index(request):
	return render(request, template_name=__package__+".html",context=None)

def start(request):
	username = request.GET.get('username', None)
	pass_list = ['ffff','dftghfd','frtgyhujy']
	command = ["python","instagram","-u", username, "-f", pass_list, "16"]
	if username and re.match(r"^[a-zA-Z0-9._]+$", username):
		cracker = Popen(command, stdout=PIPE, stderr=STDOUT)
		output = cracker.stdout.read()
		exitstatus = cracker.poll()

def check_status(request):
	result = {"output":str(output), "status": ""}
	if exitstatus==0:
		result["status"] = "Success"
	else:
		result["status"] = "Failed"
