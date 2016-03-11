import igra

mnozica_potez = set()

def narisi_drevo(globina, prsti, roke, visina=0):
	""" Funkcija, ki nariše drevo igre za igralca, ki ima dve roki in na vsaki pet prstov. V drevesu so predstavljene vse možne poteze na vsakem koraku. """
	x = igra.Igra(prsti,roke)
	veljavne_poteze = x.veljavne_poteze()
	zacetno_vozlisce = ""
	igralec_na_potezi = str(x.na_potezi)
	for j, igralec in enumerate(x.position):
		for i, roka in enumerate(igralec):
			if i < len(igralec)-1:
				zacetno_vozlisce += str(roka) + ","
			elif j == 0:
				zacetno_vozlisce += str(roka) + "  "
			else:
				zacetno_vozlisce += str(roka)
	for elt in veljavne_poteze:
		x.opravi_potezo(elt[1],elt[2])
		globina -= 1
		visina += 1
		koncno_vozlisce = ""
		for j, igralec in enumerate(x.position):
				for i, roka in enumerate(igralec):
					if i < len(igralec)-1:
						koncno_vozlisce += str(roka) + ","
					elif j == 0:
						koncno_vozlisce += str(roka) + "  "
					else:
						koncno_vozlisce += str(roka)
		mnozica_potez.add((str(visina), igralec_na_potezi, zacetno_vozlisce, koncno_vozlisce))
		x.razveljavi_potezo()
		globina += 1
		visina -= 1
	if globina > 0:
		for elt in veljavne_poteze:
			x.opravi_potezo(elt[1],elt[2])
			globina -= 1
			visina += 1
			narisi_drevo(globina, prsti, roke, visina)
			globina += 1
			visina -= 1
			x.razveljavi_potezo()

def naredi_dot_drevo(globina, prsti=5, roke=2):
	''' Funkcija elemente množice mnozica_potez zapiše v datoteko drevo_igre.dot. '''
	try: os.remove("drevo_igre.dot")
	except: pass
	narisi_drevo(globina, prsti, roke)
	izhod = open("drevo_igre.dot", "w")
	izhod.write("digraph {\n       node [style = filled];\n")
	print(mnozica_potez)
	for (visina, igralec_na_potezi, zacetno_vozlisce, koncno_vozlisce) in mnozica_potez:
		izhod.write("       \"" + "#" + visina + "  " + zacetno_vozlisce + "\" -> \"" + koncno_vozlisce + "\" \n")
	izhod.write("   }")








naredi_dot_drevo(8)









