# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category



def index(request):
    context = RequestContext(request)
    category = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category}
    return render_to_response('rango/index.html', context_dict, context)


def about(request):
    context = RequestContext(request)
    context_dict = {'variable_name': "this is a test about page"}
    return render_to_response('rango/about.html', context_dict, context)