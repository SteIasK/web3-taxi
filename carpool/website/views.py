from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import View
import mysql.connector as sql
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from requests import request
from django.contrib.auth.hashers import make_password
from website.models import Customer, Mycar, ContactUs, Booking
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.urls import reverse
import os
from datetime import datetime

# Create your views here.
def get_db_connection():
    try:
        return sql.connect(host="localhost", user="root", passwd="1649044311Wjy@", database='carpooling')
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return None

#Home page
@ensure_csrf_cookie
@never_cache
def home(request):
    return render(request, "home.html")

#Function to help login the user and open dashboard
@ensure_csrf_cookie
@never_cache
def LoginUser(request):
    if request.method == "GET":
        return render(request, "login.html")

    if request.method == "POST":
        try:
            usern = request.POST.get('usern')
            password = request.POST.get('password')
            
            if not all([usern, password]):
                messages.error(request, "用户名和密码不能为空!")
                return HttpResponseRedirect(reverse('login'))
            
            user = authenticate(username=usern, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('dashboard'))
                else:
                    messages.error(request, "账号已被禁用!")
            else:
                messages.error(request, "用户名或密码错误!")
            return HttpResponseRedirect(reverse('login'))
            
        except Exception as e:
            messages.error(request, f"登录失败: {str(e)}")
            return HttpResponseRedirect(reverse('login'))
    
    return render(request, "login.html")

@ensure_csrf_cookie
@never_cache
def Register(request):
    if request.method == 'GET':
        # 清除可能存在的会话数据
        request.session.flush()
        # 设置会话过期时间
        request.session.set_expiry(300)  # 5分钟后过期
        return render(request, "registration.html")

    if request.method == 'POST':
        try:
            # 获取并验证表单数据
            form_data = {
                'usern': request.POST.get('usern', '').strip(),
                'fname': request.POST.get('fname', '').strip(),
                'email': request.POST.get('email', '').strip(),
                'password': request.POST.get('password', ''),
                'mobile': request.POST.get('mobile', '').strip(),
                'gender': request.POST.get('gender', '').strip(),
                'address': request.POST.get('address', '').strip(),
                'city': request.POST.get('city', '').strip(),
                'state': request.POST.get('state', '').strip()
            }
            
            # 验证必填字段
            if not all(form_data.values()):
                messages.error(request, "所有字段都必须填写!")
                return render(request, "registration.html")
            
            # 验证手机号
            mobile = form_data['mobile']
            if len(mobile) != 10 or not mobile.isdigit():
                messages.error(request, "手机号必须是10位数字!")
                return render(request, "registration.html")
            
            if mobile.startswith(('1', '2', '3', '4', '5', '0')):
                messages.error(request, "无效的手机号!")
                return render(request, "registration.html")
            
            # 检查用户名是否已存在
            if User.objects.filter(username=form_data['usern']).exists():
                messages.error(request, "用户名已存在!")
                return render(request, "registration.html")
            
            # 检查邮箱是否已存在
            if User.objects.filter(email=form_data['email']).exists():
                messages.error(request, "邮箱已被注册!")
                return render(request, "registration.html")
            
            # 创建用户和客户信息
            with transaction.atomic():
                # 创建用户
                user = User.objects.create_user(
                    username=form_data['usern'],
                    email=form_data['email'],
                    password=form_data['password']
                )
                
                # 创建客户信息
                Customer.objects.create(
                    usern=user,
                    fname=form_data['fname'],
                    email=form_data['email'],
                    mobile=form_data['mobile'],
                    gender=form_data['gender'],
                    address=form_data['address'],
                    city=form_data['city'],
                    state=form_data['state']
                )
            
            # 设置成功消息并添加到会话中
            messages.success(request, "注册成功，请登录!")
            
            # 确保清除任何可能存在的会话数据
            request.session.flush()
            
            # 创建响应并设置缓存控制头
            response = HttpResponseRedirect(reverse('login'))
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # 设置安全相关的响应头
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            
            return response
            
        except IntegrityError as e:
            messages.error(request, "注册失败：数据完整性错误")
            return render(request, "registration.html")
        except Exception as e:
            messages.error(request, f"注册失败：{str(e)}")
            return render(request, "registration.html")
    
    return render(request, "registration.html")

