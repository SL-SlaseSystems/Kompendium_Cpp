[← Główny spis treści](../README.md)

# 22. Bazy danych i trwałość

Celem działu jest łączyć model danych, transakcje i RAII bez mylenia gwarancji bazy z gwarancjami wrappera C++. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [SQL i model relacyjny](01_sql_i_model_relacyjny.md)
2. [SQLite i RAII połączenia](02_sqlite_i_raii_polaczenia.md)
3. [Transakcje i poziomy izolacji](03_transakcje_i_poziomy_izolacji.md)
4. [Prepared statements i bezpieczeństwo](04_prepared_statements_i_bezpieczenstwo.md)
5. [Migracje pooling i odporność](05_migracje_pooling_i_odpornosc.md)
6. [Repozytoria i case study](06_repozytoria_i_case_study.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Zapytania parametryzujemy, ownership uchwytów zamykamy w RAII, a rollback testujemy. Poziom izolacji i trwałość opisujemy dla konkretnego silnika oraz konfiguracji.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [SQLite Documentation](https://www.sqlite.org/docs.html). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
