import json
import os
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.preprocessing import normalize
from scipy.spatial.distance import cosine
from scipy.sparse import hstack, eye, csr_matrix
from re import sub, match
import pickle

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

class ContentRecommender:
    def __init__(self, recipesFilename, dishWeight=10):
        f = open(recipesFilename)
        self.recipes = [json.loads(line) for line in f.readlines()]
        f.close()
        
        self.recipeDishes = [getDish(recipe['title']) for recipe in self.recipes]
  
        self.ingredientDictionariesAmount = []
        for recipe in self.recipes:
            ingredientDictionary = {ingredient["id"] : float(ingredient["grams"]) for ingredient in recipe["ingredients"]}
            self.ingredientDictionariesAmount.append(ingredientDictionary)

        self.vectorizerAmount = DictVectorizer(dtype=int)
        ingredientMatrixAmount = self.vectorizerAmount.fit_transform(self.ingredientDictionariesAmount)
        ingredientMatrixAmount = ingredientMatrixAmount.astype(np.double)
        ingredientMatrixAmount = normalize(ingredientMatrixAmount, norm='l1')
        
        self.dishVectorizer = CountVectorizer(token_pattern=".+")
        dishMatrix = self.dishVectorizer.fit_transform(self.recipeDishes) * dishWeight
        
        self.matrix = csr_matrix(hstack((dishMatrix, ingredientMatrixAmount)))
        
    def recommend(self, recipeBox, N):
        recipeBoxVectors = self.matrix[recipeBox].toarray()
#         normRecipeBoxVectors = recipeBoxVectors / recipeBoxVectors.sum(1)[:, np.newaxis]
#         print normRecipeBoxVectors
        userProfile = np.asarray(recipeBoxVectors.sum(0))
        distances = np.array([cosine(userProfile, recipeVector.toarray()) for recipeVector in self.matrix])
        order = distances.argsort()
        top = order[1:N+1] # exclude the item itself
        return top

class CFRecommender:
    def __init__(self, recipeWeightsFilename, userWeightsFilename):
        self.recipeWeights = np.loadtxt(recipeWeightsFilename, dtype='float', delimiter=',')
        self.userWeights = np.loadtxt(userWeightsFilename, dtype='float', delimiter=',')

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
    def __init__(self, recipesFilename, ingredientMatrixFilename, userMatrixFilename):
        f = open(recipesFilename)
        self.recipes = [json.loads(line) for line in f.readlines()]
        f.close()
  
        self.ingredientDictionariesAmount = []
        for recipe in self.recipes:
            ingredientDictionary = {ingredient["id"] : float(ingredient["grams"]) for ingredient in recipe["ingredients"]}
            self.ingredientDictionariesAmount.append(ingredientDictionary)

        vectorizerAmount = DictVectorizer(dtype=int)
        recipeIngredients = vectorizerAmount.fit_transform(self.ingredientDictionariesAmount)


        ingredientVocabularyFilePath = os.path.join(os.path.dirname(__file__), 'data/ingredient_vocabulary.dat')

        f = open(ingredientVocabularyFilePath)
        ingredient_vocabulary = pickle.load(f)
        f.close()
        
        self.chosenindices = np.array([ingredient_vocabulary.index(theid) for theid in vectorizerAmount.get_feature_names()])
        
        self.ingredientIFactors = np.loadtxt(ingredientMatrixFilename, dtype='float', delimiter=',')[self.chosenindices, :]
        self.userIFactors = np.loadtxt(userMatrixFilename, dtype='float', delimiter=',')
        
        self.recipesIFactors = np.dot(recipeIngredients.toarray(), self.ingredientIFactors)


    def recommend(self, recipeBox, N):
        recipeBoxVectors = self.recipesIFactors[recipeBox]
#         normRecipeBoxVectors = recipeBoxVectors / recipeBoxVectors.sum(1)[:, np.newaxis]
#         print normRecipeBoxVectors
        userProfile = np.asarray(recipeBoxVectors.sum(0))
        distances = np.array([cosine(userProfile, recipeVector) for recipeVector in self.recipesIFactors])
#         preferences = np.dot(self.recipesIFactors, userProfile)
        order = distances.argsort()
#         order = preferences.argsort()
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
factorsAFilePath = os.path.join(os.path.dirname(__file__), 'data/factors_50_A.dat')
factorsYFilePath = os.path.join(os.path.dirname(__file__), 'data/factors_50_Y.dat')
factorsTopFilePath = os.path.join(os.path.dirname(__file__), 'data/factorsTop.json')
recipeFactorsFilePath = os.path.join(os.path.dirname(__file__), 'data/recipeFactors.json')
ifactorsTopFilePath = os.path.join(os.path.dirname(__file__), 'data/ifactorsTop.json')
recipeIFactorsFilePath = os.path.join(os.path.dirname(__file__), 'data/recipeIFactors.json')

f = open(recipeFilePath)
recipes = [json.loads(line) for line in f.readlines()]
recipeSlugsClipped = [recipe['slug'] for recipe in recipes]
recipeTitlesClipped = [recipe['title'] for recipe in recipes]
f.close()

f = open(factorsTopFilePath)
topFactors = [factor.split(", ") for factor in f.read().translate(None, "\"").split("], [")]

f = open(recipeFactorsFilePath)
recipeFactors = json.loads(f.read())


f = open(ifactorsTopFilePath)
itopFactors = [factor.split(", ") for factor in f.read().translate(None, "\"").split("], [")]

f = open(recipeIFactorsFilePath)
recipeIFactors = json.loads(f.read())

content = ContentRecommender(recipeFilePath)
cf = CFRecommender(factorsAFilePath, factorsYFilePath)
hybrid = HybridRecommender(recipeFilePath, factorsAFilePath, factorsYFilePath)

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



