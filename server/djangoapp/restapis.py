import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data
# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        print(response)
      
    except:
        print("Network exception occured")
    status_code = response.status_code
    print("With status {}".format(status_code))
    json_data = json.loads(response.text)
    return json_data
 

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
   
    if json_result["Dealerships"]:
        json_result = json_result["Dealerships"]
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"], 
                                   state=dealer_doc["state"], st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_review_by_id_from_cf(url, dealerId):
    results = []
    url += "?dealership="+str(dealerId)
    json_request = get_request(url)
    if json_request:
        # Get the review list in JSON as reviewers
        reviewers = json_request["reviews"]
        # For each reviewer object
        for reviewer in reviewers:
            if (reviewer["dealership"] == dealerId):
                # Create a DealerReview object that matches the dealerId
                review_obj = DealerReview(dealership=reviewer["dealership"], name=reviewer["name"], purchase=reviewer["purchase"],
                                         review=reviewer["review"], purchase_date=reviewer["purchase_date"],
                                         car_make=reviewer["car_make"], car_model=reviewer["car_model"],
                                        car_year=reviewer["car_year"], sentiment=analyze_review_sentiments(reviewer["review"]), id=reviewer["id"])
                results.append(review_obj)

    return results

def get_dealership_by_id_from_cf(url, dealerId):
    results = []
    url += "?id="+str(dealerId)
    json_result = get_request(url)
    if json_result:
        dealers = json_result
      
        # Get its content in `doc` object
        for dealer_doc in dealers["DealershipsByID"]["docs"]:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                short_name=dealer_doc["short_name"], 
                                state=dealer_doc["state"], st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results
    
# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    try:
        url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/e06730f0-e7da-4bdd-a7e2-52dd5c5f7b00"
        api_key = "JNVeMIQk6SxKmZNOPdkAQ3mU0HgDkTjXhIdO7_Rhm4bm" 
        authenticator = IAMAuthenticator(api_key) 
        natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 
        natural_language_understanding.set_service_url(url) 

        response = natural_language_understanding.analyze( text=text ,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result() 
        label=json.dumps(response, indent=2) 
        label = response['sentiment']['document']['label'] 
        return (label)
    except:
        label = "Can't recognize review"
        return (label)

def get_only_1_dealer_by_id_from_cf(url, dealerId):
    results = []
    url += "?dealership="+str(dealerId)
    json_request = get_request(url)
    if json_request:
        # Get the review list in JSON as reviewers
        reviewers = json_request["reviews"]
        # For each reviewer object
        for reviewer in reviewers:
            if (reviewer["dealership"] == dealerId):
                # Create a DealerReview object that matches the dealerId
                review_obj = DealerReview(dealership=reviewer["dealership"], name=reviewer["name"], purchase=reviewer["purchase"],
                                         review=reviewer["review"], purchase_date=reviewer["purchase_date"],
                                         car_make=reviewer["car_make"], car_model=reviewer["car_model"],
                                        car_year=reviewer["car_year"], sentiment=analyze_review_sentiments(reviewer["review"]), id=reviewer["id"])
                results.append(review_obj)

    return results
