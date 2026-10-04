[← Główny spis treści](../README.md)

# 02. Podstawy języka C++

Tutaj poznajesz zapis programu i reguły, z których korzystają wszystkie dalsze działy: deklaracje, typy, wartości, konwersje, funkcje, sterowanie przepływem oraz relacje między obiektem, referencją i wskaźnikiem.

## Wymagania wstępne

Powinieneś umieć skompilować pojedynczy program w C++23 i odczytać podstawową diagnostykę. Nie zakładamy znajomości innego języka.

## Efekty uczenia się

- czytasz deklaracje i rozpoznajesz zakres nazw;
- dobierasz typ do domeny, zamiast polegać na przypadkowej konwersji;
- stosujesz `const` i `constexpr` zgodnie z kontraktem;
- piszesz funkcje o czytelnych parametrach i wyniku;
- rozumiesz różnicę między wartością, referencją, wskaźnikiem i tablicą;
- przewidujesz działanie instrukcji sterujących bez zgadywania.

## Kolejność rozdziałów

1. [Leksemy, deklaracje i zakresy](01_leksemy_deklaracje_i_zakresy.md)
2. [Typy podstawowe i literały](02_typy_podstawowe_i_literaly.md)
3. [Zmienne, const i constexpr](03_zmienne_const_i_constexpr.md)
4. [Operatory i konwersje](04_operatory_i_konwersje.md)
5. [Funkcje i przeciążanie](05_funkcje_i_przeciazanie.md)
6. [Sterowanie przepływem](06_sterowanie_przeplywem.md)
7. [Referencje, wskaźniki i tablice](07_referencje_wskazniki_i_tablice.md)
8. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak się uczyć

Przed uruchomieniem małego przykładu zapisz przewidywany typ wyrażenia i wynik. Kompiluj z ostrzeżeniami, a dla niejawnych konwersji twórz przypadki graniczne. Wskaźniki ćwicz razem z warunkami ich ważności, nigdy jako samą składnię.

## Pułapki

- mylenie inicjalizacji z późniejszym przypisaniem;
- utrata zakresu lub znaku podczas konwersji liczb;
- zwracanie referencji do obiektu lokalnego;
- używanie wskaźnika bez określenia, czy może być pusty i jak długo żyje cel;
- przeciążenia różniące się w sposób nieczytelny dla wywołującego.

## Samoocena

Potrafisz napisać niewielki program bez globalnego stanu, uzasadnić typ każdego parametru, oznaczyć niezmienność, obsłużyć niepoprawne wejście i wyjaśnić lifetime obiektów wskazywanych przez każdą referencję oraz wskaźnik.

## Co dalej

Przejdź do [pamięci i czasu życia](../03_pamiec_i_czas_zycia/README.md). Jeżeli którykolwiek przykład z tego działu wymaga „bo kompilator tak robi”, wróć do reguł typu, zakresu lub kategorii wyrażenia.
