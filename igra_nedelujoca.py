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

# Definiramo konstante, ki določajo globino posameznega algoritma.
MINIMAX_GLOBINA = 3
MINIMAXPP_GLOBINA = 5
ALPHABETA_GLOBINA = 7


def nasprotnik(igralec):
	"""Funkcija, ki vrne nasprotnika od igralca, ki je trenutno na potezi."""
	
	return (1 - igralec)

class Igra():
	"""Razred, ki skrbi za vsa pravila igre Prstki."""
	
	def __init__(self, prsti, roke, master=None):
		# Število rok in maksimalno število prstov na eni roki.
		self.roke = roke
		self.prsti = prsti
		
		# self.position je tabela, ki hrani trenutno pozicijo.
		# Inicializiramo jo s seznami enic, kjer seznam predstavlja
		# posameznega igralca.
		self.position = [[1 for _ in range(self.roke)], [1 for _ in range(self.roke)]]
		
		# Igro seveda začne prvi igralec.
		self.na_potezi = IGRALEC_1
		
		# Zgodovina nam bo služila za UNDO.
		self.history = []
		
		# Štetje pozicij je koristno za pravilo o remiju.
		self.position_count = {}
	
	def kopija(self):
		""" Vrne kopijo igre za razred Racunalnik."""
		
		kopija_igra = Igra(self.prsti, self.roke)
		kopija_igra.position = [self.position[i][:] for i in range(2)]
		kopija_igra.na_potezi = self.na_potezi
		return kopija_igra
		
	def shrani_pozicijo(self):
		"""Metoda shrani potezo v zgodovino."""
		
		# Kot je prof. Bauer odlično pripomnil, je treba seznam prepisati.
		pozicija = [self.position[i][:] for i in range(2)]
		self.history.append((pozicija, self.na_potezi))
		
		# Pozicijo dodamo še v slovar za preverjanje remija.
		try:
			self.position_count[((tuple(pozicija[IGRALEC_1]), tuple(pozicija[IGRALEC_2])), self.na_potezi)] += 1
		except KeyError:
			self.position_count[((tuple(pozicija[IGRALEC_1]), tuple(pozicija[IGRALEC_2])), self.na_potezi)] = 1
		
	def razveljavi_potezo(self):
		"""Metoda, ki razveljavi zadnjo potezo."""
		
		assert self.history != [], "Igra.razveljavi_potezo: self.history is empty."
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
		# preostali roki prstov za večkratnik rok.	
		if preostale_roke == 1 and stevilo_prstov % self.roke == 0:
			self.moznost_delitve = True
			self.prsti_po_delitvi = stevilo_prstov // self.roke
		
	def veljavne_poteze(self):
		"""Poiščemo VSE veljavne poteze, kar bo v pomoč razredu Racunalnik(),
		pa tudi nam. Poteza je trojica elementov, kjer prvi vhod pove,
		ali mora biti opravljena delitev, drugi zaporedno številko roke, s katero
		je igralec napadel, tretji pa številko napadene roke."""
		
		poteze_arr = []
		
		# Dodamo poteze brez delitve.
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
		"""Metoda opravi delitev."""
		
		# Ugotovimo, ali lahko delitev opravimo.
		self.je_veljavna_delitev()

		if self.moznost_delitve:	
			# Shranimo pozicijo, če bi si slučajno premislili o delitvi.
			self.shrani_pozicijo()
		
			# Opravimo delitev.
			self.position[self.na_potezi] = [self.prsti_po_delitvi for _ in range(self.roke)]
		
	def opravi_potezo(self, roka_napadalca, roka_napadenega):
		"""Metoda shrani trenutno pozicijo in opravi potezo."""
	
		if self.je_veljavna_poteza(roka_napadalca, roka_napadenega):
			self.shrani_pozicijo()
			self.position[nasprotnik(self.na_potezi)][roka_napadenega] = (self.position[nasprotnik(self.na_potezi)][roka_napadenega] + self.position[self.na_potezi][roka_napadalca]) % self.prsti
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
# Skrbi za vse v zvezi z uporabniškim vmesnikom. To je klasični Gui.
#
##################################################################################################

