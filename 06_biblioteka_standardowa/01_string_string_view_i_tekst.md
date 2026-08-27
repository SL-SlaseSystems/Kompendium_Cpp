[← Spis treści](../README.md)

# string, string_view i tekst

`std::string` jest właścicielskim, dynamicznym ciągiem elementów `char`. Przechowuje bajty i zapewnia ciągłość pamięci; nie rozumie automatycznie znaków Unicode ani grapheme clusters. `std::string_view` jest niewłaścicielskim widokiem na ciąg bajtów i nie zapewnia terminatora na końcu wybranego fragmentu.

~~~cpp
#include <cassert>
#include <cctype>
#include <string>
#include <string_view>

std::string normalize_name(std::string_view name) {
    std::string result{name};
    if (!result.empty()) {
        result.front() = static_cast<char>(std::toupper(
            static_cast<unsigned char>(result.front())));
    }
    return result;
}

int main() {
    assert(normalize_name("ada") == "Ada");
    const std::string text = "C++23";
    assert(std::string_view{text}.substr(0, 3) == "C++");
}
~~~

Funkcje klasyfikujące z `<cctype>` wymagają wartości reprezentowalnej jako `unsigned char` albo `EOF`; przekazanie ujemnego `char` może być UB. Przykład wykonuje bezpieczne rzutowanie, ale nadal przetwarza tylko bajt według bieżącej locale, nie pełne Unicode.

Kodowanie UTF-8 mieści się w `std::string`, lecz `size()` zwraca liczbę bajtów. Indeks może wskazać środek wielobajtowej sekwencji. Normalizacja, podział na grapheme clusters, zmiana wielkości liter i porównania językowe wymagają wyspecjalizowanej biblioteki, np. ICU; nie są częścią kompletnego modelu tekstu w C++23.

`c_str()` zwraca wskaźnik do danych zakończonych nullem, użyteczny przy C API. Wskaźnik może zostać unieważniony przez modyfikację napisu. Nul wewnątrz `std::string` jest dozwolony, ale C API może potraktować go jako koniec.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „string, string_view i tekst”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie zakresu, wykonanie operacji zgodnie z wymaganiami iteratora i aktualizację stanu kontenera wraz z regułami invalidacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij właściciela elementów od widoku, kolejność logiczną od fizycznego układu i gwarancję złożoności od konkretnego czasu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź rozmiar i capacity, ważność iteratorów, liczbę alokacji, kolejność elementów oraz klasę złożoności. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Kontenery i algorytmy biblioteki standardowej mają kontrakty dotyczące złożoności, invalidacji, własności oraz zakresów. Poprawny wybór wynika z wymaganych operacji i stabilności adresów, nie z przyzwyczajenia do jednego kontenera. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `span` i `string_view` są niewłaścicielskimi widokami; kopiowanie widoku nie przedłuża lifetime danych. API powinno dokumentować zależność czasową i unikać zwracania widoku do obiektu lokalnego lub tymczasowego napisu.
- `std::string` posiada bufor i gwarantuje zakończenie zerem dla `c_str`, a `string_view` przechowuje wskaźnik oraz długość bez własności. Bajty napisu nie określają automatycznie kodowania ani liczby znaków użytkownika.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „string, string_view i tekst” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: string, string_view i tekst
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „string, string_view i tekst”, oceniaj wzorzec dostępu, lokalność danych, stabilność referencji, koszt modyfikacji i możliwość użycia gotowego algorytmu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Widoki i dangling](../03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)
- [Strumienie i formatowanie](../11_io_i_system/01_strumienie_i_formatowanie.md)
- [Sieć i serializacja](../11_io_i_system/05_siec_serializacja_i_granice_std.md)
