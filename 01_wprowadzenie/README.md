[← Główny spis treści](../README.md)

# 01. Wprowadzenie do C++

Ten dział prowadzi od obrazu języka i jego standardów do samodzielnego zbudowania pierwszego programu. Celem nie jest zapamiętanie poleceń kompilatora, lecz zrozumienie, gdzie kończy się kod źródłowy, a zaczynają frontend, linker, biblioteka standardowa i system operacyjny.

## Wymagania wstępne

Nie jest wymagana znajomość programowania. Przyda się terminal, edytor tekstu oraz kompilator obsługujący C++23. Jeśli korzystasz z IDE, wykonaj przynajmniej raz kompilację ręcznie, aby zobaczyć rzeczywiste etapy procesu.

## Co powinieneś umieć po tym dziale

- odróżnić język C++ od konkretnego kompilatora i biblioteki standardowej;
- wyjaśnić rolę standardów oraz trybu `-std=c++23`;
- sprawdzić wersję i podstawowe możliwości toolchainu;
- skompilować, połączyć i uruchomić mały program;
- rozpoznać błąd kompilacji, linkowania i wykonania.

## Zalecana kolejność

1. [Czym jest C++](01_czym_jest_cpp.md)
2. [Standardy i implementacje](02_standardy_i_implementacje.md)
3. [Kompilatory i toolchain](03_kompilatory_i_toolchain.md)
4. [Pierwszy program](04_pierwszy_program.md)
5. [Proces budowania](05_proces_budowania.md)
6. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak pracować z materiałem

Uruchamiaj polecenia samodzielnie i zapisuj pełną diagnostykę. Zmieniaj po jednej rzeczy: usuń średnik, zadeklaruj funkcję bez definicji, wybierz inny standard. Dzięki temu komunikat błędu przestaje być przypadkowym tekstem, a staje się informacją o konkretnym etapie budowania.

## Najczęstsze pułapki

- utożsamianie „C++” z jednym kompilatorem lub IDE;
- zakładanie, że udana kompilacja oznacza poprawne zachowanie programu;
- mylenie błędu linkera z błędem składni;
- używanie niejawnego, starego standardu zamiast jawnego trybu C++23;
- kopiowanie flag bez sprawdzenia, co robią na danym toolchainie.

## Samoocena

Dział jest opanowany, jeśli potrafisz bez IDE zbudować program z dwóch plików, wskazać etap zgłaszający celowo wprowadzony błąd i wyjaśnić, dlaczego ten sam poprawny program może być kompilowany przez GCC, Clang i MSVC.

## Co dalej

Przejdź do [podstaw języka](../02_podstawy_jezyka/README.md). Do tego działu wracaj, gdy późniejsze materiały wymagają nowych flag kompilatora, osobnego linkowania lub rozróżnienia standardu od implementacji.
