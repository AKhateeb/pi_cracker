import re
from django.shortcuts import render
from subprocess import Popen, PIPE, STDOUT
from django.http import JsonResponse
from .cracker import Cracker

output = None
exitstatus = None
username = ""
DEFAULT_THREADS = 10
cracker = Cracker(DEFAULT_THREADS)

# def increase_length():
# 	new_len = cracker.engine.pass_gen.increase_pwd_len()
# 	cracker.engine.passlist = []
# 	# cracker.engine.pass_gen = cracker.pas ???? --- complete here ----
# 	return JsonResponse(new_len, safe=False) 


def index(request):
	return render(request, template_name=__package__+".html",context=None)

	
def set_username(request):
	if request.method == "GET":
		result = False
		username = request.GET.get('username', None)
		if username and re.match(r"^[a-zA-Z0-9._]+$", username):
			cracker.set_username(username)
			request.session['username'] = username
			result = True
		return JsonResponse({"result":result, "username":username}, safe=False)

def check_status(request):
	if request.method == "GET":
		return JsonResponse(cracker.get_status(), safe=False)
	pass


def parse_state(request):
	if request.method == "GET":
		result = False
		response = "Username does not exists"
		state = request.GET.get('state', None)
		# try:
		if "username" in request.session:
			function_map = {
				"start": cracker.start(),
				# "increase_length":increase_length,
				"stop": cracker.stop(),
				"pause": cracker.stop(),
			}
			if state in function_map.keys():
				response = function_map[state]
				result = True
		# except Exception as ex:
		# 	result = False
		# 	response = str(ex)
		# 	print(ex)
		return JsonResponse({"result":result, "message": response}, safe=False)
	