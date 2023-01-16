import os, requests, json, openai
from requests.auth import HTTPBasicAuth


#Replit's secrets contain the necessary keys received from newsapi and openai web pages
news_api = os.environ['news_api_key']
openai.organisation = os.environ['openai_organization_id']
openai.api_key = os.environ['openai_api_key']
#Model.list() returns information about all models available
openai.Model.list()
#spotify authentication
client_id = os.environ['spotify_client_id']
client_secret = os.environ['spotify_client_secret']
url = "https://accounts.spotify.com/api/token"
data = {"grant_type":"client_credentials"}
auth = HTTPBasicAuth(client_id, client_secret)
response = requests.post(url, data=data, auth=auth)
access_token = response.json()["access_token"]



country = "mx" #we can choose what country gb / us / etc.
url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={news_api}"

result = requests.get(url)
data = result.json()

# If there is an error in the API request, the code will exit
if result.status_code != 200:
    print("Failed to retrieve news articles. Error code: " + str(result.status_code))
    exit()

#if want to print the news stories:
#print(data["articles"][0]["content"])
#print()

#below loops through 5 news, asks openai to summarize them, and returns the keywords version
counter = 0
for article in data["articles"]:
    counter +=1
    if counter > 5:
        break

    print(f"News {counter}")
    print(article['title'])
    #promt is the key to modify our request, like when asking Chat GPT to do something
    prompt = (f"Get keywords for article {article['title']} {article['content']}, no more than four words.") 
    #this keeps giving also long answers. How to influence better?
    
    response = openai.Completion.create(model="text-davinci-002", prompt=prompt, temperature=0.5, max_tokens=50)
    #temperature influences "creativity", 0 is strict and 1 is most creative
    
    if "error" in response:
        print("Failed to connect with OpenAI. Error message: " + response["error"])
        exit()

    #preparing openai response to be used as a spotify search term
    spotify_key_words = response["choices"][0]["text"].strip()
    # print(spotify_key_words)
    spotify_key_words = spotify_key_words.replace(" ", "%20")
    
    #spotify part begins
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    search = f"?q=track%3A%20{spotify_key_words}&type=track&limit=1"
    
    full_url = f"{url}{search}"
    
    response = requests.get(full_url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to retrieve songs. Error code: " + str(response.status_code))
        exit()
        
    data = response.json()
    
    for track in data["tracks"]["items"]:
        print()
        print(track["name"])
        print(track["preview_url"])
        print()