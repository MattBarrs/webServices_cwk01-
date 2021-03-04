from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render

from webApp.models import NewsStories, Authors
from datetime import datetime, date
import datetime
import json

# Create your views here.

'''
Log In 
	//Success - 200 OK w/ text/plain payload giving some welcome 
	//Fail - 401 w/ Error message 
'''
@csrf_exempt
def user_login(request):
    try:
        #Get details from login request
        username = request.POST['username']
        password = request.POST['password']
        #attempt tp authenticate user
        user = authenticate(username=username, password=password)

        #returns none if not authenticated
        if user is not None:
            if user.is_active:
                #logs the user in
                login(request, user)

                #checks if login was successfull
                if(request.user.is_authenticated):
                    return HttpResponse('Login succesful, welcome!', status=200)
                else:
                  return HttpResponse('Invalid Login', status = 401)
            else:
                return HttpResponse('Invalid Login',status = 401)
        else:
            # Return an 'invalid login' error message.
            return HttpResponse('Invalid Login', status = 401)
    except Exception:
        return HttpResponse('Error occured, unable to login', status = 401)

    
'''
Log Out
	//Success - 200 OK w/ text/plain payload giving goodbye message
	// Fail - 401 
'''
@require_POST
@csrf_exempt
@login_required(login_url='/loginRequired')
def user_logout(request):
    try:
        #first check that user is logged in
        if(request.user.is_authenticated):
            #log the user out
            logout(request)
            # give succesfull response
            return HttpResponse('OK',status=200)
        else:
            return HttpResponse('Error Occured, unable to logout',status=401)
    except Exception:
        return HttpResponse('Error Occured, unable to logout',status=401)


        
'''
Post A Story 
	// Success - 201 CREATED 
	// Fail - 503 Service Unavilable w/ text/plain
'''
@require_POST
@csrf_exempt
@login_required(login_url='/loginRequired')
def story_post(request):
    #get body contents from reqeust
    content = json.loads(request.body)

    #extract all of the data
    headline = content['headline']
    category = content['category']
    region = content['region']
    details = content['details']

    categoryChoices =['pol', 'art','tech','trivia']
    regionChoices =['uk','eu','w']

    #make sure choices are correct
    if(category in categoryChoices) and  (region in regionChoices) and isinstance(headline,str)  and isinstance(details,str):
        #date of creation
        dateStamp = date.today()

        #author is user logged in
        #author object needed as it's the foreign key
        author = Authors(author_username = request.user)
        story = NewsStories(story_headline = headline, story_cat =category, story_region =region, story_details=details, story_date=dateStamp, story_author=author)
        #save
        author.save()
        story.save()

        return HttpResponse('CREATED',status=201)

    else:
       return HttpResponse('Validation Failed')

'''
Get Stories
	// Success - 200 OK 		replies w/ 	JSON payload 
		+ key, string
		+ headline, string
		+ story_cat, string
		+ story_region, string
		+ author, string
		+ story_date, string
		+ story_details, string 
	// Fail - 404  w/ text/plain 
'''

def story_get(request):
    #get body of the request
    content = json.loads(request.body)
    #set to null initially
    category = ""
    region =  ""

    #if not star then assign the search query value
    if content['story_cat'] != '*':
        category = content['story_cat']

    #if not star then assign the search query value
    if content['story_region'] !='*':
        region = content['story_region']

    #if no date star then run query without date filter
    #__ contains used as all of the string will contain the null character
    #Only looking for null character if it's a * for that field
    if content['story_date'] == '*':
        all_stories = NewsStories.objects.all().filter(story_cat__contains=category, story_region__contains=region)
    else:
        date = datetime.datetime.strptime(content['story_date'], '%d/%m/%Y').date()
        all_stories = NewsStories.objects.all().filter(story_cat__contains=category, story_region__contains=region).filter(story_date__gte=date)

    #checks to see how many stories found
    if not all_stories:
        return HttpResponse("No stories found matching criteria ", status=404)
    else:
        #array of stories
        stories = []
        #loops through each story found and creates a JSON object
        for story in all_stories:
            temp = {
                "key": str(getattr(story, "story_id")),
                "headline": str(getattr(story, "story_headline")),
                "story_cat" : str(getattr(story, "story_cat")),
                "story_region" : str(getattr(story, "story_region")),
                "author" : str(getattr(story, "story_author")),
                "story_date" : str(getattr(story, "story_date")),
                "story_details":  str(getattr(story, "story_details")),
            }
            #appends it to the end of the array
            stories.append(temp)

        #array then converted into JSON array of stories
        text= {}
        text['stories'] = stories
        return HttpResponse(json.dumps(text), status=200)





'''
Delete Stories 
+ Delete a story 
- POST -> /api/deletestory/     	in 	JSON 
	+ story_key, string
	// Success - 201 CREATED
	// Fail - 503 Service unavailable w/ text/plain giving reason 
'''

@csrf_exempt
@login_required(login_url='/loginRequired')
def story_delete(request):
    try:
        #loads data body
        content = json.loads(request.body)
        #extracts key of the stroy to be delteted
        key = content['story_key']
        #deletes story
        NewsStories.objects.filter(story_id=key).delete()
        return HttpResponse('CREATED',201)
    except  Exception:
        return HttpResponse('Error occured, record not deleted',501)

def loginRequired(request):
    return HttpResponse('Login required to view page',401)
