from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404


# Create your views here.

#def index(request):
#	return HttpResponse("Hello Django!")

#登录页面
def index(request):
	return render(request,"index.html")

#登录动作
def login_action(request):
	if request.method == 'POST':
		username = request.POST.get('username', '')
		password = request.POST.get('password', '')
		user = auth.authenticate(username=username, password=password)
		#if username == 'admin' and password == 'admin123':
		if user is not None:
			#return HttpResponse('login success!')				#以字符串传递给客户端
			#return HttpResponseRedirect('/event_manage/')		#对路径重定向
			auth.login(request, user)	#登录
			request.session['user'] = username
			response = HttpResponseRedirect('/event_manage/')
			#response = HttpResponseRedirect('login success!')
			#response.set_cookie('user', username, 3600)			#添加浏览器cookie
			#request.session['user'] = username
			return response
		else:
			return render(request,'index.html',{'error': 'username or password error!'})

#发布会管理
@login_required
def event_manage(request):
	event_list = Event.objects.all()
	#username = request.COOKIES.get('user', '')	#读取浏览器的cookie
	username = request.session.get('user', '')	#读取浏览器的session
	#search_name = request.GET.get("name","")
	#event_list = Event.objects.filter(name__contaions=search_name)
	#return render(request,"event_manage.html")
	#return render(request,"event_manage.html", {"user":username})
	return render(request,"event_manage.html", {"user":username, "events":event_list})

#发布会名称搜索
@login_required
def search_name(request):
	username = request.session.get('user', '')  # 读取浏览器的session
	search_name = request.GET.get("name","")
	event_list = Event.objects.filter(name__contains=search_name)
	return render(request, "event_manage.html", {"user": username, "events": event_list})

#嘉宾管理
@login_required
def guest_manage(request):
	username = request.session.get('user', '')
	guest_manage = request.GET.get("name","")
	guest_list = Guest.objects.all()

	paginator = Paginator(guest_list, 2)
	page = request.GET.get('page')
	try:
		contacts = paginator.page(page)
	except PageNotAnInteger:
		#如果page不是整数，取第一页面数据
		contacts = paginator.page(1)
	except EmptyPage:
		#如果page不在范围，取最后一页面
		contacts = paginator.page(paginator.num_pages)
	return render(request, "guest_manage.html", {"user": username, "guests": contacts})

#嘉宾名称搜索
@login_required
def search_phone(request):
	username = request.session.get('user', '')  # 读取浏览器的session
	search_phone = request.GET.get("phone","")
	search_name_bytes = search_phone.encode(encoding="utf-8")
	guest_list = Guest.objects.filter(phone__contains=search_name_bytes)
	username = request.session.get('username', '')
	'''
	paginator = Paginator(guest_list, 10)
	page = request.GET.get('page')
	try:
		contacts = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		contacts = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		contacts = paginator.page(paginator.num_pages)
'''
	return render(request, "guest_manage.html", {"user": username, "guests": guest_list})

#签到页面
@login_required
def sign_index(request, eid):
	event = get_object_or_404(Event, id=eid)
	return  render(request, 'sign_index.html', {'event': event})

#签到动作
@login_required
def sign_index_action(request, eid):
	event = get_object_or_404(Event, id=eid)
	phone = request.POST.get('phone', '')
	print(phone)

	result = Guest.objects.filter(phone=phone)
	if not result:
		return render(request, 'sign_index.html',{'event': event, 'hint': 'phone error.'})

	result = Guest.objects.filter(phone=phone, event_id=eid)
	if not result:
		return render(request, 'sign_index.html',{'event': event, 'hint': 'event id or phone error.'})

	result = Guest.objects.get(event_id=eid, phone=phone)
	if result.sign:
		return render(request, 'sign_index.html',{'event': event, 'hint': "user has sign in."})

	else:
		Guest.objects.filter(event_id=eid, phone=phone).update(sign='1')
		return render(request, 'sign_index.html',{'event': event, 'hint': 'sign in success!', 'guest': result})

#退出登录
@login_required
def logout(request):
	auth.logout(request)
	response = HttpResponseRedirect('/index/')
	return response












