[← Główny spis treści](../README.md)

# 16. Biblioteki, pakiety i dystrybucja

Celem działu jest przeprowadzić bibliotekę od grafu celów do instalowalnego i wersjonowanego pakietu. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Typy bibliotek i struktura pakietu](01_typy_bibliotek_i_struktura_pakietu.md)
2. [CMake install export i find package](02_cmake_install_export_i_find_package.md)
3. [Conan w praktyce](03_conan_w_praktyce.md)
4. [Vcpkg w praktyce](04_vcpkg_w_praktyce.md)
5. [Wersjonowanie ABI i publikacja artefaktów](05_wersjonowanie_abi_i_publikacja_artefaktow.md)
6. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Interfejs build tree i install tree traktujemy osobno. Wymagania propagujemy przez cele CMake, a zachowania zależne od wersji Conan lub vcpkg nazywamy wprost.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [CMake Importing and Exporting Guide](https://cmake.org/cmake/help/latest/guide/importing-exporting/index.html). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
