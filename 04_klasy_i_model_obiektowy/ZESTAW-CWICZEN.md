[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — klasy i model obiektowy

Każde zadanie rozpocznij od inwariantu i przykładów użycia publicznego API. Prywatny układ danych jest decyzją wtórną.

## Poziom 1 — typy i inwarianty

1. Zbuduj typ `Temperature`, który nie pozwala utworzyć wartości poniżej zera absolutnego.
2. Porównaj publiczny agregat danych z klasą chroniącą inwariant.
3. Ogranicz konstruktor jednoargumentowy przez `explicit` i pokaż odrzuconą konwersję.
4. Użyj listy inicjalizacyjnej zgodnie z kolejnością deklaracji pól.
5. Napisz metodę `const` i wyjaśnij, który obiekt jest niezmienny.

## Poziom 2 — konstrukcja i funkcje specjalne

6. Zaloguj kolejność konstrukcji baz, składowych i obiektu pochodnego.
7. Zastąp ręczny destruktor składową RAII.
8. Zablokuj kopiowanie typu reprezentującego wyłączny uchwyt.
9. Przywróć rule of zero przez zmianę reprezentacji.
10. Sprawdź wpływ `noexcept` konstruktora przenoszącego na zachowanie `vector`.

## Poziom 3 — operatory

11. Zaimplementuj symetryczne porównanie typu wartościowego.
12. Dodaj `operator+=`, a `operator+` oprzyj na nim bez duplikacji logiki.
13. Znajdź operator zwracający referencję do obiektu tymczasowego.
14. Zdecyduj, czy konwersja do `bool` powinna być jawna.
15. Przetestuj prawa algebraiczne deklarowane przez własny typ liczbowy.

## Poziom 4 — kompozycja i polimorfizm

16. Przepisz hierarchię używaną tylko do współdzielenia kodu na kompozycję.
17. Zaprojektuj minimalny interfejs strategii z wirtualnym destruktorem.
18. Dodaj nową implementację strategii bez zmiany klienta.
19. Znajdź slicing przy przekazywaniu obiektu pochodnego przez wartość.
20. Porównaj koszt i rozszerzalność `variant` z hierarchią wirtualną.

## Poziom 5 — modelowanie stanów

21. Zastąp zestaw powiązanych flag jednym `enum class`.
22. Zamodeluj rezultat będący jedną z trzech struktur przez `std::variant`.
23. Obsłuż wszystkie alternatywy przez odwiedzającego bez domyślnego „catch all”.
24. Zbuduj test dowodzący, że niepoprawnego stanu nie da się skonstruować.
25. Oceń, czy RTTI w podanym przykładzie wskazuje na brak operacji w interfejsie.

## Zadanie końcowe

Zaprojektuj model płatności z kilkoma metodami i wspólnym wynikiem autoryzacji. Przygotuj dwie wersje: `std::variant` oraz interfejs polimorficzny. Dodaj testy inwariantów, kopiowania lub jego braku, błędów oraz rozszerzenia o nową metodę. Raport ma porównać ownership, koszt, czytelność i wpływ dodawania operacji oraz typów.
