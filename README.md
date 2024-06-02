# Trap The Cat
---

## O projekcie

Implementacja gry Trap the Cat w języku Python, wykorzystująca Deep Q-Learning do realizacji i uczenia AI dwóch agentów: Gracza oraz Kota. Agenci, grając przeciwko sobie, uczą się od siebie nawzajem. Aby przyśpieszyć uczenie na początkowym etapie zaimplementowano również algorytmy zachłanne, które grają przyzwoicie i są w stanie dużo lepiej uczyć przeciwnika niż nienauczona jeszcze sieć neuronowa.

Do implementacji sztucznej inteligencji wykorzystano biblioteke ```torch```, do interfejsu graficznego ```pygame```.

W pierwowzór można zagrać na stronie https://trap-thecat.com.

## Wymagania
```
Python 3.9
torch 2.3.0
matplotlib 3.9.0
numpy 1.26.4
pygame 2.5.2
tqdm 4.66.4
```
