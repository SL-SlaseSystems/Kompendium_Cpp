[← Główny spis treści](../README.md)

# 25. Kontenery i produkcja

Celem działu jest zbudować mały artefakt runtime i uruchamiać proces C++ z ograniczonymi uprawnieniami. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Kontenery i proces C++](01_kontenery_i_proces_cpp.md)
2. [Dockerfile wieloetapowy i hardening](02_dockerfile_wieloetapowy_i_hardening.md)
3. [Docker compose i zależności](03_docker_compose_i_zaleznosci.md)
4. [Konfiguracja limity i sygnały](04_konfiguracja_limity_i_sygnaly.md)
5. [Healthcheck debugowanie i case study](05_healthcheck_debugowanie_i_case_study.md)
6. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Kompilator pozostaje w etapie build. Runtime działa jako użytkownik bez roota, zna zależności dynamiczne, obsługuje sygnały i nie wymaga zapisu poza wyznaczonymi ścieżkami.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
