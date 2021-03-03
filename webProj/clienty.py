import requests
import json


user_data = {'username':'mattyb','password':'shortest'}
jsonInput = {'headline':'asfsauieguirgoiu','category':'art','region':'uk','details':'asdaqwdad  awd awdaw wad '}
query = {'region':'uk'}

r = requests.post('http://127.0.0.1:8000/api/login/', data = user_data)
print("Code: ", r.status_code,  ", Details: ", r.content)


#r = requests.post('http://127.0.0.1:8000/api/postStory/', data = jsonInput)
#print("Code: ", r.status_code,  ", Details: ", r.content)

r = requests.get('http://127.0.0.1:8000/api/getStory',data = query)
print("Code: ", r.status_code,  ", Details: ", r.content)


r = requests.post('http://127.0.0.1:8000/api/logout/')
print("Code: ", r.status_code,  ", Details: ", r.content)
 
#r = requests.get('http://127.0.0.1:8000/api/login/', data = user_data)
#print("Code: ", r.status_code,  ", Details: ", r.content)

#r = requests.get('http://127.0.0.1:8000/api/logout/')
#print("Code: ", r.status_code,  ", Details: ", r.content)
#r = requests.get('http://127.0.0.1:8000/api/login', data = user_data)
#print("Code: ", r.status_code,  ", Details: ", r.content)

#r = requests.post('http://127.0.0.1:8000/api/logout')
#print("Code: ", r.status_code,  ", Details: ", r.content)



