[← Główny spis treści](../README.md)

# 10. Współbieżność

Współbieżność wymaga myślenia o ownership, synchronizacji i kolejności zdarzeń. Ten dział zaczyna od zarządzanego wątku, przechodzi przez blokady i zadania, a kończy na atomikach oraz koordynacji wielu uczestników.

## Wymagania wstępne

Potrzebujesz RAII, move semantics, obsługi błędów, callable objects oraz umiejętności testowania i diagnozowania kodu.

## Efekty uczenia się

- zarządzasz lifetime wątku przez `jthread` i `stop_token`;
- chronisz inwariant, a nie pojedyncze pole;
- stosujesz condition variable z predykatem;
- przekazujesz wynik i wyjątek przez future/promise;
- rozumiesz data race, happens-before i podstawowe memory ordering;
- koordynujesz fazy pracy przez latch, barrier i semaphore.

## Kolejność rozdziałów

1. [thread, jthread i stop_token](01_thread_jthread_i_stop_token.md)
2. [mutex, lock i condition_variable](02_mutex_lock_i_condition_variable.md)
3. [future, promise i async](03_future_promise_async.md)
4. [Atomiki i model pamięci](04_atomiki_i_model_pamieci.md)
5. [latch, barrier i semaphore](05_latch_barrier_semaphore.md)
6. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Bezpieczna praca

Testy muszą mieć limit czasu i deterministyczny mechanizm zakończenia. Nie używaj `sleep` jako dowodu synchronizacji. Race condition diagnozuj ThreadSanitizerem, jeśli toolchain go wspiera, lecz pamiętaj, że brak raportu nie jest dowodem poprawności modelu pamięci.

## Pułapki

- odłączony wątek korzystający z wygasłych danych;
- blokada obejmująca callback lub wolne I/O;
- czekanie bez predykatu;
- data race na pozornie „prostym” liczniku;
- użycie atomika bez argumentu happens-before.

## Samoocena

Potrafisz narysować relacje synchronizes-with i happens-before, wskazać właściciela danych, zapewnić zatrzymanie wszystkich wątków i napisać test, który nie zależy od szczęśliwego harmonogramu.

## Co dalej

Przejdź do [I/O i systemu](../11_io_i_system/README.md), gdzie współbieżność spotyka się z operacjami blokującymi i zasobami systemowymi.
