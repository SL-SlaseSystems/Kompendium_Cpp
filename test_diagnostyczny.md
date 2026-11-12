[← Spis treści](README.md) · [Ścieżka nauki](sciezka_nauki.md)

# Diagnoza rozumienia C++: 24 problemy

Przyjmij C++23 i standardowe typy oraz nagłówki wskazane w pytaniu. Fragmenty `text` są materiałem do analizy, nie gotowymi jednostkami translacji. Najpierw odpowiedz bez kompilatora. Potem sprawdź uzasadnienie i przejdź do wskazanego działu. Daj sobie 0 punktów za błędny model, 1 za poprawny wynik bez reguły i 2 za wynik wraz z wyjaśnieniem oraz ograniczeniami. Punkty pomagają porównać własne podejście przed nauką i po niej; nie są skalą stanowisk zawodowych.

## 1. Dwa wektory

Po dołączeniu `<vector>`: czym różnią się `std::vector<int> a(3, 7);` i `std::vector<int> b{3, 7};`?

<details><summary>Rozwiązanie i uzasadnienie</summary>

`a` zawiera trzy siódemki; `b` zawiera dwa elementy: 3 i 7. Inicjalizacja listowa preferuje odpowiedni konstruktor `initializer_list`; nawiasy nie są zamienną stylistyką. Przejdź do [inicjalizacji](02_podstawy_jezyka/08_inicjalizacja_i_initializer_list.md).

</details>

## 2. Typ nazwy i typ wyrażenia

Masz `int n = 0;`. Jakie typy oznaczają `decltype(n)` i `decltype((n))`? Czy dodatkowe nawiasy zawsze są obojętne?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Pierwszy to `int`, bo działa szczególna reguła nieujętej w nawiasy nazwy encji. Drugi to `int&`, bo `(n)` jest lvalue. Zmiana jest krytyczna przy `decltype(auto)` i zwracaniu referencji. Zobacz [dedukcję](05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md).

</details>

## 3. Dwa efekty uboczne

`i` ma wartość 0, a `f(int, int)` nie odwołuje się do `i`. Oceń `f(i++, i++);`: UB, jeden wynik czy kilka dozwolonych wyników?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Od C++17 inicjalizacje parametrów są indeterminately sequenced. Do `f` trafi `(0, 1)` albo `(1, 0)`, a po obliczeniu argumentów `i == 2`. Nie stosuj tej odpowiedzi do `i++ + i++`, gdzie brakuje analogicznego uporządkowania i występuje UB. Zobacz [sequencing](02_podstawy_jezyka/09_kolejnosc_ewaluacji_i_sequencing.md).

</details>

## 4. Szerszy wynik

Czy przypisanie `a * b` do `long long` zabezpiecza mnożenie dwóch wartości `int` przed przepełnieniem?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. Najpierw oblicza się iloczyn w typie wynikającym z operandów, dopiero potem konwertuje wynik. Trzeba rozszerzyć operand przed mnożeniem i upewnić się, że nawet szerszy typ mieści wynik. Dla signed overflow zachowanie jest niezdefiniowane. Zobacz [arytmetykę](02_podstawy_jezyka/10_arytmetyka_przepelnienia_i_float.md).

</details>

## 5. Widok na wynik funkcji

`make_name()` zwraca `std::string`. Oceń `std::string_view name = make_name();`, gdy widoku używasz w następnym poleceniu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Tymczasowy string ginie na końcu pełnego wyrażenia inicjalizacji. Widok nie przejmuje własności i nie przedłuża życia stringa; późniejsze czytanie danych jest błędem czasu życia. Zachowaj string jako właściciela albo zwracaj widok na właściciela o odpowiednio długim życiu. Zobacz [widoki](03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md).

</details>

## 6. Pojemność i żywe elementy

Po `std::vector<int> v; v.reserve(100);` przypisujesz `v[0] = 1;`. Czy wystarczy dostępny storage?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. Rozmiar nadal wynosi zero i indeks jest poza zakresem elementów. Użyj `push_back`, `emplace_back` albo `resize` zgodnie z celem. Pojemność nie daje prawa indeksowania. Zobacz [kontenery](06_biblioteka_standardowa/02_vector_array_deque_list.md).

