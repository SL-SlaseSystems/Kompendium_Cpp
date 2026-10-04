[← Główny spis treści](../README.md)

# 12. Współczesny C++

Współczesny C++ jest ciągłą ewolucją języka i biblioteki. Dział porządkuje mechanizmy od C++11 do C++23, pokazuje korutyny oraz uczy sprawdzać dostępność przez feature-test macros zamiast zgadywać na podstawie numeru kompilatora.

## Wymagania wstępne

Warto wcześniej przejść podstawową ścieżkę języka, biblioteki standardowej, budowania i współbieżności. Ten dział jest mapą ewolucji, nie zastępstwem tematów szczegółowych.

## Efekty uczenia się

- rozpoznajesz mechanizmy wprowadzone w kolejnych standardach;
- dobierasz współczesny idiom zamiast historycznego obejścia;
- odróżniasz opublikowany standard od stanu implementacji;
- rozumiesz rolę coroutine frame, promise i awaitera;
- sprawdzasz możliwości toolchainu przez feature-test macros i test konfiguracji.

## Kolejność rozdziałów

1. [C++11 i C++14](01_cpp11_14.md)
2. [C++17](02_cpp17.md)
3. [C++20](03_cpp20.md)
4. [C++23](04_cpp23.md)
5. [Korutyny](05_korutyny.md)
6. [Feature-test macros i przenośność](06_feature_test_macros_i_przenosnosc.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak pracować

Kompiluj przykłady w deklarowanym trybie standardu. Gdy funkcja jest niedostępna, ustal osobno wsparcie frontendu i biblioteki. Kod przenośny powinien mieć minimalny wymagany standard, test możliwości oraz świadomą ścieżkę alternatywną.

## Pułapki

- traktowanie numeru wersji kompilatora jako kompletnej macierzy funkcji;
- używanie eksperymentalnego API bez zaznaczenia statusu;
- makra wersji zamiast feature-test macro;
- ręczne implementowanie funkcji już obecnej w nowszym standardzie bez planu migracji;
- mylenie mechaniki korutyn ze standardowym runtime async.

## Samoocena

Potrafisz wskazać minimalny standard dla używanego mechanizmu, sprawdzić dostępność, przygotować czytelny fallback i wyjaśnić, dlaczego kod „C++23” może zależeć także od konkretnej wersji biblioteki standardowej.

## Co dalej

Przejdź do [wzorców, API i wydajności](../13_wzorce_api_i_wydajnosc/README.md), aby użyć współczesnych mechanizmów w stabilnym projekcie.
