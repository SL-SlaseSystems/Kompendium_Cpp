[← Spis treści](../README.md)

# Feature-test macros i przenośność

Feature-test macros pozwalają wykryć konkretną funkcję języka lub biblioteki. Makra językowe zwykle zaczynają się od `__cpp_`, biblioteczne od `__cpp_lib_`. Wartość koduje rewizję funkcji, dlatego porównanie liczbowe jest ważniejsze niż samo `#ifdef`.

~~~cpp
#include <cassert>
#include <version>

int main() {
#if defined(__cpp_consteval) && __cpp_consteval >= 201811L
    constexpr bool has_consteval = true;
#else
    constexpr bool has_consteval = false;
#endif
    assert(has_consteval);
}
~~~

`__cplusplus` wskazuje tryb języka, lecz biblioteka standardowa może mieć inny poziom kompletności. MSVC historycznie wymagał opcji `/Zc:__cplusplus`, aby makro raportowało współczesną wartość. Używaj oficjalnej dokumentacji toolchainu i testów konfiguracji.

Warunkowa kompilacja powinna mieć mały zasięg. Zamiast rozrzucać preprocesor po logice domenowej, zbuduj adapter wybierający implementację i udostępniający wspólny interfejs. Testuj obie gałęzie w macierzy CI; fallback, którego nikt nie buduje, szybko gnije.

Nie używaj wyłącznie numeru wersji kompilatora do wykrywania języka. Vendor może backportować funkcję lub używać innej biblioteki standardowej. Dla zależności systemowych CMake `try_compile`, wykrywanie target properties i pakiety config mogą być lepsze od ręcznych makr.

Przenośność obejmuje także endianess, szerokości typów, alignment, ABI, filesystem, locale i model wątków. Compile-time detekcja odpowiada tylko na część pytań; zachowanie należy testować na rzeczywistych platformach.

## Jak to działa krok po kroku

Najpierw określ konkretną funkcję i wymaganą rewizję, na przykład `byteswap` lub operacje monadyczne `optional`. Następnie włącz odpowiedni nagłówek albo `<version>`, sprawdź makro i wybierz implementację. Warunek powinien obejmować również użycie nazwy, która może nie istnieć. Zwykłe `if` wewnątrz funkcji nie usuwa nieznanej nazwy z analizy kompilatora.

Zamknij wybór w małym adapterze. Kod domenowy wywołuje jedną funkcję i nie zna liczby obsługiwanych wersji biblioteki. Dodaj konfigurację wymuszającą fallback nawet na nowym toolchainie, aby móc go regularnie testować. W przeciwnym razie warstwa zgodności może pozostać niekompilowana przez lata.

## Pogłębienie mechanizmu

Makra językowe informują o mechanizmie kompilatora, a biblioteczne o odpowiednim API biblioteki. To dwa niezależne składniki konfiguracji. `__has_include(<header>)` wykrywa dostępność nagłówka w ścieżkach wyszukiwania, lecz nie dowodzi kompletności implementacji jego zawartości. Nagłówek może istnieć w bibliotece, która jeszcze nie udostępnia wszystkich potrzebnych typów lub metod.

Wartości makr mają postać liczbową przypominającą rok i miesiąc rewizji. Przyjmij `>=` konkretnego progu, zamiast wymagać równości: późniejsza implementacja może obsługiwać rozszerzoną rewizję. Nigdy nie definiuj ręcznie standardowego makra, aby „włączyć” brakujące API. Deklaracja liczby nie dostarcza implementacji.

`if constexpr` służy do wyborów semantycznych w kodzie, zwłaszcza zależnych od parametrów szablonu. `#if` usuwa tokeny przed kompilacją i nadaje się do odcięcia nieistniejącego nagłówka lub nieobsługiwanej składni. `requires` pozwala pytać o poprawność zależnych wyrażeń, ale nie jest uniwersalnym sposobem ukrywania dowolnej nieznanej nazwy spoza zależnego kontekstu.

