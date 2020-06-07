from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import ServerDataFileName

# Create your views here.

def index(request):
    # latest_question_list = ServerDataFileName.objects.order_by('-pub_date')[:5]
    latest_filenames = ServerDataFileName.objects.all()[:5]
    # template = loader.get_template('dataimport/index.html')
    context = {
        'latest_filenames': latest_filenames,
    }
    # return HttpResponse(template.render(context, request))
    return render(request, 'dataimport/index.html', context)
# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)