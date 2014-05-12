# Create your views here.
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
import json
from django.views.decorators.csrf import csrf_exempt
import recommend




def index(request, template="core/index.html"):
    return render_to_response(template)

def recipeNames(request):
    (titles, slugs) = recommend.getRecipeInfo()
    resp = {}
    resp['names'] = titles
    data1 = resp
    data2 = recommend.getTopFactors()
    data3 = recommend.getRecipeFactors()
    data4 = recommend.getITopFactors()
    data5 = recommend.getRecipeIFactors()

    return HttpResponse(
        json.dumps(
            {
                "names": data1,
                "topFactors": data2,
                "recipeFactors": data3,
                "itopFactors": data4,
                "recipeIFactors": data5
            }
        )
    )

@csrf_exempt
def recommendRecipes(request):
    if request.is_ajax():
        recipeTitles = request.POST.getlist('recipes[]', False)
        (titles, slugs) = recommend.getRecipeInfo()
        recipes = [slugs[titles.index(title)] for title in recipeTitles]

        alg = request.POST.get('alg', False)
        print alg



        #TODO: generate the necessary recommendations
        if alg == "content":
            recommendationsSlugs = recommend.recommendContent(recipes)
        elif alg == "cf":
            recommendationsSlugs = recommend.recommendCF(recipes)
        elif alg == "hybrid":
            recommendationsSlugs = recommend.recommendHybrid(recipes)

        recommendationsTitles = [titles[slugs.index(slug)] for slug in recommendationsSlugs]

        recHTML = "<h4>Recommendations</h4><ol>"
        for i in range(len(recommendationsSlugs)):
            recHTML += "<li><a target='_blank' href='http://www.allrecipes.com/Recipe/%s/Detail.aspx'>%s</a></li>" % (recommendationsSlugs[i], recommendationsTitles[i])

        recHTML += "</ol>"

        return HttpResponse(recHTML)