</details>

## 7. Move z obiektu const

Masz `const std::string s = "abc"; std::string t = std::move(s);`. Czy wywołano konstruktor przenoszący stringa?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Standardowy konstruktor przenoszący przyjmuje `string&&`, do którego nie można przywiązać `const string&&`. Dostępny konstruktor kopiujący przyjmie `const string&`. `std::move` zmienia kategorię wyrażenia i zachowuje const; samo nie przenosi zasobu. Zobacz [copy i move](03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md).

</details>

## 8. Gwarantowane elision a NRVO

Typ `T` ma dostępne konstruktor domyślny i destruktor, ale usunięte copy oraz move. Porównaj `T f() { return T{}; }` i `T g() { T x; return x; }`.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Pierwsza funkcja jest poprawna od C++17: prvalue inicjalizuje obiekt wyniku bez pośredniej kopii. Druga nie może polegać na opcjonalnym NRVO; wymagania semantyczne nadal obejmują odpowiednią konstrukcję z `x` i tu są niespełnione. Zobacz [zwracanie wartości](03_pamiec_i_czas_zycia/07_zwracanie_wartosci_elision_i_lifetime.md).

</details>

## 9. Referencja zwrócona do lokalnej zmiennej

Oceń `decltype(auto) f() { int n = 1; return (n); }` w C++23. Czy wywołujący otrzymuje własną liczbę?

<details><summary>Rozwiązanie i uzasadnienie</summary>

W C++23 dedukowany typ to `int&&`: lokalna zmienna w tym kontekście zwrotu jest move-eligible i traktowana jako xvalue. Referencja wskazuje lokalny obiekt, który już nie żyje po wyjściu z funkcji. W starszych regułach tego przykładu można spotkać odpowiedź `int&`; trzeba pilnować wersji standardu. Zwykłe `auto` zwróciłoby `int`. Zobacz [lifetime wyniku](03_pamiec_i_czas_zycia/07_zwracanie_wartosci_elision_i_lifetime.md).

</details>

## 10. Zniszczenie polimorficzne

`Derived` dziedziczy po `Base`; obiekt `Derived` został utworzony zwykłym `new`. Czy zwykłe `delete` przez `Base*` jest bezpieczne, jeśli destruktor bazy jest publiczny i niewirtualny? Nie używamy destroying delete.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. W tym scenariuszu brak wirtualnego destruktora powoduje UB. Samo dodanie innej funkcji virtual nie czyni destruktora wirtualnym. Alternatywą projektu jest zakaz usuwania przez bazę, np. chroniony niewirtualny destruktor, jeśli taki jest zamysł interfejsu. Zobacz [polimorfizm](04_klasy_i_model_obiektowy/05_virtual_override_i_rtti.md).

</details>

## 11. Wyjątek opuszczający noexcept

Funkcja `void commit() noexcept` wywołuje operację, która rzuca. Wyjątek nie zostaje złapany wewnątrz `commit`. Czy wywołujący może obsłużyć go przez `catch`?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie; przy próbie opuszczenia funkcji `noexcept` wywoływane jest `std::terminate`. `noexcept` nie zakazuje składni `throw` wewnątrz i nie jest optymalizacyjną obietnicą bez konsekwencji. Zobacz [exception safety](07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md).

</details>

## 12. Concept i znaczenie operatora

Komparator przyjmuje dwa `int` i zwraca `bool`. Czy to wystarcza, żeby bezpiecznie użyć go w sortowaniu?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. Musi także spełniać wymagania semantyczne, m.in. strict weak ordering. Komparator `a <= b` nie jest irrefleksyjny. Weryfikacja wyrażenia w `requires` nie dowodzi praw matematycznych. Zobacz [interfejsy generyczne](05_szablony_i_generycznosc/07_projektowanie_interfejsow_generycznych.md).

</details>

