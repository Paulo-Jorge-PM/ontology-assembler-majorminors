#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os, time



def generate():

    finalFile = ""
    person = ""
    priority = ""
    article = ""

    finalFile += getSkeleton()

    path = os.path.join(os.getcwd(),"individuals")

    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'r', encoding="utf-8") as f: # open in readonly mode
            fileName = os.path.basename(f.name)
            data = f.read()
            if fileName == "article.txt":
                article += data
            elif fileName == "person.txt":
                person += data
            elif fileName == "priority.txt":
                priority += data
            else:
                finalFile += data

    finalFile += person
    finalFile += priority
    finalFile += article

    saveFinal(finalFile)

def getSkeleton():
    path = os.path.join(os.getcwd(), "ontology_skeleton.ttl")
    with open(path, 'r', encoding="utf-8") as f:
        data = f.read()
    return data

def saveFinal(data):
    timestap = time.time()
    path = os.path.join(os.getcwd(), "generated", "ontology_"+str(timestap)+".ttl")
    with open(path, 'w', encoding="utf-8") as f:
        f.write(data)
    print("File saved at: " + path)


if __name__ == '__main__':
    main = generate()