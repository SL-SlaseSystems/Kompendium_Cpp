[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — szablony i generyczność

W rozwiązaniach zapisuj kontrakt słowami przed kodem. Celowo niepoprawne wywołania kompiluj osobno i oceniaj jakość diagnostyki.

## Poziom 1 — szablony i dedukcja

1. Napisz `max_value` dla dwóch wartości tego samego typu.
2. Uogólnij prostą klasę punktu na typ współrzędnych.
3. Sprawdź dedukcję `auto` dla wartości, referencji i `const`.
4. Użyj `decltype` do zachowania typu wyrażenia.
5. Dodaj deduction guide tylko tam, gdzie CTAD bez niego daje niewłaściwy interfejs.

## Poziom 2 — wybór implementacji

6. Porównaj przeciążenie funkcji z pełną specjalizacją.
7. Zastosuj `if constexpr` do dwóch kategorii typów.
8. Napisz trait rozpoznający jedną właściwość typu.
9. Przekształć prosty przykład SFINAE na `requires`.
10. Wyjaśnij, dlaczego błąd w ciele szablonu może pojawić się dopiero przy instancjacji.

## Poziom 3 — concepts

11. Zdefiniuj concept dla typu posiadającego operację i wymagany wynik.
12. Oddziel wymóg składniowy od semantycznej obietnicy dokumentowanej tekstem.
13. Ogranicz klasę szablonową i funkcję członkowską różnymi wymaganiami.
14. Zbuduj dwa przeciążenia z relacją subsumption i sprawdź wybór.
15. Popraw concept, który przypadkowo akceptuje typ o błędnej semantyce.

## Poziom 4 — packs i forwarding

16. Zsumuj parameter pack przez fold expression z poprawnym przypadkiem pustym.
17. Wypisz wszystkie argumenty bez rekursji szablonowej.
18. Zbuduj fabrykę przekazującą argumenty przez `std::forward`.
19. Znajdź miejsce, w którym wielokrotne forwardowanie tego samego argumentu jest błędem.
20. Użyj `std::index_sequence` do pracy z krotką.

## Poziom 5 — compile time i koszt

21. Napisz `consteval` walidator prostego literału.
22. Porównaj tabelę obliczaną w runtime i `constexpr` pod względem interfejsu.
23. Zmierz wpływ wielu instancjacji na czas kompilacji lub rozmiar binarny.
24. Ogranicz liczbę instancjacji przez niegeneryczny rdzeń implementacji.
25. Zinterpretuj diagnostykę zależnej nazwy wymagającej `typename`.

## Zadanie końcowe

Zaprojektuj generyczny algorytm agregacji zakresu. Ma przyjmować operację, wartość początkową i elementy spełniające nazwany concept, zachowywać kategorie wartości tylko tam, gdzie to potrzebne, oraz czytelnie odrzucać błędny typ. Dodaj testy pustego zakresu, jednego elementu, typu move-only i niezgodnego wywołania kompilowanego jako przypadek negatywny.
