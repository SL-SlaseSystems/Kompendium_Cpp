[← Mapa działu](../10_wspolbieznosc/README.md) · [Spis treści](../README.md)

# Ćwiczenia: synchronizacja, postęp i zamykanie

Rysuj zdarzenia i relacje happens-before. Do każdego oczekiwania dopisz warunek zakończenia. Test obciążeniowy jest uzupełnieniem tego rozumowania: brak zaobserwowanego zakleszczenia nie stanowi dowodu postępu wszystkich dozwolonych przeplotów.

## 1. Zatrzymanie, którego nikt nie słyszy

**Wejście:** `jthread` czeka na zwykłej `condition_variable` z predykatem `!queue.empty()`. Właściciel niszczy wątek, a kolejka pozostaje pusta. **Oddaj:** wyjaśnienie zawieszenia i dwa kompletne protokoły zatrzymania. Uwzględnij żądanie stop przed wejściem w oczekiwanie. **Wskazówka:** żądanie zatrzymania nie przerywa dowolnej blokującej operacji.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Destruktor żąda stop i dołącza wątek, lecz zwykłe oczekiwanie nie obserwuje tokenu. Możesz zamykać kolejkę pod mutexem, dodać `closed` do predykatu i powiadomić oczekujących albo użyć wspieranego oczekiwania `condition_variable_any` z tokenem. W obu protokołach warunek musi być sprawdzany przed zaśnięciem; samo jednorazowe powiadomienie może zginąć. [Zatrzymywanie](../10_wspolbieznosc/01_thread_jthread_i_stop_token.md).

</details>

## 2. Flaga nie publikuje danych przez magię

**Wejście:** producent zapisuje nieatomowy `payload`, potem ustawia atomowe `ready` z `relaxed`. Konsument czyta flagę z `relaxed` i po true odczytuje payload. Publikacja występuje tylko raz. **Oddaj:** brakującą relację i poprawne porządki pamięci. Wyjaśnij, dlaczego wielokrotne użycie bufora wymaga dalszego protokołu. **Wskazówka:** atomowość flagi nie synchronizuje automatycznie pozostałych pól.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Zapis flagi z release i odczyt acquire obserwujący ten zapis tworzą synchronizację; wcześniejsze zapisy payload stają się widoczne konsumentowi. Po publikacji producent nie może nadal modyfikować odczytywanego payload bez dodatkowej ochrony. Przy ponownym użyciu potrzebne jest potwierdzenie zakończenia odczytu, mutex lub inny udowodniony protokół własności. [Model pamięci](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md).

</details>

## 3. Atomowe operacje, nieatomowy niezmiennik

**Wejście:** licznik dostępnych biletów to atomowy `int` o wartości 1. Dwa wątki wykonują „jeśli load > 0, to fetch_sub(1) i sukces”. **Oddaj:** przeplot sprzedający dwa bilety i poprawkę zachowującą nieujemność. Sprawdź początkowe zero oraz konieczność ponowienia CAS. **Wskazówka:** sprawdzenie i zmiana muszą stanowić jedną logiczną operację.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Oba wątki mogą odczytać 1 przed pierwszym odejmowaniem i oba zgłosić sukces, pozostawiając -1. Najprościej chroń całość mutexem. Alternatywnie CAS zamienia dodatnie `current` na `current-1`; po porażce używa odświeżonej wartości i ponawia sprawdzenie. Dla samego licznika odpowiednie może być relaxed, ale nie publikuje ono danych biletu. [Atomiki](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md).

</details>

## 4. Zamknięcie pełnej kolejki

**Wejście:** kolejka o pojemności 2 zawiera A i B; producent czeka z C. Właściciel wywołuje `close`. Kontrakt wymaga opróżnienia przyjętych elementów i odrzucenia nowych. **Oddaj:** predykaty `push` i `pop`, wyniki po zamknięciu oraz test pustej kolejki. **Wskazówka:** zamknięcie powinno budzić obie grupy oczekujących.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Producent czeka na `closed || size < capacity`, a po obudzeniu odrzuca operację, jeśli zamknięto kolejkę. Konsument czeka na `closed || !empty`; zwraca A i B, a potem sygnał końca. Zmiany stanu i sprawdzanie predykatów odbywają się pod tym samym mutexem. `close` powiadamia producentów i konsumentów; jest idempotentne. [Backpressure i zamykanie](../10_wspolbieznosc/06_kolejka_backpressure_i_zamykanie.md).

</details>

## 5. Równoległe zadania wykonane po kolei

**Wejście:** pętla trzy razy wywołuje `std::async(std::launch::async, work)` i odrzuca zwracany future. Każde zadanie trwa sekundę. **Oddaj:** wyjaśnienie możliwego czasu około trzech sekund i poprawkę zbierającą wyniki oraz błędy. **Wskazówka:** zniszczenie ostatniego uchwytu do stanu z async może czekać na zakończenie.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Tymczasowy future jest niszczony na końcu każdego wyrażenia, więc oczekiwanie może serializować pętlę. Zachowaj wszystkie future, dopiero potem wywołuj `get`, które również przekazuje wyjątek. Obsłuż każdy wynik, także gdy poprzedni zgłosi błąd. Bez jawnego `launch::async` domyślna polityka dopuszcza odroczenie wykonania. [Future i async](../10_wspolbieznosc/03_future_promise_async.md).

</details>

## 6. Dwa rachunki, dwie kolejności blokad

**Wejście:** transfer A→B blokuje mutex A, potem B; transfer B→A robi odwrotnie. **Oddaj:** przeplot zakleszczenia i implementacyjny plan blokowania dwóch różnych rachunków. Uwzględnij transfer rachunku do samego siebie oraz wyjątek walidacji. **Wskazówka:** RAII zwalnia posiadaną blokadę, lecz samo nie zapobiega cyklowi oczekiwań.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Każdy wątek może trzymać pierwszy mutex i czekać na drugi. Dla różnych rachunków użyj `std::scoped_lock` z dwoma mutexami albo konsekwentnego globalnego porządku. Ten sam rachunek obsłuż osobno, aby nie próbować podwójnie blokować tego samego nierkurencyjnego mutexu. Walidacja ma pozostawiać niezmiennik; RAII zwolni blokady przy wyjątku. [Mutexy](../10_wspolbieznosc/02_mutex_lock_i_condition_variable.md).

</details>
