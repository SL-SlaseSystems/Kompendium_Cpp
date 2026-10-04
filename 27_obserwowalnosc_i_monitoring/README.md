[← Główny spis treści](../README.md)

# 27. Obserwowalność i monitoring

Celem działu jest łączyć logi, metryki i ślady w dowody przydatne podczas incydentu bez niekontrolowanego kosztu. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Logi strukturalne i korelacja](01_logi_strukturalne_i_korelacja.md)
2. [Metryki i histogramy](02_metryki_i_histogramy.md)
3. [Tracing i OpenTelemetry](03_tracing_i_opentelemetry.md)
4. [Health readiness i liveness](04_health_readiness_i_liveness.md)
5. [Crash reporting i symbole](05_crash_reporting_i_symbole.md)
6. [Case study incydent produkcyjny](06_case_study_incydent_produkcyjny.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Kontrolujemy cardinality, sampling, retencję i redakcję. Identyfikatory korelacji nie zastępują modelu przyczynowego, a symbole debugowe przechowujemy zgodnie z wersją artefaktu.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [OpenTelemetry Observability Primer](https://opentelemetry.io/docs/concepts/observability-primer/). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
