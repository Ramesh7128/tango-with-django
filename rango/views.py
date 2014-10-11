# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query

def encode_url(url):
    url = url.replace(' ', '_')
    return url

def decode_url(url):
    url = url.replace('_', ' ')
    return url

def get_category_list():
    cat_list = Category.objects.all()
    return cat_list


def index(request):

    context = RequestContext(request)
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    for category in category_list:
         category.url = encode_url(category.name)#category.name.replace(' ', '_')

    # response = render_to_response('rango/index.html', context_dict, context)
    #
    # visits = int(request.COOKIES.get('visits','0'))
    #
    # if 'last_visit' in request.COOKIES:
    #     last_visit = request.COOKIES['last_visit']
    #     last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
    #
    #     if (datetime.now() - last_visit_time).seconds > 5:
    #         response.set_cookie('visits', visits+1)
    #         response.set_cookie('last_visit', datetime.now())

    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).seconds > 0:
            request.session['visits'] = visits+1
            request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    context_dict['cat_list'] = get_category_list()

    return render_to_response('rango/index.html', context_dict, context)


    # else:
    #     response.set_cookie('last_visit', datetime.now())
    #
    # return response

    #return render_to_response('rango/index.html', context_dict, context)


def about(request):
    context = RequestContext(request)
    context_dict = {'variable_name': "this is a test about page"}
    if request.session.get('visits'):
        visits = request.session.get('visits')
    context_dict['visits'] = visits
    context_dict['cat_list'] = get_category_list()

    return render_to_response('rango/about.html', context_dict, context)

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)#category_name_url.replace('_', ' ')
    context_dict = {'category_name': category_name}

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_url'] = category_name_url
    except Category.DoesNotExist:
        pass
    context_dict['cat_list'] = get_category_list()

    ##search###
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)


    context_dict['result_list'] = result_list


    return render_to_response('rango/category.html', context_dict, context)

def add_category(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)

            return index(request)
        else:
            print form.errors

    else:
        form = CategoryForm()


    return render_to_response('rango/add_category.html', {'form':form}, context)

def add_pages(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == "POST":
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)

            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {}, context)

            page.views = 0

            page.save()

            return category(request, category_name_url)

        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response("rango/add_page.html", {'form': form, 'category_name_url': category_name_url,
                                                      'category_name':category_name}, context)

def register(request):

    context = RequestContext(request)
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response('rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered,}, context)

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('your rango account is disabled')
        else:
            print "invalid login details : {0}, {1}".format(username, password)
            return HttpResponse("invalid login details supplied")
    else:
        return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
    return HttpResponse("since you are logged in , you can see this")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')





