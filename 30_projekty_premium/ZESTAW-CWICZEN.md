[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Proces realizacji projektu premium

Ten zestaw nie dodaje kolejnych pomysłów. Prowadzi przez wybór i dostarczenie jednego projektu w małych, sprawdzalnych iteracjach.

## Etap 1 — wybór i kontrakt

1. Wybierz problem, którego użytkownika potrafisz nazwać jednym zdaniem.
2. Zapisz efekt portfolio i jedną umiejętność, którą projekt ma udowodnić.
3. Ogranicz minimalny zakres do pionu możliwego do wydania.
4. Wypisz dane wejściowe, wynik, limity oraz stany błędów.
5. Zdefiniuj „gotowe” przez obserwowalne kryteria.

## Etap 2 — ADR i prototyp ryzyka

6. Napisz ADR z kontekstem, trzema opcjami i konsekwencjami.
7. Wybierz największą niewiadomą techniczną.
8. Zbuduj wyrzucalny prototyp tej niewiadomej.
9. Zapisz wynik, który obaliłby wybraną architekturę.
10. Zaktualizuj zakres na podstawie dowodu, nie przywiązania do pomysłu.

## Etap 3 — plan testów

11. Dodaj test najważniejszej reguły domenowej.
12. Dodaj test granicy i niepoprawnego wejścia.
13. Zaprojektuj test kontraktu adaptera.
14. Wprowadź kontrolowaną awarię zależności.
15. Ustal test niefunkcjonalny z budżetem czasu albo pamięci.

## Etap 4 — iteracyjne dostarczanie

16. Dostarcz pierwszy pion od wejścia do wyniku.
17. Zbuduj go od świeżego klonu według README.
18. Dodaj diagnostykę pozwalającą wyjaśnić błąd bez debuggera.
19. Wydaj wersję 0.1 z digestem i listą ograniczeń.
20. Poproś o review kontraktu, a nie wyłącznie stylu.

## Etap 5 — pomiar i operacyjność

21. Zmierz reprezentatywny scenariusz i zachowaj bazę.
22. Sprawdź zachowanie przy limicie oraz kontrolowanym shutdownie.
23. Dla usługi połącz log, metrykę i trace jednego żądania.
24. Uruchom test wydanego artefaktu w czystym środowisku.
25. Zapisz decyzję o tym, czego świadomie nie optymalizujesz.

## Etap 6 — retrospektywa

26. Porównaj efekt z pierwszym kryterium ukończenia.
27. Wypisz trzy dowody jakości i dwie pozostałe niewiadome.
28. Usuń rozszerzenie, które nie wzmacnia historii portfolio.
29. Uzupełnij diagram i instrukcję demo do dziesięciu minut.
30. Wydaj stabilną wersję i zaplanuj następny projekt o innym profilu ryzyka.

## Wynik końcowy

Gotowe portfolio zawiera działający release, historię małych decyzji, testy sukcesu i awarii, pomiar oraz instrukcję reprodukcji. Retrospektywa ma być uczciwa: znane ograniczenie opisane precyzyjnie jest silniejszym dowodem dojrzałości niż ogólna deklaracja „production ready”.
