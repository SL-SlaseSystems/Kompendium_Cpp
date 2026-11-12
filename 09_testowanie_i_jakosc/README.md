[← Główny spis treści](../README.md)

# 09. Testowanie i jakość

Jakość programu C++ wymaga kilku niezależnych sygnałów: testów zachowania, ostrzeżeń, analizy statycznej, sanitizerów, debuggera, benchmarków i fuzzingu. Żadne z tych narzędzi pojedynczo nie dowodzi poprawności.

## Wymagania wstępne

Powinieneś rozumieć kontrakty, RAII, strukturę wieloplikowego projektu i podstawy CMake.

## Efekty uczenia się

- piszesz małe testy zachowania i integracji;
- utrzymujesz ostrzeżenia jako część jakości, nie jako hałas;
- dobierasz sanitizer do klasy błędu;
- diagnozujesz awarię debuggerem;
- projektujesz benchmark odporny na typowe zniekształcenia;
- wykorzystujesz fuzzing i testy właściwości dla dużej przestrzeni wejść.

## Kolejność rozdziałów

1. [Testy jednostkowe i integracyjne](01_testy_jednostkowe_i_integracyjne.md)
2. [Ostrzeżenia i analiza statyczna](02_ostrzezenia_i_analiza_statyczna.md)
3. [Sanitizery i debuggery](03_sanitizery_i_debuggery.md)
4. [Benchmarki i profilowanie](04_benchmarki_i_profilowanie.md)
5. [Fuzzing i property-based testing](05_fuzzing_i_property_based_testing.md)
6. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak pracować

Każdy test powinien nazywać błąd, który wykrywa. Obserwuj test najpierw na błędnej implementacji. Sanitizery uruchamiaj w osobnych konfiguracjach i czytaj pierwszy raport. Benchmarki powtarzaj w kontrolowanym środowisku, a wynik zapisuj razem z konfiguracją.

## Pułapki

- testowanie prywatnej struktury zamiast kontraktu;
- mockowanie kodu, którego zachowanie miało zostać sprawdzone;
- ignorowanie ostrzeżeń zależnych od platformy bez analizy;
- łączenie niekompatybilnych sanitizerów w jeden build;
- optymalizator usuwający pracę benchmarku.

## Samoocena

Potrafisz odtworzyć błąd testem, zobaczyć RED, naprawić go do GREEN, a następnie dobrać analizę dynamiczną lub statyczną dla klasy problemu, której test przykładowy nie wyczerpuje.

## Co dalej

Przejdź do [współbieżności](../10_wspolbieznosc/README.md), gdzie testowanie musi uwzględnić nondeterminizm i model pamięci.

## Pogłębienie dla osoby programującej w C++

Przed ponowną lekturą rozwiąż scenariusze i uzasadnij odpowiedzi regułą języka lub kontraktem. Wynik eksperymentu porównuj z przewidywaniem; kompilacja nie jest dowodem poprawności wykonania.

[Sześć zadań z rozwiązaniami](../cwiczenia/09_testowanie_i_jakosc.md) uzupełnia dotychczasowy [zestaw ćwiczeń](ZESTAW-CWICZEN.md). Pełną kolejność pogłębiania opisuje [ścieżka nauki](../sciezka_nauki.md).
