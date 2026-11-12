[← Spis treści](README.md)

# Dalsza nauka i specjalizacje

Po przejściu podstaw wybierz ścieżkę odpowiadającą projektom. Każda specjalizacja nadal wymaga solidnego lifetime, RAII, testów i narzędzi diagnostycznych.

Jeśli już programujesz w C++, zacznij od [diagnozy 24 problemów](test_diagnostyczny.md) i [pogłębionej ścieżki](sciezka_nauki.md). Do każdej specjalizacji wracaj z konkretnym projektem i dowodami jego poprawności. [Laboratoria](praktyka/README.md) oraz [zadania działowe](cwiczenia/README.md) pomagają sprawdzić, czy umiesz zastosować mechanizm poza przykładem z rozdziału.

## Narzędzia CLI

Przejdź wprowadzenie, typy, RAII, string, kontenery, błędy, filesystem, chrono i CMake. Dodaj parsowanie argumentów przez bibliotekę zewnętrzną tylko po zdefiniowaniu modelu konfiguracji. Ćwiczenie: narzędzie indeksujące pliki, używające `filesystem`, `expected` lub jawnego typu błędu oraz testów katalogu tymczasowego.

## Backend i usługi

Przeczytaj ownership, concurrency, coroutines, sieć/serializację, dependency injection i profiling. Następnie wybierz jeden ekosystem I/O, np. Boost.Asio, i naucz się jego executora, cancellation oraz backpressure. Ćwiczenie: serwis z limitami rozmiaru, deadline, structured logging i testowalnym zegarem.

## Systemy i biblioteki niskopoziomowe

Po części głównej przejdź kolejno cały katalog [zaawansowane](zaawansowane/README.md). Szczególny nacisk połóż na UB, lifetime/provenance, layout, allocators, ABI i sanitizery. Ćwiczenie: mały kontener RAII z ręcznym storage, silną exception safety i testami ASan/UBSan — edukacyjnie, nie jako zamiennik STL.

## Embedded i real-time

Skup się na storage duration, allocation policy, `constexpr`, atomikach, fixed-capacity containers i toolchainie platformy. Freestanding C++ zapewnia tylko odpowiedni podzbiór języka i biblioteki; sprawdź dokumentację konkretnej implementacji. Ćwiczenie: kolejka o stałej pojemności bez dynamicznej alokacji, z jawnym overflow policy i testami hostowymi.

## Gry i grafika

Potrzebujesz value semantics, layout, cache locality, allocators/PMR, SIMD, concurrency oraz profilowania. API grafiki i silniki są zewnętrzne. Ćwiczenie: prosty ECS lub pipeline cząstek, porównujący Array of Structures i Structure of Arrays na realistycznym profilu.

## Tworzenie bibliotek

Przejdź szablony, concepts, API/ABI, CMake, zależności, ODR, moduły i feature-test macros. Zdefiniuj minimalny standard, wspierane toolchainy, politykę wyjątków oraz własności. Ćwiczenie: mała biblioteka z targetem CMake, install/export config, testami konsumenta i kontrolą exported symbols.

## Wysoka współbieżność

Najpierw mutexy, condition variables i atomiki seq_cst. Dopiero potem zaawansowane memory ordering, lock-free, ABA i reclamation. Korzystaj z literatury algorytmów oraz formalnych narzędzi tam, gdzie to możliwe. Ćwiczenie: bounded queue z mutexem i backpressure, profilowana jako baseline przed rozważeniem lock-free.

## Proponowany rytm

Po każdym rozdziale napisz mały program, skompiluj Clangiem i GCC z ostrzeżeniami, uruchom testy pod sanitizerami i wyjaśnij własnymi słowami lifetime każdego wskaźnika lub widoku. Raz w tygodniu przeanalizuj wygenerowany assembly tylko dla zmierzonej gorącej funkcji. Czytaj dokument WG21 lub fragment draftu dopiero po opanowaniu praktycznego problemu, który opisuje.

## Powiązane tematy

- [Główny spis treści](README.md)
- [Ściąga](sciaga.md)
- [Źródła](zrodla.md)

## Ścieżki pogłębienia

Ścieżka systemowa prowadzi przez lifetime, RAII, model pamięci, atomiki, I/O i ABI. Ścieżka biblioteczna skupia się na value semantics, templates, concepts, ranges, testowaniu kompatybilności i projektowaniu publicznego API. Ścieżka wydajnościowa zaczyna się od layoutu danych, cache, profilerów i benchmarków, a dopiero później przechodzi do SIMD lub lock-free.

~~~text
Etap 1: przeczytaj model i przewidź wynik przykładu
Etap 2: zmodyfikuj jeden warunek graniczny
Etap 3: włącz warnings oraz sanitizery
Etap 4: zapisz kontrakt ownership i lifetime
Etap 5: porównaj dwa toolchainy
Etap 6: uzasadnij decyzję pomiarem lub regułą standardu
~~~

Najlepszym ćwiczeniem nie jest przepisywanie kodu, lecz diagnoza: przygotuj minimalną reprodukcję, nazwij przypuszczalną regułę, wybierz narzędzie i spróbuj obalić własną hipotezę. Notuj wersję standardu i kompilatora, aby późniejszy wynik pozostawał odtwarzalny.

