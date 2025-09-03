from django.shortcuts import render

def show_main(request):
    context = {
        'npm' : '2406437615',
        'name': 'Garuga Dewangga Putra Handikto',
        'class': 'PBP F'
    }

    return render(request, "main.html", context)

