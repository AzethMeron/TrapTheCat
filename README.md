# Trap The Cat
---

## O projekcie

Implementacja gry Trap the Cat w języku Python, wykorzystująca Deep Q-Learning do realizacji i uczenia AI dwóch agentów: Gracza oraz Kota. Agenci, grając przeciwko sobie, uczą się od siebie nawzajem. Aby przyśpieszyć uczenie na początkowym etapie zaimplementowano również algorytmy zachłanne, które grają przyzwoicie i są w stanie dużo lepiej uczyć przeciwnika niż nienauczona jeszcze sieć neuronowa.

Do implementacji sztucznej inteligencji wykorzystano biblioteke ```torch```, do interfejsu graficznego ```pygame```.

W pierwowzór można zagrać na stronie https://trap-thecat.com.

Autorzy:
* Jakub Grzana 241530
* Julia Rzepka 253119

## Deep Q-Learning

DQL jest modyfikacją algorytmu Q-Learningu, który zastępuje Q-table <i>(czyli tablice opisującą, jaką akcje należy podjąc dla danego stanu)</i> siecią neuronową, co pozwala na nauczenie agenta do podejmowania decyzji w niestacjonarnym <i>(zmiennym)</i> środowisku.

## Prezentacja
https://github.com/AzethMeron/TrapTheCat/assets/41695668/809351de-cf95-4876-ac87-a3931638ad8f

## Wymagania
```
Python 3.9
torch 2.3.0
matplotlib 3.9.0
numpy 1.26.4
pygame 2.5.2
tqdm 4.66.4
```

## Uruchomienie projektu

Do uruchomienia wykorzystać należy plik ```main.py```, np. ```python main.py```. Kilka linijek wartych uwagi:
```
[14] DISPLAY = True/False # Określe, czy ma być wykorzystywany interfejs graficzny. Podczas uczenia lepiej jest go wyłączyć
[46] cat_mode = constants.MODE_LEARNING / constants.MODE_FROZEN / constants.MODE_GREEDY / constants.MODE_MANUAL
[47] player_mode = constants.MODE_LEARNING / constants.MODE_FROZEN / constants.MODE_GREEDY / constants.MODE_MANUAL
MODE_LEARNING i MODE_FROZEN wykorzystują Deep Q-Learning do sterowania agentem. MODE_FROZEN wyłącza uczenie.
MODE_GREEDY wykorzystuje algorytm zachłanny.
MODE_MANUAL pozwala na ręczne sterowanie danym agentem.
[39] initial_traps = 20 # Integer. Poczatkowa liczba losowo generowanych pułapek
[40,41] min_traps, max_traps # Integer. Dolna i górna granica dla liczby generowanych losowo pułapek.
```

Wymiary planszy, a także niektóre parametry dotyczące wizualizacji można dostosować w pliku ```settings.py```.
