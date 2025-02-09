from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_review_by_id_from_cf, post_request, get_dealership_by_id_from_cf, analyze_review_sentiments
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

 

# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)
# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context={}
    if request.method == "GET":
        url = "https://d1934b55.us-south.apigw.appdomain.cloud/dealership/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context["dealerships"] = dealerships
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":

        url = "https://d1934b55.us-south.apigw.appdomain.cloud/dealershipReviews/api/review"
        # Get Reviewers from the URL
        context["reviews"] = get_review_by_id_from_cf(url, dealer_id)
        context["dealer_id"] = [dealer_id]
        return render(request, 'djangoapp/dealer_details.html', context)
 

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    context = {}
    if request.method == "POST":
        # username = request.POST['username']
        # password = request.POST['password']
        # user = authenticate(username=username, password=password)
        # if user is not None:
        review = {}
        url = "https://d1934b55.us-south.apigw.appdomain.cloud/dealershipReviews/api/review"
        if request.POST['purchasecheck'] == 'on':
            review["purchase"] = True
        else:
            review["purchase"] = False
        review["name"] = "Calvin"
        review["dealership"] = dealer_id
        review["id"] = 37
        review["review"] = request.POST['content']
        review["sentiment"] = analyze_review_sentiments(request.POST['content'])
        if "purchasedate" in request.POST:
            review["purchase_date"] = request.POST['purchasedate']
        for car_model in CarModel.objects.all():
            if (car_model.id == int(request.POST["car"])):
                review["car_make"] = car_model.car_make.name
                review["car_model"] = car_model.name
                review["car_year"] = car_model.year.strftime("%Y")
        json_payload = {}
        json_payload["reviews"] = review
        post_request(url, json_payload, dealer_id=dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

        # else:
        #     context['message'] = "Invalid username or password."
        #     return render(request, 'djangoapp/index.html')
    else:
        car_modelList = []
        for car_model in CarModel.objects.all():
            if (car_model.dealer_id == dealer_id):
                car_modelList.append(car_model)
        url_review = "https://d1934b55.us-south.apigw.appdomain.cloud/dealershipReviews/api/review"
        url_dealership = "https://d1934b55.us-south.apigw.appdomain.cloud/dealership/api/dealership"
        # Get Reviewers from the URL
        context["cars"] = car_modelList
        context["reviews"] = get_review_by_id_from_cf(url_review, dealer_id)
        context["dealerships"] = get_dealership_by_id_from_cf(url_dealership, dealer_id)
        
        return render(request, 'djangoapp/add_review.html', context)


