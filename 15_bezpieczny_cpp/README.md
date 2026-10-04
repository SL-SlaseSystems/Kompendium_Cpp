[← Główny spis treści](../README.md)

# 15. Bezpieczny C++

Celem działu jest oddzielić bezpieczeństwo pamięci od bezpieczeństwa całej aplikacji i projektować jawne granice zaufania. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

## Wymagania wstępne

Przed rozpoczęciem warto znać RAII, typowane błędy, podstawy testowania, CMake oraz pracę z repozytorium. Gdy rozdział używa systemu lub biblioteki zewnętrznej, traktuje ją jako jawne rozszerzenie, a nie część ISO C++.

## Efekty uczenia się

- modelujesz sukces, błąd, limit i częściowe wykonanie;
- rozdzielasz mechanizm od polityki aplikacji;
- projektujesz ownership i cleanup przed implementacją;
- dobierasz testy do ryzyka oraz granicy systemu;
- zapisujesz obserwowalne kryteria decyzji;
- weryfikujesz opcje narzędzia w źródle właściwym dla używanej wersji.

## Kolejność rozdziałów

1. [Model zagrożeń i granice zaufania](01_model_zagrozen_i_granice_zaufania.md)
2. [Bezpieczne API i typy](02_bezpieczne_api_i_typy.md)
3. [Walidacja danych i arytmetyka](03_walidacja_danych_i_arytmetyka.md)
4. [Bezpieczeństwo pamięci i lifetime](04_bezpieczenstwo_pamieci_i_lifetime.md)
5. [Pliki ścieżki i procesy](05_pliki_sciezki_i_procesy.md)
6. [Hardening i sanitizery](06_hardening_i_sanitizery.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Nie uruchamiamy przykładów z niezdefiniowanym zachowaniem. Ryzykowny przypadek opisujemy jako model, a demonstrację budujemy przez bezpieczną walidację, test lub sanitizer w kontrolowanym środowisku.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
