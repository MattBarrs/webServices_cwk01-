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
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:

          if user.is_active:
              login(request, user)

              if(request.user.is_authenticated):

                  return HttpResponse('Login succesful, welcome!', status=200)
              else:

                  return HttpResponse('Invalid Login', status = 401)

          else:

              return HttpResponse('Account Locked',status = 401)
        else:
          # Return an 'invalid login' error message.
          return HttpResponse('Invalid Login', status = 401)
    except Exception:
        return HttpResponse('Error occured, unable to login', status = 401)

    
'''
Log Out
	//Success - 200 OK w/ text/plain payload giving goodbye message
	// Fail - 
'''
@require_POST
@csrf_exempt
@login_required(login_url='/loginRequired')
def user_logout(request):
    try:
        if(request.user.is_authenticated):
            #print(user.username+' is logged in')
            logout(request)
            # Redirect back to index page.
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
    content = json.loads(request.body)

    headline = content['headline']
    category = content['category']
    region = content['region']
    details = content['details']

    categoryChoices =['pol', 'art','tech','trivia']
    regionChoices =['uk','eu','w']


    if(category in categoryChoices) and  (region in regionChoices) and isinstance(headline,str)  and isinstance(details,str):
        dateStamp = date.today()

        author = Authors(author_username = request.user)
        story = NewsStories(story_headline = headline, story_cat =category, story_region =region, story_details=details, story_date=dateStamp, story_author=author)

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

    content = json.loads(request.body)

    category = ""
    region =  ""

    if content['story_cat'] != '*':
        category = content['story_cat']

    if content['story_region'] !='*':
        region = content['story_region']


    if content['story_date'] == '*':
        all_stories = NewsStories.objects.all().filter(story_cat__contains=category, story_region__contains=region)
    else:
        date = datetime.datetime.strptime(content['story_date'], '%d/%m/%Y').date()
        all_stories = NewsStories.objects.all().filter(story_cat__contains=category, story_region__contains=region).filter(story_date__gte=date)

    if not all_stories:
        return HttpResponse("No stories found matching criteria ", status=404)
    else:
        stories = []
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
            stories.append(temp)
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
        content = json.loads(request.body)
        key = content['story_key']
        NewsStories.objects.filter(story_id=key).delete()
        return HttpResponse('CREATED',201)
    except  Exception:
        return HttpResponse('Error occured, record not deleted',501)

def loginRequired(request):
    return HttpResponse('Login required to view page',401)
