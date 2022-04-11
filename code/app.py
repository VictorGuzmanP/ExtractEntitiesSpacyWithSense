from flask import Flask, render_template, request
import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from classifier import SentimentClassifier

UPLOAD_FOLDER = 'textos'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_lang_detector(nlp, name):
    return LanguageDetector()

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/process', methods = ['POST', ])
def process_text():
    NO_VALID_TEXT = "No se ha proporcionado un texto válido."
    if request.method == 'POST' and 'rawtext' in request.form:
        text = request.form.get('rawtext')
        taskoption = request.form.get('taskoption')

        nlp = spacy.load("es_core_news_md")
        Language.factory("language_detector", func=get_lang_detector)
        nlp.add_pipe('language_detector', last=True)
          
        doc = nlp(text)
        # Vamos a declarar un valor fijo para los sentimientos
        # 0 = negativo, 0.5 = neutral y 1 = positivo
        sentimiento = 0.5
        if (doc._.language["language"] == "es"):
            clf = SentimentClassifier()
            senses = clf.predict(text)
            print("Lenguaje seleccionado Español: es_core_news_md ")
            print("Sentimiento ES: " + str(senses))

            #Esta libreria devuelve valores cerca del 0 como negativos, cerca de 0.5 como neutrales y cerca del 1 como positivos
            sentimiento = 0
            if (senses >=0 and senses < 0.4):
                sentimiento = 'NEGATIVO'
            else:
                if (senses >= 0.4 and senses < 0.6):
                    sentimiento = 'NEUTRAL'
                else:
                    if (senses >= 0.6):
                        sentimiento = 'POSITIVO'
            
            print ("Sentimiento final ES: " + sentimiento)

        else:
            sid = SentimentIntensityAnalyzer()
            senses = sid.polarity_scores(text)['compound']
            print("Sentimiento EN: " + str(senses))

            nlp = spacy.load("en_core_web_md")
            print("Lenguaje seleccionado otro: en_core_web_md ")
            doc = nlp(text)

            #Esta libreria devuelve valores cerca del -1 como negativos, cerca de 0 como neutrales y cerca del 1 como positivos
            sentimiento = 0.5
            if (senses >= -1 and senses < -0.4):
                sentimiento = 'NEGATIVO'
            else:
                if (senses >= -0.4 and senses < 0.4):
                    sentimiento = 'NEUTRAL'
                else:
                    if (senses >= 0.4):
                        sentimiento = 'POSITIVO'

            print ("Sentimiento final EN: " + str(sentimiento))

        opt = ''
        print ("taskoption: " + taskoption)
        if  taskoption == "":
            opt = ""
        else:
            if  taskoption == "organization":
                opt = "ORG"
            else:
                if  taskoption == "person":
                    opt = "PER"
                else:
                    if  taskoption == "location":
                        opt = "LOC"
                    else:
                        if taskoption == "nounproper":
                           opt = "NNP"
                        else:
                            if  taskoption == "miscellane":
                                opt = "MISC" 

        entidades = []
        
        print ("opt: " + opt)
        if opt == '':
            for ent in doc.ents:
                entidades.append(ent.text + ' - ' + ent.label_)
        else:
            for ent in doc.ents:
                if ent.label_ == opt:
                    entidades.append(ent.text + ' - ' + ent.label_)

    print ('Valor de entidades: ' )
    for i in entidades:
        print ('valor entidades: ' + i)

    return render_template('index.html', results=entidades, polaridad=senses, calcsenti=sentimiento)
    #return render_template('index.html', results=entidades)

if __name__ == '__main__':
    app.run(debug = True)