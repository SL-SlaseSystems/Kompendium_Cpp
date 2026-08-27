[← Spis treści](../README.md)

# Projektowanie API i ABI

Publiczne API obejmuje nazwy, typy, preconditions, ownership, błędy, złożoność i zachowanie współbieżne. ABI obejmuje binarną reprezentację: calling convention, layout, name mangling, vtables, wyjątki i runtime. Zgodność źródłowa nie gwarantuje binarnej, a standard C++ nie definiuje uniwersalnego ABI.

~~~cpp
#include <cassert>
#include <span>
#include <string>
#include <string_view>
#include <utility>

class Report {
public:
    explicit Report(std::string title) : title_{std::move(title)} {}
    [[nodiscard]] std::string_view title() const noexcept { return title_; }
    [[nodiscard]] int sum(std::span<const int> values) const noexcept {
        int result = 0;
        for (int value : values) result += value;
        return result;
    }

private:
    std::string title_;
};

int main() {
    const Report report{"Q1"};
    const int values[]{20, 22};
    assert(report.title() == "Q1" && report.sum(values) == 42);
}
~~~

Parametr `string` przez wartość jest dobry, gdy obiekt przejmuje dane; klient może skopiować lvalue lub przenieść rvalue. `string_view` jest dobry dla synchronicznego odczytu bez przechowania, a `span` dla ciągłego zakresu. Zwracany widok wiąże lifetime z `Report`, co musi być częścią kontraktu.

Minimalizuj publiczne zależności i liczbę typów ujawnionych w nagłówku. Dodanie pola private zmienia layout i może złamać ABI klientów; PImpl pomaga, ale nie rozwiązuje wszystkich zmian. Eksport symboli kontroluj atrybutami lub mapą visibility specyficzną dla platformy.

Stabilna granica pluginu często używa C ABI, opaque handles, jawnych wersji struktur i funkcji do tworzenia/niszczenia po tej samej stronie runtime. Nie przenoś standardowych kontenerów ani wyjątków przez granicę kompilatorów o nieustalonym ABI.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Projektowanie API i ABI”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz ustanowienie kontraktu typu, rozdzielenie interfejsu od implementacji, wykonanie operacji i zmierzenie kosztu na granicy abstrakcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie domenowe od mechanizmu implementacyjnego, publiczne ABI od prywatnego layoutu i hipotezę wydajności od pomiaru. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź przykładowe użycie API, rozmiar i layout typu, symbole biblioteki, profil CPU oraz liczbę alokacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projektowanie C++ łączy semantykę wartości, własność, stabilność ABI i koszt abstrakcji. Dobra abstrakcja utrudnia niewłaściwe użycie, ale pozostawia kompilatorowi wystarczającą informację do optymalizacji. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- API opisuje kontrakt źródłowy, a ABI layout, mangling, calling convention i binarną zgodność. Zmiana prywatnego pola może złamać ABI klasy eksportowanej, choć kod klientów nadal kompilowałby się ze źródeł.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Projektowanie API i ABI” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Projektowanie API i ABI
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Projektowanie API i ABI”, oceniaj łatwość poprawnego użycia, value semantics, stabilność kontraktu, koszt kompilacji i zmierzona wydajność krytycznej ścieżki. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [PImpl](01_rule_of_zero_pimpl_i_non_virtual_interface.md)
- [ABI i visibility](../zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)
- [ODR, moduły i FFI](../zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)
