[← Główny spis treści](../README.md)

# 28. Wieloplatformowość, FFI i pluginy

Celem działu jest zaprojektować cienką warstwę platformową i stabilną granicę C dla rozszerzeń. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Warstwy platformowe i porty](01_warstwy_platformowe_i_porty.md)
2. [FFI C i stabilne ABI](02_ffi_c_i_stabilne_abi.md)
3. [Biblioteki dynamiczne i pluginy](03_biblioteki_dynamiczne_i_pluginy.md)
4. [Wersjonowanie pluginów i capabilities](04_wersjonowanie_pluginow_i_capabilities.md)
5. [Cross compilation i toolchain files](05_cross_compilation_i_toolchain_files.md)
6. [Dystrybucja windows linux macos](06_dystrybucja_windows_linux_macos.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Nie przenosimy STL przez stabilne ABI pluginu. Interfejs opisuje wersję struktury, capabilities, ownership, alokator, regułę zwalniania i zakaz propagacji wyjątków.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [CMake Toolchains](https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
