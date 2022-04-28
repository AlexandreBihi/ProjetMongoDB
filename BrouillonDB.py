from pymongo import MongoClient

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["food"]

print(db.list_collection_names())

coll = db["NYfood"]
print(coll.index_information())


query = {"borough": "Manhattan", "name": {"$regex": "^A"}}
cursor = coll.find(query)
print(list(cursor)[:10])
print(cursor.count())

liste_docs = []

for doc in coll.find(query).limit(5):
    liste_docs.append(doc)
    
for doc in coll.find(query).sort("name", -1).limit(5):
    print(doc)
    
    
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
    

# A l'aide d'une boucle on recupère, pour chaque auteur de la liste les documents qu'il a écrits:

for doc in liste_auteurs:
    nom1 = doc['Name']
    prenom1 = doc['firstname']
    for doc in liste_auteurs:
        nom2 = 
        preno
        pipeline_collab = [
                        {'$match': {"authors.name":''.format(nom1),"authors.firstname":"{}".format(prenom1),"authors.name":"Sébillot"}},
                        {'$group': {'_id': 'null',
                                  'nb_collab': {'$sum':1}}}
                      ]
    
#Test collab entre Gravier Guillaume et Pascale Sébillot:
        
pipeline_test =[
                        {'$match': {"authors.name":'Gravier',"authors.firstname":"Guillaume","authors.name":"Sébillot"}},
                        {'$group': {'_id': 'null',
                                  'nb_collab': {'$sum':1}}}
                      ]
cursor_test = coll.aggregate(pipeline_test)
test_liste = []
for doc in list(cursor_test):
    test_liste.append(doc['nb_collab'])
dico_test = {'start' : nom+" "+prenom,"time":test_liste[0]}
    
    

    
    