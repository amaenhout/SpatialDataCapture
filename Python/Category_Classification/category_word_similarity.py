from __future__ import division
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import nltk.tokenize
import csv, os, re
import scipy.spatial.distance as distance
import collections
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

print('Package ready')

word = ['édifice religieux','écrivain','écrivain','winkelcentrum','wijk','unité militaire','unité','television season','television','television','televisieprogramma','straße','strada','station','settlement','settlement','settlement','settlement','settlement','settlement','settlement','settlement','settlement','settlement','settlement','royalty','river','rennstrecke','pont','plaats in belgië','plaats in belgië','personnalité politique','paus','ortsgliederung','ortsgliederung','oper','occupation','musique (artiste)','mountain','montagne','montagne','militärischer konflikt','military unit','militair conflict','localité de belgique','linea metropolitana','land plus','land plus','krant','historic site','gemeinde in südtirol','gemeinde in italien','gemeinde in italien','gemeinde in italien','gemeinde in deutschland','gemeinde in deutschland','gemeinde in deutschland','french region','football club','football biography','football biography','finnish municipality','dynastie','cyclist','continent','compétition sportive','company','commune de suisse','commune de suisse','commune d\'allemagne','civilian attack','biographie2','auteur','ambassador','Continent', 'Quartier', 'Commune', 'settlement','Municipalité du Canada', 'French commune', 'Pays','Italian comune', 'German location', 'street', 'Département de France', 'Localité',
'Voie parisienne','Ville','Région de France', "Communauté autonome d'Espagne",'Région naturelle','Espace public','former country','Localité du Burkina','Municipalité de Colombie','Ancienne commune de','French region','Subdivision administrative','Swiss town','Ville','UK place',"Région d'Italie",'Quartier canadien','État','Voie de New','country','road','Pays Bretagne','Subdivision','Gare','Pont','Route/France|statut=A|numéro=16','Montagne', "Étendue d'eau", 'Sentier de randonnée', 'islands', 'Grotte',
"Cours d'eau",'Île','forest','Vallée','river', 'mountain pass','wine region','Espace vert','Col',
'Biome','Gorge','mountain range','protected area','Région viticole','Lac''university','building','Museum','Inventaire du patrimoine','Monument','Château','Campus','theatre','Site archéologique','Patrimoine mondial','Musée','Abbaye cistercienne','Paroisse anglo-normande','ancient site','Hippodrome','Porte de Paris','school','Hôpital', 'Maison princière','station','Centre commercial','color','Personnage (fiction)','Langue','album','Cinéma (film)','Livre','Pièce de théâtre','opera','Sport','Célébration','Sport olympique','orchestra','Couleur','film','instrument','Presse|','Mets','Art','people','song','book|','Ouvrag','prepared food', 'beverage','Boisson','Musique (\x9cuvre)','Unité','number','medical condition (new)','Unit','Grandeur physique','physical quantity','Chimie','named horse','grape variety','horse breed','Biohomonymie','Soleil','Ordre religieux','Divinité','Saint','Créature','Juridiction christianisme',
'deity','Prélat catholique','Rabbi','Christian leader', 'saint','Unité militaire', 'military conflict', 'Liste de fichiers', 'Société','political party', 'Métier', 'company', 'organization', 'Groupe ethnique','ethnic group','Distinction','Conflit militaire|','Compétition sportive','Circuit automobile','Organization', "Communauté d'Arménie",'Aircraft Begin','aircraft begin','U.S. state symbols','Navire', 'Récompense','Éphéméride mois de','Association','Équipe nationale de','Écrivain', 'Artiste', 'Cinéma (personnalité)', 'Musique classique (personnalité)', 'Musique (artiste)','artist', 'Artist', 'Architecte','writer','architect','musical artist','comics creator','musician','scientist', 'Scientifique', 'Personnalité des sciences','engineer','Explorateur','Égyptologue','Personnalité politique', 'Personnalité militaire', 'Politicien','military person','officeholder', 'Roman emperor', 'Prime Minister','Empereur romain','Poste politique','Boxeur','Footballeur','racing driver','Alpiniste, grimpeur','Sportif','football biography','Athlète','F1 driver','Rugbyman','Joueur de tennis','sportsperson','Philosophe','philosopher','Aristocrate', 'Rôle monarchique', 'Nobility','royalty','pirate','Famille noble','royalty|type=monarch','Given Name Revised','Family','family','surname','person','given name2','given name']
 
words_single = []
for words in word:
    if words not in words_single:
        words_single.append(words)

print(words_single)