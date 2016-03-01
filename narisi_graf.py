def najdi_vozlisca(stevilo_potez, roke=2, prsti=5):
    '''Program vrne množico vozlišč, ketere elementi so trojice (trenutno_vozlisce, igralec, novo_vozlisce).'''
    mnozica_vozlisc = set()
    novi = [((1,1),(1,1))] 
    prvi_na_vrsti = True
    for poteza in range(stevilo_potez):
        if prvi_na_vrsti == True:
            for ((L,D),(l,d)) in novi:
                seznam = []
                # Udari z levo:
                if L != 0:
                    if l != 0: seznam.append(((L,D),(min((l+L)%prsti,d),max((l+L)%prsti,d))))
                    if d != 0: seznam.append(((L,D),(min(l,(d+L)%prsti),max(l,(d+L)%prsti))))
                # Udari z desno:
                if D != 0:
                    if l != 0: seznam.append(((L,D),(min((l+D)%prsti,d),max((l+D)%prsti,d))))
                    if d != 0: seznam.append(((L,D),(min(l,(d+D)%prsti),max(l,(d+D)%prsti))))
                for element in seznam:
                    mnozica_vozlisc.add((((L,D),(l,d)),1,element))
            prvi_na_vrsti = False
            novi = seznam
            #print(novi)
        else:
            for ((L,D),(l,d)) in novi:
                seznam = []
                # Udari z levo:
                if l != 0:
                    if L != 0: seznam.append(((min((L+l)%prsti,D),max((L+l)%prsti,D)),(l,d)))
                    if D != 0: seznam.append(((min(L,(D+l)%prsti),max(L,(D+l)%prsti)),(l,d)))
                # Udari z desno:
                if d != 0:
                    if L != 0: seznam.append(((min((L+d)%prsti,D),max((L+d)%prsti,D)),(l,d)))
                    if D != 0: seznam.append(((min(L,(D+d)%prsti),max(L,(D+d)%prsti)),(l,d)))
                for element in seznam:
                    mnozica_vozlisc.add((((L,D),(l,d)),2,element))
            prvi_na_vrsti = True
            novi = seznam
            #print(novi)
    #print(mnozica_vozlisc)
    return mnozica_vozlisc



def naredi_dot_sp(stevilo_potez, roke=2, prsti=5):
    try: os.remove("narisi_graf_sp.dot")
    except: pass
    izhod = open("narisi_graf_sp.dot", "w")
    izhod.write("digraph {\n")
    for (((L,D),(l,d)), poteza, ((A,B),(a,b))) in najdi_vozlisca(stevilo_potez, roke, prsti):
        if (A,B) == (0,0) or (a,b) == (0,0):
            izhod.write("       \""+str(L)+","+str(D)+"  "+str(l)+","+str(d)+"\" -> \""+str(A)+","+str(B)+"  "+str(a)+","+str(b)+"\" [label ="+str(poteza)+", color=coral3];\n")
        else: izhod.write("       \""+str(L)+","+str(D)+"  "+str(l)+","+str(d)+"\" -> \""+str(A)+","+str(B)+"  "+str(a)+","+str(b)+"\" [label ="+str(poteza)+"];\n")
    izhod.write("   }")
 
 
 
 
#najdi_vozlisca(4)
naredi_dot_sp(4)


def poteza_prvega(seznam_vozlisc, prsti=5):
	mnozica_potez = set()
	seznam_novih = []
	konec = 0
	for ((L,D),(l,d)) in seznam_vozlisc:
		novo_vozlisce = None
		# Udari z levo:
		if L != 0:
			if l != 0:
				novo_vozlisce_1 = ((L,D),(min((l+L)%prsti,d),max((l+L)%prsti,d)))
				if novo_vozlisce_1 not in seznam_novih: seznam_novih.append(novo_vozlisce_1)
				mnozica_potez.add((((L,D),(l,d)),1,novo_vozlisce_1))
			if d != 0:
				novo_vozlisce_2 = ((L,D),(min(l,(d+L)%prsti),max(l,(d+L)%prsti)))
				if novo_vozlisce_2 not in seznam_novih: seznam_novih.append(novo_vozlisce_2)
				mnozica_potez.add((((L,D),(l,d)),1,novo_vozlisce_2))
			else: konec += 1
		# Udari z desno:
		if D != 0:
			if l != 0:
				novo_vozlisce_3 = ((L,D),(min((l+D)%prsti,d),max((l+D)%prsti,d)))
				if novo_vozlisce_3 not in seznam_novih: seznam_novih.append(novo_vozlisce_3)
				mnozica_potez.add((((L,D),(l,d)),1,novo_vozlisce_3))
			if d != 0: 
				novo_vozlisce_4 = ((L,D),(min(l,(d+D)%prsti),max(l,(d+D)%prsti)))
				if novo_vozlisce_4 not in seznam_novih: seznam_novih.append(novo_vozlisce_4)
				mnozica_potez.add((((L,D),(l,d)),1,novo_vozlisce_4))
			else: konec += 1
	#print(len(seznam_novih))
	#print(mnozica_potez)
	if konec != 2: return(seznam_novih, mnozica_potez)
	else: return([], mnozica_potez)
	
