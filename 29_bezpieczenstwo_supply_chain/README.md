[← Główny spis treści](../README.md)

# 29. Bezpieczeństwo supply chain

Celem działu jest znać pochodzenie zależności i artefaktów oraz reagować na podatność od triage po poprawkę. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Model zagrożeń secure SDLC i sekrety](01_model_zagrozen_secure_sdlc_i_sekrety.md)
2. [Zależności CVE i SCA](02_zaleznosci_cve_i_sca.md)
3. [SBOM podpisy i proweniencja](03_sbom_podpisy_i_proweniencja.md)
4. [Fuzzing parsowanie i protokoły](04_fuzzing_parsowanie_i_protokoly.md)
5. [Incydenty patchowanie i case study](05_incydenty_patchowanie_i_case_study.md)
6. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

CVE jest identyfikatorem, nie automatycznym werdyktem ryzyka. SBOM opisuje skład, podpis wiąże dane z kluczem, a proweniencja rejestruje proces powstania artefaktu.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [SLSA specification](https://slsa.dev/spec/). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
