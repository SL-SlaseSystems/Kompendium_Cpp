[← Główny spis treści](../README.md)

# 05. Szablony i generyczność

Szablony pozwalają pisać kod dla wielu typów, ale najważniejszym problemem jest kontrakt: jakie operacje są wymagane i jak błąd ma zostać pokazany użytkownikowi. Dział prowadzi od prostych szablonów do concepts i obliczeń czasu kompilacji.

## Wymagania wstępne

Potrzebujesz swobody w czytaniu funkcji, klas, przeciążeń, referencji, copy/move i operatorów.

## Efekty uczenia się

- tworzysz szablony funkcji i klas bez niepotrzebnej generalizacji;
- przewidujesz podstawowe reguły dedukcji `auto`, `decltype` i CTAD;
- rozróżniasz specjalizację, przeciążenie i SFINAE;
- zapisujesz kontrakty przez `concept` i `requires`;
- stosujesz parameter packs i fold expressions;
- przenosisz uzasadnione obliczenia do compile time.

## Kolejność rozdziałów

1. [Szablony funkcji i klas](01_function_i_class_templates.md)
2. [Dedukcja, auto, decltype i CTAD](02_dedukcja_auto_decltype_i_ctad.md)
3. [Specialization i SFINAE](03_specialization_i_sfinAE.md)
4. [Concepts i requires](04_concepts_i_requires.md)
5. [Variadic templates i fold expressions](05_variadic_templates_i_fold.md)
6. [constexpr, consteval i metaprogramowanie](06_constexpr_consteval_i_metaprogramowanie.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak pracować

Zaczynaj od konkretnej funkcji i uogólniaj dopiero po drugim rzeczywistym przypadku. Dla każdego szablonu zapisz wymagane wyrażenia oraz typ wyniku. Porównuj diagnostykę bez constraints i z dobrze nazwanym conceptem.

## Pułapki

- szablon „na zapas”, który ma tylko jedno użycie;
- mylenie forwarding reference ze zwykłą referencją rvalue;
- specjalizacja funkcji, gdy czytelniejsze jest przeciążenie;
- concept sprawdzający składnię, ale nie semantykę deklarowanego kontraktu;
- niekontrolowany wzrost czasu kompilacji i rozmiaru kodu.

## Samoocena

Potrafisz zaprojektować mały algorytm generyczny, ograniczyć go czytelnym conceptem, wyjaśnić wynik dedukcji i zinterpretować błąd instancjacji bez przypadkowego dodawania `typename`, `template` lub `std::move`.

## Co dalej

Przejdź do [biblioteki standardowej](../06_biblioteka_standardowa/README.md), gdzie generyczne kontrakty spotykają się z kontenerami, iteratorami, algorytmami i ranges.

## Pogłębienie dla osoby programującej w C++

Przed ponowną lekturą rozwiąż scenariusze i uzasadnij odpowiedzi regułą języka lub kontraktem. Wynik eksperymentu porównuj z przewidywaniem; kompilacja nie jest dowodem poprawności wykonania.

- [Projektowanie interfejsów generycznych](07_projektowanie_interfejsow_generycznych.md)

[Sześć zadań z rozwiązaniami](../cwiczenia/05_szablony_i_generycznosc.md) uzupełnia dotychczasowy [zestaw ćwiczeń](ZESTAW-CWICZEN.md). Pełną kolejność pogłębiania opisuje [ścieżka nauki](../sciezka_nauki.md).
