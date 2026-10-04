[← Główny spis treści](../README.md)

# 17. Runtime, kompilator i ABI

Celem działu jest zrozumieć drogę od źródła do procesu oraz diagnozować granice kompilatora, linkera i loadera. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Od main do procesu](01_od_main_do_procesu.md)
2. [Fazy kompilacji i IR](02_fazy_kompilacji_i_ir.md)
3. [Symbole linker i ładowanie dynamiczne](03_symbole_linker_i_ladowanie_dynamiczne.md)
4. [ABI name mangling i wyjątki](04_abi_name_mangling_i_wyjatki.md)
5. [Diagnostyka kompilatora i linkera](05_diagnostyka_kompilatora_i_linkera.md)
6. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Polecenia i formaty oznaczamy jako ELF/Linux, Mach-O/macOS albo PE/COFF/Windows. Obserwacji konkretnego toolchainu nie przedstawiamy jako gwarancji ISO C++.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [Clang Compiler User’s Manual](https://clang.llvm.org/docs/UsersManual.html). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
