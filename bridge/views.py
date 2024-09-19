from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from .models import Event, Violation, Discount
import requests
import csv
from django import forms
from io import TextIOWrapper
from django.http import HttpResponse
from django.conf import settings
import googlemaps
import joblib
import os
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# Create your views here.

def home(request):
    events = Event.objects.all()
    return render(request, 'home.html', {'events': events})

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Logged In.')
            return redirect('home')

        else:
            messages.error(request, "Username or password invalid")
            return redirect('login')
    return render(request, 'login.html')

def register(request):
    if request.method == "POST":
        username= request.POST['username']
        firstname= request.POST['firstname']
        lastname= request.POST['lastname']
        email= request.POST['email']
        pasw1= request.POST['pasw1']
        pasw2= request.POST['pasw2']
        user = User.objects.create_user(username,email,pasw1)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        messages.success(request, 'User created.')
        return render(request, 'home.html')
    return render(request, 'register.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            messages.success(request, 'Password recovery email sent.')
        else:
            messages.error(request, 'No user found with this email.')
    return render(request, 'forgot_password.html')

def logout_view(request):
    logout(request)
    messages.success(request,"Logged out")
    return redirect('home')

class CSVUploadForm(forms.Form):
    file = forms.FileField()

# def add_rc(request):
#     if request.method == 'POST':
#         form = CSVUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             csv_file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
#             reader = csv.DictReader(csv_file)
#             for row in reader:
#                 Violation.objects.create(
#                     violation_type=row['violation_type'],
#                     description=row['description'],
#                     address=row['address'],
#                 )
#             messages.success(request, "CSV file has been successfully uploaded and processed.")
#             return redirect('add_rc')
#     else:
#         form = CSVUploadForm()
    
#     return render(request, 'add_rc.html', {'form': form})

def add_rc(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            for row in reader:
                Discount.objects.create(
                    title=row['title'],
                    description=row['description'],
                )
            messages.success(request, "CSV file has been successfully uploaded and processed.")
            return redirect('add_rc')
    else:
        form = CSVUploadForm()
    
    return render(request, 'add_rc.html', {'form': form})


def navigation(request):
    if request.method == 'POST':
        source = request.POST['source']
        destination = request.POST['destination']
        mode = request.POST['mode']
        api_key = 'AIzaSyDSRumQMKR9GclqYS9AlfwlTRd1pUpcWRk'
        base_url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "key": api_key,
            "origin": source,
            "destination": destination,
            "mode": mode
        }
        response = requests.get(base_url, params=params)
        directions = response.json()
        route = directions["routes"][0]
        legs = route["legs"][0]
        duration = legs["duration"]["text"]
        distance = legs["distance"]["text"]
        steps = legs["steps"]

        print(duration)
        print(distance)

        return render(request, 'navigation.html', {'route': route, 'distance': distance,'duration': duration, 'steps': steps})
        
    return render(request, 'navigation.html')

def rental_check(request):
    violations = []
    if request.method == 'POST':
        address = request.POST.get('address', '') 
        violations = Violation.objects.filter(address__icontains=address)
    return render(request, 'rental_check.html', {'violations': violations})

def nearby_events(request):
    places = []
    if request.method == 'POST':
        api_key = 'AIzaSyDSRumQMKR9GclqYS9AlfwlTRd1pUpcWRk'
        keyword = request.POST.get('activity', '')
        address = request.POST.get('address', '')
        location = geocode_address(api_key, address)
        radius = "5000"
        places = find_places_nearby(api_key, location, radius, keyword=keyword)
        return render(request, 'nearby_events.html', {'places': places, 'address':address})
    return render(request, 'nearby_events.html', {'places': places})

def geocode_address(api_key, address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "key": api_key,
        "address": address
    }
    response = requests.get(base_url, params=params)
    result = response.json()["results"][0]
    location = result["geometry"]["location"]
    return f"{location['lat']},{location['lng']}"

def find_places_nearby(api_key, location, radius, keyword=None, type=None):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": location,
        "radius": radius
    }
    if keyword:
        params["keyword"] = keyword
    if type:
        params["type"] = type

    response = requests.get(base_url, params=params)
    results = response.json()["results"]
    return results

