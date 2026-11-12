[← Główny spis treści](../README.md)

# 13. Wzorce, API i wydajność

Ten dział spina wiedzę językową w decyzje projektowe. Omawia małe, stabilne API, semantykę wartości, type erasure, granice ABI, dependency injection i optymalizację zgodną z zasadą zero-overhead.

## Wymagania wstępne

Zalecane jest ukończenie działów 01–12. Szczególnie ważne są lifetime, klasy, templates, obsługa błędów, budowanie i profilowanie.

## Efekty uczenia się

- preferujesz rule of zero i świadomie izolujesz implementację przez PImpl;
- wybierasz value semantics, type erasure albo polimorfizm runtime;
- projektujesz API odporne na błędne użycie;
- rozróżniasz kompatybilność źródłową, binarną i semantyczną;
- stosujesz dependency injection bez frameworkowego narzutu;
- optymalizujesz na podstawie pomiaru oraz modelu danych.

## Kolejność rozdziałów

1. [Rule of zero, PImpl i NVI](01_rule_of_zero_pimpl_i_non_virtual_interface.md)
2. [Value semantics i type erasure](02_value_semantics_i_type_erasure.md)
3. [Projektowanie API i ABI](03_projektowanie_api_i_abi.md)
4. [Architektura i dependency injection](04_architektura_i_dependency_injection.md)
5. [Wydajność, cache i zero-overhead](05_wydajnosc_cache_i_zero_overhead.md)
6. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak pracować

Projekt zaczynaj od klienta API i niepoprawnych użyć, które mają być niemożliwe. Wydajność mierz na danych reprezentatywnych. Granice binarne oceniaj osobno od elegancji kodu źródłowego. Każda abstrakcja ma ujawniać potrzebny kontrakt i ukrywać decyzje, które mogą się zmienić.

## Pułapki

- PImpl użyty bez realnej potrzeby stabilności lub redukcji zależności;
- type erasure tam, gdzie zamknięty `variant` jest prostszy;
- interfejs ujawniający ownership przez przypadek;
- service locator ukryty pod nazwą dependency injection;
- optymalizacja mikrobenchmarku bez wpływu na system.

## Samoocena

Potrafisz porównać co najmniej dwa projekty API pod względem lifetime, rozszerzalności, ABI, testowalności i kosztu. Umiesz wskazać pomiar, który obaliłby Twoją decyzję wydajnościową.

## Co dalej

Po tym dziale możesz wejść w [ścieżkę ekspercką](../zaawansowane/README.md) albo kontynuować do produkcyjnych narzędzi i systemów w dalszych działach, które zostaną połączone z głównym indeksem.

## Pogłębienie dla osoby programującej w C++

Przed ponowną lekturą rozwiąż scenariusze i uzasadnij odpowiedzi regułą języka lub kontraktem. Wynik eksperymentu porównuj z przewidywaniem; kompilacja nie jest dowodem poprawności wykonania.

[Sześć zadań z rozwiązaniami](../cwiczenia/13_wzorce_api_i_wydajnosc.md) uzupełnia dotychczasowy [zestaw ćwiczeń](ZESTAW-CWICZEN.md). Pełną kolejność pogłębiania opisuje [ścieżka nauki](../sciezka_nauki.md).
