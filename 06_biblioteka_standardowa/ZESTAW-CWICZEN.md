[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — biblioteka standardowa

Przy każdym rozwiązaniu podaj złożoność dominującej operacji, warunki invalidacji i wymagania lifetime.

## Poziom 1 — tekst i sekwencje

1. Napisz funkcję przyjmującą `string_view`, która niczego nie przechowuje.
2. Znajdź widok do tymczasowego tekstu i popraw kontrakt.
3. Porównaj `array`, `vector` i `deque` dla stałego rozmiaru, dopisywania i stabilności.
4. Zaobserwuj zmianę `capacity` wektora podczas wzrostu.
5. Zastosuj `reserve` po oszacowaniu wielkości wyniku.

## Poziom 2 — asocjacja i hash

6. Policz częstość słów przez `unordered_map`.
7. Zwróć wyniki w porządku przez `map` i porównaj koszt.
8. Zdefiniuj hash oraz equality dla małego typu klucza.
9. Przetestuj duplikaty w `set` i `multiset`.
10. Wyjaśnij wpływ słabego hasha na złożoność i bezpieczeństwo wejścia zewnętrznego.

## Poziom 3 — iteratory i invalidacja

11. Usuń wybrane elementy wektora bez używania unieważnionego iteratora.
12. Zbuduj tabelę invalidacji dla użytych operacji `vector`, `deque` i `list`.
13. Znajdź referencję unieważnioną przez realokację.
14. Użyj `std::span` do pracy z ciągłym buforem bez kopiowania.
15. Napisz własny mały iterator albo wyjaśnij wymagania wybranej kategorii iteratora.

## Poziom 4 — algorytmy i ranges

16. Zastąp ręczne wyszukiwanie przez odpowiedni algorytm.
17. Posortuj rekordy po dwóch polach stabilnym, czytelnym komparatorem.
18. Zbuduj pipeline filtrujący i transformujący dane bez materializacji pośredniej.
19. Znajdź dangling view w funkcji zwracającej pipeline.
20. Zmaterializuj wynik ranges w wybranym kontenerze i uzasadnij moment alokacji.

## Poziom 5 — typy sum i produkty

21. Zastąp parę o niejasnych polach nazwaną strukturą.
22. Użyj `tuple` do pomocniczego porównania kilku pól.
23. Zamodeluj trzy możliwe rodzaje komunikatu przez `variant`.
24. Obsłuż `variant` odwiedzającym, który wymusza kompletność w compile time.
25. Oceń przypadek `std::any` i zaproponuj bezpieczniejszy typ, jeśli zbiór alternatyw jest znany.

## Zadanie końcowe

Zbuduj analizator tekstowego dziennika zdarzeń działający na kolekcji wierszy. Ma filtrować rekordy, agregować liczniki, utrzymywać ranking i zwracać nazwany wynik zawierający poprawne dane albo opis błędu. Dodaj testy pustego wejścia, duplikatów, niepoprawnego rekordu, dużej liczby elementów oraz lifetime widoków. Uzasadnij każdy kontener i algorytm.
