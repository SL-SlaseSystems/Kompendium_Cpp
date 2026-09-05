[← Spis treści](../README.md)

# Fuzzing i property-based testing

Fuzzer generuje lub mutuje wejścia i obserwuje awarie, raporty sanitizerów, timeouty oraz inne naruszenia. Coverage-guided fuzzing, np. libFuzzer lub AFL++, wykorzystuje informację o nowych ścieżkach. Property-based testing generuje dane pod zadane własności, np. „dekodowanie zakodowanej wartości daje oryginał”. Oba podejścia uzupełniają przykładowe testy jednostkowe.

~~~cpp
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <span>

bool valid_packet(std::span<const std::uint8_t> bytes) {
    if (bytes.size() < 2) {
        return false;
    }
    return bytes.front() == 0xCA && bytes.back() == 0xFE;
}

int main() {
    const std::uint8_t packet[]{0xCA, 0x01, 0xFE};
    assert(valid_packet(packet));
}
~~~

Harness libFuzzer zwykle udostępnia `extern "C" int LLVMFuzzerTestOneInput(const uint8_t*, size_t)` i przekazuje dane parserowi. Ten entry point zależy od toolchainu, dlatego nie jest elementem ISO C++. Funkcja pod testem powinna przyjmować jawny zakres, mieć ograniczenia rozmiaru i nie zakładać terminatora.

Największą wartość daje fuzzing kodu parsującego, kompresji, protokołów, formatów plików i konwersji, szczególnie w połączeniu z ASan/UBSan. Corpus z realnymi przykładami przyspiesza dotarcie do głębokich stanów. Po awarii fuzzer minimalizuje wejście; zachowaj je jako test regresyjny.

Property powinno być mocniejsze niż powtórzenie implementacji. Przydatne są round-trip, idempotence, monotonicity, zachowanie inwariantów i zgodność z prostą implementacją referencyjną. Generator musi obejmować granice: pusty zakres, wartości maksymalne, błędne kodowanie i powtarzalne struktury.

## Jak to działa krok po kroku

Harness otrzymuje dowolną sekwencję bajtów i przekazuje ją funkcji pod testem. Pierwszym wymaganiem jest bezpieczna obsługa pustego oraz bardzo krótkiego wejścia. Parser nie może odczytywać nagłówka przed sprawdzeniem długości. Dla formatu zawierającego deklarowany rozmiar sprawdź relację do rzeczywistego bufora i unikaj przepełnienia przy obliczaniu końcowej pozycji.

Fuzzer uruchamia instrumentowany program, obserwuje nowe pokrycie i zachowuje wejścia otwierające nowe ścieżki. Mutacje tych wejść pomagają docierać głębiej niż zupełnie losowe bajty. Warto dostarczyć niewielki corpus poprawnych oraz błędnych przykładów i ewentualny słownik tokenów formatu. Jednocześnie harness nie powinien odrzucać niemal wszystkich danych na wstępie, zanim dotrą do właściwego parsera.

Po znalezieniu awarii utrwal dokładny plik, konfigurację kompilacji i raport. Minimalizacja usuwa zbędne części wejścia przy zachowaniu objawu, co ułatwia diagnozę. Napraw przyczynę, a następnie dodaj najmniejszy przypadek do testów regresyjnych i ponownie uruchom kampanię. Sam brak awarii dla jednego znalezionego pliku nie oznacza, że wszystkie pokrewne ścieżki zostały naprawione.

## Pogłębienie mechanizmu

Fuzzer potrzebuje wyroczni, czyli sposobu rozpoznania niepoprawnego zachowania. Awaria procesu i raport sanitizatora są jednymi z możliwości, ale wiele błędów parsera daje po prostu złą wartość. Możesz sprawdzać inwariant, porównywać wynik z niezależną implementacją albo testować relację między kilkoma wykonaniami. Nie traktuj każdego normalnego odrzucenia niepoprawnego wejścia jako awarii.

Round-trip wymaga określenia dziedziny i równoważności. `decode(encode(x)) == x` ma sens dla wartości, które format potrafi reprezentować. Odwrotne `encode(decode(bytes)) == bytes` może być fałszywe dla poprawnego dekodera, jeśli format dopuszcza wiele równoważnych reprezentacji i enkoder wybiera kanoniczną. Wtedy właściwa jest zgodność semantyczna, a nie identyczność bajtów.

