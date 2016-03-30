###################################################################################################################
## Risanje grafa
#
# Program narisi_graf_5_2.py naredi datoteko graf_5_2.dot, ki predstavlja graf vseh možnih potez in pozicij v igri.
# 
# POZOR! Datoteka graf_5_2.dot se odpira približno 30 minut.
#
###################################################################################################################


def najdi_vozlisca(stevilo_potez, roke=2, prsti=5):
    '''Funkcija vrne množico vozlišč, ketere elementi so trojice (trenutno_vozlisce, igralec, novo_vozlisce).'''
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
    return mnozica_vozlisc
    
def delitev_prvega(seznam_vozlisc, prsti=5, roke=2):
	''' Funkcija vrne seznam parov, kjer prva komponenta predstavlja vozlišče pred opravljeno delitvijo, druga pa vozlišče po delitvi. Velja za prvega igralca. '''
	seznam_novih = []
	for ((L,D),(l,d)) in seznam_vozlisc:
		staro_vozlisce = ((L,D),(l,d))
		if (L == 0 and D == 0): pass
		elif (L == 0 and D%roke == 0):
			novo_vozlisce = ((D//roke,D//roke),(l,d))
			seznam_novih.append((staro_vozlisce,novo_vozlisce))
		elif (D == 0 and L%roke == 0):
			novo_vozlisce = ((L//roke,L//roke),(l,d))
			seznam_novih.append((staro_vozlisce,novo_vozlisce))
	return(seznam_novih)
	
def delitev_drugega(seznam_vozlisc, prsti=5, roke=2):
	''' Funkcija vrne seznam parov, kjer prva komponenta predstavlja vozlišče pred opravljeno delitvijo, druga pa vozlišče po delitvi. Velja za drugega igralca.'''
	seznam_novih = []
	for ((L,D),(l,d)) in seznam_vozlisc:
		staro_vozlisce = ((L,D),(l,d))
		if (L == 0 and D == 0): pass
		elif (l == 0 and d%roke == 0):
			novo_vozlisce = ((L,D),(d//roke,d//roke))
			seznam_novih.append((staro_vozlisce,novo_vozlisce))
		elif (d == 0 and l%roke == 0):
			novo_vozlisce = ((L,D),(l//roke,l//roke))
			seznam_novih.append((staro_vozlisce,novo_vozlisce))
	return(seznam_novih)
	
def poteza_prvega_z_delitvijo(seznam_vozlisc, prsti=5):
	''' Funkcija vrne seznam vseh potencialnih vozlišč, ki nastanejo po opravljeni potezi prvega igralca in množico vseh potencialnih potez, katere elementi so trojice (trenutno_vozlisce, igralec, novo_vozlisce). '''
	mnozica_potez = set()
	seznam_novih = []
	for ((L,D),(l,d)) in seznam_vozlisc:
		novo_vozlisce = None
		### CE NI DELITVE:
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
		### CE JE DELITEV:
		for (staro,novo) in delitev_prvega(seznam_vozlisc):
			((L,D),(l,d)) = staro
			((A,B),(l,d)) = novo
			if l != 0:
				novo_vozlisce_1 = ((A,B),(min((l+A)%prsti,d),max((l+A)%prsti,d)))
				if novo_vozlisce_1 not in seznam_novih: seznam_novih.append(novo_vozlisce_1)
				mnozica_potez.add((((L,D),(l,d)),1,novo_vozlisce_1))
			if d != 0:
				novo_vozlisce_2 = ((A,B),(min(l,(d+A)%prsti),max(l,(d+A)%prsti)))
				if novo_vozlisce_2 not in seznam_novih: seznam_novih.append(novo_vozlisce_2)
				mnozica_potez.add((((L,D),(l,d)),1,novo_vozlisce_2))
	return(seznam_novih, mnozica_potez)
	
def poteza_drugega_z_delitvijo(seznam_vozlisc, prsti=5):
	''' Funkcija vrne seznam vseh potencialnih vozlišč, ki nastanejo po opravljeni potezi drugega igralca in množico vseh potencialnih potez, katere elementi so trojice (trenutno_vozlisce, igralec, novo_vozlisce). '''
	mnozica_potez = set()
	seznam_novih = []
	for ((L,D),(l,d)) in seznam_vozlisc:
		novo_vozlisce = None
		### CE NI DELITVE:
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
		### CE JE DELITEV:
		for (staro,novo) in delitev_drugega(seznam_vozlisc):
			((L,D),(l,d)) = staro
			((L,D),(a,b)) = novo
			if L != 0:
				novo_vozlisce_1 = ((min((L+a)%prsti,D),max((L+a)%prsti,D)),(a,b))
				if novo_vozlisce_1 not in seznam_novih: seznam_novih.append(novo_vozlisce_1)
				mnozica_potez.add((((L,D),(l,d)),2,novo_vozlisce_1))
			if D != 0:
				novo_vozlisce_2 = ((min(L,(D+a)%prsti),max(L,(D+a)%prsti)),(a,b))
				if novo_vozlisce_2 not in seznam_novih: seznam_novih.append(novo_vozlisce_2)
				mnozica_potez.add((((L,D),(l,d)),2,novo_vozlisce_2))
	return(seznam_novih, mnozica_potez)
	
zacetek = najdi_vozlisca(2) # NE ZBRISI!!
	
def vrni_mnozico_potez(mnozica=set(), seznam_zacetnih=[((1,1),(1,1))], k=0):
	''' Mnozica vseh potez (trojic), ki jih lahko opravimo v igri. '''
	k += 1
	if k > 10:
		return mnozica.union(zacetek)
	else:
		return vrni_mnozico_potez((poteza_prvega_z_delitvijo(seznam_zacetnih))[1].union(poteza_drugega_z_delitvijo((poteza_prvega_z_delitvijo(seznam_zacetnih))[0])[1]),(poteza_drugega_z_delitvijo((poteza_prvega_z_delitvijo(seznam_zacetnih))[0]))[0], k)

def naredi_dot(roke=2, prsti=5):
	''' Funkcija vse trojice iz vrni_mnozico_potez zapise v datoteko graf_5_2.dot. '''
	try: os.remove("graf_5_2.dot")
	except: pass
	izhod = open("graf_5_2.dot", "w")
	izhod.write("digraph {\n       node [style = filled];\n")
	for (((L,D),(l,d)), poteza, ((A,B),(a,b))) in vrni_mnozico_potez():
		if ((L,D),(l,d)) == ((A,B),(a,b)): pass
		else:
			izhod.write("       \""+str(L)+","+str(D)+"  "+str(l)+","+str(d)+"\" -> \""+str(A)+","+str(B)+"  "+str(a)+","+str(b)+"\" [label ="+str(poteza)+"];\n")
			if (A,B) == (0,0) or (a,b) == (0,0):
				izhod.write("       \""+str(A)+","+str(B)+"  "+str(a)+","+str(b)+"\" [color=coral];\n")
			if (L,D) == (1,1) and (l,d) == (1,1):
				izhod.write("       \""+str(L)+","+str(D)+"  "+str(l)+","+str(d)+"\" [color=darkseagreen];\n")
	izhod.write("   }")

naredi_dot()
