[← Główny spis treści](../README.md)

# 07. Błędy i kontrakty

Obsługa błędów nie zaczyna się od wyboru `throw` albo kodu błędu. Najpierw trzeba określić kontrakt, rozróżnić błąd programisty od przewidywalnego niepowodzenia oraz ustalić, jakie inwarianty pozostają po porażce.

## Wymagania wstępne

Potrzebujesz znajomości funkcji, RAII, konstrukcji i destrukcji obiektów, move semantics oraz podstaw typów sum, takich jak `optional` i `variant`.

## Efekty uczenia się

- klasyfikujesz błędy przed wyborem mechanizmu;
- zachowujesz zasoby i inwarianty podczas propagacji wyjątku;
- rozumiesz znaczenie `noexcept` dla kontraktu i optymalizacji;
- wybierasz między wyjątkiem, `optional`, `expected` i kodem błędu;
- oddzielasz assertion od obsługi niepoprawnych danych zewnętrznych.

## Kolejność rozdziałów

1. [Wyjątki: try, catch i throw](01_wyjatki_try_catch_throw.md)
2. [RAII, exception safety i noexcept](02_raii_exception_safety_i_noexcept.md)
3. [optional, expected i kody błędów](03_optional_expected_i_kody_bledow.md)
4. [Assertions, preconditions i contracts](04_assertions_preconditions_i_contracts.md)
5. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak pracować

Dla każdego API wypisz warunki wstępne, poprawny wynik, możliwe niepowodzenia i gwarancję stanu po błędzie. Testuj ścieżkę sukcesu i każdą klasę błędu. Nie łap wyjątku, jeśli nie potrafisz go obsłużyć, wzbogacić kontekstem lub zamienić na kontrakt warstwy wyżej.

## Pułapki

- wyjątek użyty do zwykłego sterowania przepływem;
- pusty `catch (...)`, który niszczy diagnostykę;
- `noexcept` dodane bez audytu wszystkich wywołań;
- `optional` bez informacji, dlaczego wartości nie ma;
- assertion użyte do walidacji wejścia użytkownika.

## Samoocena

Umiesz zaprojektować operację z jawną taksonomią błędów, udowodnić basic lub strong exception guarantee, zapewnić cleanup przez RAII i napisać testy zachowania po częściowym niepowodzeniu.

## Co dalej

Przejdź do [budowania i organizacji](../08_budowanie_i_organizacja/README.md), gdzie kontrakty rozciągają się na granice plików, bibliotek i procesu linkowania.

## Pogłębienie dla osoby programującej w C++

Przed ponowną lekturą rozwiąż scenariusze i uzasadnij odpowiedzi regułą języka lub kontraktem. Wynik eksperymentu porównuj z przewidywaniem; kompilacja nie jest dowodem poprawności wykonania.

[Sześć zadań z rozwiązaniami](../cwiczenia/07_bledy_i_kontrakty.md) uzupełnia dotychczasowy [zestaw ćwiczeń](ZESTAW-CWICZEN.md). Pełną kolejność pogłębiania opisuje [ścieżka nauki](../sciezka_nauki.md).
