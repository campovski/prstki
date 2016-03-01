##################################################################################
## Igra
#
# V igra.py je implementirano vse, kar je potrebno za igro in uporabniški vmesnik.
#
##################################################################################


# Definiramo konstante, s katerimi bomo dostopali do podatkov o prvem in drugem
# igralcu, ki bodo shranjene v arrayu, zato torej 0 in 1.
IGRALEC_1 = 0
IGRALEC_2 = 1

def nasprotnik(igralec):
	"""Funkcija, ki vrne nasprotnika od igralca, ki je trenutno na potezi."""
	
	return (1 - igralec)

class Igra():
	"""Razred, ki skrbi za vsa pravila igre Prstki."""
	
	def __init__(self, prsti, roke, master=None):
		# Število rok in maksimalno število prstov na eni roki
		self.roke = roke
		self.prsti = prsti	
		
		# self.position je tabela, ki hrani trenutno pozicijo.
		# Inicializiramo jo s seznami enic, kjer seznam predstavlja
		# posameznega igralca.
		self.position = [[1 for _ in range(self.roke)], [1 for _ in range(self.roke)]]
		
		# Igro seveda začne prvi igralec
		self.na_potezi = IGRALEC_1
		
		# Zgodovina nam bo služila za UNDO in pravilo o remiju
		self.history = []
		
	def shrani_pozicijo(self):
		"""Metoda shrani potezo v zgodovino."""
		
		# Kot je prof. Bauer odlično pripomnil, je treba seznam prepisati.
		pozicija = [self.position[i][:] for i in range(2)]
		self.history.append((pozicija, self.na_potezi))
		
	def razveljavi_potezo(self):
		"""Metoda, ki razveljavi zadnjo potezo."""
		
		(self.position, self.na_potezi) = self.history.pop()
		
	def je_veljavna_poteza(self, roka_napadalca, roka_nasprotnika):
		"""Preveri, ali morda igralec ne napada s prazno roko in ali
		morda ne napada prazne roke."""
		
		return self.position[self.na_potezi][roka_napadalca] != 0 and self.position[nasprotnik(self.na_potezi)][roka_nasprotnika] != 0
		
	def je_veljavna_delitev(self):
		"""Preveri, ali je možna delitev."""
		
		preostale_roke = 0
		self.moznost_delitve = False
		for roka in self.position[self.na_potezi]:
			if roka != 0:
				preostale_roke += 1
				stevilo_prstov = roka
		
		# Preverimo, ali nam je preostala le ena roka in če je na
		# preostali roki prstov za večkratnik rok	
		if preostale_roke == 1 and stevilo_prstov % self.roke == 0:
			self.moznost_delitve = True
			self.prsti_po_delitvi = stevilo_prstov // self.roke
		
	def veljavne_poteze(self):
		"""Poiščemo VSE veljavne poteze, kar bo v pomoč razredu Racunalnik(),
		pa tudi nam. Poteza je trojica elementov, kjer prvi vhod pove,
		ali je bila opravljena delitev, drugi zaporedno številko roke, s katero
		je igralec napadel, tretji pa številko napadene roke."""
		
		# Odločimo se za eno implementacijo, torej z množico oziroma seznamom,
		# bomo videli, kaj pride bolj prav (množica: lažje preveriti, ali je
		# poteza med dovoljenimi - if poteza in poteze:...; seznam: lažje dostopati
		# do točno določenih elementov, razporejeni so v nekem redu)
		poteze = set()
		poteze_arr = []
		
		# Dodamo poteze brez delitve
		for roka_napadalca in range(self.roke):
			for roka_napadenega in range(self.roke):
				if self.je_veljavna_poteza(roka_napadalca, roka_napadenega):
					poteze.add((False, roka_napadalca, roka_napadenega))
					poteze_arr.append((False, roka_napadalca, roka_napadenega))
				
		# Če je možna delitev, dodamo še vse poteze z delitvijo. Seveda so to
		# vse možne kombinacije, zato preverjanje, ali je poteza veljavna, ni
		# potrebno, oziroma je celo napačno.
		self.je_veljavna_delitev()
		if self.moznost_delitve:
			for roka_napadalca in range(self.roke):
				for roka_napadenega in range(self.roke):
					poteze.add((True, roka_napadalca, roka_napadenega))
					poteze_arr.append((True, roka_napadalca, roka_napadenega))
		return poteze_arr
						
	def opravi_delitev(self):
		"""Metoda opravi delitev. Preverjanje, ali je delitev možna ali ne,
		je potrebno narediti pred klicem same metode!"""
		
		self.je_veljavna_delitev()
		if self.moznost_delitve:	
			# Shranimo pozicijo, če bi si slučajno premislili o delitvi
			self.shrani_pozicijo()
		
			# Opravimo delitev
			self.position[self.na_potezi] = [self.prsti_po_delitvi for _ in range(self.roke)]
		
	def opravi_potezo(self, roka_napadalca, roka_napadenega):
		"""Metoda shrani trenutno pozicijo in opravi potezo."""
	
		if self.je_veljavna_poteza(roka_napadalca, roka_napadenega):
			self.shrani_pozicijo()
			self.position[nasprotnik(self.na_potezi)][roka_napadenega] = (self.position[nasprotnik(self.na_potezi)][roka_napadenega] + self.position[self.na_potezi][roka_napadalca]) % self.prsti
			self.na_potezi = nasprotnik(self.na_potezi)
			
	def je_konec(self):
		"""Preveri, ali je morda konec igre, torej, če ima igralec na potezi prazne roke."""
		
		return self.position[self.na_potezi] == [0 for _ in range(self.roke)]
		
	
	
###################################################################################################
#
# PRIMER IGRE
#
###################################################################################################

if __name__ == "__main__":	
	game = Igra(5,2)
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	game.opravi_potezo(0, 0)
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	game.opravi_potezo(0, 0)
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	game.opravi_potezo(0, 0)
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	game.opravi_potezo(1, 0)
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	game.opravi_potezo(1, 1)
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	game.opravi_delitev()
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	game.razveljavi_potezo()
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	game.razveljavi_potezo()
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	game.opravi_potezo(0, 1)
	print(game.position)
	print(game.na_potezi)
	print(game.veljavne_poteze())
	print(game.je_konec())
	
