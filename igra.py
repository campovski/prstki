import tkinter as tk
import threading
import time

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

MINIMAX_GLOBINA = 3
MINIMAXpp_GLOBINA = 5
ALPHABETA_GLOBINA = 5


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
	
	def kopija(self):
		""" Vrne kopijo igre za računalnik."""
		
		kopija_igra = Igra(self.prsti, self.roke)
		kopija_igra.position = [self.position[i][:] for i in range(2)]
		kopija_igra.na_potezi = self.na_potezi
		return kopija_igra
		
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
		
		if self.history != []:
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
		ali mora biti opravljena delitev, drugi zaporedno številko roke, s katero
		je igralec napadel, tretji pa številko napadene roke."""
		
		poteze_arr = []
		
		# Dodamo poteze brez delitve
		for roka_napadalca in range(self.roke):
			for roka_napadenega in range(self.roke):
				if self.je_veljavna_poteza(roka_napadalca, roka_napadenega):
					poteze_arr.append((False, roka_napadalca, roka_napadenega))
				
		# Če je možna delitev, dodamo še vse poteze z delitvijo. Preverimo
		# le, da napadena roka ni enaka 0 (roka napadalca ne more biti 0).
		self.je_veljavna_delitev()
		if self.moznost_delitve:
			for roka_napadalca in range(self.roke):
				for roka_napadenega in range(self.roke):
					if self.position[nasprotnik(self.na_potezi)][roka_napadenega] != 0:
						poteze_arr.append((True, roka_napadalca, roka_napadenega))
		return poteze_arr
						
	def opravi_delitev(self):
		"""Metoda opravi delitev. Preverjanje, ali je delitev možna ali ne,
		je potrebno narediti pred klicem same metode!"""
		
		self.je_veljavna_delitev()
		if self.moznost_delitve:	
			# Shranimo pozicijo, če bi si slučajno premislili o delitvi
			#self.shrani_pozicijo()
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
		"""Preveri, ali smo se morda znašli v isti poziciji.
		Preverimo, ali je bila pozicija že zabeležena."""
		
		try:
			return self.position_count[((tuple(self.position[IGRALEC_1]), tuple(self.position[IGRALEC_2])), self.na_potezi)] == 1
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
		
		self.scale_tezavnost = tk.Scale(self.main, from_=0, to=2)

		label_tezavnost = tk.Label(self.main, text="Tezavnost:")
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
		label_tezavnost.grid(row=3, column=0, sticky='e')
		self.scale_tezavnost.grid(row=3, column=1, sticky='w')
		button_HUvsHU.grid(row=4, columnspan=2)
		button_HUvsAI.grid(row=5, columnspan=2)
		button_AIvsHU.grid(row=6, columnspan=2)
		button_AIvsAI.grid(row=7, columnspan=2)
		
	def zacni_igro(self, igralec1, igralec2):
		""" Metoda, ki začne igro, torej nastavi izbrane igralce in uvodni UI."""
		
		# Preberemo število rok in prstov ter tezavnost
		self.roke = int(self.entry_roke.get())
		self.prsti = int(self.entry_prsti.get())
		self.tezavnost = int(self.scale_tezavnost.get())
		
		# Nastavimo razrede igralcev, ki so bili izbrani
		if igralec1 == 'clovek':
			self.igralec_1 = Clovek(self)
			print("Prvi igralec je clovek")
		else:
			if self.tezavnost == 1:
				self.igralec_1 = Racunalnik(self, Minimax(globina=3))
			elif self.tezavnost == 2:
				self.igralec_1 = Racunalnik(self, Minimax(globina=4))
			print("Prvi igralec je racunalnik.")
		if igralec2 == 'clovek':
			self.igralec_2 = Clovek(self)
			print("Drugi igralec je clovek")
		else:
			if self.tezavnost == 1:
				self.igralec_2 = Racunalnik(self, Minimax(globina=3))
			elif self.tezavnost == 2:
				self.igralec_2 = Racunalnik(self, Minimax(globina=4))
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
			
		button_move = tk.Button(self.main, text="NAPAD!", command=self.preberi_potezo)
		button_move.grid(row=0, column=2)
		
		self.label_na_potezi = tk.Label(self.main, text="Na potezi je Igralec {}".format(self.igra.na_potezi+1))
		self.label_na_potezi.grid(row=self.roke+1, columnspan=3)
		
		if self.igra.history != []:
					self.button_razveljavi = tk.Button(self.main, text="Undo", command=self.razveljavi)
					self.button_razveljavi.grid(row=0, column=0)
					
	def preberi_potezo(self):
		"""Preberemo in ponastavimo vrednosti spremenljivk"""
		roka_igralca1 = self.variable_igralca1.get()
		roka_igralca2 = self.variable_igralca2.get()
		self.variable_igralca1.set(None)
		self.variable_igralca2.set(None)
		
		self.naredi_potezo(roka_igralca1, roka_igralca2)
		
	def naredi_potezo(self, roka_igralca1, roka_igralca2):
		"""Metoda, ki opravi potezo. Pri tem mora preveriti veljavnost poteze, spremeniti self.igra.position"""
		
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
				self.label_na_potezi = tk.Label(self.main, text="KONEC IGRE!\nPrvič ponovljeno, na pol izgubljeno.")
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
					
	def preracunaj_potezo(self, p):
		pass
			
			
	def naredi_delitev(self):
		"""Metoda, ki opravi delitev."""
		
		self.igra.opravi_delitev()
		self.setup_ui()
			
		
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
		
#######################################################################################
#
# Razred NewGui
#
# Provides more enhanced GUI then class Gui
#
#######################################################################################
		
class NewGui():

	# Definiramo konstante
	OVAL_SIZE = 60
	DIFF_MID = 100
	DIFF_KROGCI = 10
	
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
		
		self.igralec_1 = Clovek(self)
		self.igralec_2 = Clovek(self)
		self.izbira_igre()
		
	def izbira_igre(self):
		"""Uporabniku damo možnost, da se odloči za število rok in prstov
		ter način igre, torej npr. HUMAN vs HUMAN."""
		
		self.prekini_igralce()
		
		# Konstante za širino Entry-ja in Button-a
		WDTH_BUTTON = 20
		WDTH_ENTRY = 5
		
		self.new_frame()
		
		self.option1 = tk.StringVar(self.main)
		self.option2 = tk.StringVar(self.main)
		self.option1.set("Človek")
		self.option2.set("Človek")

		label_hello = tk.Label(self.main, text="Hello human, please select who the players shall be!")
		label_roke = tk.Label(self.main, text="ROKE: ")
		self.entry_roke = tk.Entry(self.main, width=WDTH_ENTRY)
		label_prsti = tk.Label(self.main, text="PRSTI: ")
		self.entry_prsti = tk.Entry(self.main, width=WDTH_ENTRY)
		self.optionmenu_igralec1 = tk.OptionMenu(self.main, self.option1, "Človek", "Minimax", "Minimax++", "Alpha-Beta")
		self.optionmenu_igralec2 = tk.OptionMenu(self.main, self.option2, "Človek", "Minimax", "Minimax++", "Alpha-Beta")
		label_igralec1 = tk.Label(self.main, text="Igralec 1")
		label_igralec2 = tk.Label(self.main, text="Igralec 2")
		button_zacni = tk.Button(self.main, text="Začni igro!", command=self.preberi_igralce)

		label_hello.grid(row=0, columnspan=2)
		label_roke.grid(row=1, column=0, sticky='e')
		self.entry_roke.grid(row=1, column=1, sticky='w')
		self.entry_roke.insert(0, "2")
		label_prsti.grid(row=2, column=0, sticky='e')
		self.entry_prsti.grid(row=2, column=1, sticky='w')
		self.entry_prsti.insert(0, "5")
		label_igralec1.grid(row=3, column=0, sticky='e')
		label_igralec2.grid(row=3, column=1, sticky='w')
		self.optionmenu_igralec1.grid(row=4, column=0, sticky='e')
		self.optionmenu_igralec2.grid(row=4, column=1, sticky='w')
		button_zacni.grid(row=5, columnspan=2)
		
	def preberi_igralce(self):
		option1 = self.option1.get()
		option2 = self.option2.get()
		if option1 == "Človek":
			if option2 == "Človek":
				self.zacni_igro(Clovek(self), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina=MINIMAXpp_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Clovek(self), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))
		elif option1 == "Minimax":
			if option2 == "Človek":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAXpp_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))
		elif option1 == "Minimax++":
			if option2 == "Človek":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXpp_GLOBINA)), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXpp_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXpp_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAXpp_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXpp_GLOBINA)), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))
		elif option1 == "Alpha-Beta":
			if option2 == "Človek":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXpp_GLOBINA)), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAXpp_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))	
				
	def zacni_igro(self, igralec1, igralec2):
		""" Metoda, ki začne igro, torej nastavi izbrane igralce in uvodni UI."""
		
		self.prekini_igralce()
		
		# Preberemo število rok in prstov
		self.roke = int(self.entry_roke.get())
		self.prsti = int(self.entry_prsti.get())
		
		self.igralec_1 = igralec1
		self.igralec_2 = igralec2
			
		# Začnemo igro
		self.igra = Igra(self.prsti, self.roke)
		
		if isinstance(self.igralec_1, Racunalnik):
			self.naredi_potezo(0,0)
		# Nastavimo UI za igro
		self.setup_ui()
		
	def setup_ui(self):
		"""Metoda (na novo) vzpostavi celotno igralno desko in jo nastavi na izbrano pozicijo."""
		
		self.new_frame()
		print(self.igra.veljavne_poteze())
		print(self.igra.position)
		
		self.potrebno_opraviti = [None, None]
		
		self.WDTH_CANVAS = 2 * self.prsti * (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI) + NewGui.DIFF_MID
		self.HGHT_CANVAS = self.roke * (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI)
		
		# Ustvarimo igralno desko
		self.igralna_deska = tk.Canvas(self.main, width=self.WDTH_CANVAS, height=self.HGHT_CANVAS)
		self.igralna_deska.grid()
		self.igralna_deska.focus_set()
		
		self.igralna_deska.bind("<Button-1>", self.deska_klik)
		self.igralna_deska.bind("<Button-3>", self.naredi_delitev)
		self.igralna_deska.bind("<BackSpace>", self.razveljavi)
		
		for roka in range(self.roke):			
			x = NewGui.DIFF_KROGCI
			y = roka * (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI) + NewGui.DIFF_KROGCI//2
			self.seznam_krogci = [[[None for _ in range(self.prsti)] for _ in range(self.roke)], [[None for _ in range(self.prsti)] for _ in range(self.roke)]]
			
			for prst in range(self.prsti):
				self.seznam_krogci[IGRALEC_1][roka][prst] = self.igralna_deska.create_oval(x, y, x+NewGui.OVAL_SIZE, y+NewGui.OVAL_SIZE, outline='red')
				self.seznam_krogci[IGRALEC_2][roka][prst] = self.igralna_deska.create_oval(self.WDTH_CANVAS-x-NewGui.OVAL_SIZE, y, self.WDTH_CANVAS-x, y+NewGui.OVAL_SIZE, outline='green')
				
				if self.igra.position[IGRALEC_1][roka] == 0 or self.igra.position[IGRALEC_2][roka] == 0:
					if self.igra.position[IGRALEC_1][roka] == 0:
						self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][roka][prst], outline='grey', dash=(5,))
					if self.igra.position[IGRALEC_2][roka] == 0:
						self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][roka][prst], outline='grey', dash=(5,))
				if prst < self.igra.position[IGRALEC_1][roka] or prst < self.igra.position[IGRALEC_2][roka]:
					if prst < self.igra.position[IGRALEC_1][roka]:
						self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][roka][prst], fill='red')
					if prst < self.igra.position[IGRALEC_2][roka]:
						self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][roka][prst], fill='green')
				
				x += NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI
				
		try:
			self.napis.destroy()
		except: pass
		if self.igra.je_konec():
			self.napis = tk.Label(self.main, text="KONEC IGRE!\nZmagal je igralec {}".format(nasprotnik(self.igra.na_potezi)+1))
			self.igralna_deska.unbind("<Button-1>")
			self.igralna_deska.unbind("<Button-3>")
			self.igralna_deska.unbind("<BackSpace")
			self.prekini_igralce()
		elif self.igra.je_remi():
			self.napis = tk.Label(self.main, text="KONEC IGRE!\nPrvič ponovljeno, na pol izgubljeno.")
			self.igralna_deska.unbind("<Button-1>")
			self.igralna_deska.unbind("<Button-3>")
			self.igralna_deska.unbind("<BackSpace")
			self.prekini_igralce()
		else:
			self.napis = tk.Label(self.main, text="Na potezi je Igralec {}".format(self.igra.na_potezi+1))
			if self.igra.na_potezi == IGRALEC_1:
				self.igralec_1.igraj()
			elif self.igra.na_potezi == IGRALEC_2:
				self.igralec_2.igraj()
		self.napis.grid()
		
	def prekini_igralce(self):
		if self.igralec_1: self.igralec_1.prekini()
		if self.igralec_2: self.igralec_2.prekini()
		
				
	def deska_klik(self, event):
		x = event.x
		y = event.y
		self.preracunaj_potezo((x,y))
				
	def preracunaj_potezo(self, p):
		(x,y) = p
		igralec = None
		if x < (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI) * self.prsti:
			igralec = IGRALEC_1
		elif x > self.WDTH_CANVAS - (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI) * self.prsti:
			igralec = IGRALEC_2
		
		if igralec != None:
			roka = (int(y) - NewGui.DIFF_KROGCI//2)//(NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI)
			self.potrebno_opraviti[igralec] = roka
			if self.potrebno_opraviti[IGRALEC_1] != None and self.potrebno_opraviti[IGRALEC_2] != None:
				if self.igra.position[IGRALEC_1][self.potrebno_opraviti[IGRALEC_1]] != 0 and self.igra.position[IGRALEC_1][self.potrebno_opraviti[IGRALEC_1]] != 0:
					self.naredi_potezo(self.potrebno_opraviti[IGRALEC_1], self.potrebno_opraviti[IGRALEC_2])
				
	def naredi_potezo(self, roka_igralca1, roka_igralca2):
		if self.igra.na_potezi == IGRALEC_1:
			self.igra.opravi_potezo(roka_igralca1, roka_igralca2)
		elif self.igra.na_potezi == IGRALEC_2:
			self.igra.opravi_potezo(roka_igralca2, roka_igralca1)
		self.setup_ui()
			
	def naredi_delitev(self, event=None):
		self.igra.je_veljavna_delitev()
		if self.igra.moznost_delitve:
			self.igra.opravi_delitev()
			self.setup_ui()
			
	def razveljavi(self, event):
	
		if self.igra.na_potezi == IGRALEC_1 and isinstance(self.igralec_1, Clovek):
			if isinstance(self.igralec_2, Racunalnik) and self.igra.history[len(self.igra.history)-1][1] != IGRALEC_1:
				self.igra.razveljavi_potezo()
			self.igra.razveljavi_potezo()
			self.setup_ui()
		elif self.igra.na_potezi == IGRALEC_2 and isinstance(self.igralec_2, Clovek):
			if isinstance(self.igralec_1, Racunalnik) and self.igra.history[len(self.igra.history)-1][1] != IGRALEC_2:
				self.igra.razveljavi_potezo()
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
# Razred Clovek
#
##################################################################################################

class Clovek():
	def __init__(self, gui):
		self.gui = gui
	
	def igraj(self):
		pass
		
	def prekini(self):
		pass
	
	def klik(self, p):
		self.gui.preracunaj_potezo()


##################################################################################################
#	
# Razred Racunalnik
#
#
##################################################################################################	
		
class Racunalnik():
	def __init__(self, gui, algoritem):
		self.gui = gui
		self.algoritem = algoritem
		self.mislec = None
		
	def igraj(self):
		self.mislec = threading.Thread(target=lambda:self.algoritem.izracunaj_potezo(self.gui.igra.kopija()))	
		
		self.mislec.start()
		
		self.gui.igralna_deska.after(100, self.preveri_potezo)
		
	def preveri_potezo(self):
		if self.algoritem.poteza is not None:
			if self.algoritem.poteza[0]:
				self.gui.naredi_delitev()
			if self.gui.igra.na_potezi == IGRALEC_1:
				try:
					self.gui.naredi_potezo(self.algoritem.poteza[1], self.algoritem.poteza[2])
				except: pass
			else:
				try:
					self.gui.naredi_potezo(self.algoritem.poteza[2], self.algoritem.poteza[1])
				except: pass
			
			self.mislec = None
		else:
			self.gui.igralna_deska.after(100, self.preveri_potezo)
			
	def prekini(self):
		if self.mislec:
			self.algoritem.prekini()
			self.mislec.join()
			self.mislec = None
			
	def klik(self, p):
		pass
	

##################################################################################################
#
# Razred Minimax 
#
# Računalnik računa svoje poteze.
#
##################################################################################################

class Minimax():
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
		self.jaz = self.igra.na_potezi
		self.prekinitev = False
		self.poteza = None # Sem napišemo potezo, ki jo najdemo
		# Poženemo minimax
		(poteza, vrednost) = self.minimax(self.globina, True)
		self.jaz = None
		self.igra = None
		if not self.prekinitev:
			time.sleep(2)
			self.poteza = poteza
			
	# Vrednosti igra
	ZMAGA = 1000000000
	NESKONCNO = ZMAGA + 1
	
	def vrednost_pozicije(self):
		"""Oceni vrednost pozicije po postopku: želimo, da bo po
		opravljeni potezi čim večje število prstov na vseh rokah (0 prstov je 5)."""
		
		stevilo_prstov = 0
		#for igralec in self.igra.position:
		for roka in self.igra.position[self.igra.na_potezi]:
			if roka == 0:
				stevilo_prstov += 5
			else: stevilo_prstov += roka
		for roka in self.igra.position[nasprotnik(self.igra.na_potezi)]:
			if roka == 0:
				stevilo_prstov -= 5
			else: stevilo_prstov -= roka

		if self.igra.na_potezi != self.jaz:
			return stevilo_prstov
		else: return -stevilo_prstov
		
	def minimax(self, globina, maksimiziramo):
		if self.prekinitev:
			return (None, 0)
		if self.igra.je_konec():
			if self.igra.na_potezi != self.jaz:
				return (None, Minimax.ZMAGA)
			else:
				return (None, -Minimax.ZMAGA)
		elif self.igra.je_remi():
			return (None, 0)
		else:
			if globina == 0:
				return (None, self.vrednost_pozicije())
			else:
				if maksimiziramo:
					najboljsa_poteza = None
					vrednost_najboljsa = -Minimax.NESKONCNO
					poteze = self.igra.veljavne_poteze()
					for (delitev, roka_napadalca, roka_napadenega) in poteze:
						if delitev:
							self.igra.opravi_delitev()
						self.igra.opravi_potezo(roka_napadalca, roka_napadenega)
						vrednost = self.minimax(globina-1, not maksimiziramo)[1]
						self.igra.razveljavi_potezo()
						if delitev:
							self.igra.razveljavi_potezo()
						
						if vrednost > vrednost_najboljsa:
							vrednost_najboljsa = vrednost
							najboljsa_poteza = (delitev, roka_napadalca, roka_napadenega)
				else: # Minimiziramo
					najboljsa_poteza = None
					vrednost_najboljsa = Minimax.NESKONCNO
					poteze = self.igra.veljavne_poteze()
					for (delitev, roka_napadalca, roka_napadenega) in poteze:
						if delitev:
							self.igra.opravi_delitev()
						self.igra.opravi_potezo(roka_napadalca, roka_napadenega)
						vrednost = self.minimax(globina-1, not maksimiziramo)[1]
						self.igra.razveljavi_potezo()
						if delitev:
							self.igra.opravi_delitev()
						
						if vrednost < vrednost_najboljsa:
							vrednost_najboljsa = vrednost
							najboljsa_poteza = (delitev, roka_napadalca, roka_napadenega)
				return (najboljsa_poteza, vrednost_najboljsa)

###################################################################################################
#
# Razred AlphaBeta
#
###################################################################################################

class AlphaBeta():
	def __init__(self, globina):
		self.globina = globina
		self.prekinitev = False
		self.igra = None
		self.jaz = None
		self.poteza = None
		
	def prekini(self):
		self.prekinitev = True
		
	def izracunaj_potezo(self, igra):
		self.igra = igra
		self.prekinitev = False
		self.jaz = self.igra.na_potezi
		self.poteza = None
		(poteza, vrednost) = self.alphabeta(self.globina, -AlphaBeta.NESKONCNO, AlphaBeta.NESKONCNO, True)
		self.jaz = None
		self.igra = None
		if not self.prekinitev:
			time.sleep(2)
			self.poteza = poteza
			
	ZMAGA = 1000000000
	NESKONCNO = ZMAGA + 1
	
	def vrednost_pozicije(self):
		"""Oceni vrednost pozicije po postopku: želimo, da bo po
		opravljeni potezi čim večje število prstov na vseh rokah (0 prstov je 5)."""
		
		stevilo_prstov = 0
		for igralec in self.igra.position:
			for roka in igralec:
				if roka == 0:
					stevilo_prstov += 5
				else: stevilo_prstov += roka
		if self.igra.na_potezi == self.jaz:
			return stevilo_prstov
		else:
			return -stevilo_prstov
			
	def alphabeta(self, globina, alpha, beta, maksimiziramo):
		
		if self.prekinitev == True:
			return (None, 0)
		if self.igra.je_konec():
			if self.igra.na_potezi != self.jaz:
				return (None, AlphaBeta.ZMAGA)
			else:
				return (None, -AlphaBeta.ZMAGA)
		elif self.igra.je_remi():
			return (None, 0)
		else:
			if globina == 0:
				return (None, self.vrednost_pozicije())
			else:
				if maksimiziramo:
					najboljsa_poteza = None
					vrednost_najboljsa = -AlphaBeta.NESKONCNO
					poteze = self.igra.veljavne_poteze()
					for (delitev, roka_napadalca, roka_napadenega) in poteze:
						if delitev:
							self.igra.opravi_delitev()
						self.igra.opravi_potezo(roka_napadalca, roka_napadenega)
						vrednost = self.alphabeta(globina-1, alpha, beta, not maksimiziramo)[1]
						self.igra.razveljavi_potezo()
						if delitev:
							self.igra.razveljavi_potezo()
						if vrednost > vrednost_najboljsa:
							vrednost_najboljsa = vrednost
							najboljsa_poteza = (delitev, roka_napadalca, roka_napadenega)
						if vrednost > alpha:
							alpha = vrednost
						if beta <= alpha:
							break
				else:
					najboljsa_poteza = None
					vrednost_najboljsa = AlphaBeta.NESKONCNO
					poteze = self.igra.veljavne_poteze()
					for (delitev, roka_napadalca, roka_napadenega) in poteze:
						if delitev:
							self.igra.opravi_delitev()
						self.igra.opravi_potezo(roka_napadalca, roka_napadenega)
						vrednost = self.alphabeta(globina-1, alpha, beta, not maksimiziramo)[1]
						self.igra.razveljavi_potezo()
						if delitev:
							self.igra.razveljavi_potezo()
							
						if vrednost < vrednost_najboljsa:
							vrednost_najboljsa = vrednost
							najboljsa_poteza = (delitev, roka_napadalca, roka_napadenega)
						if vrednost < beta:
							beta = vrednost
						if beta <= alpha:
							break
							
				return (najboljsa_poteza, vrednost_najboljsa)
				
					
				

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Prstki Beta")
	
	app = NewGui(root)
	
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
