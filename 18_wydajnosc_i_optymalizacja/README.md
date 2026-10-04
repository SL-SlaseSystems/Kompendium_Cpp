[← Główny spis treści](../README.md)

# 18. Wydajność i optymalizacja

Celem działu jest prowadzić proces pomiar–hipoteza–zmiana–weryfikacja zamiast optymalizować na podstawie intuicji. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Metodologia benchmarków](01_metodologia_benchmarkow.md)
2. [Profilowanie CPU](02_profilowanie_cpu.md)
3. [Profilowanie pamięci i alokacji](03_profilowanie_pamieci_i_alokacji.md)
4. [Cache lokalność i layout danych](04_cache_lokalnosc_i_layout_danych.md)
5. [I/O streaming i backpressure](05_io_streaming_i_backpressure.md)
6. [Wektoryzacja PGO i LTO](06_wektoryzacja_pgo_i_lto.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Każdy eksperyment ma wariant bazowy, kontrolę usunięcia kodu przez optymalizator i zapis środowiska. Wynik lokalny nie staje się obietnicą uniwersalnego przyspieszenia.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [Google Benchmark User Guide](https://github.com/google/benchmark/blob/main/docs/user_guide.md). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
