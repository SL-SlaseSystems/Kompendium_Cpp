[← Główny spis treści](../README.md)

# 24. Messaging i systemy rozproszone

Celem działu jest modelować awarie częściowe, dostarczenie wiadomości i spójność przepływu biznesowego. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Kolejki brokerzy i delivery](01_kolejki_brokerzy_i_delivery.md)
2. [Retry backoff i idempotencja](02_retry_backoff_i_idempotencja.md)
3. [Eventual consistency i sagi](03_eventual_consistency_i_sagi.md)
4. [RabbitMQ Kafka i NATS](04_rabbitmq_kafka_i_nats.md)
5. [Outbox inbox i deduplication](05_outbox_inbox_i_deduplication.md)
6. [Case study system zamówień](06_case_study_system_zamowien.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Nie obiecujemy exactly once bez określenia zakresu. Retry obejmuje timeout, backoff, jitter, limit prób i idempotencję, a deduplikacja ma trwały klucz.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [RabbitMQ Reliability Guide](https://www.rabbitmq.com/docs/reliability). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
