[← Główny spis treści](../README.md)

# 23. Architektura aplikacji produkcyjnych

Celem działu jest złożyć proces z jawnych portów, jednego composition root i kontrolowanego cyklu życia. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Granice modułów i zależności](01_granice_modulow_i_zaleznosci.md)
2. [Konfiguracja i sekrety](02_konfiguracja_i_sekrety.md)
3. [Dependency injection i composition root](03_dependency_injection_i_composition_root.md)
4. [Obsługa błędów i odporność](04_obsluga_bledow_i_odpornosc.md)
5. [Zadania w tle i shutdown](05_zadania_w_tle_i_shutdown.md)
6. [Case study usługa produkcyjna](06_case_study_usluga_produkcyjna.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Nie powtarzamy katalogu wzorców. Śledzimy przepływ danych, błędu i shutdown przez konkretne granice oraz nazywamy ownership każdego długo żyjącego zasobu.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
