import tkinter as tk

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
		self.position_count = {}
		
	def shrani_pozicijo(self):
		"""Metoda shrani potezo v zgodovino."""
		
		# Kot je prof. Bauer odlično pripomnil, je treba seznam prepisati.
		pozicija = [self.position[i][:] for i in range(2)]
		self.history.append((pozicija, self.na_potezi))
		
		# Pozicijo dodamo še v slovar
		try:
			self.position_count[((tuple(pozicija[IGRALEC_1]), tuple(pozicija[IGRALEC_2])), self.na_potezi)] += 1
		except KeyError:
			self.position_count[((tuple(pozicija[IGRALEC_1]), tuple(pozicija[IGRALEC_2])), self.na_potezi)] = 1
		
	def razveljavi_potezo(self):
		"""Metoda, ki razveljavi zadnjo potezo."""
		
		(self.position, self.na_potezi) = self.history.pop()
		self.position_count[((tuple(self.position[IGRALEC_1]), tuple(self.position[IGRALEC_2])), self.na_potezi)] -= 1
		
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
			
	def zamenjaj_igralca_na_potezi(self):
		"""Zamenja igralca, ki je na potezi."""
		
		self.na_potezi = nasprotnik(self.na_potezi)
		
	def je_remi(self):
		"""Preveri, ali smo se morda znašli tretjič v isti poziciji.
		Preverimo, ali je bila pozicija že dvakrat zabeležena."""
		
		try:
			return self.position_count[((tuple(self.position[IGRALEC_1]), tuple(self.position[IGRALEC_2])), self.na_potezi)] == 2
		except KeyError:
			return False
			
	def je_konec(self):
		"""Preveri, ali je morda konec igre, torej, če ima igralec na potezi prazne roke."""
		
		return self.position[self.na_potezi] == [0 for _ in range(self.roke)]



##################################################################################################
#
# Razred Gui
#
# Skrbi za vse v zvezi z uporabniškim vmesnikom.
#
##################################################################################################