## 13. Funkcja ukryta w klasie

Klasa deklaruje `friend bool equal(X, X)` z definicją w środku, bez osobnej deklaracji w namespace. Dlaczego `equal(x, x)` może działać, a kwalifikowane wyszukanie nazwy nie musi jej znaleźć?

<details><summary>Rozwiązanie i uzasadnienie</summary>

To hidden friend. ADL uwzględnia funkcje zaprzyjaźnione związane z klasą argumentu; zwykłe wyszukiwanie nazw ma inne reguły. Nie oznacza to, że funkcja stała się metodą `X`. Zobacz [ADL](zaawansowane/06_overload_resolution_adl_i_hidden_friends.md).

</details>

## 14. Równoważność kluczy i hash

W `unordered_set` ignorujesz wielkość liter przy porównaniu kluczy. Hash liczysz z oryginalnych bajtów. Co jest błędne?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Klucze równoważne według predykatu muszą otrzymać jednakowy hash. Zmiana samego porównania narusza kontrakt kontenera. Normalizacja musi być spójna i jednoznaczna; Unicode wymaga ponadto świadomej polityki, której proste ASCII tolower nie załatwia. Zobacz [silne typy i hash](04_klasy_i_model_obiektowy/07_silne_typy_porownania_i_hash.md).

</details>

## 15. NaN w danych do sortowania

Dla implementacji z NaN w `double`, czy zwykły `<` zapewnia strict weak ordering na zbiorze wszystkich liczb wraz z NaN?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. NaN jest nieporównywalne przez `<` z innymi wartościami, co psuje wymagania relacji równoważności indukowanej przez komparator. Ustal politykę: odrzuć NaN albo zdefiniuj spójną kolejność klas wartości. Samo skompilowanie `sort` nie dowodzi spełnienia precondition. Zobacz [arytmetykę](02_podstawy_jezyka/10_arytmetyka_przepelnienia_i_float.md).

</details>

## 16. Widok i przechwycona referencja

Funkcja zwraca pipeline `filter` nad zewnętrznym wektorem. Predykat przechwytuje przez referencję lokalny parametr `threshold`. Wektor nadal żyje. Czy wynik jest bezpieczny?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie, jeśli obiekt, do którego odnosi się przechwycona referencja, już nie żyje. Widok może przechowywać lambdę, ale nie przedłuża automatycznie życia jej referencji. Przechwycenie progu przez wartość usuwa tę konkretną wadę; osobno trzeba zapewnić lifetime wektora i iteratorów. Zobacz [ranges](06_biblioteka_standardowa/06_ranges_i_views.md).

</details>

## 17. Silna gwarancja wyjątków

Aktualizujesz dwa kontenery: pierwszy zmieniasz, a druga operacja może rzucić. Czy RAII sam zapewnia, że oba wrócą do poprzedniego stanu?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. RAII zarządza zasobami; silna gwarancja wymaga przygotowania stanu i bezpiecznego commit albo poprawnego rollback. Możesz skonstruować nowy stan poza obiektem i podmienić go operacją o wymaganej gwarancji. Zobacz [RAII i wyjątki](07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md).

</details>

## 18. Flaga relaxed i zwykłe dane

Producent zapisuje zwykłe `int data`, potem atomową flagę przez relaxed. Konsument w pętli odczytuje flagę przez relaxed, po czym czyta `data`. Czy atomowość flagi wystarcza?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. Brak synchronizacji publikującej zwykłe dane; sam relaxed nie tworzy potrzebnego synchronizes-with. W typowym jednorazowym protokole publikacji stosuje się release/acquire, przy czym odczyt acquire musi zobaczyć odpowiedni zapis i dane nie mogą być potem modyfikowane bez dalszej synchronizacji. Zobacz [model pamięci](10_wspolbieznosc/04_atomiki_i_model_pamieci.md).

</details>

## 19. Powiadomienie przed oczekiwaniem