#Function to help user contact the admin
def Contactus(request):
    if request.method=="GET":
        return render(request, "contact.html")
    
    if request.method=="POST":
        m=sql.connect(host="localhost", user="root", passwd="1649044311Wjy@", database='carpooling')
        name=request.POST['name']
        email=request.POST['email']
        phone=request.POST['phone']
        msg=request.POST['msg']
        if len(phone)!=10 or phone.isdigit()==False:
            messages.warning(request, "The phone number provided is not 10 digits!")
        elif phone.startswith(('1', '2', '3', '4', '5', '0')):
            messages.warning(request, "The phone number provided is not valid!")
        else:
            contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg)

        
        # save the contact details in database
            #print(request.user)
            #customer = Customer.objects.get(usern=user_name)
            #    contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg, cust=customer)
            #else:
            #    contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg, cust=None)

            #print(contact_us)
            contact_us.save()
            m.commit()
            messages.success(request, "Thank you for contacting us, we will reach you soon.")

        return render(request, "contact.html")


#Function to search the car on search.html page and redirect to the searched_cars.html
def Search(request):
    if request.method=="GET":
        return render(request, "search.html")
    
    if request.method=="POST":
        m=sql.connect(host="localhost", user="root", passwd="1649044311Wjy@", database='carpooling')
        from_place=request.POST['from_place']
        to_place=request.POST['to_place']
        from_date=request.POST['from_date']
        to_date=request.POST['to_date']
        cars = Mycar.objects.filter(from_place=from_place,to_place=to_place,from_date=from_date, to_date=to_date)
        print(cars)
        context = {'cars': cars}
        return render(request, "searched_cars.html", context)
        



#Function to show details of the car to the user, but if the user is not logged in then take to login page    
@login_required(login_url='login')
def Cardetails(request, car_id):
    if request.method == "GET":
        try:
            car = Mycar.objects.get(pk=car_id)
            # 获取该车辆的所有预订记录
            bookings = Booking.objects.filter(car=car)
            car.bookings = bookings
            return render(request, "cardetails.html", {'car': car})
        except Mycar.DoesNotExist:
            messages.error(request, "未找到该车辆")
            return redirect('allcars')
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                user = request.user
                cust = Customer.objects.get(usern=user)
                car = Mycar.objects.get(pk=car_id)
                
                contact = request.POST['contact']
                email = request.POST['email']
                pickup = request.POST['pickup']
                dropoff = request.POST['dropoff']
                pick_add = request.POST['pick_add']
                drop_add = request.POST['drop_add']
                
                # 检查日期是否在车主设定的范围内
                if pickup < str(car.from_date) or dropoff > str(car.to_date):
                    messages.error(request, "预订日期必须在车主设定的可用时间范围内！")
                    return HttpResponseRedirect(reverse('cardetails', args=[car_id]))
                
                # 检查日期冲突
                overlap_bookings = Booking.objects.filter(
                    car=car,
                    pickup__lte=dropoff,
                    dropoff__gte=pickup
                )
                
                if overlap_bookings.exists():
                    messages.error(request, "该时间段已被预订！")
                    return HttpResponseRedirect(reverse('cardetails', args=[car_id]))
                
                # 创建预订
                booking = Booking.objects.create(
                    name=cust,
                    car=car,
                    contact=contact,
                    email=email,
                    pickup=pickup,
                    dropoff=dropoff,
                    pick_add=pick_add,
                    drop_add=drop_add
                )
                
                messages.success(request, "预订成功！")
                return HttpResponseRedirect(reverse('bookedcar', args=[car_id]))
                
        except Exception as e:
            messages.error(request, f"预订失败：{str(e)}")
            return HttpResponseRedirect(reverse('cardetails', args=[car_id]))
    
    return render(request, "cardetails.html", {'car': car})