class Gui():
	def __init__(self, master):
		self.master = master
		menu = tk.Menu(self.master)
		self.master.config(menu=menu)
		
		menu_igra = tk.Menu(menu)
		menu.add_cascade(label="Igra", menu=menu_igra)
		menu_igra.add_command(label="Nova igre", command=self.izbira_igre)
		menu_igra.add_command(label="Pravila igre", command=self.pravila)
		menu_igra.add_separator()
		menu_igra.add_command(label="Izhod", command=self.master.destroy)
		
		self.izbira_igre()
		
	def izbira_igre(self):
		"""Uporabniku damo možnost, da se odloči za število rok in prstov
		ter način igre, torej npr. HUMAN vs HUMAN."""
		
		# Konstante za širino Entry-ja in Button-a
		WDTH_BUTTON = 20
		WDTH_ENTRY = 5
		
		self.new_frame()

		label_hello = tk.Label(self.main, text="Hello human, please select who the players shall be!")
		label_roke = tk.Label(self.main, text="ROKE: ")
		self.entry_roke = tk.Entry(self.main, width=WDTH_ENTRY)
		label_prsti = tk.Label(self.main, text="PRSTI: ")
		self.entry_prsti = tk.Entry(self.main, width=WDTH_ENTRY)
		button_HUvsHU = tk.Button(self.main, text="HUMAN vs HUMAN", width=WDTH_BUTTON, command=lambda: self.zacni_igro('clovek', 'clovek'))
		button_HUvsAI = tk.Button(self.main, text="HUMAN vs COMPUTER", width=WDTH_BUTTON, command=lambda: self.zacni_igro('clovek', 'racunalnik'))
		button_AIvsHU = tk.Button(self.main, text="COMPUTER vs HUMAN", width=WDTH_BUTTON, command=lambda: self.zacni_igro('racunalnik', 'clovek'))
		button_AIvsAI = tk.Button(self.main, text="COMPUTER vs COMPUTER", width=WDTH_BUTTON, command=lambda: self.zacni_igro('racunalnik', 'racunalnik'))

		label_hello.grid(row=0, columnspan=2)
		label_roke.grid(row=1, column=0, sticky='e')
		self.entry_roke.grid(row=1, column=1, sticky='w')
		self.entry_roke.insert(0, "2")
		label_prsti.grid(row=2, column=0, sticky='e')
		self.entry_prsti.grid(row=2, column=1, sticky='w')
		self.entry_prsti.insert(0, "5")
		button_HUvsHU.grid(row=3, columnspan=2)
		button_HUvsAI.grid(row=4, columnspan=2)
		button_AIvsHU.grid(row=5, columnspan=2)
		button_AIvsAI.grid(row=6, columnspan=2)
		
	def zacni_igro(self, igralec1, igralec2):
		""" Metoda, ki začne igro, torej nastavi izbrane igralce in uvodni UI."""
		
		# Preberemo število rok in prstov
		self.roke = int(self.entry_roke.get())
		self.prsti = int(self.entry_prsti.get())
		
		# Nastavimo razrede igralcev, ki so bili izbrani
		if igralec1 == 'clovek':
			#self.igralec_1 = Clovek()
			print("Prvi igralec je clovek")
		else:
			#self.igralec_1 = Racunalnik()
			print("Prvi igralec je racunalnik.")
		if igralec2 == 'clovek':
			#self.igralec_2 = Clovek()
			print("Drugi igralec je clovek")
		else:
			#self.igralec_2 = Racunalnik()
			print("Drugi igralec je racunalnik.")
			
		# Začnemo igro
		self.igra = Igra(self.prsti, self.roke)
		
		# Nastavimo UI za igro
		self.setup_ui()
		
	def setup_ui(self):
		"""Metoda (na novo) vzpostavi celotno igralno desko in jo nastavi na izbrano
		pozicijo."""
		
		self.new_frame()
		self.variable_igralca1 = tk.IntVar()
		self.variable_igralca1.set(None)
		self.variable_igralca2 = tk.IntVar()
		self.variable_igralca2.set(None)
		
		self.seznam_radiobutton = [[None for _ in range(self.roke)],[None for _ in range(self.roke)]]
		for i in range(self.roke):
			self.seznam_radiobutton[IGRALEC_1][i] = tk.Radiobutton(self.main, text=self.igra.position[IGRALEC_1][i], variable=self.variable_igralca1, value=i)
			self.seznam_radiobutton[IGRALEC_2][i] = tk.Radiobutton(self.main, text=self.igra.position[IGRALEC_2][i], variable=self.variable_igralca2, value=i)
			if self.igra.position[IGRALEC_1][i] == 0:
				self.seznam_radiobutton[IGRALEC_1][i].config(state="disabled")
			if self.igra.position[IGRALEC_2][i] == 0:
				self.seznam_radiobutton[IGRALEC_2][i].config(state="disabled")
			self.seznam_radiobutton[IGRALEC_1][i].grid(row=i+1, column=0)
			self.seznam_radiobutton[IGRALEC_2][i].grid(row=i+1, column=2)
			
		button_move = tk.Button(self.main, text="NAPAD!", command=self.naredi_potezo)
		button_move.grid(row=0, column=2)
		
		self.label_na_potezi = tk.Label(self.main, text="Na potezi je Igralec {}".format(self.igra.na_potezi+1))
		self.label_na_potezi.grid(row=self.roke+1, columnspan=3)
		
		if self.igra.history != []:
					self.button_razveljavi = tk.Button(self.main, text="Undo", command=self.razveljavi)
					self.button_razveljavi.grid(row=0, column=0)
		
	def naredi_potezo(self):
		"""Metoda, ki opravi potezo. Pri tem mora preveriti veljavnost poteze, spremeniti self.igra.position"""
		
		# Preberemo in ponastavimo vrednosti spremenljivk
		roka_igralca1 = self.variable_igralca1.get()
		roka_igralca2 = self.variable_igralca2.get()
		self.variable_igralca1.set(None)
		self.variable_igralca2.set(None)
		
		# Preverimo, ali je igralec izbral obe roki
		if roka_igralca1 != None and roka_igralca2 != None:
			if self.igra.na_potezi == IGRALEC_1:
				# Opravimo potezo
				self.igra.opravi_potezo(roka_igralca1, roka_igralca2)
				
				# Spremenimo število prstov na Radiobuttonu
				self.seznam_radiobutton[IGRALEC_2][roka_igralca2].config(text=self.igra.position[IGRALEC_2][roka_igralca2])
				
				# Če je število prstov slučajno 0, to roko onemogočimo
				if self.igra.position[IGRALEC_2][roka_igralca2] == 0:
					self.seznam_radiobutton[IGRALEC_2][roka_igralca2].config(state="disabled")
			else:
				# Opravimo potezo
				self.igra.opravi_potezo(roka_igralca2, roka_igralca1)
				
				# Spremenimo število prstov na Radiobuttonu
				self.seznam_radiobutton[IGRALEC_1][roka_igralca1].config(text=self.igra.position[IGRALEC_1][roka_igralca1])
				
				# Če je število prstov slučajno , to roko onemogočimo
				if self.igra.position[IGRALEC_1][roka_igralca1] == 0:
					self.seznam_radiobutton[IGRALEC_1][roka_igralca1].config(state="disabled")
			
			self.label_na_potezi.destroy()
			if self.igra.je_konec():
				self.label_na_potezi = tk.Label(self.main, text="KONEC IGRE!\nZmagal je igralec {}".format(nasprotnik(self.igra.na_potezi)+1))
				self.label_na_potezi.grid(row=self.roke+1, columnspan=3)
			elif self.igra.je_remi():
				self.label_na_potezi = tk.Label(self.main, text="KONEC IGRE!\nTrikrat ponovljeno, na pol izgubljeno.")
				self.label_na_potezi.grid(row=self.roke+1, columnspan=3)
			else:
				self.label_na_potezi = tk.Label(self.main, text="Na potezi je Igralec {}".format(self.igra.na_potezi+1))
				self.label_na_potezi.grid(row=self.roke+1, columnspan=3)
			
				# Preverimo veljavnost delitve. Če je na voljo, se pojavi gumb razdeli
				self.igra.je_veljavna_delitev()
				if self.igra.moznost_delitve:
					button_delitev = tk.Button(self.main, text="Razdeli", command=self.naredi_delitev)
					button_delitev.grid(row=0, column=1)
				
				if self.igra.history != []:
					self.button_razveljavi = tk.Button(self.main, text="Undo", command=self.razveljavi)
					self.button_razveljavi.grid(row=0, column=0)
			
			
	def naredi_delitev(self):
		"""Metoda, ki opravi delitev."""
		
		self.igra.opravi_delitev()
		for i, button in enumerate(self.seznam_radiobutton[self.igra.na_potezi]):
			button.config(text=self.igra.position[self.igra.na_potezi][i], state='normal')
			
		
	def razveljavi(self):
		"""Metoda, ki razveljavi potezo."""
		
		self.igra.razveljavi_potezo()
		self.setup_ui()
		
		
	def new_frame(self):
		try:
			self.main.destroy()
		except:
			pass
		finally:
			self.main = tk.Frame(self.master)
			self.main.grid()
		
		
	def pravila(self):
		self.new_frame()
		
		f = open('README.md', 'r') 
		pravila = f.read()
		f.close()
		
		tk.Label(self.main, text=pravila, justify='left').grid()

