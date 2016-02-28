# Prstki

Projekt pri predmetu Programiranje 2, napisan v programskem jeziku Python 3.

## Pravila igre

V igri sodelujeta dva igralca. Oba sta prebivalca istega planeta, zatorej imata enako število rok, recimo *R* in na vsaki roki enako število prstov, recimo *P(MAX)*.

Igra se prične tako, da oba igralca začneta s po enim prstom na vsaki roki. Igra nato sestoji iz t.i. potez, vsaka poteza pa iz dveh delov:
1. Delitev (neobvezno): Če ima igralec *R-1* rok praznih in na preostali roki *kR* prstov, lahko razdeli prste s preostale roke na vse roke tako, da po delitvi na vsaki, tudi prej uničenih, ostane *k* prstov.
2. Napad (obvezno): Igralec na potezi izbere svojo roko, s katero napade katerokoli izmed nasprotnikovih preostalih rok.

Po napadu napadalcu ostane na vseh rokah enako število prstov, nasprotniku pa se na napadeni roki število prstov spremeni po formuli *P(B') = P(A) + P(B) % P(MAX)*, kjer je *P(A)* število prstov na roki, s katero je igralec napadel, *P(B)* pa število prstov napadene roke pred napadom. Če je slučajno *P(B') = 0*, igralec to roko izgubi in z njo ne more več igrati, razen če kasneje opravi delitev.

**Trikrat ponovljeno, na pol izgubljeno**: Če se pozicija trikrat ponovi in je vsakič na vrsti isti igralec, je avtomatsko razglašen remi.

Cilj igre je nasprotniku uničiti vse roke. Zmaga prinese eno točko, remi pol in zguba nič.
