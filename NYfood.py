from pymongo import MongoClient
from collections import Counter
from math import pi
from bokeh.layouts import row, column

import pandas as pd

from bokeh.palettes import Category20c
from bokeh.plotting import figure, show
from bokeh.transform import cumsum
from bokeh.models import HoverTool,Div


#Connexion à la base de données:

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["food"]
coll = db["NYfood"]


#On extrait les types de restaurants les plus populaires dans la collection NYfood:
#On regroupe par $cuisine, on trie en ordre décroissant pr avoir les plus populaires 
#On se limite à 15 types différents 

pipeline_extraction = [
                        {'$group': {'_id': "$cuisine",
                                  'nb_restos': {'$sum':1}}},
                        {'$sort': {'nb_restos':-1}},
                        {'$limit':12}
                                  
                      ]
cursor = coll.aggregate(pipeline_extraction)
data_brut = list(cursor)
liste_types = []

#On recupere les données dans une liste: 
for categorie in data_brut:
    liste_types.append(categorie)
    
#On recupere la liste de toutes les catégories de restaurants:
liste_cuisine = []
for categorie in data_brut:
    categ = categorie['_id']
    liste_cuisine.append(categ)
    
#On crée un dictionnaire qui fait correspondre à chaque type le nombre de restaus correspondants
#cas particulier pour la catégorie latin on raccourcit le nom pour simplifier la suite
    
dico_nb = {}
for categorie in liste_types:
    nom = categorie['_id']
    if len(nom) > 15:
        nom = "Latin"
    nb = categorie['nb_restos']
    dico_nb[nom] = nb
    
#Création du PieChart associé:
    
x = dico_nb

data = pd.DataFrame.from_dict(dict(x), orient='index').reset_index()
data = data.rename(index=str, columns={0:'value', 'index':'categorie'})
data['angle'] = data['value']/sum(x.values()) * 2*pi
data['color'] = Category20c[len(x)]

p = figure(plot_height=350, title="Répartition des restaurants par type", toolbar_location=None,
           tools="hover", tooltips=[("Type", "@categorie"),("Value", "@value")])

p.wedge(x=0, y=1, radius=0.4, 
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='categorie', source=data)

p.axis.axis_label=None
p.axis.visible=False
p.grid.grid_line_color = None

description_p = Div(text="""
<p><b>Description: </b> Représentation de la proportion des 20 catégories de restaurants les plus populaires</p>
</p>On voit que la catégorie American est très présente avec près d'un tiers des restaurants.</p>
""",width=500)

p = column(p,description_p)

#Deuxième requête : cette fois on veut avoir les notes pour chaque type de restaurants:

#pour rappel on a la liste des types de restaurants dans liste_cuisine

dico_notes_cuisine = {}

for cuisine in liste_cuisine:
    pipeline_extraction2 = [
                        {'$match': {"cuisine": cuisine}},
                        {'$project': {'taille': {'$size': "$grades"},
                                    'cuisine': "$cuisine"}},
                        {'$group': {'_id': "$cuisine",
                                 'note_moy': {'$avg': "$taille"}}}
                      ]
    cursor = coll.aggregate(pipeline_extraction2)
    data_brut = list(cursor)
    if len(cuisine) > 15:
        cuisine = "Latin"
    dico_notes_cuisine[cuisine] = data_brut[0]['note_moy']
    

#On associe à x les différentes cuisines et à y la note moyenne correspondante:
x = list(dico_notes_cuisine.keys())
y = list(dico_notes_cuisine.values())

p2 = figure(x_range=x, height=250, title="Notes moyennes des différents types de restaurants",
           toolbar_location=None, tools="")
outilsurvol = HoverTool(tooltips=[("Type de restaurant", "@x")])
p2.add_tools(outilsurvol)
p2.vbar(x=x, top=y, width=0.9,color=Category20c[len(x)])

description_p2 = Div(text="""
<p><b>Description: </b> Représentation des notes moyennes par type de restaurants parmi les 20 plus populaires de la base de données</p>
</p>On voit que pour la catégorie other il y a une valeur extrême très inférieure aux autres moyennes.</p>
""",width=500)

p2 = column(p2,description_p2)
    

#Mise en page finale


Presentation = Div(text="""
<h1>Projet MongoDB- Analyse de la base "food"<h1>
<h2> Visualisation des données </h2>
<p>Le travail s'est concentré sur les 20 catégories les plus populaires de la base. J'ai ensuite déterminé, via une requête mongoDB, les notes moyennes pour chaque catégorie retenue. De là j'ai pu en déduire et construire les graphes ci-dessous : </p>
""")

layout = row(p,p2)
layout_final = column(Presentation,layout)
output_file('NYfood.html')
show(layout_final)