[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — I/O i system

Używaj katalogu tymczasowego i danych testowych utworzonych przez program. Przed operacją destrukcyjną sprawdź, że ścieżka należy do tego katalogu. Sieć zawsze otrzymuje timeout.

## Poziom 1 — strumienie

1. Wczytaj liczbę i obsłuż niepoprawny stan strumienia.
2. Sformatuj tabelę bez pozostawiania przypadkowego stanu formatowania.
3. Użyj `ostringstream` do budowy komunikatu bez efektu na stdout.
4. Odczytaj wiersz zawierający spacje po wcześniejszym odczycie liczby.
5. Rozróżnij EOF od błędu formatu.

## Poziom 2 — pliki i ścieżki

6. Utwórz katalog testowy przez `filesystem`.
7. Zbuduj ścieżkę operatorem `/`, nie konkatenacją tekstu.
8. Odczytaj plik binarny bez założenia zakończenia nullem.
9. Zapisz plik tymczasowy i zamień go atomowo w granicach możliwości platformy.
10. Obsłuż brak uprawnień bez utraty poprzednich danych.

## Poziom 3 — czas

11. Zmierz duration zegarem monotonicznym.
12. Przelicz jednostki czasu jawnie przez `duration_cast`.
13. Zbuduj timeout oparty na deadline, nie liczbie iteracji.
14. Przetestuj logikę czasu przez wstrzyknięty zegar.
15. Wyjaśnij wpływ zmiany zegara systemowego na pomiar.

## Poziom 4 — losowość i numeryka

16. Oddziel seed, engine i distribution.
17. Wygeneruj liczby całkowite w zadanym domkniętym zakresie.
18. Zapewnij deterministyczny seed w teście.
19. Porównaj błąd sumowania float w dwóch kolejnościach.
20. Sprawdź overflow przed operacją całkowitą.

## Poziom 5 — granice systemu

21. Zaprojektuj interfejs serializatora niezależny od konkretnego formatu.
22. Dodaj wersję schematu do przykładowego rekordu.
23. Wskaż brakujące elementy potrzebne do niezawodnego klienta sieciowego.
24. Dodaj timeout, limit rozmiaru i walidację do pseudokodu odbioru wiadomości.
25. Sklasyfikuj użyte API jako ISO C++, systemowe albo biblioteka zewnętrzna.

## Zadanie końcowe

Zbuduj narzędzie zapisujące wersjonowany snapshot danych do katalogu wskazanego w teście. Zastosuj plik tymczasowy, kontrolę błędów, znaczniki czasu i deterministyczny identyfikator testowy. Dodaj przypadki braku katalogu, uszkodzonego pliku, częściowego zapisu i niezgodnej wersji. Testy nie mogą dotykać danych poza własnym katalogiem tymczasowym.
