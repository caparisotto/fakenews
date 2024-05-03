from django.shortcuts import render
from .forms import *
import re
from googlesearch import search
from htmldate import find_date
from datetime import date
from threading import Thread
import time

# Create your views here.

def submeter(request):
    if request.method ==  "POST":
        form = FormFrase(request.POST, request.FILES)
        if form.is_valid():
            pontuacao = 0
            itens = []
            urls = []
            frase = form.cleaned_data['texto']

            countinter=0
            countexcl=0
            for z in frase:
                if z == '!':
                    countexcl+=1
                if z == '?':
                    countinter+=1

            if countinter > 10 or countexcl > 10:
                pontuacao+=2
                itens.append(["Mais do que 10 ? ou !. Expressões muito enfáticas podem ser um indicativo de fake news","text-bg-warning"])
            elif countinter > 5 or countexcl > 5:
                pontuacao+=1
                itens.append(["Mais do que 5 ? ou !. Expressões muito enfáticas podem ser um indicativo de fake news","text-bg-warning"])

            #Expressão de enfase
            if '!!!' in frase or '!?!?' in frase:
                pontuacao+=1
                itens.append(["Contém expressões muito enfáticas(!!! ou !?!?) podem ser um indicativo de fake news","text-bg-warning"])

            #Palavras indicativas
            words = ['não vai acreditar','est.+escondendo','ompartilh.+antes','quer.+censurar','vão censurar', 'vai censurar']
            sumwords=0
            for x in words:
                reg = re.compile(x)
                if re.search(reg, frase.lower()):
                    sumwords+=1
            if sumwords == 1:
                pontuacao+=1
                itens.append(["No texto há expressão sensacionalista normalmente encontrada em fake news(ex.: 'compartilhe antes que apaguem' ou 'querem nos censurar)'.","text-bg-secondary"])
            elif sumwords == 2:
                pontuacao+=2
                itens.append(["No texto há mais de uma expressão sensacionalista normalmente encontradas em fake news(ex.: 'compartilhe antes que apaguem' ou 'querem nos censurar)'.","text-bg-warning"])
            elif sumwords > 2:
                pontuacao+=5
                itens.append(["No texto há diversas expressões sensacionalistas encontradas em fake news(ex.: 'compartilhe antes que apaguem' ou 'querem nos censurar').","text-bg-danger"])

            #Palavras ideológicas
            words = ['petista','bolsonarista','extrema direita','extrema esquerda','direitista', 'esquerdista']
            sumwords=0
            for x in words:
                reg = re.compile(x)
                if re.search(reg, frase.lower()):
                    sumwords+=1
            if sumwords == 1 or sumwords == 2:
                pontuacao+=1
                itens.append(["No texto há algumas expressões que rotulam posições políticas(esquerdista, direitista). Textos com apelo político podem conter sensacionalismo..","text-bg-secondary"])
            elif sumwords > 2:
                pontuacao+=1
                itens.append(["No texto há várias expressões que rotulam posições políticas(esquerdista, direitista). Textos com apelo político podem conter sensacionalismo..","text-bg-warning"])


            #CAPS
            alph = list(filter(str.isalpha, frase)) 
            valorupper = sum(map(str.isupper, alph)) / len(alph)
            if frase.isupper():
                pontuacao+=2
                itens.append(["Texto todo em maiúscula. Esse recurso normalmente é usado em mensagens apelativas.","text-bg-warning"])
            elif (valorupper >= 0.1):
                pontuacao+=1
                itens.append(["Mais de 10% do texto em maiúscula. Esse recurso normalmente é usado em mensagens apelativas.","text-bg-secondary"])
            else:
                pontuacao-=1
                if (not '!!!' in frase or not '!?!?' in frase) and countinter < 3 and countexcl < 3:
                    itens.append(["Texto sem muitas maiúsculas e caracteres chamativos.","text-bg-success"])


            #Indicações falacia
            words = ['se.+não.+revoltar','se.+não.+agir','ou.+reagimos','ou.+nos.+revoltamos.+','na hora de responder']
            sumwords=0
            for x in words:
                reg = re.compile(x)
                if re.search(reg, frase.lower()):
                    sumwords+=1
            if sumwords == 1:
                pontuacao+=2
                itens.append(["Foi utilizada a falácia do falso dilema(ex.: se não nos revoltarmos agora).","text-bg-secondary"])
            if sumwords > 1:
                pontuacao+=3
                itens.append(["Foi utilizada a falácia do falso dilema(ex.: se não nos revoltarmos agora) mais do que uma vez.","text-bg-danger"])
            
            #Indicações 
            words = ['ouvi dizer','ouvi falar','me disseram']
            sumwords=0
            for x in words:
                reg = re.compile(x)
                if re.search(reg, frase.lower()):
                    sumwords=1
            if sumwords > 0:
                pontuacao+=2
                itens.append(["Cuidado com expressões que tiram a responsabilidade do locutor( ex.: 'ouvi dizer que', 'me disseram que' )","text-bg-warning"])


            words = ['boato','fake','desment','nao.+verdade','falso','falsa', 'farsa']
            trustedwords = ['cnn.com', 'guardian.com', 'economist.com', 'bbc.com', 'apnews.com', 'reuters.com', 'npr.org', 'pbs.org', 'globo.com', 'uol.com', 'r7.com', 'cnnbrasil.com', 'abril.com', 'estadao.com' ]
            social = ['youtube.com','facebook.com','twitter.com','x.com']
            sumwords=0
            sumtrusted=0
            sumsocial=0
            sumoldd=0
            dataatu=date.today()
            anoatu=int(str(dataatu).split('-')[0])
            mesatu=int(str(dataatu).split('-')[1])
            diaatu=int(str(dataatu).split('-')[2])

            foundword=0
            foundtrust=0
            foundsocial=0

            for j in search(frase, tld="co.in", num=10, stop=10, pause=2):
                t = Thread(target=find_date, args=(j,))
                t.start()
                time.sleep(1)
                #comando normalmente é imediato, se demorar mais de 2 segundos, ignorar, pra não deixar lenta a aplicação
                if t.is_alive():
                    datalink=None
                else:
                    try:
                        datalink=find_date(j)
                        if datalink:
                            anolk=int(datalink.split('-')[0])
                            meslk=int(datalink.split('-')[1])
                            dialk=int(datalink.split('-')[2])
                            difdias=((anoatu-anolk)*365)+((mesatu-meslk)*30)+(diaatu-dialk)
                        if difdias >= 365:
                            sumoldd+=1
                    except:
                        datalink=None

                urls.append([j,datalink])
                for x in words:
                    reg = re.compile(x)
                    if re.search(reg, j.lower()):
                        foundword=1
                for x in trustedwords:
                    reg = re.compile(x)
                    if re.search(reg, j.lower()):
                        foundtrust=1
                for x in social:
                    reg = re.compile(x)
                    if re.search(reg, j.lower()):
                        foundsocial=1

                #se for rede social ignora outros fatores
                if foundsocial==1:
                    sumsocial+=1
                elif foundword==1:
                    sumwords+=1
                #antes foi testado se tem as palavras, porque caso tenha uma fonte confiavel com a palavra farsa ou boato, é indicativo de boato
                elif foundtrust==1:
                    sumtrusted+=1


            if sumwords == 1:
                pontuacao+=1
                itens.append(["Nos 10 principais sites com esse texto, encontrada uma URL associada a boatos ou fake news com essa notícia","text-bg-warning"])
            elif sumwords == 2:
                pontuacao+=2
                itens.append(["Nos 10 principais sites com esse texto, encontradas duas URLs associada a boatos ou fake news com essa notícia","text-bg-warning"])
            elif sumwords == 3:
                pontuacao+=3
                itens.append(["Nos 10 principais sites com esse texto, encontradas tres URLs associada a boatos ou fake news com essa notícia","text-bg-danger"])
            elif sumwords > 3:
                pontuacao+=5
                itens.append(["Nos 10 principais sites com esse texto, encontradas varias URLs associada a boatos ou fake news com essa notícia","text-bg-danger"])

            if sumtrusted == 1:
                pontuacao-=1
                itens.append(["Nos 10 principais sites com esse texto, encontrada uma URL de site confiável(não avaliamos ideologia, mas sim a confiabilidade dos fatos de acordo com fontes) associada a essa notícia","text-bg-secondary"])
            elif sumtrusted == 2:
                pontuacao-=1
                itens.append(["Nos 10 principais sites com esse texto, encontradas duas URLs de site confiável(não avaliamos ideologia, mas sim a confiabilidade dos fatos de acordo com fontes) associada a essa notícia","text-bg-secondary"])
            elif sumtrusted == 3:
                pontuacao-=2
                itens.append(["Nos 10 principais sites com esse texto, encontradas tres URLs de site confiável(não avaliamos ideologia, mas sim a confiabilidade dos fatos de acordo com fontes) associada a essa notícia","text-bg-success"])
            elif sumtrusted > 3:
                pontuacao-=3
                itens.append(["Nos 10 principais sites com esse texto, encontradas varias URLs de site confiável(não avaliamos ideologia, mas sim a confiabilidade dos fatos de acordo com fontes) associada a essa notícia","text-bg-success"])

            if sumsocial == 0:
                pontuacao-=1
                itens.append(["Nos 10 principais sites com esse texto, não foi encontrada nenhum dos principais sites de redes sociais associados a essa notícia.","text-bg-success"])
            elif sumsocial <= 2:
                pontuacao+=1
                itens.append(["Nos 10 principais sites com esse texto, encontradas algumas URLs que são links de redes sociais. Apesar de não haver indício de fake news, redes sociais não são uma fonte confiável de informação. ","text-bg-secondary"])
            elif sumsocial > 2:
                pontuacao+=2
                itens.append(["Nos 10 principais sites com esse texto, encontradas mais de tres URLs que são links de redes sociais. Apesar de não haver indício de fake news, redes sociais não são uma fonte confiável de informação.","text-bg-danger"])

            if sumoldd == 1 or sumoldd == 2:
                pontuacao+=1
                itens.append(["Nos 10 principais sites com esse texto, encontradas algumas URLs com mais de 1 ano. Não necessariamente é fake news, mas pode ser uma notícia antiga voltando a circular","text-bg-secondary"])
            elif sumoldd > 2:
                pontuacao+=2
                itens.append(["Nos 10 principais sites com esse texto, encontradas varias URLs com mais de 1 ano. Não necessariamente é fake news, mas pode ser uma notícia antiga voltando a circular","text-bg-warning"])

            if pontuacao <= 0:
                nivel=0
            elif pontuacao > 0 and pontuacao <= 3:
                nivel=1
            elif pontuacao > 3 and pontuacao <= 7:
                nivel=2
            elif pontuacao > 7 and pontuacao <= 10:
                nivel=3
            else:
                nivel=4

        #verificar fontes cnn, bbx
            if not itens:
                itens.append(["Nenhuma informação identificada","text-bg-primary"])

            context = {"pontuacao": pontuacao, "itens": itens, "urls": urls, "frase": frase, "nivel": nivel}
            return render(request, "resultado.html", context)
    else:
        form = FormFrase()
    return render(request, 'submeter.html', {'form': form})

