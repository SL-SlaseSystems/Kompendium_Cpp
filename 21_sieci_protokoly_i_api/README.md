[← Główny spis treści](../README.md)

# 21. Sieci, protokoły i API

Celem działu jest budować niezawodną komunikację przez jawny protokół, limity, timeouty i model błędów częściowych. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Modele sieci TCP UDP i DNS](01_modele_sieci_tcp_udp_i_dns.md)
2. [HTTP i REST](02_http_i_rest.md)
3. [TLS certyfikaty i zaufanie](03_tls_certyfikaty_i_zaufanie.md)
4. [Serializacja JSON Protobuf i schema](04_serializacja_json_protobuf_i_schema.md)
5. [Klient HTTP timeouty retry i pooling](05_klient_http_timeouty_retry_i_pooling.md)
6. [Serwer API limity i testy](06_serwer_api_limity_i_testy.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Fragment zależny od biblioteki oznaczamy jako zewnętrzny. Retry nie może ukrywać braku timeoutu, idempotencji ani limitu, a TLS wymaga poprawnej weryfikacji tożsamości.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [RFC Editor — Internet Standards](https://www.rfc-editor.org/standards). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
