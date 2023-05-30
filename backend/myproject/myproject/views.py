import random
import requests
from django.http import JsonResponse
from django.http import HttpResponse

all_breeds = []
available_breeds = []
sended_breeds = []
LEVELS = ['affection_level','adaptability','energy_level','intelligence','vocalisation','social_needs']
EXTRA_LEVELS = ['stranger_friendly','child_friendly','dog_friendly','grooming','health_issues','shedding_level']
THE_CAT_API_ENDPOINT = 'https://api.thecatapi.com/v1'
HEADERS = {'x-api-key': 'live_lnQuYxTbHPNxcVNbaQhbjqnJyLDBNVaCR5VnexkoAKePK2hEdqju23593jVaMMpB'}

def get_breed(request):
    print ('--> REQUEST RECEIVED')
    global all_breeds
    global available_breeds
    global sended_breeds

    # GETTING ARGUMENTS
    reset = request.GET.get('reset')
    selected_index = request.GET.get('selected_index')
    selected_level = request.GET.get('selected_level')    
    selected_action = request.GET.get('selected_action')

    # FETCHING ALL BREEDS AT FIRST TIME
    if len(all_breeds) == 0:
        response = requests.get(f'{THE_CAT_API_ENDPOINT}/breeds', headers=HEADERS)
        data = response.json()
        all_breeds.extend(data)
        available_breeds = all_breeds.copy()
        print ('--> ALL BREEDS FETCHED')

    # RESET FUNCTION
    if reset:
        available_breeds.clear()
        sended_breeds.clear()
        available_breeds = all_breeds.copy()
        sended_breeds = []
        print ('--> RESETED BACKEND')
        print (f'All breeds length: {len(all_breeds)}')
        print (f'Available breeds length: {len(available_breeds)}')
        return HttpResponse()

    # LOOKING FOR MAX-SCORED BREED IF SELECTED INDEX IS DEFINED
    if selected_index != 'undefined':
        selected_index = int(selected_index)
        selected_level = LEVELS[int(selected_level) - 1]

        # UPDATING SENDED_BREEDS IF THE ORIGIN BREED IS NOT THE LAST SENDED 
        if selected_index + 1 < len(sended_breeds) :
            sended_breeds = sended_breeds[:selected_index + 1]
            available_breeds = [breed for breed in all_breeds if breed not in sended_breeds]
            print ('--> SENDED BREEDS UPDATED')

        # GETTING BREEDS THAT MEET THE REQUERIMENT
        if selected_action == '=': 
            match_breeds = [breed for breed in available_breeds if breed.get(selected_level) == sended_breeds[selected_index].get(selected_level)]
        elif selected_action == '-':
            match_breeds = [breed for breed in available_breeds if breed.get(selected_level) < sended_breeds[selected_index].get(selected_level)]
        else:
            match_breeds = [breed for breed in available_breeds if breed.get(selected_level) > sended_breeds[selected_index].get(selected_level)]

        # GETTING MAX-SCORED BREED
        def scoring(breed):
            score = 0
            for level in LEVELS:
                level_score = 5 - abs(sended_breeds[selected_index].get(level) - breed.get(level))
                score += level_score
            return score
        breed = max(match_breeds, key=scoring)
        print ('--> MAX-SCORED BREED FINDED')

    # LOOKING FOR RANDOM BREED IF SELECTED INDEX IS UNDEFINED
    else:
        randomIndex = random.randint(0, len(available_breeds) - 1)
        breed = available_breeds[randomIndex]
        print ('--> RANDOM BREED FINDED')

    sended_breeds.append(breed)
    available_breeds.remove(breed)
    print (f'Sended breeds length: {len(sended_breeds)}')
    print (f'Available breeds length: {len(available_breeds)}')

    # FETCHING IMAGES
    imagesResponse = requests.get(f'{THE_CAT_API_ENDPOINT}/images/search?limit=10&breed_ids={breed["id"]}', headers=HEADERS)
    imagesData = imagesResponse.json()
    print ('--> IMAGES FETCHED')

    # BREED TO RETURN
    new_breed = {
        'id': breed['id'],
        'name': breed['name'],
        'images': imagesData,
        'description': breed['description'],
        'fav': False,
        'selected_level': None,
        'selected_action': None,
        'levels': {},
        'extra_levels': {}
    }

    # ADDING LEVELS AND ACTION ABILITIES
    for level in LEVELS:
        new_breed['levels'][level] = {
            'points': breed[level],
            'plus_ability': any(available_breed.get(level) > breed.get(level) for available_breed in available_breeds),
            'equal_ability': any(available_breed.get(level) == breed.get(level) for available_breed in available_breeds),
            'less_ability': any(available_breed.get(level) < breed.get(level) for available_breed in available_breeds),
        }
    for extra_level in EXTRA_LEVELS:
        new_breed['extra_levels'][extra_level] = {
            'points': breed[extra_level],
        }

    print ('--> BREED RETURNED')

    return JsonResponse(new_breed)
