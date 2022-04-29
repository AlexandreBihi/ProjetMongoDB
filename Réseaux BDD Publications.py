from pymongo import MongoClient
from bokeh.io import output_notebook, show, save
import networkx as nx
from bokeh.plotting import figure, output_file, show,ColumnDataSource,from_networkx
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine
from bokeh.models import EdgesAndLinkedNodes, NodesAndLinkedEdges,Div
from bokeh.layouts import row, column
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
    
#On récupère les 25 auteurs les plus prolifiques : 

#Connexion à la base de données:

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["publications"]
coll = db["hal_irisa_2021"]

#On recupère les 20 auteurs les plus prolifiques sur lesquels on va travailler:

pipeline = [
                        {'$unwind': "$authors"},
                        {'$group': {'_id': {"name": "$authors.name","Firstname": "$authors.firstname"}, 
                                  'nb_publis': {'$sum':1}}},
                        {'$sort': {'nb_publis':-1}},
                        {'$project': {"Name": "$_id.name","firstname": "$_id.Firstname",'_id': 0, "nb_publis": 1}},
                        {'$limit': 20}
                      ] 
cursor = coll.aggregate(pipeline)
liste_auteurs = []


for doc in list(cursor):
    liste_auteurs.append(doc)
    
dic_auteurs_nb = {}
liste_nb_test=[]
for auteur in liste_auteurs:
    name = auteur['Name']+" "+auteur['firstname']
    nb_publis = auteur['nb_publis']
    liste_nb_test.append(nb_publis)
    dic_auteurs_nb[name] = nb_publis
    
liste_noms_auteurs = []
for arete in liste_auteurs:
    nom_complet = arete['Name']+" "+arete['firstname']
    if nom_complet not in liste_noms_auteurs:
        liste_noms_auteurs.append(nom_complet)

# A l'aide d'une boucle on recupère, pour chaque auteur de la liste les documents qu'il a écrits:
liste_dic = []

for doc in liste_noms_auteurs:
    nom1 = doc.split()[0]
    prenom1 = doc.split()[1]
    for doc in liste_noms_auteurs:
        nom2 = doc.split()[0]
        prenom2 = doc.split()[1]
        if (nom2 != nom1 and prenom2 != prenom1):
            pipeline_collab = [
                    {'$match': {'$and': [{"authors.name": {"$all": [nom1,nom2]}},{"authors.firstname": {"$all": [prenom1,prenom2]}}]}},


                        
                        
                        
                        
                        {'$group': {'_id': 'null',
                                  'nb_collab': {'$sum':1}}}
                      ]
            cursor_collab = coll.aggregate(pipeline_collab)
            data = list(cursor_collab)
            print(data)
            if len(data) >0:
                nb_collab = data[0]['nb_collab']
                dico = {"depart":nom1+" "+prenom1,"arrivee":nom2+" "+prenom2,"nb":nb_collab}
                liste_dic.append(dico)
                
            
        
                
                
            
            
                    
        
    

#On crée le graphe:
G = nx.Graph()
    
#On rajoute un noeud pour chaque auteur de nos données:
for auteur in liste_noms_auteurs:
    #print(dic_auteurs_nb[auteur]*100)
    #print(auteur)
    G.add_node(auteur)


#On rajoute les aretes à partir du dictionnaire qu'on a précedemment calculé:
    
for pts in liste_dic:
    G.add_edge(pts['depart'], pts['arrivee'])
    

nx.draw(G,with_labels=True,node_color='#00b4d9')

#Représentation graphique avec bokeh:







degrees = dict(nx.degree(G))
nx.set_node_attributes(G, name='degree', values=degrees)



number_to_adjust_by = 5
adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in nx.degree(G)])
nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

#Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
size_by_this_attribute = 'adjusted_node_size'
color_by_this_attribute = 'adjusted_node_size'

#Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
color_palette = Reds8


#Choose a title!
title = 'Réseau des 20 auteurs les plus prolifiques'

#Establish which categories will appear when hovering over each node
HOVER_TOOLTIPS = [
       ("Auteur", "@index"),
        ("Nombre de connexions", "@degree")
]

#Create a plot — set dimensions, toolbar, and title
plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
            x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

#Create a network graph object
# https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html\
network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

#Set node sizes and colors according to node degree (color as spectrum of color palette)
minimum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
maximum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=linear_cmap(color_by_this_attribute, color_palette, minimum_value_color, maximum_value_color))

#Set edge opacity and width
network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

plot.renderers.append(network_graph)

div = Div(text="""
<h1>Projet MongoDB- Réseau de la base publications<h1>
<h2> Présentation du graphe: </h2>
<p>Le travail s'est concentré sur les 20 auteurs les plus prolifiques de la base. J'ai ensuite déterminé, via une requête mongoDB, la liste d'article en commun pour chaque auteur de la base. De là j'ai pu en déduire et construire le graphe et obtenir le réseau ci-dessous : </p>
""")

description_graphe = Div(text="""
<p><b>Description: </b> Les noeuds du graphe sont colorés en fonction de leur connexion aux autres noeuds: plus un noeud est rouge moins il est connecté et à l'inverse, plus un noeud est pâle voire blanc plus il est connecté aux autres individus.</p>
<p>On voit que certains noeuds sont complétement isolés et donc complétement rouges puisqu'ils n'ont aucune connexion</p>
""",width=500)

plot = row(plot,description_graphe)
layout = column(div,plot)




output_file('Reseau.html')
show(layout)
#save(plot, filename=f"{title}.html")


degrees = dict(nx.degree(G))
nx.set_node_attributes(G, name='degree', values=degrees)