Własność idempotencji, np. `normalize(normalize(x)) == normalize(x)`, bywa użyteczna, lecz sama nie wystarcza: funkcja zawsze zwracająca pusty napis także może ją spełnić. Łącz ją z zachowaniem znaczenia lub ograniczeniami wyjścia. Test porównujący implementację z identycznym kodem przepisanym do testu może powielać ten sam błąd. Prostszą referencję wolno stosować tylko dla małych wejść, nawet jeśli jest dużo wolniejsza.

Harness powinien być szybki, deterministyczny dla tego samego wejścia i odporny na narastanie globalnego stanu między wywołaniami. Ogranicz pamięć, czas i rozmiary tak, aby pojedynczy przypadek nie blokował całej kampanii. Odróżnij rzeczywistą złożoność algorytmiczną prowadzącą do odmowy usługi od zwykłego testu z arbitralnie zbyt krótkim limitem czasu. Losowe opóźnienia, sieć i zegar ścienny utrudniają odtwarzanie wyników.

## Drugi przykład

Poniższy test własności sprawdza round-trip liczb całkowitych przez standardowe funkcje konwersji. Korzysta z ustalonego ziarna i dodaje granice jawnie, zamiast liczyć, że generator kiedyś je trafi.

~~~cpp
#include <array>
#include <charconv>
#include <limits>
#include <random>
#include <system_error>

bool round_trip(int value) {
    std::array<char, 64> buffer{};
    const auto encoded = std::to_chars(buffer.data(), buffer.data() + buffer.size(), value);
    if (encoded.ec != std::errc{}) return false;
    int decoded = 0;
    const auto parsed = std::from_chars(buffer.data(), encoded.ptr, decoded);
    return parsed.ec == std::errc{} && parsed.ptr == encoded.ptr && decoded == value;
}

int main() {
    for (int value : {0, 1, -1, std::numeric_limits<int>::min(),
                      std::numeric_limits<int>::max()}) {
        if (!round_trip(value)) return 1;
    }
    std::mt19937 generator{2026};
    std::uniform_int_distribution<int> distribution{-1'000'000, 1'000'000};
    for (int i = 0; i < 10000; ++i) {
        if (!round_trip(distribution(generator))) return 1;
    }
}
~~~

Test wymaga implementacji `int` reprezentującej użyty zakres generatora. Nie sprawdza niepoprawnych zapisów, ponieważ wszystkie teksty pochodzą z `to_chars`. Osobny test parsera powinien generować błędne znaki, nadmiarowe końcówki i liczby poza zakresem. Sprawdzenie `parsed.ptr` jest ważne: konwersja poprawnego prefiksu nie oznacza akceptacji całego tekstu.

~~~text
# Typowy sposób budowania harnessu libFuzzer w obsługiwanym Clang:
clang++ -std=c++23 -g -O1 -fsanitize=fuzzer,address,undefined \
    fuzz_parser.cpp parser.cpp -o fuzz_parser
mkdir -p corpus
./fuzz_parser corpus -max_total_time=60
~~~

Plik harnessu definiuje wymagany entry point libFuzzer zamiast zwykłego `main`; runtime dostarcza pętlę sterującą. Polecenia nie dotyczą każdego kompilatora C++ i wymagają zainstalowanego odpowiedniego runtime.

## Porównanie i decyzje

Property-based testing najlepiej wyraża reguły domeny i zwykle oferuje generowanie oraz zmniejszanie przypadków. Coverage-guided fuzzing szczególnie dobrze eksploruje parsery i zależne od danych ścieżki. Testy przykładów pozostają potrzebne do ważnych, nazwanych scenariuszy. Te sposoby uzupełniają się, jeśli współdzielą sensowne inwarianty oraz zbiór znalezionych regresji.

**Ćwiczenie.** Enkoder i dekoder zamieniają kolejność dwóch pól w zgodny sposób, więc round-trip przechodzi. Jak wykryć błąd formatu? **Odpowiedź:** dodaj niezależne znane wektory kodowania albo porównanie z inną implementacją. Wzajemnie zgodne błędy dwóch funkcji mogą spełniać relację odwracalności, a mimo to naruszać specyfikację protokołu.

Źródła: [LLVM libFuzzer](https://llvm.org/docs/LibFuzzer.html), [RapidCheck: testy własności](https://github.com/emil-e/rapidcheck), [C++23: konwersje znakowe](https://timsong-cpp.github.io/cppwp/n4950/charconv).

## Powiązane tematy

- [Testy jednostkowe](01_testy_jednostkowe_i_integracyjne.md)
- [Sanitizery](03_sanitizery_i_debuggery.md)
- [Sieć i serializacja](../11_io_i_system/05_siec_serializacja_i_granice_std.md)