class Gui():
	def __init__(self, master):
		self.master = master
		
		# Naredimo menu.
		menu = tk.Menu(self.master)
		self.master.config(menu=menu)
		
		# Naredimo child menu Igra.
		menu_igra = tk.Menu(menu)
		menu.add_cascade(label="Igra", menu=menu_igra)
		menu_igra.add_command(label="Nova igra", command=self.izbira_igre)
		menu_igra.add_command(label="Pravila igre", command=self.pravila)
		menu_igra.add_separator()
		menu_igra.add_command(label="Izhod", command=self.master.destroy)
		
		# Naredimo child menu Možnosti.
		menu_options = tk.Menu(menu)
		menu.add_cascade(label="Možnosti", menu=menu_options)
		menu_options.add_command(label="Spremeni grafični vmesnik", command=lambda:select_gui(self.master, self))
		menu_options.add_command(label="Help", command=self.help)
		
		# Nastavimo igralca na človek, da lahko v izbira_igre lažje
		# kličemo prekini_igralce.
		self.igralec_1 = Clovek(self)
		self.igralec_2 = Clovek(self)
		
		self.izbira_igre()
		
	def izbira_igre(self):
		"""Uporabniku damo možnost, da se odloči za število rok in prstov
		ter izbor igralcev."""
		
		self.prekini_igralce()
		
		# Konstante za širino Entry-ja in Button-a.
		WDTH_BUTTON = 20
		WDTH_ENTRY = 5
		
		self.new_frame()
		
		# Spremenljivke za OptionMenu.
		self.option1 = tk.StringVar(self.main)
		self.option2 = tk.StringVar(self.main)
		self.option1.set("Človek")
		self.option2.set("Minimax")

		# Ustvarimo labele, entryje, gumbe...
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

		# Gridamo labele, entryje, gumbe...
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
		"""Metoda, ki prebere izbrane igralce in začne igro."""
		
		# Dobimo izbiri.
		option1 = self.option1.get()
		option2 = self.option2.get()
		
		if option1 == "Človek":
			if option2 == "Človek":
				self.zacni_igro(Clovek(self), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Clovek(self), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))
		elif option1 == "Minimax":
			if option2 == "Človek":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))
		elif option1 == "Minimax++":
			if option2 == "Človek":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))
		elif option1 == "Alpha-Beta":
			if option2 == "Človek":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))	
				
	def zacni_igro(self, igralec1, igralec2):
		""" Metoda, ki začne igro, torej nastavi izbrane razrede igralcev in uvodni UI."""
		
		# Preberemo število rok in prstov. Če število rok ni int,
		# ali ne ustreza določenim zahtevam, vrnemo None.
		try:
			self.roke = int(self.entry_roke.get())
			if self.roke <= 0:
				return
		except: 
			return
		try:
			self.prsti = int(self.entry_prsti.get())
			if self.prsti <= 1:
				return
		except: 
			return
		
		# Ustvarimo objekte igralcev.
		self.igralec_1 = igralec1
		self.igralec_2 = igralec2
			
		# Začnemo igro.
		self.igra = Igra(self.prsti, self.roke)
		
		# Nastavimo UI za igro.
		self.setup_ui()
		
	def setup_ui(self):
		"""Metoda (na novo) vzpostavi celotno igralno desko in jo nastavi na izbrano
		pozicijo."""
		
		self.new_frame()
		
		# Ustvarimo spremenljivke za RadioButton-e.
		self.variable_igralca1 = tk.IntVar()
		self.variable_igralca1.set(None)
		self.variable_igralca2 = tk.IntVar()
		self.variable_igralca2.set(None)
		
		# Ustvarimo seznam RadioButtonov in ga nastavimo na trenutno pozicijo.
		self.seznam_radiobutton = [[None for _ in range(self.roke)],[None for _ in range(self.roke)]]
		for i in range(self.roke):
			self.seznam_radiobutton[IGRALEC_1][i] = tk.Radiobutton(self.main, text=self.igra.position[IGRALEC_1][i], variable=self.variable_igralca1, value=i)
			self.seznam_radiobutton[IGRALEC_2][i] = tk.Radiobutton(self.main, text=self.igra.position[IGRALEC_2][i], variable=self.variable_igralca2, value=i)
			
			# Če je število prstov na roki 0, onemogočimo gumb, ki predstavlja to roko.
			if self.igra.position[IGRALEC_1][i] == 0:
				self.seznam_radiobutton[IGRALEC_1][i].config(state="disabled")
			if self.igra.position[IGRALEC_2][i] == 0:
				self.seznam_radiobutton[IGRALEC_2][i].config(state="disabled")
				
			self.seznam_radiobutton[IGRALEC_1][i].grid(row=i+1, column=0)
			self.seznam_radiobutton[IGRALEC_2][i].grid(row=i+1, column=2)
		
		# Če je na potezi človek, potrebuje gumb za napad.
		if (self.igra.na_potezi == IGRALEC_1 and isinstance(self.igralec_1, Clovek))\
			or (self.igra.na_potezi == IGRALEC_2 and isinstance(self.igralec_2, Clovek)):
			button_move = tk.Button(self.main, text="NAPAD!", command=self.preberi_potezo)
			button_move.grid(row=0, column=2)
		
		try:
			self.label_na_potezi.destroy()
		except: pass
		
		# Preverimo, ali je konec igre, remi.
		if self.igra.je_konec():
			self.label_na_potezi = tk.Label(self.main, text="KONEC IGRE!\nZmagal je igralec {}".format(nasprotnik(self.igra.na_potezi)+1))
			self.label_na_potezi.grid(row=self.roke+1, columnspan=3)
		elif self.igra.je_remi():
			self.label_na_potezi = tk.Label(self.main, text="KONEC IGRE!\nPrvič ponovljeno, na pol izgubljeno.")
			self.label_na_potezi.grid(row=self.roke+1, columnspan=3)
		else:
			self.label_na_potezi = tk.Label(self.main, text="Na potezi je Igralec {}".format(self.igra.na_potezi+1))
			self.label_na_potezi.grid(row=self.roke+1, columnspan=3)
		
			# Preverimo veljavnost delitve. Če je na voljo, se pojavi gumb razdeli.
			self.igra.je_veljavna_delitev()
			if self.igra.moznost_delitve:
				button_delitev = tk.Button(self.main, text="Razdeli", command=self.naredi_delitev)
				button_delitev.grid(row=0, column=1)
			
			# Če imamo kaj zgodovine, lahko ponudimo možnost razveljavitve poteze.
			if self.igra.history != []:
				self.button_razveljavi = tk.Button(self.main, text="Undo", command=self.razveljavi)
				self.button_razveljavi.grid(row=0, column=0)
				
			# Prisilimo igralca, da igra. Potrebno le za računalnik
			# (metoda igraj pri cloveku passa).
			if self.igra.na_potezi == IGRALEC_1:
				self.igralec_1.igraj()
			elif self.igra.na_potezi == IGRALEC_2:
				self.igralec_2.igraj()
					
	def preberi_potezo(self):
		"""Preberemo in ponastavimo vrednosti spremenljivk ter naredimo potezo."""
		
		roka_igralca1 = self.variable_igralca1.get()
		roka_igralca2 = self.variable_igralca2.get()
		self.variable_igralca1.set(None)
		self.variable_igralca2.set(None)
		
		self.naredi_potezo(roka_igralca1, roka_igralca2)
		
	def naredi_potezo(self, roka_igralca1, roka_igralca2):
		"""Metoda, ki opravi potezo. Pri tem mora preveriti veljavnost poteze, spremeniti self.igra.position."""
		
		# Preverimo, ali je igralec izbral obe roki.
		if roka_igralca1 != None and roka_igralca2 != None:
			if self.igra.na_potezi == IGRALEC_1:
				# Opravimo potezo
				self.igra.opravi_potezo(roka_igralca1, roka_igralca2)
				self.setup_ui()
			else:
				# Opravimo potezo
				self.igra.opravi_potezo(roka_igralca2, roka_igralca1)
				self.setup_ui()
			
	def naredi_delitev(self):
		"""Metoda, ki opravi delitev."""
		
		self.igra.opravi_delitev()
		self.setup_ui()
			
	def razveljavi(self):
		"""Metoda, ki razveljavi potezo."""
		
		self.igra.razveljavi_potezo()
		self.setup_ui()
		
	def prekini_igralce(self):
		"""Metoda, ki prekine igralce. Potrebno le za računalnik (pri človeku passa)."""
		
		if self.igralec_1: self.igralec_1.prekini()
		if self.igralec_2: self.igralec_2.prekini()
		
	def new_frame(self):
		"""Metoda, ki ustvari nov Frame in pred tem pobriše starega, če obstaja."""
		
		try:
			self.main.destroy()
		except:
			pass
		finally:
			self.main = tk.Frame(self.master)
			self.main.grid()
		
	def pravila(self):
		"""Metoda, ki napiše pravila igre."""
		
		self.new_frame()
		
		f = open('README.md', 'r') 
		pravila = f.read()
		f.close()
		
		tk.Label(self.main, text=pravila, justify='left').grid()
		
	def help(self):
		"""Metoda, ki napiše nekaj namigov."""
		
		self.new_frame()
		
		help = "Ko je možna delitev, se pojavi gumb, na katerega klikni, če želi opraviti delitev.\nZa razveljavitev poteze je prav tako na voljo gumb.\n\nNasvet: Za boljšo preglednost priporočamo uporabo klasičnega uporabniškega vmesnika za število prstov, ki presega 10."
		tk.Label(self.main, text=help, justify='left').grid()
		
