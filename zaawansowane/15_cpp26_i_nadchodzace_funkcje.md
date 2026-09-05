[← Spis treści](../README.md)

# C++26 i nadchodzące funkcje

**Status zweryfikowany 2026-09-05:** prace WG21 nad zestawem funkcji C++26 są ukończone; szczegóły i źródło podano poniżej. Bazowy tekst kompendium i testy dotyczą C++23. Funkcje C++26 wymagają osobnej kontroli frontendu, biblioteki standardowej oraz konfiguracji platformy.

Do głównych mechanizmów C++26 należą statyczna refleksja oparta o `std::meta::info`, contracts, pack indexing i dalsze rozszerzenia constant evaluation. Draft rozróżnia także erroneous behavior w części sytuacji wcześniej opisywanych przez wartości indeterminate. Biblioteka rozwija execution, narzędzia współbieżne, kontenery oraz interfejsy numeryczne, w tym standardowe SIMD.

Poniższy zapis pokazuje jedynie ideę pack indexing i jest nietestowany przez bazowy Clang 17:

~~~cpp,notest
#include <cstddef>
#include <concepts>

template<std::size_t I, class... Types>
using element_t = Types...[I]; // C++26 pack indexing

static_assert(std::same_as<element_t<1, int, double>, double>);
~~~

Reflection umożliwia reprezentowanie encji programu jako wartości compile-time, introspekcję i generowanie deklaracji przez splicing zgodnie z przyjętym modelem. Jest to duża zmiana metaprogramowania, ale składnia, ograniczenia i zakres powinny być czytane z opublikowanej wersji lub aktualnego draftu, nie ze starych prototypów.

Contracts w working draft opisują contract assertions i semantyki ewaluacji. Historia tej funkcji zawiera wcześniejsze projekty usunięte z C++20, dlatego nie mieszaj dawnych składni z aktualnym tekstem. Toolchain może nie implementować mechanizmu albo używać flag eksperymentalnych.

~~~cpp
#include <cassert>

int main() {
#if defined(__cpp_pack_indexing) && __cpp_pack_indexing >= 202311L
    constexpr bool has_pack_indexing = true;
#else
    constexpr bool has_pack_indexing = false;
#endif
    // Informacja konfiguracji; właściwe użycie funkcji bada osobny test kompilacji.
    (void)has_pack_indexing;
}
~~~

## Strategia adopcji

Najpierw ustal realną macierz kompilator–biblioteka–platforma. Izoluj nową funkcję w małym adapterze, zapewnij fallback i buduj obie ścieżki w CI. Nie emuluj refleksji lub contracts rozbudowanym makrem, jeśli koszt utrzymania przewyższa korzyść. Wersjonuj dokumentację według konkretnego tekstu standardu i rewizji implementowanej funkcji.

## Jak to działa krok po kroku

Adopcję zaczyna się od konkretnej funkcji, nie od samej flagi `-std=c++26`. Frontend rozpoznaje składnię, biblioteka dostarcza klasy i funkcje, a środowisko docelowe może wymagać dodatkowej obsługi runtime. Kompilator akceptujący pack indexing nie musi mieć standardowej refleksji, a nagłówek execution nie dowodzi obecności kompletnego modelu senders/receivers.

Przy pack indexing `Types...[I]` wybiera typ o ustalonym indeksie w parameter pack. Indeks musi być właściwą stałą dostępną przy kompilacji i mieścić się w granicach paczki. Mechanizm zastępuje część rekurencji metaprogramowania lub pośrednictwo `tuple_element`, lecz nie pozwala wybierać typu na podstawie zwykłej liczby runtime. Podobieństwo do indeksowania tablicy nie zmienia tej różnicy faz języka.

## Pogłębienie mechanizmu

**Stan sprawdzony 2026-09-05:** prace komitetu nad C++26 zakończono na spotkaniu WG21 w Croydon w marcu 2026, co potwierdza [P3850R0](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p3850r0.pdf). Ukończenie prac WG21, formalna publikacja ISO i dostępność konkretnej implementacji są odrębnymi zdarzeniami. Ten rozdział nie zakłada pełnego wsparcia w toolchainach ani nie nadaje przyszłym propozycjom C++29 statusu części C++26.

Refleksja statyczna reprezentuje informacje o programie przez wartości compile-time, pozwala je badać oraz używać określonych rezultatów przez splicing. Nie jest runtime RTTI: nie polega na odnajdywaniu dowolnych klas po tekście w działającym procesie. Nie zmienia też automatycznie prywatnych pól w publiczny format serializacji. Generator oparty na refleksji musi nadal ustalić wersjonowanie schematu, wybór pól i znaczenie danych; zmiana nazwy pola nie powinna przypadkowo łamać trwałego protokołu.