#Function to show the booked cars, booked by the user
def Booked(request,car_id):
    if request.method=="GET":
        try:
            if request.user.is_authenticated:
                user = request.user
                cust = Customer.objects.get(usern=user)
                
                # 获取最新的预订记录
                book = Booking.objects.filter(car_id=car_id, name=cust).latest('date_added')
                context = {'book': book}
                messages.success(request, "预订成功！")
                return render(request, "booked.html", context)
            else:
                messages.error(request, "请先登录")
                return redirect('login')
        except Booking.DoesNotExist:
            messages.error(request, "未找到预订记录")
            return redirect('cardetails', car_id=car_id)
        except Exception as e:
            messages.error(request, f"发生错误：{str(e)}")
            return redirect('cardetails', car_id=car_id)
    return redirect('home')




#Function to show dashboard to the logged in users
@login_required(login_url='login')
@never_cache
def dash(request):
    try:
        user = request.user
        customer = Customer.objects.get(usern=user)
        
        # 获取用户的车辆信息
        user_cars = Mycar.objects.filter(cust=customer)
        car_count = user_cars.count()
        
        # 获取用户的预订信息
        user_bookings = Booking.objects.filter(name=customer)
        booking_count = user_bookings.count()
        
        # 获取用户车辆的预订信息
        cars_booked = Booking.objects.filter(car__in=user_cars)
        cars_booked_count = cars_booked.count()
        
        context = {
            'car_count': car_count,
            'booking_count': booking_count,
            'cars_booked_count': cars_booked_count,
            'recent_cars': user_cars.order_by('-id')[:5],  # 最近添加的5辆车
            'recent_bookings': user_bookings.order_by('-date_added')[:5],  # 最近的5个预订
            'recent_cars_booked': cars_booked.order_by('-date_added')[:5]  # 最近的5个车辆被预订记录
        }
        
        return render(request, "dashboard.html", context)
    except Exception as e:
        messages.error(request, f"获取仪表盘信息失败：{str(e)}")
        return render(request, "dashboard.html")