Producent wywołał `notify_one` zanim konsument wszedł w `wait`. Co musi przechowywać informację, żeby praca nie utknęła?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Stan chroniony mutexem, np. `!queue.empty() || closed`. Powiadomienie nie jest zapamiętanym żetonem. Oczekiwanie z predykatem sprawdza stan i poprawnie obsługuje również spurious wakeups. Zobacz [condition_variable](10_wspolbieznosc/02_mutex_lock_i_condition_variable.md).

</details>

## 20. jthread a blokujące oczekiwanie

Worker w `jthread` czeka na zwykłej `condition_variable`. Czy destruktor `jthread`, żądając stop i wykonując join, zawsze obudzi ten wait?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. Stop token musi być powiązany z protokołem oczekiwania. Zwykły wait na `condition_variable` sam nie reaguje na stop. Zaprojektuj zmianę stanu i notify albo użyj odpowiedniego stop-aware wait w `condition_variable_any`. Zobacz [zamykanie kolejki](10_wspolbieznosc/06_kolejka_backpressure_i_zamykanie.md).

</details>

## 21. Unicode i długość

Czy `std::string::size()` nad UTF-8 odpowiada liczbie znaków widocznych dla użytkownika? Czy `u8string` automatycznie waliduje i normalizuje tekst?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie i nie. Rozmiar to liczba jednostek kodowych `char`; UTF-8 używa wielu jednostek dla części punktów kodowych, a znaki postrzegane mogą składać się z wielu punktów. `char8_t` oznacza typ jednostki kodowej, nie gwarant poprawności całego ciągu. Zobacz [Unicode](06_biblioteka_standardowa/08_unicode_utf8_i_parsowanie.md).

</details>

## 22. Kompilator i biblioteka

Czy akceptacja `-std=c++23` dowodzi dostępności każdej funkcji biblioteki C++23 i zgodności ABI z każdą biblioteką skompilowaną w tym trybie?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. Frontend, biblioteka standardowa, konfiguracja ABI i platforma są odrębnymi elementami. Sprawdź konkretne feature-test macro, test użycia i macierz konfiguracji. Zgodność ABI wymaga dodatkowych warunków. Zobacz [przenośność](12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md).

</details>

## 23. Niezawodny benchmark

Pętla wykonuje obliczenie, którego wynik nie wpływa na obserwowalne zachowanie. Po optymalizacji czas spada prawie do zera. Czy znaleziono wyjątkowo szybki algorytm?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Być może usunięto pracę. Zadbaj o wykorzystanie wyniku, reprezentatywne dane i metodologię; sprawdź kod maszynowy właściwego fragmentu. Jeden bardzo mały pomiar może też mierzyć głównie narzut zegara. Zobacz [benchmarki](09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md).

</details>

## 24. consteval i parametry

Czy parametr zwykłej funkcji `constexpr int f(int n)` może bezwarunkowo stać się argumentem szablonu wymagającym stałej wyłącznie dlatego, że funkcję czasem wywołuje się przy kompilacji?

<details><summary>Rozwiązanie i uzasadnienie</summary>

Nie. Parametr nie staje się w definicji funkcji stałą odpowiednią do dowolnego wymagającego jej kontekstu. Rozdziel instancjację typu od ewaluacji wywołania. Jeśli wartość ma wybierać typ lub instancjację, przekaż ją jako parametr szablonu. Samo dodanie `consteval` również nie pozwala użyć zwykłego parametru funkcji w dowolnym argumencie szablonu wymagającym stałej. Zobacz [compile time](zaawansowane/09_constexpr_consteval_i_compile_time.md).

</details>

## Jak wykorzystać wynik

Pogrupuj błędy: 1–4 model wyrażeń, 5–9 lifetime, 10–17 projektowanie i biblioteka, 18–20 współbieżność, 21–24 reprezentacja i narzędzia. Zacznij od grupy, w której nie potrafisz podać reguły. Następnie wykonaj właściwy [zestaw zadań](cwiczenia/README.md) i projekt z [laboratoriów](praktyka/README.md). Wysoki wynik bez umiejętności napisania poprawnego programu nie zwalnia z praktyki.
