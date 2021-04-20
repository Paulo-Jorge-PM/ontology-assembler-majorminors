 #!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
sys.path.append("..")

import re, pathlib, importlib

from sentimentAnalysis import sentiment

class Ontology():

    def __init__(self, articleData):

        ### DATA
        self.articleData = articleData

        #self.uri = 'http://www.semanticweb.org/lei'
        self.uri = 'http://sparql.ilch.uminho.pt/minors'

        self.individuals = {#Placeholder for the individuals found in the text
        "animal":[],
        "city":[],
        "continent":[],
        "country":[],
        "otherPlace":[],
        "entity":[],
        "ethnicity":[],
        "keyword":[],
        "politicalParty":[],
        "religion":[],
        "weekday":[],
        "month":[],
        "footballClub":[],
        "brand":[],
        "carBrand":[],
        "sport":[],
        "tvChannel":[],

        "job":[],
        "person":[],

        "minority":[],
        "tag":[],
        "priority":[],

        "comment":[],
        "image":[],
        }

        self.sa = sentiment.SentimentAnalysis()

        
        
        if not self.doArticleExist():#If article not already inserted (avoids duplicates)
            ### PROCESS
            for individualType in self.individuals:
                self.searchIndividuals(individualType)
            
            self.generateArticle()

    """def load(self, lista):
        filePath = pathlib.Path.cwd().joinpath('ontology','data','individuals',lista+'.txt')
        search = r'###  ' + self.uri+'#'
        for individualType in self.individuals:
            with open(filePath, "r", encoding="utf-8") as file:
                data = file.read()
                search = re.search(searchFor, data)"""
    
    def searchIndividuals(self, individualType):
        if individualType not in ["priority", "minority", "tag", "job", "comment", "image"]:
            listImport = importlib.import_module(".lists."+individualType, package="ontology")
            searchList = getattr(listImport, "data")
            for item in searchList:
                    #\b procura se é terminação ou começo de palavra. Assim procurando p.e. "Barreiro" ou "arreiros", "Barreiros" não dá resultado.
                    pattern = r'\b' + re.escape(item) + r'\b'
                    try:
                        #try because if the item or body_text is empty it gives error. a if x and y could also work
                        search = re.search(pattern, self.articleData._body, flags=re.IGNORECASE)
                    except:
                        search = False
                    if search:
                        if individualType == "person":
                            self.generateIndividual(individualType, item, extra=searchList[item])
                        else:
                            self.generateIndividual(individualType, item)
        elif individualType == "minority":
            for x in self.articleData._minorias:
                self.generateIndividual("minority", x)
        elif individualType == "tag":
            for x in self.articleData._tags:
                self.generateIndividual("tag", x)
        elif individualType == "priority":
            for x in self.articleData._prioridade:
                self.generatePriority(x, str(self.articleData._prioridade[x]))
        elif individualType == "job":
            for item in self.individuals["job"]:
                self.generateIndividual("job", item)
        elif individualType == "comment":
            c=1
            for x in self.articleData._comentarios:
                articleId = self.articleData._fileName.replace('.html','').replace('.','-')
                nameId = articleId + '_' + str(c)
                self.generateIndividual("comment", nameId, extra=x)
                c+=1
        elif individualType == "image":
                #Meti 1 no id, para o caso de um dia se fazer uma lista de imagens e quisermos adicionarmar mais do que uma por artigo
                articleId = self.articleData._fileName.replace('.html','').replace('.','-')
                nameId = articleId + '_1'
                self.generateIndividual("image", nameId, extra=self.articleData._imageURL)



    def generateIndividual(self, individualType, name, extra=None):
        #name_filtered=name.replace(" ", "_").replace("'","").replace(",","")
        name_filtered=name.replace(" ", "_")
        name_filtered=re.sub(r'\W+', '', name_filtered)#remove non alfabetical and numberical carachteres
        if individualType == 'person':
            line = '''
###  ''' + self.uri + '''#person-'''+name_filtered+'''
:person-'''+name_filtered+''' rdf:type owl:NamedIndividual ,
                               :Person ;'''
            if extra["job"]:
                jobID = extra["job"].lower().strip().replace(" ", "_")
                jobID = re.sub(r'\W+', '', jobID)
                line += '''
                      :hasJob :job-'''+jobID+''' ;'''
                if extra["job"].lower().strip() not in self.individuals["job"]:
                    self.individuals["job"].append(extra["job"].lower().strip())
            if extra["wikiPage"]:
                line += '''
                      :wikiPage "'''+extra["wikiPage"]+'''"^^xsd:anyURI ;'''
            line += '''          
                      :personName "'''+name.strip()+'''"^^xsd:string .

            '''
        elif individualType == 'comment':
            line = '''
###  ''' + self.uri + '''#comment-'''+name_filtered+'''
:comment-'''+name_filtered+''' rdf:type owl:NamedIndividual ,
                          :Comment ;
                 :comment """'''+extra.strip().replace('"',r'\"')+'''"""^^xsd:string .

            '''
        elif individualType == 'image':
            line = '''
###  ''' + self.uri + '''#image-'''+name_filtered+'''
:image-'''+name_filtered+''' rdf:type owl:NamedIndividual ,
                        :Image ;
               :imageLink "'''+extra.strip()+'''"^^xsd:anyURI .

           '''
        else:
            line = '''
###  ''' + self.uri + '''#'''+individualType+'''-'''+name_filtered+'''
:'''+individualType+'''-'''+name_filtered+''' rdf:type owl:NamedIndividual ,
                 :'''+individualType[0].upper()+individualType[1:]+''' ;
        :'''+individualType+''' "'''+name.strip()+'''"^^xsd:string .

            '''
        self.saveIndividual(individualType, line, individualType+"-"+name_filtered)
        self.individuals[individualType].append(individualType+"-"+name_filtered)


    def generatePriority(self, minority, priority):
        minority_filtered=minority.replace(" ", "_")
        line = '''
###  ''' + self.uri + '''#priority-'''+minority_filtered+'''-'''+priority+'''
:priority-'''+minority_filtered+'''-'''+priority+''' rdf:type owl:NamedIndividual ;
                     :referesMinority :minority-'''+minority_filtered+''' ;
                     :priority '''+priority+''' .

        '''
        self.saveIndividual('priority', line, 'priority-'+minority_filtered+'-'+priority)
        self.individuals['priority'].append('priority-'+minority_filtered+'-'+priority)


    def generateArticle(self):
        articleId = self.articleData._fileName.replace('.html','').replace('.','-')
        link = self.articleData._url.strip().split('#')[0]
        #delete the arquivi.pt parte, so we cna use the source url for checking if the article is not repeated
        #journalLink = re.sub(r'https.*/http','http', link)
        journalLink = re.sub(r'https://arquivo.pt/wayback/[0-9]*/','', link)
        journalLink = re.sub(r'http.*://www\.','', journalLink)
        journalLink = re.sub(r'http.*://','', journalLink)
        line = '''
###  ''' + self.uri + '''#article-'''+articleId+'''
:article-'''+articleId+''' rdf:type owl:NamedIndividual ,
                   :Article ;
                   :articleFrom :newspaper-Público ;'''

        line += self.articleReferes("referesEntity",["entity"])
        line += self.articleReferes("referesKeyword",["keyword"])
        line += self.articleReferes("referesAnimal",["animal"])
        line += self.articleReferes("referesEthnicity",["ethnicity"])
        line += self.articleReferes("referesReligion",["religion"])
        line += self.articleReferes("referesPoliticalParty",["politicalParty"])
        #line += self.articleReferes("referesPlace",["city","country","continent","otherPlace"])
        #line += self.articleReferes("referesTime",["weekday","month"])
        line += self.articleReferes("referesCity",["city"])
        line += self.articleReferes("referesCountry",["country"])
        line += self.articleReferes("referesContinent",["continent"])
        line += self.articleReferes("referesOtherPlace",["otherPlace"])
        line += self.articleReferes("referesMonth",["month"])
        line += self.articleReferes("referesWeekday",["weekday"])
        
        line += self.articleReferes("referesFootballClub",["footballClub"])
        line += self.articleReferes("referesBrand",["brand"])
        line += self.articleReferes("referesCarBrand",["carBrand"])
        line += self.articleReferes("referesSport",["sport"])
        line += self.articleReferes("referesTvChannel",["tvChannel"])
        
        line += self.articleReferes("referesTag",["tag"])
        line += self.articleReferes("referesMinority",["minority"])
        line += self.articleReferes("referesPerson",["person"])
        line += self.articleReferes("referesJob",["job"])
        line += self.articleReferes("hasPriority",["priority"])
        line += self.articleReferes("hasComment",["comment"])
        line += self.articleReferes("hasImage",["image"])


        if self.articleData._introNoticia:
            line += '''
           :preview "'''+self.articleData._introNoticia.strip().replace('"',r'\"')+'''"^^xsd:string ;
            '''

        if self.articleData._anteTitulo:
            line += '''
           :subTittle "'''+self.articleData._anteTitulo.strip().replace('"',r'\"')+'''"^^xsd:string ;
            '''
        title=self.articleData._title.strip().replace('"',r'\"')
        line += '''
           :dataPub "'''+self.articleData._date.strip()+'''T00:00:00"^^xsd:dateTime ;
           :link "'''+link+'''"^^xsd:anyURI ;
           :text """'''+self.articleData._body.strip().replace('"',r'\"')+'''"""^^xsd:string ;
           :fileName "'''+self.articleData._fileName.strip()+'''"^^xsd:string ;
           :title "'''+title+'''"^^xsd:string ;
           :sentimentAnalysis """'''+self.sa.sentiment(title)+'''"""^^xsd:string .

'''
        #self.saveIndividual('article', line, 'article-'+articleId)

        #self.saveIndividual('article', line, journalLink)
        filePath = pathlib.Path.cwd().joinpath('ontology','data','individuals','article.txt')
        with open(filePath, "a+", encoding="utf-8") as file:
            file.write(line)
        print("Ontology generated and saved for the article: "+articleId)

    def articleReferes(self, referesX, individuals):
        line = ''
        c=0
        for individual in individuals:
            if self.individuals[individual] != []:
                if c == 0:
                    line = '''
                   :'''+referesX+''' '''
                    c+=1
                for entity in self.individuals[individual]:
                    if c>0:
                        line += '''
                        :'''+entity+''' ,'''
                    else:
                        line += ':'+entity+' ,'
        if c!=0:
            line = line[:-1]+";"
        return line

    def makeArticleId(self, fullLink):
        articleId = re.sub(r'https://arquivo.pt/wayback/[0-9]*/','', fullLink)
        articleId = re.sub(r'http.*://www\.','', articleId)
        articleId = re.sub(r'http.*://','', articleId)
        return articleId

    def doArticleExist(self):
        # TRUE = Exist / FALSE = Dont Exist Yet
        absoluteLink = self.articleData._url.strip().split('#')[0]
        journalLink = re.sub(r'https://arquivo.pt/wayback/[0-9]*/','', absoluteLink)
        journalLink = re.sub(r'http.*://www\.','', journalLink)
        journalLink = re.sub(r'http.*://','', journalLink)
        
        title = self.articleData._title.strip().replace('"',r'\"')

        filePath = pathlib.Path.cwd().joinpath('ontology','data','individuals','article.txt')
        search = False
        try:
            with open(filePath, "r", encoding="utf-8") as file:
                data = file.read()
                searchLink = re.search(r':link ".*' + journalLink, data)
                searchTitle = re.search(':title "' + title, data)
                if searchLink:
                    search = True
                if searchLink and searchTitle == None:
                    log = '>>>DOUBT (link exist but title not) in file: ' + self.articleData._fileName.strip() + ' | Link: ' + journalLink + ' | ' + 'Title: ' + title + '\n'
                    logFile = pathlib.Path.cwd().joinpath('ontology','logs','doubt-not-sure-files.txt')
                    with open(logFile, "a+", encoding="utf-8") as file:
                        file.write(log)
        except:
            search = False
        return search

    def saveIndividual(self, individualType, line, searchFor):
        filePath = pathlib.Path.cwd().joinpath('ontology','data','individuals',individualType+'.txt')
        try:
            with open(filePath, "r", encoding="utf-8") as file:
                data = file.read()
                search = re.search(searchFor, data)
        except:
            search = None
        if search == None:
            with open(filePath, "a+", encoding="utf-8") as file:
                file.write(line)

#if __name__ == '__main__':
#    main = Ontology()