#Function to show logged in user's bookings from the dashboard
def MyBookings(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user=request.user
            cust=Customer.objects.get(usern=user)
            custs=Booking.objects.filter(name=cust)
            print(custs)
            context={'custs':custs}
            return render(request, "mybooking.html",context)
    #if request.method == 'POST':
    #    if request.user.is_authenticated:
    #       user=request.user
    #        cust=Customer.objects.get(usern=user)
    #        custs=Booking.objects.get(name=cust)
    #        print(custs)
    #        context={'custs':custs}
    #        return render(request, "mybooking.html",context)



#Function to show logged in user's account details
def MyAccount(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            cust=Customer.objects.get(usern=user)
            #print(cust)
            context={'cust': cust}
            return render(request, "myaccount.html", context)



#Function to show logged in user's cars booked by other customer's
def CustomerBookings(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user=request.user
            cust=Customer.objects.get(usern=user)
            mybook=Booking.objects.filter(name=cust)
            mycar=Mycar.objects.filter(cust=cust)
            otherbookings=Booking.objects.filter(car__in=mycar).exclude(name=cust)
            context={'otherbookings':otherbookings}
            return render(request, "cust_booking.html", context)




#Function to show logged in user, their added cars
def MyCarList(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            username=Customer.objects.get(usern=user)
            custs=Mycar.objects.filter(cust=username)
            print(custs)
            context={'custs': custs}
            return render(request, "mycar_list.html", context)



#Function to show all the cars to the logged in or unloggedin users on the allcars.html
def Cars(request):
    if request.method == 'GET':
        mycars=Mycar.objects.all()
        context={'mycars': mycars}
        return render(request, "allcars.html", context)
    
    #if request.method == 'POST':
    #    if request.user.is_authenticated:
    #        return render("")



#Function to help logged in user to change password on change.html
def Change(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, "change.html")
    
    if request.method=='POST':
        if request.user.is_authenticated:
            user=request.user
            print(user)
            old_password=request.POST['old_password']
            print(old_password)
            new_password = request.POST['new_password']
            print(new_password)
            confirm_password = request.POST['confirm_password']
            print(confirm_password)
            usern = authenticate(request, username=user, password=old_password)
            print(usern)
            if usern is None:
                messages.error(request, 'The old password is incorrect!')
                return redirect('changepassword')
            
            if new_password != confirm_password:
                messages.error(request, 'The new password and confirm password does not match!')
                return redirect('changepassword')
            
            print(user.password)
            user.password = make_password(new_password)
            user.save()
            login(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('changepassword')
    return render(request, 'change.html')
            
            
#Function to add user's car in the database
def Addcar(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, "addmycar.html")
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            m=sql.connect(host="localhost", user="root", passwd="1649044311Wjy@", database='carpooling')
            car_num=request.POST['car_num']
            car_name=request.POST['car_name']
            from_place=request.POST['from_place']
            to_place=request.POST['to_place']
            car_type=request.POST['car_type']
            company=request.POST['company']
            price=request.POST['price']
            from_date=request.POST['from_date']
            to_date=request.POST['to_date']
            car_img=request.FILES['car_img']
            custom=Customer.objects.get(usern=request.user)
            print(custom)
            car=Mycar.objects.filter(car_num=car_num)
            if car.exists():
                messages.warning(request, 'Car Already exists')
                return redirect('addmycar')
            obj=Mycar.objects.create(car_num=car_num,from_date=from_date,to_date=to_date,car_name=car_name,from_place=from_place,to_place=to_place,car_type=car_type,company=company, price=price, car_img=car_img, cust=custom)
            obj.save()
            m.commit()
            return redirect('dashboard') 
                     
    return render(request,"addmycar.html")

@never_cache
def logout_user(request):
    try:
        logout(request)
        request.session.flush()
    except Exception as e:
        print(f"注销时发生错误: {str(e)}")
    return HttpResponseRedirect(reverse('home'))
    
# 错误处理视图
def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

@login_required(login_url='login')
def DeleteCar(request, car_id):
    try:
        car = Mycar.objects.get(pk=car_id)
        
        # 检查是否是车主
        if car.cust.usern != request.user:
            messages.error(request, "您没有权限删除这辆车！")
            return redirect('mycar_list')
            
        # 检查是否有未完成的预订
        active_bookings = Booking.objects.filter(
            car=car,
            dropoff__gte=datetime.now().date()
        ).exists()
        
        if active_bookings:
            messages.error(request, "这辆车有未完成的预订，无法删除！")
            return redirect('mycar_list')
            
        # 删除所有相关的预订记录
        with transaction.atomic():
            # 先删除所有相关的预订记录
            Booking.objects.filter(car=car).delete()
                
            # 删除车辆图片
            if car.car_img:
                if os.path.isfile(car.car_img.path):
                    os.remove(car.car_img.path)
                    
            # 删除车辆记录
            car.delete()
            
        messages.success(request, "车辆及其相关预订记录已成功删除！")
        
    except Mycar.DoesNotExist:
        messages.error(request, "未找到该车辆！")
    except Exception as e:
        messages.error(request, f"删除失败：{str(e)}")
        
    return redirect('mycar_list')

@login_required(login_url='login')
def DeleteBooking(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
        
        # 检查是否是预订人
        if booking.name.usern != request.user:
            messages.error(request, "您没有权限删除这条预订记录！")
            return redirect('mybookings')
            
        # 检查是否是未来的预订
        if booking.pickup < datetime.now().date():
            messages.error(request, "无法删除已开始或已完成的预订！")
            return redirect('mybookings')
            
        # 删除预订记录
        booking.delete()
        messages.success(request, "预订记录已成功删除！")
        
    except Booking.DoesNotExist:
        messages.error(request, "未找到该预订记录！")
    except Exception as e:
        messages.error(request, f"删除失败：{str(e)}")
        
    return redirect('mybookings')
    