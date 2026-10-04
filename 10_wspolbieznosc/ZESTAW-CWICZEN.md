[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Ćwiczenia — współbieżność

Każdy program ma mieć ograniczony czas wykonania i kontrolowane zatrzymanie. Kod z potencjalnym data race uruchamiaj wyłącznie jako test pod ThreadSanitizerem albo analizuj bez wykonywania.

## Poziom 1 — wątki i lifetime

1. Uruchom pracę w `jthread` i pozwól RAII wykonać join.
2. Przekaż dane przez wartość i przez referencję, porównując lifetime.
3. Dodaj kooperatywne zatrzymanie przez `stop_token`.
4. Znajdź odłączony wątek używający obiektu lokalnego.
5. Zapewnij propagację wyjątku z zadania do właściciela.

## Poziom 2 — blokady

6. Chroń wspólny inwariant jednym mutexem.
7. Użyj `scoped_lock` dla dwóch mutexów bez deadlocka.
8. Skróć critical section, przenosząc I/O poza blokadę.
9. Zbuduj kolejkę z condition variable i predykatem.
10. Obsłuż zakończenie konsumenta bez czekania w nieskończoność.

## Poziom 3 — zadania

11. Zwróć wartość przez `promise` i `future`.
12. Przenieś wyjątek przez future i sprawdź go w teście.
13. Porównaj polityki `std::async` bez zakładania zawsze nowego wątku.
14. Zbuduj pulę dwóch prostych workerów z kolejką i shutdown.
15. Dodaj timeout do oczekiwania na wynik.

## Poziom 4 — atomiki

16. Wykryj data race zwykłego licznika przez ThreadSanitizer.
17. Zastąp licznik atomikiem i uzasadnij ordering.
18. Zapisz relację publikacji danych przez release/acquire.
19. Wyjaśnij, dlaczego `relaxed` nie publikuje zwykłych pól.
20. Porównaj `compare_exchange_weak` w pętli z wersją strong.

## Poziom 5 — koordynacja i testy

21. Użyj latch do wspólnego startu grupy workerów.
22. Użyj barrier do dwóch faz obliczenia.
23. Ogranicz równoległość semaforem.
24. Napisz test synchronizacji bez `sleep_for`.
25. Dodaj watchdog kończący test po przekroczeniu limitu.

## Zadanie końcowe

Zbuduj ograniczoną kolejkę producent–konsument z `jthread`, condition variable i kontrolowanym shutdown. Dodaj wielu producentów i konsumentów, limit pojemności, propagację błędu oraz testy pustej kolejki, pełnej kolejki i zatrzymania. Uruchom zestaw wielokrotnie oraz pod ThreadSanitizerem, jeśli dostępny, i opisz relacje happens-before.
