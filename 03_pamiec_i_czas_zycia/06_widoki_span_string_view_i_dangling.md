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

Utworzenie `string_view` z napisu nie kopiuje jego znaków. Widok zapamiętuje początek i długość, a indeksowanie odwołuje się do danych właściciela. Zmiana istniejącego znaku w żywym, nierealokowanym napisie może stać się widoczna przez widok. Zniszczenie właściciela lub operacja unieważniająca jego bufor sprawia natomiast, że ta sama para adresu i długości nie uprawnia już do dostępu.

`span` działa analogicznie dla elementów dowolnego odpowiedniego typu. `span<const int>` zabrania modyfikowania elementów przez ten interfejs. `const span<int>` jest stałym uchwytem, który nadal pozwala modyfikować wskazane liczby. Trzeba więc odczytywać miejsce kwalifikatora, a nie tylko jego obecność. Zwykły widok przekazuje się przez wartość, ponieważ kopia uchwytu jest mała i nie kopiuje całego zakresu.

W pierwszym programie tablica w `main` żyje przez wszystkie wywołania `sum`, a literały napisowe mają statyczny czas przechowywania. Żaden widok nie ucieka poza bezpieczny czas użycia. Inna sytuacja to `std::string_view v = std::string{"abc"};`: temporary jest niszczone przy średniku, więc późniejszy odczyt z `v` byłby użyciem wiszącego widoku.

## Pogłębienie mechanizmu

Wywołanie synchroniczne `consume(std::string{"abc"})`, gdzie parametr ma typ `string_view`, może być poprawne: napis trwa do końca pełnego wyrażenia, czyli przez całe wywołanie. Funkcja nie może zachować widoku do późniejszego użycia bez dodatkowej umowy. Przeniesienie tego samego kodu do kolejki zadań zmienia wymagania czasu życia, choć typ parametru i składnia jego utworzenia pozostają identyczne.

`string::substr` zwraca nowy właścicielski napis. Dlatego `string_view v = text.substr(0, 3);` tworzy widok do temporary, a nie bezpośrednio do `text`. Jeśli potrzebny jest fragment istniejącego bufora, najpierw utwórz `string_view{text}`, a potem wywołaj jego `substr`. To ważne rozróżnienie dwóch metod o takiej samej nazwie, ale innej semantyce własności.

`string_view::data()` nie gwarantuje terminatora za końcem widoku. Dla prefiksu większego napisu funkcja C oczekująca zera może odczytać więcej znaków niż obejmuje fragment. Dla dowolnego bufora może wyjść poza legalny zakres. Gdy zewnętrzne API wymaga C stringa, utwórz niezależny `std::string` i użyj jego `c_str`, zachowując właściciela przez całe wywołanie.

`span<T, N>` przechowuje rozmiar w typie, natomiast `span<T>` ma dynamiczny extent. Stały extent pozwala wyrażać interfejs dla dokładnie określonej liczby elementów, lecz sam `span` nie sprawdza wszystkich indeksów podczas wykonania. W C++23 wyjście poza zakres przez `operator[]` narusza wymagania; nie zakładaj automatycznego wyjątku. Konstrukcja widoku z wskaźnika i rozmiaru również wymaga prawdziwego legalnego zakresu.

Nie każdy typ będący `ranges::view` jest niewłaścicielski: istnieje na przykład `owning_view`. Z kolei `borrowed_range` oznacza możliwość zachowania iteratorów po zniszczeniu samego obiektu zakresu, nie obietnicę życia jego zewnętrznych danych. `string_view` może być borrowed range i jednocześnie wskazywać zniszczony napis. Te pojęcia opisują różne zależności.

## Drugi przykład

Funkcja zwraca fragment argumentu, więc wynik pozostaje zależny od oryginalnego właściciela. Program tworzy także kopię znaków, aby pokazać różnicę między aliasem i niezależną wartością.

~~~cpp
#include <cassert>
#include <string>
#include <string_view>

std::string_view first_word(std::string_view text) {
    const auto space = text.find(' ');
    return text.substr(0, space);
}

int main() {
    std::string line = "alpha beta";
    std::string_view word = first_word(line);
    std::string saved{word};
    line[0] = 'A';
    assert(word == "Alpha");
    assert(saved == "alpha");
    assert(word.size() == 5);
    assert(line.size() == 10);
}
~~~

Zmiana pojedynczego istniejącego znaku przez `operator[]` nie realokuje napisu. Widok obserwuje zmianę, a kopia pozostaje niezależna. Gdyby funkcję wywołano z tymczasowym `std::string` i zachowano sam widok po średniku, ten model przestałby być bezpieczny.

## Porównanie i decyzje

Zwracaj widok, gdy API celowo identyfikuje część istniejących danych i potrafisz jasno opisać ich właściciela. Zwracaj wartość, gdy wynik ma żyć niezależnie lub przechodzi do asynchronicznego zadania. Dla klasy przechowującej jednocześnie napis i widok do własnego napisu szczególnie ostrożnie projektuj kopiowanie i ruch: domyślna kopia widoku może nadal wskazywać bufor starego obiektu. Indeksy względem własnego bufora często lepiej wyrażają taki fragment.

**Ćwiczenie.** Czy skopiowanie wiszącego `string_view` do nowego `string_view` naprawia czas życia? Czy utworzenie `std::string` zawsze naprawi problem?

**Odpowiedź.** Kopia widoku przenosi ten sam nieaktualny adres. Kopia znaków do `string` jest poprawnym rozwiązaniem tylko wtedy, gdy źródło jeszcze żyje w chwili kopiowania. Próba skopiowania już wiszących danych sama wykonuje nielegalny odczyt.

Źródła: [string_view](https://timsong-cpp.github.io/cppwp/n4950/string.view), [span](https://timsong-cpp.github.io/cppwp/n4950/views.span), [borrowed_range](https://timsong-cpp.github.io/cppwp/n4950/range.range).

## Powiązane tematy

- [Referencje, wskaźniki i tablice](../02_podstawy_jezyka/07_referencje_wskazniki_i_tablice.md)
- [string i string_view](../06_biblioteka_standardowa/01_string_string_view_i_tekst.md)
- [Ranges i views](../06_biblioteka_standardowa/06_ranges_i_views.md)