Contracts opisują warunki wstępne, końcowe i asercje kontraktowe. Model C++26 rozróżnia semantyki ewaluacji, dlatego predykat nie powinien wykonywać istotnych dla logiki programu efektów ubocznych. Contract assertion nie jest uniwersalnym zamiennikiem walidacji danych wejściowych: program nadal potrzebuje jawnej ścieżki obsługi niepoprawnego żądania użytkownika. Historyczna składnia atrybutów z propozycji dla C++20 nie jest obecnym mechanizmem.

Biblioteczne `inplace_vector` łączy zmienny rozmiar z pojemnością ustaloną w typie. Unika osobnej alokacji storage elementów, ale elementy nadal mogą same alokować, a przekroczenie pojemności ma własny kontrakt zależny od wybranej operacji. Standardowe SIMD opisuje operacje na wielu elementach bez uzależniania źródła od jednego zestawu intrinsics. Nie zapewnia jednak, że każdy procesor i każda liczba lanes uzyskają tę samą wydajność.

Senders/receivers opisują kompozycję asynchronicznych operacji, ich completion channels i relację ze środowiskiem wykonania. Sender nie jest synonimem uruchomionego wątku ani gotowego future. Operacja musi zostać połączona z odbiorcą i uruchomiona według protokołu; zasoby jej stanu powinny istnieć przez właściwy okres. Przy adopcji najpierw zrozum rozdzielenie wartości, błędu i zatrzymania, zanim połączysz wiele adapterów w rozbudowany pipeline.

## Drugi przykład

~~~cpp
#include <cassert>
#include <cstddef>
#include <tuple>
#include <type_traits>

template<std::size_t I, class... T>
using selected_t = std::tuple_element_t<I, std::tuple<T...>>;

int main() {
    static_assert(std::is_same_v<selected_t<1, int, double>, double>);
    constexpr std::tuple values{3, 4.5};
    static_assert(std::get<0>(values) == 3);
    assert(std::get<1>(values) == 4.5);
}
~~~

To działający wariant bazowy C++23 dla wyboru typu z paczki. `selected_t` oblicza typ, a `get` pokazuje oddzielny dostęp do wartości przechowywanej w tuple. W przyszłej ścieżce z pack indexing można uprościć alias, zachowując testy semantyki. Obie ścieżki powinny odrzucać indeks poza zakresem; fallback nie powinien zwracać przypadkowego typu, aby ukryć błąd użytkownika.

## Porównanie i decyzje

Feature-test macro jest deklaracją dostępności określonej rewizji funkcji. Makra biblioteczne należy sprawdzać po dołączeniu odpowiedniego nagłówka albo `<version>`, a wynik potwierdzać małym testem kompilacji konkretnego użycia. `__has_include` dowodzi tylko obecności nagłówka. Numer producenta kompilatora nie wystarcza, ponieważ ta sama wersja frontendu może współpracować z różnymi bibliotekami standardowymi i SDK.

**Ćwiczenie.** Czy dodatni wynik makra pack indexing uprawnia do użycia `std::meta`? **Odpowiedź:** nie; to niezależne funkcje. Czy istniejący `#include <execution>` w C++17 dowodzi wsparcia senders/receivers C++26? Nie; starszy nagłówek zawiera polityki wykonania algorytmów. Czy bieżący eel.is jest zamrożonym tekstem C++23? Nie; do bazowych reguł używamy [N4950](https://timsong-cpp.github.io/cppwp/n4950/), a [working draft](https://eel.is/c++draft/) może obejmować późniejsze zmiany.

Weryfikację wsparcia prowadź w tabelach producenta: [Clang C++ status](https://clang.llvm.org/cxx_status.html), [libc++ C++26 status](https://libcxx.llvm.org/Status/Cxx26.html). Przykłady oznaczone `cpp,notest` pozostają poza walidacją C++23 i wymagają oddzielnego środowiska.

Erroneous behavior z C++26 ma inne wymagania diagnostyczne niż undefined behavior i nie oznacza, że można celowo czytać dowolne niezainicjalizowane obiekty. Analizę trzeba prowadzić według rodzaju storage, sposobu inicjalizacji i operacji konsumującej wartość. Najlepsza praktyka aplikacyjna nadal polega na inicjalizacji i reprezentowaniu braku wartości przez odpowiedni typ. Podobnie mechanizmy hardened library nie zastępują walidacji obcego wejścia: sprawdzenie kontraktu biblioteki i błąd domenowy są odrębnymi poziomami odpowiedzialności.

## Powiązane tematy

- [Standardy i implementacje](../01_wprowadzenie/02_standardy_i_implementacje.md)
- [Feature-test macros](../12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)
- [Compile time](09_constexpr_consteval_i_compile_time.md)