Konfiguracja wpływa też na ODR i ABI. Jeśli makro zmienia pola publicznej klasy, a różne jednostki translacji widzą różne wartości, program może zawierać sprzeczne definicje. Preferuj wybór implementacji za stabilnym interfejsem; gdy różnica musi być publiczna, propaguj ją jako część wymagań targetu i pakietu.

## Drugi przykład

~~~cpp
#include <bit>
#include <cassert>
#include <climits>
#include <cstdint>
#include <version>

static_assert(CHAR_BIT == 8, "Adapter wymaga bajtow 8-bitowych");

constexpr std::uint32_t reverse_bytes(std::uint32_t value) noexcept {
#if !defined(COMPENDIUM_FORCE_PORTABLE) && defined(__cpp_lib_byteswap) && __cpp_lib_byteswap >= 202110L
    return std::byteswap(value);
#else
    return ((value & 0x000000ffu) << 24)
         | ((value & 0x0000ff00u) << 8)
         | ((value & 0x00ff0000u) >> 8)
         | ((value & 0xff000000u) >> 24);
#endif
}

int main() {
    static_assert(reverse_bytes(0x01020304u) == 0x04030201u);
    static_assert(reverse_bytes(reverse_bytes(0xaabbccddu)) == 0xaabbccddu);
    assert(reverse_bytes(0u) == 0u);
}
~~~

Adapter wymaga dostępności dokładnego typu `uint32_t` oraz ośmiobitowego bajtu. Samo istnienie `uint32_t` nie zapewnia `CHAR_BIT == 8`: bez dodatkowego warunku biblioteczne odwracanie bajtów mogłoby nie odpowiadać czterem oktetom fallbacku. Obie gałęzie realizują tę samą permutację czterech bajtów; nie wybierają automatycznie porządku sieciowego względem natywnej endianowości. Przykład kompiluj normalnie oraz z `-DCOMPENDIUM_FORCE_PORTABLE`, aby objąć kontrolą również fallback. Wymuszenie jest prywatnym makrem projektu, więc nie fałszuje informacji biblioteki.

## Porównanie i decyzje

Wybieraj feature-test macro dla standaryzowanego mechanizmu, a próbę kompilacji i linkowania dla zależności wymagającej dodatkowego runtime lub nietypowego połączenia flag. Test wykonania stosuj tam, gdzie istotny jest stan środowiska: baza stref czasowych, system plików lub uprawnienia. Dla cross-compilation test uruchomienia nie musi być dostępny na komputerze budującym, co wymaga jawnej konfiguracji docelowej.

Macierz CI powinna reprezentować rzeczywiste deklarowane wsparcie. Kilka niemal identycznych kompilatorów na jednej platformie nie sprawdzi różnic systemowego ABI i kodowania ścieżek. Z drugiej strony utrzymywanie szerokiej macierzy bez użytkowników też ma koszt. Dokumentuj minimalne wersje i warunki, które sprawdzasz, aby odbiorca wiedział, co oznacza „przenośny”.

## Ćwiczenie z odpowiedzią

Nagłówek istnieje, makro ma zbyt niską wartość, a prosty fragment kodu przypadkiem się kompiluje. Czy możesz usunąć warunek wersji? Dopiero po ustaleniu, jakiej konkretnej rewizji wymaga pełny kod. Jeden przechodzący overload nie dowodzi kompletności późniejszego rozszerzenia. Bezpieczniej testować dokładne wymagane operacje i utrzymać udokumentowany próg.

Źródło listy makr C++23: [version synopsis](https://timsong-cpp.github.io/cppwp/n4950/version.syn). Rozszerzenia kompilatora opisuje osobno [Clang Language Extensions](https://clang.llvm.org/docs/LanguageExtensions.html).

## Powiązane tematy

- [Standardy i implementacje](../01_wprowadzenie/02_standardy_i_implementacje.md)
- [C++23](04_cpp23.md)
- [C++26](../zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)

