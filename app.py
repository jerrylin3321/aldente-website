from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask import session
from yelpapi import YelpAPI
from flask import redirect, url_for


### Yelp API setup
yelp_api = YelpAPI("REDACTED")
####----


app = Flask(__name__)
app.secret_key = 'REDACTED'
pos = None 

#Handles location access
@app.route('/postmethod', methods=['POST'])
def got_location():
    data = request.get_json()
    global pos
    pos = data
    print (data)
    return jsonify(data)

#Homepage
@app.route('/')
def home():
    if session.get('foodtype') == None: #Booting up for first time
        foodtype = "Ice Cream"
    else: #Via "Quick Recommendations"
        foodtype = session.get('foodtype')

    render_temp = return_yelp_results(foodtype)
    return render_temp
    
#Search Results Page
@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    render_temp = return_yelp_results(text)
    return render_temp

#About Page
@app.route('/about')
def about():
    return render_template('about.html')

#Links for Quick Recommendations
@app.route('/food/<ft>')
def food_recommendation(ft):
    session['foodtype'] = ft
    return redirect(url_for('home'))

#Takes Yelp queries and returns html template
def return_yelp_results(search_text):
    if pos == None: #Don't have location yet
        lat = 36.0015028
        lon = -78.9334095999999
    else: 
        lat = pos['location']['lat']
        lon = pos['location']['lng']
    response = yelp_api.search_query(term=search_text, latitude=lat, longitude=lon, sort_by='rating', limit=10)
    business_dict = {}
    label_index = 1
    for business in response['businesses']: #Loads restaurant(s) information into dict to be loaded on HTML page
        label = label_index
        business_dict[label] = {}
        business_dict[label]['latitude'] = business['coordinates']['latitude']
        business_dict[label]['longitude'] = business['coordinates']['longitude']
        business_dict[label]['name'] = str(label_index) + ". " + business['name']
        business_dict[label]['phone'] =  "(" + business['phone'][2:5] + ") " + business['phone'][5:8] + "-" + business['phone'][8:]
        business_dict[label]['address'] = business['location']
        business_dict[label]['rating'] = business['rating']
        business_dict[label]['review_count'] = business['review_count']
        business_dict[label]['url'] = business['url'] #image for the restaurant
        business_dict[label]['image_url'] = business['image_url']
        business_dict[label]['id'] = business['id']
        business_dict[label]['rating_and_number'] = str(business['rating']) + "/5.0, " + str(business['review_count']) + " reviews"
        excerpt = yelp_api.reviews_query(id=business['id'])
        business_dict[label]['first_review'] = excerpt['reviews'][0]['text']
        category_string = ""
        for category_dict in business['categories']: #Creates a comma-separated string of categories
            category_string += category_dict['title']
            category_string += ", "
        business_dict[label]['category_string'] = category_string[:-2]
        label_index += 1

    



    
    return render_template('response.html', name=response, latitude=response['region']['center']['latitude'], 
    longitude=response['region']['center']['longitude'], business_dict = business_dict)
    