#######################################################################################
#
# Razred NewGui
#
# Provides more enhanced GUI then class Gui
#
#######################################################################################
		
class NewGui():

	# Definiramo konstante.
	OVAL_SIZE = 60
	DIFF_MID = 100
	DIFF_KROGCI = 10
	
	def __init__(self, master):
		self.master = master
		
		# Naredimo menu.
		menu = tk.Menu(self.master)
		self.master.config(menu=menu)
		
		# Naredimo child menu Igra.
		menu_igra = tk.Menu(menu)
		menu.add_cascade(label="Igra", menu=menu_igra)
		menu_igra.add_command(label="Nova igra", command=self.izbira_igre)
		menu_igra.add_command(label="Pravila igre", command=self.pravila)
		menu_igra.add_separator()
		menu_igra.add_command(label="Izhod", command=self.master.destroy)
		
		# Naredimo child menu Možnosti.
		menu_options = tk.Menu(menu)
		menu.add_cascade(label="Možnosti", menu=menu_options)
		menu_options.add_command(label="Spremeni grafični vmesnik", command=lambda:select_gui(self.master, self))
		menu_options.add_command(label="Help", command=self.help)
		
		# Nastavimo igralca na človek, da lahko v izbira_igre lažje
		# kličemo prekini_igralce.
		self.igralec_1 = Clovek(self)
		self.igralec_2 = Clovek(self)
		
		self.izbira_igre()
		
	def izbira_igre(self):
		"""Uporabniku damo možnost, da se odloči za število rok in prstov
		ter izbor igralcev."""
		
		self.prekini_igralce()
		
		# Konstante za širino Entry-ja in Button-a.
		WDTH_BUTTON = 20
		WDTH_ENTRY = 5
		
		self.new_frame()
		
		# Spremenljivke za OptionMenu.
		self.option1 = tk.StringVar(self.main)
		self.option2 = tk.StringVar(self.main)
		self.option1.set("Človek")
		self.option2.set("Človek")

		# Ustvarimo labele, entryje, gumbe...
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

		# Gridamo labele, entryje, gumbe...
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
		"""Metoda, ki prebere izbrane igralce in začne igro."""
		
		# Dobimo izbiri.
		option1 = self.option1.get()
		option2 = self.option2.get()
		
		if option1 == "Človek":
			if option2 == "Človek":
				self.zacni_igro(Clovek(self), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Clovek(self), Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Clovek(self), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))
		elif option1 == "Minimax":
			if option2 == "Človek":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))
		elif option1 == "Minimax++":
			if option2 == "Človek":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))
		elif option1 == "Alpha-Beta":
			if option2 == "Človek":
				self.zacni_igro(Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)), Clovek(self))
			elif option2 == "Minimax":
				self.zacni_igro(Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAX_GLOBINA)))
			elif option2 == "Minimax++":
				self.zacni_igro(Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)), Racunalnik(self, Minimax(globina=MINIMAXPP_GLOBINA)))
			elif option2 == "Alpha-Beta":
				self.zacni_igro(Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)), Racunalnik(self, AlphaBeta(globina=ALPHABETA_GLOBINA)))	
				
	def zacni_igro(self, igralec1, igralec2):
		""" Metoda, ki začne igro, torej nastavi izbrane igralce in uvodni UI."""
		
		# Preberemo število rok in prstov. Če število rok ni int,
		# ali ne ustreza določenim zahtevam, vrnemo None.
		try:
			self.roke = int(self.entry_roke.get())
			if self.roke <= 0:
				return
		except: 
			return
		try:
			self.prsti = int(self.entry_prsti.get())
			if self.prsti <= 1:
				return
		except: 
			return
		
		# Ustvarimo objekte igralcev.
		self.igralec_1 = igralec1
		self.igralec_2 = igralec2
			
		# Začnemo igro
		self.igra = Igra(self.prsti, self.roke)
		
		# Nastavimo UI za igro
		self.setup_ui()
		
	def setup_ui(self):
		"""Metoda (na novo) vzpostavi celotno igralno desko in jo nastavi na izbrano pozicijo."""
		
		self.new_frame()
		
		# S tem bomo preverjali, ali lahko že opravimo potezo.
		self.potrebno_opraviti = [None, None]
		
		# Nastavimo dimenzije Canvasa.
		self.WDTH_CANVAS = 2 * self.prsti * (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI) + NewGui.DIFF_MID
		self.HGHT_CANVAS = self.roke * (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI)
		
		# Ustvarimo igralno desko.
		self.igralna_deska = tk.Canvas(self.main, width=self.WDTH_CANVAS, height=self.HGHT_CANVAS)
		self.igralna_deska.grid()
		
		# Bindamo tipkovnico na igralna_deska.
		self.igralna_deska.focus_set()
		
		# Če je na potezi človek, bindamo gumbe, sicer ne.
		if (self.igra.na_potezi == IGRALEC_1 and isinstance(self.igralec_1, Clovek))\
			or (self.igra.na_potezi == IGRALEC_2 and isinstance(self.igralec_2, Clovek)):
			self.igralna_deska.bind("<Button-1>", self.deska_klik)
			self.igralna_deska.bind("<Button-3>", self.naredi_delitev)
			self.igralna_deska.bind("<BackSpace>", self.razveljavi)
		
		# Za vsak prst na vsaki roki naredimo krogec.
		for roka in range(self.roke):			
			x = NewGui.DIFF_KROGCI
			y = roka * (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI) + NewGui.DIFF_KROGCI//2
			self.seznam_krogci = [[[None for _ in range(self.prsti)] for _ in range(self.roke)], [[None for _ in range(self.prsti)] for _ in range(self.roke)]]
			
			for prst in range(self.prsti):
				if self.igra.position[IGRALEC_1][roka] == 0:
					self.seznam_krogci[IGRALEC_1][roka][prst] = self.igralna_deska.create_oval(x, y, x+NewGui.OVAL_SIZE, y+NewGui.OVAL_SIZE, outline='grey', dash=(5,), fill="")
				elif prst < self.igra.position[IGRALEC_1][roka]:
					self.seznam_krogci[IGRALEC_1][roka][prst] = self.igralna_deska.create_oval(x, y, x+NewGui.OVAL_SIZE, y+NewGui.OVAL_SIZE, outline='red', fill='red')
				else:
					self.seznam_krogci[IGRALEC_1][roka][prst] = self.igralna_deska.create_oval(x, y, x+NewGui.OVAL_SIZE, y+NewGui.OVAL_SIZE, outline='red')
					
				if self.igra.position[IGRALEC_2][roka] == 0:
					self.seznam_krogci[IGRALEC_2][roka][prst] = self.igralna_deska.create_oval(self.WDTH_CANVAS-x-NewGui.OVAL_SIZE, y, self.WDTH_CANVAS-x, y+NewGui.OVAL_SIZE, outline='grey', dash=(5,), fill="")
				elif prst < self.igra.position[IGRALEC_2][roka]:
					self.seznam_krogci[IGRALEC_2][roka][prst] = self.igralna_deska.create_oval(self.WDTH_CANVAS-x-NewGui.OVAL_SIZE, y, self.WDTH_CANVAS-x, y+NewGui.OVAL_SIZE, outline='green', fill='green')
				else:
					self.seznam_krogci[IGRALEC_2][roka][prst] = self.igralna_deska.create_oval(self.WDTH_CANVAS-x-NewGui.OVAL_SIZE, y, self.WDTH_CANVAS-x, y+NewGui.OVAL_SIZE, outline='green')
				
				x += NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI
		
		for roka in range(self.roke):
			for prst in range(self.prsti):
				print(self.seznam_krogci[IGRALEC_1][roka][prst])
				print(self.seznam_krogci[IGRALEC_2][roka][prst])
				print("\n")
				
		try:
			self.napis.destroy()
		except: pass
		
		# Preverimo, ali je konec igre, remi.
		if self.igra.je_konec():
			if self.igra.na_potezi == IGRALEC_1:
				self.napis = tk.Label(self.main, text="KONEC IGRE!\nZmagal je ZELENI.")
			elif self.igra.na_potezi == IGRALEC_2:
				self.napis = tk.Label(self.main, text="KONEC IGRE!\nZmagal je RDECI.")
			self.igralna_deska.unbind("<Button-1>")
			self.igralna_deska.unbind("<Button-3>")
			self.igralna_deska.unbind("<BackSpace")
			self.prekini_igralce()
		elif self.igra.je_remi():
			self.napis = tk.Label(self.main, text="KONEC IGRE!\nPrvic ponovljeno, na pol izgubljeno.")
			self.igralna_deska.unbind("<Button-1>")
			self.igralna_deska.unbind("<Button-3>")
			self.igralna_deska.unbind("<BackSpace")
			self.prekini_igralce()
		else:
			if self.igra.na_potezi == IGRALEC_1:
				self.napis = tk.Label(self.main, text="Na potezi je RDECI.")
			elif self.igra.na_potezi == IGRALEC_2:
				self.napis = tk.Label(self.main, text="Na potezi je ZELENI.")
			if self.igra.na_potezi == IGRALEC_1:
				self.igralec_1.igraj()
			elif self.igra.na_potezi == IGRALEC_2:
				self.igralec_2.igraj()
		self.napis.grid()
		
	def prekini_igralce(self):
		"""Metoda, ki prekine igralce. Potrebno le za računalnik (pri človeku passa)."""
		
		if self.igralec_1: self.igralec_1.prekini()
		if self.igralec_2: self.igralec_2.prekini()
		
				
	def deska_klik(self, event):
		"""Metoda posrednik med klikom in preraunavanjem poteze. Skrbi le za shranitev koordinat,
		da lahko ob kliku kličemo funkcijo brez 'lambda:...'."""
		
		x = event.x
		y = event.y
		self.preracunaj_potezo((x,y))
				
	def preracunaj_potezo(self, p):
		"""Metoda, ki na podlagi koordinat klika določi, katero roko smo izbrali.
		Če smo izbrali že svojo in nasprotnikovo roko, opravi potezo. Tu je v pomoč
		seznam potrebno_opraviti."""
		
		(x,y) = p
		igralec = None
		
		# Po x koordinati določimo, ali gre za roko igralca 1 ali igralca 2.
		if x < (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI) * self.prsti:
			igralec = IGRALEC_1
		elif x > self.WDTH_CANVAS - (NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI) * self.prsti:
			igralec = IGRALEC_2
		
		if igralec != None:
			tmp = self.potrebno_opraviti[igralec]
			print(tmp)
			roka = (int(y) - NewGui.DIFF_KROGCI//2)//(NewGui.OVAL_SIZE + NewGui.DIFF_KROGCI)
			self.potrebno_opraviti[igralec] = roka
			
			if tmp != None and tmp != roka:
				for prst in range(self.prsti):
					if self.igra.na_potezi == IGRALEC_1:
						if prst < self.igra.position[IGRALEC_1][tmp]:
							self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][tmp][prst], fill="red", outline="red")
						else:
							self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][tmp][prst], outline="red")
					else:
						if prst < self.igra.position[IGRALEC_2][tmp]:
							self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][tmp][prst], fill="green", outline="green")
						else:
							self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][tmp][prst], outline="green")
				
			for prst in range(self.prsti):
				if prst < self.igra.position[igralec][roka]:
					self.igralna_deska.itemconfig(self.seznam_krogci[igralec][roka][prst], fill="blue", outline="blue")
				else:
					self.igralna_deska.itemconfig(self.seznam_krogci[igralec][roka][prst], outline="blue")
			
			# Če sta izbrani obe roki, opravimo potezo in spremenimo barvo krogcev.
			if self.potrebno_opraviti[IGRALEC_1] != None and self.potrebno_opraviti[IGRALEC_2] != None:
				for prst in range(self.prsti):
					if prst < self.igra.position[IGRALEC_1][roka]:
						self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][roka][prst], fill="red", outline="red")
					else:
						self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][roka][prst], outline="red")
					if prst < self.igra.position[IGRALEC_2][roka]:
						self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][roka][prst], fill="green", outline="green")
					else:
						self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][roka][prst], outline="green")
						
				if self.igra.je_veljavna_poteza(self.potrebno_opraviti[IGRALEC_1], self.potrebno_opraviti[IGRALEC_2]):	
					self.naredi_potezo(self.potrebno_opraviti[IGRALEC_1], self.potrebno_opraviti[IGRALEC_2])
				
	def naredi_potezo(self, roka_igralca1, roka_igralca2):
		"""Metoda, ki naredi potezo."""
		
		if self.igra.na_potezi == IGRALEC_1:
			self.igra.opravi_potezo(roka_igralca1, roka_igralca2)
						
			for prst in range(self.prsti):
				if self.igra.position[IGRALEC_2][roka_igralca2] == 0:
					self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][roka_igralca2][prst], fill="", outline='grey', dash=(5,))
					print("Uniči roko")
				elif prst < self.igra.position[IGRALEC_2][roka_igralca2]:
					self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][roka_igralca2][prst], fill='green', outline='green')
					print("Barvaj zeleno")
				else:
					self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][roka_igralca2][prst], fill="", outline='green')
					print("Prazen zelen")
			
		elif self.igra.na_potezi == IGRALEC_2:
			self.igra.opravi_potezo(roka_igralca2, roka_igralca1)
			
			for prst in range(self.prsti):
				if self.igra.position[IGRALEC_1][roka_igralca1] == 0:
					self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][roka_igralca1][prst], fill="", outline='grey', dash=(5,))
					print("Uniči roko")
				elif prst < self.igra.position[IGRALEC_1][roka_igralca1]:
					self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][roka_igralca1][prst], fill='red', outline='red')
					print("Barvaj rdeče")
				else:
					self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][roka_igralca1][prst], fill="", outline='red')
					print("Prazen rdeč")
		
		self.igralna_deska.update_idletasks()			

		self.potrebno_opraviti = [None, None]
		
		if (self.igra.na_potezi == IGRALEC_1 and isinstance(self.igralec_1, Clovek))\
			or (self.igra.na_potezi == IGRALEC_2 and isinstance(self.igralec_2, Clovek)):
			self.igralna_deska.bind("<Button-1>", self.deska_klik)
			self.igralna_deska.bind("<Button-3>", self.naredi_delitev)
			self.igralna_deska.bind("<BackSpace>", self.razveljavi)
		else:
			self.igralna_deska.unbind("<Button-1>")
			self.igralna_deska.unbind("<Button-3>")
			self.igralna_deska.unbind("<BackSpace>")
			
		try:
			self.napis.destroy()
		except: pass
		
		# Preverimo, ali je konec igre, remi.
		if self.igra.je_konec():
			if self.igra.na_potezi == IGRALEC_1:
				self.napis = tk.Label(self.main, text="KONEC IGRE!\nZmagal je ZELENI.")
			elif self.igra.na_potezi == IGRALEC_2:
				self.napis = tk.Label(self.main, text="KONEC IGRE!\nZmagal je RDECI.")
			self.igralna_deska.unbind("<Button-1>")
			self.igralna_deska.unbind("<Button-3>")
			self.igralna_deska.unbind("<BackSpace")
			self.prekini_igralce()
		elif self.igra.je_remi():
			self.napis = tk.Label(self.main, text="KONEC IGRE!\nPrvic ponovljeno, na pol izgubljeno.")
			self.igralna_deska.unbind("<Button-1>")
			self.igralna_deska.unbind("<Button-3>")
			self.igralna_deska.unbind("<BackSpace")
			self.prekini_igralce()
		else:
			if self.igra.na_potezi == IGRALEC_1:
				self.napis = tk.Label(self.main, text="Na potezi je RDECI.")
			elif self.igra.na_potezi == IGRALEC_2:
				self.napis = tk.Label(self.main, text="Na potezi je ZELENI.")
			if self.igra.na_potezi == IGRALEC_1:
				self.igralec_1.igraj()
			elif self.igra.na_potezi == IGRALEC_2:
				self.igralec_2.igraj()
		self.napis.grid()
			
	def naredi_delitev(self, event=None):
		"""Metoda, ki naredi delitev."""
		
		self.igra.je_veljavna_delitev()
		if self.igra.moznost_delitve:
			self.igra.opravi_delitev()
			
			for roka in range(self.roke):
				for prst in range(self.prsti):
					if self.igra.na_potezi == IGRALEC_1:
						if prst < self.igra.position[IGRALEC_1][roka]:
							self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][roka][prst], fill='red', outline='red', dash=())
						else:
							self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_1][roka][prst], fill="", outline='red', dash=())
					
					elif self.igra.na_potezi == IGRALEC_2:
						if prst < self.igra.position[IGRALEC_2][roka]:
							self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][roka][prst], fill='green', outline='green', dash=())
						else:
							self.igralna_deska.itemconfig(self.seznam_krogci[IGRALEC_2][roka][prst], fill="", outline='green', dash=())
			
	def razveljavi(self, event):
		"""Metoda, ki razveljavi potezo. Seveda lahko to stori le človek, zato preverimo,
		ali je na potezi človek."""
		
		if self.igra.history != []:
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
		"""Metoda, ki ustvari nov Frame in pred tem pobriše starega, če obstaja."""
		
		try:
			self.main.destroy()
		except:
			pass
		finally:
			self.main = tk.Frame(self.master)
			self.main.grid()
			
	def pravila(self):
		"""Metoda, ki napiše pravila igre."""
		
		self.new_frame()
		
		f = open('README.md', 'r') 
		pravila = f.read()
		f.close()
		
		tk.Label(self.main, text=pravila, justify='left').grid()
		
	def help(self):
		"""Metoda, ki napiše nekaj namigov."""
		
		help = "Za delitev pritisni desni miškin gumb.\nZa razveljavitev poteze pritisni povratnico.\n\nNasvet: Za boljšo preglednost priporočamo uporabo klasičnega uporabniškega vmesnika za število prstov, ki presega 10."
		tk.Label(self.main, text=help, justify='left').grid()
		tk.Button(self.main, text="Nova igra", command=self.izbira_igre).grid()
		
