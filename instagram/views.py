from django.shortcuts import render

cracker = None
current_password = "xxxx"


def index(request):
    return render(request, template_name=__package__+".html",context=None)

def start(request):
    username = request.GET.get('username', None)
    if username:
        cracker = ""