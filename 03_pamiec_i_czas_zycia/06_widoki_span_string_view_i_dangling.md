[← Spis treści](../README.md)

# Widoki, span, string_view i dangling

Widok (*view*) zapewnia dostęp do danych, ale zwykle ich nie posiada. `std::span<T>` opisuje ciągły zakres elementów, a `std::string_view` sekwencję znaków. Kopiowanie widoku jest tanie, ponieważ kopiuje wskaźnik i rozmiar, lecz właściciel danych musi żyć dłużej niż każde użycie widoku.

~~~cpp
#include <array>
#include <cassert>
#include <span>
#include <string_view>

int sum(std::span<const int> values) {
    int result = 0;
    for (int value : values) {
        result += value;
    }
    return result;
}

bool has_prefix(std::string_view text, std::string_view prefix) {
    return text.starts_with(prefix);
}

int main() {
    const std::array values{2, 4, 6};
    assert(sum(values) == 12);
    assert(has_prefix("kompendium", "kom"));
}
~~~

`string_view` może wskazywać literał, `std::string` albo fragment bufora. Nie dodaje terminatora `\0` i jego `.data()` nie musi wskazywać C stringa. Utworzenie widoku do tymczasowego `std::string`, a następnie użycie go po zniszczeniu napisu, daje dangling view. Podobnie `span` zostaje unieważniony przez destrukcję właściciela albo realokację wektora.

Widoki są znakomite jako parametry funkcji wykonujących synchroniczną operację. Zachowaj ostrożność, gdy funkcja przechowuje widok, zwraca go lub przekazuje do zadania asynchronicznego. Interfejs powinien jasno sygnalizować, że nie przejmuje danych. Jeśli wynik ma być niezależny, zwróć właścicielski `std::string` albo kontener.

Ranges views są często leniwe i również mogą przechowywać referencje do zakresu źródłowego. Biblioteka ranges posiada pojęcie borrowed range, ale nie rozwiązuje każdego błędu czasu życia.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Widoki, span, string_view i dangling”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz rozpoczęcie lifetime, ustanowienie inwariantu, przekazywanie własności lub widoku oraz zakończenie lifetime w dokładnie określonym miejscu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel storage od obiektu, właściciela od obserwatora oraz semantykę przeniesienia od zwykłego kopiowania bitów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź miejsce konstrukcji i destrukcji, graf właścicieli, ważność referencji oraz zachowanie sanitizerów. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Poprawność pamięci w C++ wynika z czasu życia obiektów i własności zasobów. Adres jest tylko reprezentacją położenia; nie dowodzi, że obiekt nadal istnieje ani że wolno uzyskać przez niego dostęp do przechowywanej wartości. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `span` i `string_view` są niewłaścicielskimi widokami; kopiowanie widoku nie przedłuża lifetime danych. API powinno dokumentować zależność czasową i unikać zwracania widoku do obiektu lokalnego lub tymczasowego napisu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Widoki, span, string_view i dangling” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Widoki, span, string_view i dangling
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Widoki, span, string_view i dangling”, oceniaj jednoznaczna własność, automatyczne sprzątanie, brak dangling i możliwie mała liczba ręcznych operacji na pamięci. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Referencje, wskaźniki i tablice](../02_podstawy_jezyka/07_referencje_wskazniki_i_tablice.md)
- [string i string_view](../06_biblioteka_standardowa/01_string_string_view_i_tekst.md)
- [Ranges i views](../06_biblioteka_standardowa/06_ranges_i_views.md)