##################################################################################################
#
# Razred Clovek
#
##################################################################################################

class Clovek():
	def __init__(self, gui):
		self.gui = gui
	
	def igraj(self):
		# Človeka ne rabimo siliti k opravljanju potez.
		pass
		
	def prekini(self):
		# Človeka ne rabimo prekiniti; on se sam prekine.
		pass
	
	def klik(self, p):
		# Ob kliku preračunamo potezo.
		self.gui.preracunaj_potezo()


##################################################################################################
#	
# Razred Racunalnik
#
# Razred, ki skrbi za vse v zvezi z računalnikom in komunikacijo z izbranim algoritmom.
#
##################################################################################################	
		
class Racunalnik():
	def __init__(self, gui, algoritem):
		
		# Zapomnimo si gui in nastavimo izbran algoritem.
		self.gui = gui
		self.algoritem = algoritem
		self.mislec = None
		
	def igraj(self):
		"""Metoda, ki prisili algoritem, da izračuna potezo."""
		
		self.mislec = threading.Thread(target=lambda:self.algoritem.izracunaj_potezo(self.gui.igra.kopija()))	
		self.mislec.start()
		
		# Čez 100ms preverimo, ali že imamo potezo.
		self.gui.main.after(100, self.preveri_potezo)

	def preveri_potezo(self):
		"""Metoda, ki preveri, ali že imamo potezo. Če jo imamo, jo opravimo, drugače se spet pokličemo."""
		
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
			
			# Ker smo našli potezo, misleca ne rabimo več.
			self.mislec = None
		else:
			self.gui.main.after(100, self.preveri_potezo)
			
	def prekini(self):
		"""Metoda, ki prekine misleca, če smo to zahtevali."""
		
		if self.mislec:
			self.algoritem.prekini()
			self.mislec.join()
			self.mislec = None
			
	def klik(self, p):
		# Se ne odzivamo na klike, ko razmišljamo.
		pass
	

