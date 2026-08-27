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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Fuzzing i property-based testing”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz sformułowanie hipotezy, przygotowanie kontrolowanego wejścia, zebranie wyniku, porównanie z oczekiwaniem i zachowanie reprodukcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd funkcjonalny, undefined behavior, problem przenośności i regresję wydajności, ponieważ wymagają innych narzędzi. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przypadek, kod wyjścia, raport sanitizera, statystyczny rozkład pomiarów i konfigurację kompilacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Żadne pojedyncze narzędzie nie dowodzi poprawności programu C++. Test sprawdza zachowanie dla danych, analiza statyczna szuka wzorców, sanitizer obserwuje wykonanie, a profiler mierzy koszt; wiarygodność daje dopiero połączenie niezależnych dowodów. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Fuzzer mutuje wejścia i wykorzystuje pokrycie do docierania do nowych ścieżek, a property-based testing generuje przypadki sprawdzające inwariant. Sanitizery zwiększają zdolność obu metod do wykrycia cichego UB.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Fuzzing i property-based testing” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Fuzzing i property-based testing
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Fuzzing i property-based testing”, oceniaj zdolność wykrycia realnej regresji, powtarzalność, koszt utrzymania testu i reprezentatywność środowiska. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Testy jednostkowe](01_testy_jednostkowe_i_integracyjne.md)
- [Sanitizery](03_sanitizery_i_debuggery.md)
- [Sieć i serializacja](../11_io_i_system/05_siec_serializacja_i_granice_std.md)