def poteza_drugega(seznam_vozlisc, prsti=5):
	mnozica_potez = set()
	seznam_novih = []
	konec = 0
	for ((L,D),(l,d)) in seznam_vozlisc:
		novo_vozlisce = None
		# Udari z levo:
		if l != 0:
			if L != 0:
				novo_vozlisce_1 = ((min((L+l)%prsti,D),max((L+l)%prsti,D)),(l,d))
				if novo_vozlisce_1 not in seznam_novih: seznam_novih.append(novo_vozlisce_1)
				mnozica_potez.add((((L,D),(l,d)),2,novo_vozlisce_1))
			if D != 0:
				novo_vozlisce_2 = ((min(L,(D+l)%prsti),max(L,(D+l)%prsti)),(l,d))
				if novo_vozlisce_2 not in seznam_novih: seznam_novih.append(novo_vozlisce_2)
				mnozica_potez.add((((L,D),(l,d)),2,novo_vozlisce_2))
			else: konec += 1
		# Udari z desno:
		if d != 0:
			if L != 0:
				novo_vozlisce_3 = ((min((L+d)%prsti,D),max((L+d)%prsti,D)),(l,d))
				if novo_vozlisce_3 not in seznam_novih: seznam_novih.append(novo_vozlisce_3)
				mnozica_potez.add((((L,D),(l,d)),2,novo_vozlisce_3))
			if D != 0:
				novo_vozlisce_4 = ((min(L,(D+d)%prsti),max(L,(D+d)%prsti)),(l,d))
				if novo_vozlisce_4 not in seznam_novih: seznam_novih.append(novo_vozlisce_4)
				mnozica_potez.add((((L,D),(l,d)),2,novo_vozlisce_4))
			else: konec += 1
	#print(len(seznam_novih))
	#print(mnozica_potez)
	if konec != 2: return(seznam_novih, mnozica_potez)
	else: return([], mnozica_potez)
	
zacetek = najdi_vozlisca(2)
	
def vrni_mnozico_potez(mnozica=set(), seznam_zacetnih=[((1,1),(1,1))], k=0):
	k += 1
	if k > 10:
		print(mnozica)
		return mnozica.union(zacetek)
	else: return vrni_mnozico_potez((poteza_prvega(seznam_zacetnih))[1].union(poteza_drugega((poteza_prvega(seznam_zacetnih))[0])[1]),(poteza_drugega((poteza_prvega(seznam_zacetnih))[0]))[0], k)
	
#poteza_prvega([((1,3),(1,2)),((1,2),(1,2))])
#poteza_drugega([((1,1),(1,2))])
#vrni_mnozico_potez(set())

def naredi_dot(roke=2, prsti=5):
	try: os.remove("narisi_graf.dot")
	except: pass
	izhod = open("narisi_graf.dot", "w")
	izhod.write("digraph {\n")
	for (((L,D),(l,d)), poteza, ((A,B),(a,b))) in vrni_mnozico_potez():
		izhod.write("       \""+str(L)+","+str(D)+"  "+str(l)+","+str(d)+"\" -> \""+str(A)+","+str(B)+"  "+str(a)+","+str(b)+"\" [label ="+str(poteza)+"];\n")
		if (A,B) == (0,0) or (a,b) == (0,0):
			izhod.write("       \""+str(A)+","+str(B)+"  "+str(a)+","+str(b)+"\" [color=blue];\n")
		if (A,B) == (1,1) and (a,b) == (1,1):
			izhod.write("       \""+str(A)+","+str(B)+"  "+str(a)+","+str(b)+"\" [color=red];\n")
	izhod.write("   }")
    
naredi_dot()

def naredi_dot_poskus(roke=2, prsti=5):
    try: os.remove("narisi_graf_poskus.dot")
    except: pass
    izhod = open("narisi_graf_poskus.dot", "w")
    izhod.write("digraph {\n       node [style = filled];\n")
    for (((L,D),(l,d)), poteza, ((A,B),(a,b))) in vrni_mnozico_potez_poskus():
        izhod.write("       \""+str(L)+","+str(D)+"  "+str(l)+","+str(d)+"\" -> \""+str(A)+","+str(B)+"  "+str(a)+","+str(b)+"\" [label ="+str(poteza)+"];\n")
        if (A,B) == (0,0) or (a,b) == (0,0):
        	izhod.write("       \""+str(A)+","+str(B)+"  "+str(a)+","+str(b)+"\" [color=blue];\n")
    izhod.write("   }")
    
def vrni_mnozico_potez_poskus(mnozica=set(), seznam_zacetnih=[((1,1),(1,1))], k=0):
	k += 1
	if k > 3:
		print(mnozica)
		return mnozica.union(zacetek)
	else: return vrni_mnozico_potez_poskus((poteza_prvega(seznam_zacetnih))[1].union(poteza_drugega((poteza_prvega(seznam_zacetnih))[0])[1]),(poteza_drugega((poteza_prvega(seznam_zacetnih))[0]))[0], k)
    
naredi_dot_poskus()