##################################################################################################
#
# Razred Minimax 
#
# Računalnik računa svoje poteze z algoritmom Minimax
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
		
		# Sem napišemo potezo, ki jo najdemo.
		self.poteza = None
		
		# Poženemo minimax.
		(poteza, vrednost) = self.minimax(self.globina, True)
		
		self.jaz = None
		self.igra = None
		
		# Če nismo prekinili razmišljanja, lahko nastavimo potezo.
		if not self.prekinitev:
			time.sleep(2)
			self.poteza = poteza
			
	# Vrednosti igre
	ZMAGA = 1000000000
	NESKONCNO = ZMAGA + 1
	
	def vrednost_pozicije(self):
		"""Oceni vrednost pozicije po postopku: naši prsti so plus, nasprotnikovi minus."""
		
		stevilo_prstov = 0

		for roka in self.igra.position[self.igra.na_potezi]:
			if roka == 0:
				stevilo_prstov -= 5
			else: stevilo_prstov -= roka
		for roka in self.igra.position[nasprotnik(self.igra.na_potezi)]:
			if roka == 0:
				stevilo_prstov += 5
			else: stevilo_prstov += roka

		# != self.jaz zato, ker je po opravljeni potezi nasprotnik na vrsti.
		# Z uporabo negacije, 'smo spet mi'.
		if self.igra.na_potezi != self.jaz:
			return stevilo_prstov
		else: return -stevilo_prstov
		
	def minimax(self, globina, maksimiziramo):
		"""Glavna metoda algoritma."""
		
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
		"""Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
           
		self.prekinitev = True
		
	def izracunaj_potezo(self, igra):
		self.igra = igra
		self.prekinitev = False
		self.jaz = self.igra.na_potezi
		
		# Sem napišemo potezo, ki jo najdemo.
		self.poteza = None
		
		# Poženemo alphabeta.
		(poteza, vrednost) = self.alphabeta(self.globina, -AlphaBeta.NESKONCNO, AlphaBeta.NESKONCNO, True)
		self.jaz = None
		self.igra = None
		
		# Če nas niso prekinili, lahko nastavimo potezo.
		if not self.prekinitev:
			time.sleep(2)
			self.poteza = poteza
			
	ZMAGA = 1000000000
	NESKONCNO = ZMAGA + 1
	
	def vrednost_pozicije(self):
		"""Oceni vrednost pozicije po postopku: naši prsti so plus, nasprotnikovi minus."""
		
		stevilo_prstov = 0

		for roka in self.igra.position[self.igra.na_potezi]:
			if roka == 0:
				stevilo_prstov -= 5
			else: stevilo_prstov -= roka
		for roka in self.igra.position[nasprotnik(self.igra.na_potezi)]:
			if roka == 0:
				stevilo_prstov += 5
			else: stevilo_prstov += roka

		if self.igra.na_potezi != self.jaz:
			return stevilo_prstov
		else: return -stevilo_prstov
			
	def alphabeta(self, globina, alpha, beta, maksimiziramo):
		"""Glavna metoda algoritma."""
		
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
				
def select_gui(master, current_game=None):
	"""Funkcija, s katero lahko izberemo GUI med igro."""
	
	# Ustvarimo popup window
	window = tk.Toplevel()
	window.title("Izbira grafičnega vmesnika")
	
	msg = tk.Message(window, text="Prosim, izberi grafični vmesnik.\nOpozorilo: Trenutna igra bo prekinjena!")
	msg.grid(row=0, columnspan=2)
	
	button_classic = tk.Button(window, text="Classic", command=lambda:select_gui_now("Classic", master, current_game, window))
	button_classic.grid(row=1, column=0)
	button_new = tk.Button(window, text="New", command=lambda:select_gui_now("New", master, current_game, window))
	button_new.grid(row=1, column=1)
	
def select_gui_now(gui_type, master, current_game=None, window=None):
	"""Funkcija, ki nastavi izbran GUI. To funkcijo kličemo tudi ob zagonu igrice."""
	
	# Če je slučajno kakšna igra v teku, prekinemo vse
	# igralce in uničimo okno main.
	if current_game != None:
		current_game.prekini_igralce()
		current_game.main.destroy()
		
	# Če je funkcijo klicala funkcija select_gui, moramo
	# uničiti popup okno.
	if window != None:
		window.destroy()
		
	# Nastavimo in vrnemo željen GUI.
	if gui_type == "Classic":
		gui = Gui(master)
	elif gui_type == "New":
		gui = NewGui(master)
	return gui
				

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Prstki Beta")
	
	app = select_gui_now("New", root)
	
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
