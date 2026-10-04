[← Główny spis treści](../README.md)

# 19. Debugowanie i utrzymanie

Celem działu jest zamieniać objaw w reprodukcję, hipotezę, dowód i bezpieczną poprawkę regresji. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Strategia debugowania i MRE](01_strategia_debugowania_i_mre.md)
2. [GDB i LLDB](02_gdb_i_lldb.md)
3. [Core dump i crash report](03_core_dump_i_crash_report.md)
4. [Regresje git bisect i reprodukcja](04_regresje_git_bisect_i_reprodukcja.md)
5. [Diagnostyka wielowątkowości](05_diagnostyka_wielowatkowosci.md)
6. [Refaktoryzacja starego kodu](06_refaktoryzacja_starego_kodu.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Oddzielamy polecenia GDB od LLDB i narzędzi Windows. Najpierw zachowujemy dowody, potem minimalizujemy przypadek, a po poprawce dodajemy test regresyjny.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [GDB Documentation](https://sourceware.org/gdb/current/onlinedocs/gdb.html/). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
