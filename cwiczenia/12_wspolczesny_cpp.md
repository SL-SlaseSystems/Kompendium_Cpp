[← Mapa działu](../12_wspolczesny_cpp/README.md) · [Spis treści](../README.md)

# Ćwiczenia: migracja o określonym celu

Nie modernizuj kodu na podstawie samego wieku składni. Dla każdej zmiany nazwij problem, zachowanie po zmianie i wymaganą dostępność mechanizmu. Rozwiązanie powinno obejmować również koszt utrzymania starszego środowiska.

## 1. Minimalny standard i koszt zgodności

**Wejście:** biblioteka używa `make_unique`, `if constexpr`, `span` i `expected`. Zespół deklaruje jednocześnie wsparcie C++17. **Oddaj:** tabelę standardów oraz dwie spójne polityki wydania: podniesienie minimum i utrzymanie starszej bazy. Kryterium: publiczne nagłówki działają w deklarowanym trybie. **Wskazówka:** zastąpienie jednego słowa w implementacji nie usuwa nowszego typu z API.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Minimalne standardy to odpowiednio C++14, C++17, C++20 i C++23. Można wymagać C++23 z dostępnymi funkcjami biblioteki albo zapewnić zgodne adaptery widoku i wyniku dla C++17. Adaptery muszą utrzymywać udokumentowaną semantykę i być testowane. Sam warunek na `__cplusplus` nie potwierdza kompletności biblioteki. [Przenośność](../12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md).

</details>

## 2. Wiązanie strukturalne modyfikuje kopię

**Wejście:** `std::map<int, int> counts` ma wpisy `(1,3)` i `(2,5)`. Pętla `for (auto [id, count] : counts)` zwiększa `count`. **Oddaj:** stan mapy po pętli i poprawkę zmieniającą wartości. Zbadaj próbę zmiany klucza oraz mapę, której wartością jest `unique_ptr`. **Wskazówka:** rozpakowanie nie usuwa reguł kopiowania ani const klucza.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Mapa pozostaje bez zmian: zwiększano składową ukrytej kopii pary. `auto& [id,count]` pozwala modyfikować wartości w miejscu, dając 4 i 6. Klucz nadal jest const, aby nie naruszyć struktury mapy. Wersja kopiująca nie zadziała dla pary z niekopiowalnym `unique_ptr`; wersja referencyjna nie wymaga jego kopii. [C++17](../12_wspolczesny_cpp/02_cpp17.md).

</details>

## 3. Gałąź zależna od typu

**Wejście:** funkcja szablonowa zwraca `x.size()`, jeśli typ wspiera tę operację, a dla pojedynczej wartości zwraca 1. Zwykły `if` powoduje błąd dla `int`. **Oddaj:** szkic wyboru C++23 i kontrakt typu wyniku. Sprawdź pusty string, tablicę wartości i pojedynczą liczbę. **Wskazówka:** oba ramiona zwykłego if muszą być poprawne po instancjacji.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Użyj `if constexpr` z zależnym `requires { x.size(); }`; nieinstancjonowana gałąź nie żąda tej metody od `int`. Ustal wspólny typ wyniku, np. `size_t`, i wymagaj zgodności wyniku metody z tym typem. Dla standardowego kontenera wynik pustego zakresu to zero; surowa tablica nie ma metody i w tym szkicu da 1. Jeśli oczekujesz długości tablicy, zmień kontrakt na `ranges::size`. [C++20](../12_wspolczesny_cpp/03_cpp20.md).

</details>

## 4. Lambda dłuższa niż właściciel

**Wejście:** metoda obiektu zwraca callback `[this] { return state_; }`; kolejka wykonuje go po zniszczeniu obiektu. Autor zmienia przechwycenie na `[=]`. **Oddaj:** ocenę poprawki i wybór między migawką a obserwacją żywego obiektu. Uwzględnij koszt kopii i wygaśnięcie obserwacji. **Wskazówka:** kopiowanie wskaźnika nie kopiuje wskazywanego obiektu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

`[=]` nie naprawia czasu życia: odwołanie do pola nadal korzysta z przechwyconego `this`. Dla migawki przechwyć potrzebną wartość, np. `state = state_`, albo świadomie kopię `*this`, jeśli typ jest kopiowalny. Dla obserwacji współdzielonego obiektu przechwyć `weak_ptr` i sprawdź `lock`; opisz wynik braku właściciela. [Ewolucja lambd](../12_wspolczesny_cpp/02_cpp17.md).

</details>

## 5. Referencja zachowana w ramce korutyny

**Wejście:** leniwa korutyna `use(const std::string& text)` zaczyna ciało dopiero po wznowieniu. Klient zapisuje wynik `use(std::string{"abc"})` i wznawia go w następnym wierszu. **Oddaj:** oś lifetime i naprawę parametrów. Kryterium: treść pozostaje dostępna po początkowym zawieszeniu. **Wskazówka:** ramka przechowująca referencję nadal nie jest właścicielem argumentu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Tymczasowy string znika na końcu pełnego wyrażenia tworzącego zadanie, przed pierwszym wznowieniem. Przyjęcie stringa przez wartość pozwala przenieść posiadaną wartość do ramki. Alternatywnie klient musi gwarantować życie zewnętrznego właściciela aż do ostatniego użycia. Własność ramki i prawo do jej zniszczenia wymagają odrębnego kontraktu. [Korutyny](../12_wspolczesny_cpp/05_korutyny.md).

</details>

## 6. Adapter, którego fallback nigdy nie widział CI

**Wejście:** biblioteka wybiera `std::byteswap`, jeśli istnieje `<bit>`. Wszystkie komputery autorów mają nową bibliotekę, lecz klient używa starszej. **Oddaj:** warunek wykrywania i macierz dwóch konfiguracji testowych. Uwzględnij wartości 0, pojedynczy ustawiony bajt i dwukrotne odwrócenie. **Wskazówka:** obecność nagłówka jest słabszą informacją niż poziom obsługi funkcji.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Sprawdź `__cpp_lib_byteswap >= 202110L` po właściwym nagłówku lub `<version>`, osłaniając również użycie nazwy. Dodaj prywatną opcję projektu wymuszającą fallback i buduj obie gałęzie. Dla określonego typu i szerokości bajtu porównaj z oczekiwaną permutacją oraz własnością podwójnego odwrócenia. Nie definiuj ręcznie makr standardowych. [Feature-test macros](../12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md).

</details>
