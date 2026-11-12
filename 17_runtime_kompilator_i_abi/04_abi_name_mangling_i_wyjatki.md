[← Spis treści](../README.md)

# ABI name mangling i wyjątki

API opisuje sposób używania kodu na poziomie źródeł. ABI określa uzgodnienia pozwalające połączyć już skompilowane fragmenty: reprezentację argumentów, układ obiektów, nazwy symboli, obsługę wyjątków i współpracę z runtime. Dwa moduły mogą mieć zgodne deklaracje w nagłówkach, a mimo to nie współpracować binarnie. Zmiana kompilatora, biblioteki standardowej albo ustawień budowania może więc wymagać przebudowy wszystkich uczestników granicy.

Standard C++ nie definiuje jednego wspólnego ABI dla wszystkich implementacji. `extern "C"` nadaje językowe powiązanie C, ale nie stanowi obietnicy dowolnej zgodności między platformami. Nadal trzeba uzgodnić architekturę, konwencję wywołania, reprezentację typów i reguły eksportu symboli. Mała granica C jest użyteczna, ponieważ ogranicza liczbę zależnych od C++ szczegółów, które muszą pozostać zgodne. Specyfikację powiązania językowego zawiera [N4950, dcl.link](https://raw.githubusercontent.com/cplusplus/draft/n4950/source/declarations.tex).

## Jak to działa krok po kroku

Kompilator musi odróżnić przeciążenia, na przykład funkcje o tej samej nazwie przyjmujące `int` i `double`. ABI może kodować tę informację w nazwach symboli, czyli stosować mangling. Dokładny zapis jest zależny od wybranego ABI, a narzędzie demanglujące odtwarza czytelną postać. Nie należy ręcznie budować takich nazw ani zakładać, że nazwa symbolu zawiera pełny kontrakt funkcji. Różne definicje klasy mogą nadal doprowadzić do pozornie poprawnego linkowania.

Przy projektowaniu wtyczki najpierw ustalamy granicę, która nie przekazuje klas biblioteki standardowej ani wyjątków. Funkcje zwracają udokumentowane kody, a wynik zapisują w pamięci należącej do wywołującego. Implementacja może wewnętrznie używać wyjątków, lecz przechwytuje je przed powrotem przez granicę. Każdy handler musi sam być bezpieczny: tworzenie dynamicznego napisu błędu podczas obsługi braku pamięci może rzucić kolejny wyjątek.

~~~cpp
#include <cassert>
#include <cstdint>
#include <limits>
#include <stdexcept>

namespace {
std::uint32_t twice_checked(std::uint32_t value) {
    if (value > std::numeric_limits<std::uint32_t>::max() / 2) {
        throw std::range_error("wynik poza zakresem");
    }
    return value * 2;
}
}

// Kody: 0 sukces, 1 argument/zakres, 2 inny blad wewnetrzny.
extern "C" int meter_twice(std::uint32_t input,
                           std::uint32_t* output) noexcept {
    if (output == nullptr) return 1;
    try {
        const auto result = twice_checked(input);
        *output = result;
        return 0;
    } catch (const std::range_error&) {
        return 1;
    } catch (...) {
        return 2;
    }
}

int main() {
    std::uint32_t result = 99;
    assert(meter_twice(21, &result) == 0 && result == 42);
    assert(meter_twice(std::numeric_limits<std::uint32_t>::max(),
                       &result) != 0);
    assert(result == 42); // Przy bledzie wynik pozostaje bez zmian.
    assert(meter_twice(1, nullptr) == 1);
}
~~~

`noexcept` nie przechwytuje wyjątków. Jeżeli wyjątek opuści funkcję z taką specyfikacją, następuje wywołanie `terminate`; konwersję na kod wykonują bloki `catch`. Tu nawet błąd powstały podczas konstruowania `range_error` zostanie przejęty przez `catch (...)`. Odrębne kody pozwalają konsumentowi odrzucić złe dane bez zgadywania treści komunikatu. Zasady specyfikacji wyjątków opisuje [N4950, rozdział except](https://raw.githubusercontent.com/cplusplus/draft/n4950/source/exceptions.tex).

Publiczny nagłówek przeznaczony również dla C wymaga odpowiednich osłon `#ifdef __cplusplus` wokół `extern "C"` i `noexcept`, a typy pobiera wtedy z nagłówków C. Powyższy kompletny program pokazuje obie strony w jednej jednostce C++, aby dało się sprawdzić ścieżki błędów. Nie jest testem współpracy różnych kompilatorów ani systemów operacyjnych.

## Pogłębienie mechanizmu

Wyjątek wymaga współpracy kodu generowanego przez kompilator, mechanizmu rozwijania stosu, informacji o typach oraz biblioteki ABI. Zgodna nazwa eksportowanej funkcji nie zapewnia zgodności tych składników. LLVM rozróżnia bibliotekę standardową, bibliotekę C++ ABI i unwinder; [dokumentacja toolchainu Clang](https://clang.llvm.org/docs/Toolchain.html) wyjaśnia ich role. Przekazywanie `std::string` pomiędzy modułami z różnymi bibliotekami standardowymi jest szczególnie złym założeniem, nawet jeśli oba moduły skompilowano Clangiem.

Praktyczny przykład daje libstdc++: przejście na nowe reprezentacje `string` i `list` wprowadziło równoległe ABI wybierane przez `_GLIBCXX_USE_CXX11_ABI`. Wybór ten nie wynika po prostu z `-std=c++11` albo `-std=c++23`. Opisuje to [GCC, Dual ABI](https://gcc.gnu.org/onlinedocs/libstdc++/manual/using_dual_abi.html). Podobne ryzyko dotyczy ustawień debugowania kontenerów, pakowania struktur i przełączników wpływających na układ typów. Macierz wspieranych konfiguracji jest częścią produktu binarnego.

Pimpl może ukryć pola klasy przed konsumentem i ograniczyć liczbę zmian wymagających przebudowy. Nadal pozostają jednak wywołania metod, konstrukcja, destrukcja oraz uzgodnienia ABI C++. Gdy obie strony mają uzgodniony toolchain, taki interfejs może być właściwy. Dla niezależnie rozwijanych wtyczek często korzystniejszy jest nieprzezroczysty uchwyt oraz zestaw wersjonowanych funkcji C.

Własność pamięci musi być jawna. Pamięć zwalnia moduł, który ją przydzielił, poprzez opublikowaną funkcję niszczącą. Wywołujący nie używa `delete` na uchwycie ani `free` na buforze pochodzącym z nieznanego alokatora. Alternatywą jest bufor wywołującego, do którego biblioteka kopiuje wynik. Oba warianty unikają przenoszenia wiedzy o prywatnym układzie obiektu do konsumenta.

Zgodność sprawdzamy na poziomie, na którym zamierzamy ją obiecać. Test źródłowy przebudowujący konsumenta wykrywa inne problemy niż test uruchamiający dawny plik wykonywalny z nową biblioteką. Ten drugi powinien obejmować konstrukcję, odczyt, błędy i niszczenie obiektów oraz konfiguracje rzeczywiście wspierane przez produkt. Listę eksportowanych symboli można porównać narzędziami platformy, lecz brak zmian na tej liście nie dowodzi zachowania układu obiektów ani semantyki.

Wtyczka musi też określić kolejność zamykania. Biblioteki nie wolno odładować, dopóki istnieją uchwyty, funkcje zwrotne albo wątki wykonujące jej kod. Deleter zapisany w konsumenckim `unique_ptr` wskazuje funkcję z modułu; po jego odładowaniu sam poprawny adres danych nie wystarczy. Protokół zamknięcia powinien zatrzymać pracę, odwołać callbacki i zniszczyć zasoby przed zwolnieniem modułu. To część czasu życia granicy binarnej, której nie rozwiązuje sam mangling.

## Drugi przykład

Nieprzezroczysty uchwyt pozwala zachować stan wewnętrzny. W prawdziwej bibliotece nagłówek zawiera jedynie deklarację `struct Store;` oraz funkcje; definicja struktury pozostaje w implementacji. `store_copy` zwraca surowe bajty bez końcowego zera, podaje wymagany rozmiar i nie zapisuje częściowego wyniku, jeśli bufor jest zbyt mały.

~~~cpp
#include <array>
#include <cassert>
#include <cstddef>
#include <cstring>
#include <memory>
#include <string>

struct Store { std::string value = "sample"; };

extern "C" Store* store_create() noexcept {
    try { return new Store; }
    catch (...) { return nullptr; }
}

extern "C" void store_destroy(Store* handle) noexcept {
    delete handle;
}

// 0 sukces, 1 za maly bufor, 2 niepoprawne argumenty.
extern "C" int store_copy(const Store* handle, char* output,
                          std::size_t capacity,
                          std::size_t* required) noexcept {
    if (handle == nullptr || required == nullptr) return 2;
    *required = handle->value.size();
    if (capacity < *required) return 1;
    if (*required != 0 && output == nullptr) return 2;
    if (*required != 0) {
        std::memcpy(output, handle->value.data(), *required);
    }
    return 0;
}

int main() {
    std::unique_ptr<Store, decltype(&store_destroy)> handle(
        store_create(), &store_destroy);
    assert(handle);
    std::size_t required{};
    assert(store_copy(handle.get(), nullptr, 0, &required) == 1);
    assert(required == 6);
    std::array<char, 16> output{};
    assert(store_copy(handle.get(), output.data(), output.size(),
                      &required) == 0);
    assert(std::string(output.data(), required) == "sample");
    assert(store_copy(nullptr, output.data(), output.size(), &required) == 2);
}
~~~

Sprawdzenie `nullptr` nie potwierdza, że dowolny niezerowy adres jest poprawnym uchwytem. Użycie uchwytu po zniszczeniu nadal łamie kontrakt. Tak samo biblioteka musi dokumentować, czy uchwyt można współdzielić między wątkami. Przy rozbudowie API warto dodać funkcję zwracającą wersję protokołu i rozmiar struktur opcji. Dodawanie pól bez uzgodnionego mechanizmu wersjonowania nie staje się bezpieczne tylko dlatego, że struktura pochodzi z C.

Zmiana biblioteki powinna zachować również znaczenie kodów błędu i warunki ważności wskaźników. Nowy kod statusu wymaga ustalonego zachowania starego konsumenta, na przykład bezpiecznego potraktowania nieznanej wartości jako błędu. Wskaźnik pożyczony z uchwytu może przestać obowiązywać po jego modyfikacji, więc taki warunek trzeba opisać tak samo dokładnie jak funkcję zwalniającą. Stabilność binarna obejmuje możliwość poprawnego użycia interfejsu przez wcześniej skompilowany program, a nie samo odnalezienie eksportu przez linker.

## Porównanie i decyzje

Interfejs źródłowy C++ jest wygodny, gdy cały produkt buduje się razem. Stabilna granica binarna wymaga mniejszego zbioru typów oraz opisanego cyklu życia. Interfejs C ogranicza ryzyko, lecz kosztuje jawne kody błędów, funkcje niszczące i wersjonowanie. Dla komunikacji między różnymi architekturami właściwą granicą bywa serializowany protokół procesu, a nie współdzielenie struktur w pamięci.

**Zadanie 1.** Biblioteka zwraca `char*` utworzony przez `new[]`. Konsument wywołuje `free`. Jak zmienić interfejs?

<details><summary>Rozwiązanie</summary>

Dodaj funkcję biblioteki zwalniającą wynik przy użyciu właściwego mechanizmu albo przyjmuj bufor konsumenta i pojemność. Opisz długość, terminator oraz zachowanie przy zbyt małym buforze. Konsument nie powinien zgadywać alokatora.

</details>

**Zadanie 2.** Wszystkie eksporty mają `extern "C"`, ale funkcja zwraca `std::vector<int>`. Czy granica jest niezależna od biblioteki standardowej?

<details><summary>Rozwiązanie</summary>

Nie. Powiązanie nazwy nie stabilizuje reprezentacji wektora, alokatora ani destruktora. Zwróć status i skopiuj elementy do bufora wywołującego lub udostępnij uchwyt z funkcjami odczytu oraz niszczenia.

</details>

## Powiązane tematy

- [Mapa działu](README.md)
- [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)
- [Symbole, linker i ładowanie dynamiczne](03_symbole_linker_i_ladowanie_dynamiczne.md)
- [Projektowanie API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
