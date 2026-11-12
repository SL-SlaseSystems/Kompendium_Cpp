[← Mapa działu](../05_szablony_i_generycznosc/README.md) · [Spis treści](../README.md)

# Ćwiczenia: wymagania zamiast przypadkowych ograniczeń

Dla każdego interfejsu zbuduj zestaw typów akceptowanych i odrzucanych. Oddziel to, co można sprawdzić w wyrażeniu `requires`, od właściwości semantycznych, które muszą pozostać opisanym kontraktem i przedmiotem testów.

## 1. Trzy deklaracje, różne aliasowanie

**Wejście:** `const int n = 7; auto a = n; auto& b = n; decltype(auto) c = (n);`. **Oddaj:** dokładne typy, informację o nowym obiekcie lub aliasie i ocenę próby przypisania 8 do każdej zmiennej. Zmień następnie `n` na nieconst. **Wskazówka:** nawiasy mają znaczenie dla `decltype`.

<details><summary>Rozwiązanie i uzasadnienie</summary>

`a` ma typ `int` i jest osobną kopią; `b` oraz `c` mają typ `const int&`. Modyfikacja `a` jest dozwolona, pozostałych nie. Po usunięciu `const` dwa odwołania mają typ `int&` i ich modyfikacja zmienia `n`. Samo `decltype(n)` daje typ deklarowany, a `decltype((n))` uwzględnia lvalue. [Dedukcja](../05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md).

</details>

## 2. Nazwana referencja do rvalue

**Wejście:** wrapper ma dedukowany parametr `T&& x` i przekazuje `x` do przeciążeń `consume(Item&)` oraz `consume(Item&&)`. **Oddaj:** dedukcję dla zmiennej `Item`, zmiennej `const Item` i tymczasowego `Item`; popraw przekazanie. Kryterium: const nie znika, a lvalue nie jest bezwarunkowo przenoszone. **Wskazówka:** nazwa parametru jest wyrażeniem lvalue.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Dedukowane `T` to odpowiednio `Item&`, `const Item&` i `Item`. Po zwinięciu referencji parametry mają typy `Item&`, `const Item&`, `Item&&`. Użyj `std::forward<T>(x)`. Dwa podane przeciążenia nie obsłużą const lvalue, więc wrapper powinien je odrzucić czytelnym wymaganiem albo świadomie dodać obsługę `const Item&`. [Projektowanie przekazywania](../05_szablony_i_generycznosc/07_projektowanie_interfejsow_generycznych.md).

</details>

## 3. Wyszukiwanie w strumieniu bez kopiowania

**Wejście:** funkcja `contains` ma jedynie zwracać bool i działać dla wektora oraz jednoprzebiegowego zakresu wejściowego. Element może być niekopiowalny. **Oddaj:** wymagania i pseudokod bez `size`, sortowania i materializacji. Sprawdź pusty zakres oraz trafienie w pierwszym elemencie. **Wskazówka:** wynik bool nie pożycza iteratora od argumentu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Wystarczy zakres wejściowy oraz dopuszczalne porównanie referencji elementu z szukaną wartością dające wynik interpretowalny jako bool. Przechodź raz i zakończ po trafieniu; pusty zakres daje false. Nie wymagaj `random_access_range`, kopiowania elementów ani znajomości rozmiaru. Kontrakt uprzedza, że zakres wejściowy może zostać zużyty. [Interfejs generyczny](../05_szablony_i_generycznosc/07_projektowanie_interfejsow_generycznych.md).

</details>

## 4. Koncept przepuszcza cykliczny comparator

**Wejście:** comparator na liczbach 0, 1, 2 uznaje `0<1`, `1<2` i `2<0`; jego wywołanie zwraca bool i przechodzi sprawdzenie `std::strict_weak_order` na poziomie składni. **Oddaj:** naruszoną własność i minimalny test kontrprzykładu. **Wskazówka:** nazwa konceptu nie oznacza automatycznego dowodu matematycznego.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Naruszona jest przechodniość: z porównań `(0,1)` oraz `(1,2)` powinno wynikać `(0,2)`, tymczasem comparator twierdzi odwrotnie. Koncept może sprawdzić dostępność operacji i typ wyniku, lecz nie dowodzi tej własności dla całej dziedziny. Funkcja nie modeluje wymaganego konceptu semantycznie; nie wolno przekazywać jej do sortowania. [Concepts](../05_szablony_i_generycznosc/04_concepts_i_requires.md).

</details>

## 5. Pusty pakiet jako przypadek projektowy

**Wejście:** biblioteka implementuje `all`, `any` i sumę argumentów przez jednoargumentowe fold expressions. Klient wywołuje każdą funkcję bez argumentów. **Oddaj:** wyniki dwóch pierwszych i świadomą politykę sumy. Uwzględnij niejednorodne typy liczbowe. **Wskazówka:** nie każdy operator ma domyślną wartość dla pustego foldu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Pusty fold `&&` daje true, a `||` false. Pusty jednoargumentowy fold `+` jest niepoprawny. Odrzuć pustą sumę wymaganiem albo przyjmij jawny typ akumulatora oraz jego zero. Dopisanie literału `0` w binarnym foldzie wprowadza `int` do dedukcji i konwersji, co trzeba uwzględnić w kontrakcie. [Fold expressions](../05_szablony_i_generycznosc/05_variadic_templates_i_fold.md).

</details>

## 6. Obliczenie stałe a obowiązek kompilacji

**Wejście:** `square` jest `constexpr`, `checked_id` jest `consteval`, a `read()` pobiera liczbę podczas wykonania. **Oddaj:** ocenę `square(read())`, `checked_id(read())` i `constexpr auto k = square(4)`. Zaproponuj API walidacji działające w obu momentach bez dublowania reguł. **Wskazówka:** możliwość obliczenia podczas kompilacji i wymóg takiego obliczenia są różne.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Pierwsze wywołanie może działać podczas wykonania; drugie jest niepoprawne, bo bezpośrednie wywołanie funkcji natychmiastowej wymaga stałego wyrażenia. Trzecie wymusza stałe obliczenie i daje 16. Wspólną czystą walidację umieść w `constexpr`, a osobne wejścia określają politykę raportowania i moment wymaganego sprawdzenia. [Stałe obliczenia](../05_szablony_i_generycznosc/06_constexpr_consteval_i_metaprogramowanie.md).

</details>