def rent_predict(request):
    gmaps = googlemaps.Client(key='AIzaSyDSRumQMKR9GclqYS9AlfwlTRd1pUpcWRk')

    if request.method == 'POST':
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'rent_price.joblib')
        rf = joblib.load(model_path)
        address = request.POST['address']
        rooms = request.POST['rooms']
        baths = request.POST['baths']
        typeofhouse = request.POST['typeofhouse']
        geocode_result = gmaps.geocode(address)
        
        if geocode_result:
            latitude = geocode_result[0]['geometry']['location']['lat']
            longitude = geocode_result[0]['geometry']['location']['lng']
    
            for component in geocode_result[0]['address_components']:
                if 'postal_code' in component['types']:
                    zipcode = component['long_name']
                    break
            prediction=rf.predict(np.array([zipcode,latitude,longitude,typeofhouse,baths,rooms]).reshape(1, -1))
            print(prediction)
            print(f"Latitude: {latitude}, Longitude: {longitude}, ZIP Code: {zipcode}")
            return render(request, 'rent_predict.html', {'prediction': prediction, })
        else:
            print("No results found.")
        
    return render(request, 'rent_predict.html')

def commuter_crowd(request):
    if request.method == 'POST':
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'commuter_count.joblib')
        model = joblib.load(model_path)
        selectedoption = request.POST['line_route']
        date_str = request.POST['date']
        time_str = request.POST['time']
        date_selected = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_selected = datetime.strptime(time_str, '%H:%M').time()
        purplelineroutes={'year':0,'month':0,'day':0,'hour':0,'Middleborough/Lakeville':0,'Lowell':0,'Haverhill':0,'Kingston':0,'Needham':0,'Fitchburg':0,
                          'Greenbush':0,'Fairmount':0,'Providence/Stoughton':0,'Newburyport/Rockport':0,'Framingham/Worcester':0,
                          'Franklin/Foxboro':0}
        lables = purplelineroutes.keys() - ['year','month','day','hour']
        purplelineroutes[selectedoption] = 1
        
        purplelineroutes['year'] = date_selected.year
        purplelineroutes['month'] = date_selected.month
        purplelineroutes['day'] = date_selected.day
        purplelineroutes['hour']=time_selected.hour
        
        print(purplelineroutes)
        
        df = pd.DataFrame(purplelineroutes,index=[0])
        predicted = model.predict(df)
        prediction = float(predicted[0])
        if prediction > 4000:
            pop_index="HIGH"
        else:
            pop_index="LOW"
        return render(request, 'commuter_crowd.html', {'crowd_index': pop_index, 'selectedoption':selectedoption, 
                                                'date_str':date_str, 'time_str':time_str})
        
    return render(request, 'commuter_crowd.html')

def lyft_uber(request):
    if request.method == 'POST':
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'ride_price.joblib')
        model_2 = joblib.load(model_path)
        response = {'hour':0,'day':0,'month':0,'source':'','destination':'','cab_type':[]}
        df_response = response
        input_source=request.POST['source']
        input_destination=request.POST['destination']
        response['destination']=input_destination
        response['source']=input_source
        date_str = request.POST['date']
        time_str = request.POST['time']
        date_1 = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_2 = datetime.strptime(time_str, '%H:%M').time()
        response['month'] = date_1.month
        response['day'] = date_1.day
        response['hour']=time_2.hour
        response['cab_type']=['Lyft','Uber']
        df_response['month'] = date_1.month
        df_response['day'] = date_1.day
        df_response['hour']=time_2.hour
        df_response['cab_type']=['Lyft','Uber']
        df_response['source']=input_source
        df_response['destination']=input_destination
        dataframe_df=pd.DataFrame(df_response)
        enc1=LabelEncoder()
        enc1.classes_=np.load('Testing/class_source.npy',allow_pickle=True)
        enc2=LabelEncoder()
        enc2.classes_=np.load('Testing/class_destination.npy',allow_pickle=True)
        enc3=LabelEncoder()
        enc3.classes_=np.load('Testing/class_cab.npy',allow_pickle=True)
        dataframe_df['source']=enc1.transform(dataframe_df['source'])
        dataframe_df['destination']=enc2.transform(dataframe_df['destination'])
        dataframe_df['cab_type']=enc3.transform(dataframe_df['cab_type'])
        prediction  = model_2.predict(dataframe_df)
        lyft = prediction[0]
        uber = prediction[1]
        return render(request, 'lyft_uber.html', {'uber': uber, 'lyft': lyft, 'prediction': prediction})
    
    return render(request, 'lyft_uber.html')

def student_discount(request):
    discount = []
    if request.method == 'POST':
        title = request.POST.get('title', '') 
        discount = Discount.objects.filter(title__icontains=title)
    return render(request, 'student_discount.html', {'discounts': discount})

    

