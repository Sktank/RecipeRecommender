import json
import os
import numpy as np

def getDish(recipeTitle):
    title = sub(r'\([^)]*\)', '', recipeTitle)
    words = title.split(" ")
    words = [w for w in words if len(w) > 0]
    if 'with' in words:
        words = words[0:words.index('with')]
    if '-' in words:
        words = words[0:words.index('-')]
    
    if len(words) > 1 and match("I+|VI*", words[-1]):
        dish = words[-2]
    else:
        dish = words[-1]

    return dish
    
def slugsToClippedIndices(slugs):
    indices = []
    for slug in slugs:
        indices.append(recipeSlugsClipped.index(slug))
    return np.array(indices)

def clippedIndicesToSlugs(indices):
    return [recipeSlugsClipped[i] for i in indices]


def cosine(arr1, arr2):
    return np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))

class ContentRecommender:
    def __init__(self, cachedFilename):
        self.matrix = np.loadtxt(cachedFilename)
        
    def recommend(self, recipeBox, N):
        recipeBoxVectors = self.matrix[recipeBox]
        userProfile = np.asarray(recipeBoxVectors.sum(0))
        distances = np.array([cosine(userProfile, recipeVector) for recipeVector in self.matrix])
        order = distances.argsort()
        top = order[1:N+1] # exclude the item itself
        return top

class CFRecommender:

    def __init__(self, cachedFilename):
        self.recipeWeights = np.loadtxt(cachedFilename)

    def recommend(self, recipeBox, N, metric='cosine'):
        userProfile = self.recipeWeights[recipeBox, :].sum(0)

        if metric == 'dot':
            preferences = np.dot(self.recipeWeights, userProfile)
            order = preferences.argsort()[::-1]
        elif metric == 'cosine':
            distances = np.array([cosine(userProfile, recipeVector) for recipeVector in self.recipeWeights])
            order = distances.argsort()

        top = order[0:N]
        return top
    
class HybridRecommender:
    def __init__(self, cachedFilename):
        self.recipesIFactors = np.loadtxt(cachedFilename)

    def recommend(self, recipeBox, N):
        recipeBoxVectors = self.recipesIFactors[recipeBox]
        userProfile = np.asarray(recipeBoxVectors.sum(0))
        distances = np.array([cosine(userProfile, recipeVector) for recipeVector in self.recipesIFactors])
        order = distances.argsort()
        top = order[0:N] # exclude the item itself
        return top 

def recommendSlugs(recommender, recipeBoxSlugs, N=100):
    recipeBox = [recipeSlugsClipped.index(slug) for slug in recipeBoxSlugs]
    recommendationIndices = recommender.recommend(recipeBox, N=N)
    recommendations = [recipeSlugsClipped[i] for i in recommendationIndices]
    return recommendations

#f = open('data/recipe_info.csv')
#recipeLinesClipped = f.readlines()
#recipeTitlesClipped = [line.split(',')[1].strip() for line in recipeLinesClipped]
#recipeSlugsClipped = [line.split(',')[0].strip() for line in recipeLinesClipped]
#f.close()

recipeFilePath = os.path.join(os.path.dirname(__file__), 'data/recipes.jl')
# factorsAFilePath = os.path.join(os.path.dirname(__file__), 'data/factors_50_A.dat')
# factorsYFilePath = os.path.join(os.path.dirname(__file__), 'data/factors_50_Y.dat')
factorsTopFilePath2 = os.path.join(os.path.dirname(__file__), 'data/factorsTop.json')
recipeFactorsFilePath2 = os.path.join(os.path.dirname(__file__), 'data/recipeFactors.json')
ifactorsTopFilePath2 = os.path.join(os.path.dirname(__file__), 'data/ifactorsTop.json')
recipeIFactorsFilePath2 = os.path.join(os.path.dirname(__file__), 'data/recipeIFactors.json')

#ingredientsDishMatrixFilePath = os.path.join(os.path.dirname(__file__), 'data/ingredientsDishMatrix.dat')
recipeFactorsFilePath = os.path.join(os.path.dirname(__file__), 'data/recipeWeights.dat')
recipeIFactorsFilePath = os.path.join(os.path.dirname(__file__), 'data/recipesIFactors.dat')

f = open(recipeFilePath)
recipes = [json.loads(line) for line in f.readlines()]
recipeSlugsClipped = [recipe['slug'] for recipe in recipes]
recipeTitlesClipped = [recipe['title'] for recipe in recipes]
f.close()

f = open(factorsTopFilePath2)
topFactors = [factor.split(", ") for factor in f.read().translate(None, "\"").split("], [")]

f = open(recipeFactorsFilePath2)
recipeFactors = json.loads(f.read())


f = open(ifactorsTopFilePath2)
itopFactors = [factor.split(", ") for factor in f.read().translate(None, "\"").split("], [")]

f = open(recipeIFactorsFilePath2)
recipeIFactors = json.loads(f.read())

#content = ContentRecommender(ingredientsDishMatrixFilePath)
cf = CFRecommender(recipeFactorsFilePath)
hybrid = HybridRecommender(recipeIFactorsFilePath)

# Public Methods

def recommendContent(recipeBoxSlugs, N=100):
    return recommendSlugs(content, recipeBoxSlugs)

def recommendCF(recipeBoxSlugs, N=100):
    return recommendSlugs(cf, recipeBoxSlugs)

def recommendHybrid(recipeBoxSlugs, N=100):
    return recommendSlugs(hybrid, recipeBoxSlugs)

def getRecipeInfo():
    return (recipeTitlesClipped, recipeSlugsClipped)

def getTopFactors():
    return topFactors

def getRecipeFactors():
    return recipeFactors

def getITopFactors():
    return itopFactors

def getRecipeIFactors():
    return recipeIFactors



