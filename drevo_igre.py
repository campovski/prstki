import re
import igra
x = igra.Igra(5,2)
mnozica_potez = set()

#### POPRAVI: narisi_drevo(4)??

def narisi_drevo(globina, prsti, roke, visina=0):
	""" Funkcija, ki nariše drevo igre za igralca s poljubnim številom rok in prstov. V drevesu so predstavljene vse možne poteze na vsakem koraku. """
	zacetno_vozlisce = ""
	igralec_na_potezi = str(x.na_potezi)
	for j, igralec in enumerate(x.position):
		# Zapiši zacetno_vozlisce v string
		for i, roka in enumerate(igralec):
			if i < len(igralec)-1:
				zacetno_vozlisce += str(roka) + ","
			elif j == 0:
				zacetno_vozlisce += str(roka) + "  "
			else:
				zacetno_vozlisce += str(roka)
	for elt in x.veljavne_poteze():
		if elt[0]:
			x.opravi_delitev()
			x.opravi_potezo(elt[1],elt[2])
			koncno_vozlisce = ""
			for j, igralec in enumerate(x.position):
				# Zapiši koncno_vozlisce v string
				for i, roka in enumerate(igralec):
					if i < len(igralec)-1:
						koncno_vozlisce += str(roka) + ","
					elif j == 0:
						koncno_vozlisce += str(roka) + "  "
					else:
						koncno_vozlisce += str(roka)
			mnozica_potez.add((str(visina), str(visina+1), igralec_na_potezi, zacetno_vozlisce, koncno_vozlisce))
			x.razveljavi_potezo()
		else:
			print("Bedno")
			x.opravi_potezo(elt[1],elt[2])
			koncno_vozlisce = ""
			for j, igralec in enumerate(x.position):
				print(x.position)
				# Zapiši koncno_vozlisce v string
				for i, roka in enumerate(igralec):
					if i < len(igralec)-1:
						koncno_vozlisce += str(roka) + ","
					elif j == 0:
						koncno_vozlisce += str(roka) + "  "
					else:
						koncno_vozlisce += str(roka)
			mnozica_potez.add((str(visina), str(visina+1), igralec_na_potezi, zacetno_vozlisce, koncno_vozlisce))
			x.razveljavi_potezo()
	if globina > 0:
		for elt in x.veljavne_poteze():
			if elt[0]:
				x.opravi_delitev()
				x.opravi_potezo(elt[1],elt[2])
				if x.je_konec(): pass
				else:
					narisi_drevo(globina-1, prsti, roke, visina+1)
				x.razveljavi_potezo()
			else:
				print("Blabla")
				x.opravi_potezo(elt[1],elt[2])
				if x.je_konec(): pass
				else:
					print("Ne dela!")
					narisi_drevo(globina-1, prsti, roke, visina+1)
				x.razveljavi_potezo()	
				

def naredi_dot_drevo(globina, prsti=5, roke=2):
	''' Funkcija elemente množice mnozica_potez zapiše v datoteko drevo_igre.dot. '''
	try: os.remove("drevo_igre.dot")
	except: pass
	narisi_drevo(globina, prsti, roke)
	izhod = open("drevo_igre.dot", "w")
	izhod.write("digraph {\n       node [style = filled];\n")
	konec1 = re.compile('0,0  \d,\d')
	konec2 = re.compile('\d,\d  0,0')
	for (visina, visina2, igralec_na_potezi, zacetno_vozlisce, koncno_vozlisce) in mnozica_potez:
		izhod.write("       \"" + "#" + visina + "  " + zacetno_vozlisce + "\" -> \"" + "#" + visina2 + "  " + koncno_vozlisce + "\" [label ="+igralec_na_potezi+"];\n")
		if konec1.match(koncno_vozlisce) or konec2.match(koncno_vozlisce):
			izhod.write("       \"#" + visina2 + "  " + koncno_vozlisce + "\" [color=coral];\n")
	izhod.write("   }")

x.opravi_potezo(0,0)
x.opravi_potezo(0,0)
x.opravi_potezo(0,0)
x.opravi_potezo(1,0)
x.opravi_potezo(1,1)
naredi_dot_drevo(1)