##################################################################################################
#
# Razred Minimax 
#
# Računalnik računa svoje poteze.
#
##################################################################################################

class Minimax:
	def __init__(self, globina):
		self.globina = globina
		self.prekinitev = False
		self.igra = None # dobimo kasneje
		self.jaz = None # dobimo kasneje
		self.poteza = None
		
	def prekini(self):
		"""Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
		self.prekinitev = True
		
	def izracunaj_potezo(self, igra):
		"""Izračunaj potezo za trenutno stanje dane igre."""
		self.igra = igra
		self.prekinitev = False
		self.jaz = self.igra.na_potezi
		self.poteza = None # Sem napišemo potezo, ki jo najdemo
		# Poženemo minimax
		(poteza, vrednost) = self.minimax(self.globina, True)
		self.jaz = None
		self.igra = None
		if not self.prekinitev:
			logging.debug("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
			self.poteza = poteza
			
		# Vrednosti igra
		ZMAGA = 100000
		NESKONCNO = ZMAGA + 1
		
	def vrednost_pozicije(self):
		razlika_v_prstih = 0
		vrednost_poteze = {}
		for roka, prsti in Igra.position[Igra.na_potezi - 1]:
			Igra.opravi_potezo(prvi, drugi) # prvi, drugi!!
			razlika_v_prstih = abs(prsti - (Igra.position[Igra.na_potezi])[roka])
			Igra.razveljavi_potezo() # dvakrat, če je bila opravljena delitev??? kako je tukaj delitev???
			vrednost_poteze[str(prvi) + " " + str(drugi)] = razlika_v_prstih
		vrednost = 0

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Prstki Beta")
	
	app = Gui(root)
	
	root.mainloop()
	
###################################################################################################
#
# PRIMER IGRE
#
###################################################################################################
'''

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
	print(game.je_konec()'''
