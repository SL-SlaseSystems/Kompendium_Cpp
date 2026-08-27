[← Spis treści](../README.md)

# Namespaces, visibility i ADL

Przestrzeń nazw grupuje nazwy i ogranicza kolizje. Może być otwierana w wielu miejscach, zagnieżdżana i aliasowana. Namespace nie jest mechanizmem ochrony dostępu; publiczność symbolu binarnego i eksport biblioteki to osobne zagadnienia ABI.

~~~cpp
#include <cassert>
#include <utility>

namespace geometry {
struct Point {
    int x;
    int y;
    friend bool operator==(const Point&, const Point&) = default;
};

void swap(Point& left, Point& right) noexcept {
    using std::swap;
    swap(left.x, right.x);
    swap(left.y, right.y);
}
} // namespace geometry

int main() {
    geometry::Point first{1, 2};
    geometry::Point second{3, 4};
    using std::swap;
    swap(first, second); // ADL znajduje geometry::swap
    assert((first == geometry::Point{3, 4}));
}
~~~

Argument-dependent lookup (ADL) dodaje do wyszukiwania przestrzenie i klasy powiązane z typami argumentów. Dzięki temu niekwalifikowane `swap(a, b)` może znaleźć przeciążenie obok typu. Wzorzec `using std::swap; swap(a, b);` zachowuje standardowy fallback i customization przez ADL.

Dyrektywa `using namespace` w globalnym zakresie nagłówka zanieczyszcza przestrzeń każdego klienta i może zmienić overload resolution. W `.cpp` ograniczona dyrektywa bywa akceptowalna, ale deklaracja `using std::string;` jest bardziej precyzyjna. Alias namespace ułatwia pracę z długą nazwą bez importowania wszystkich symboli.

Ukryty friend (*hidden friend*) definiowany wewnątrz klasy jest znajdowany głównie przez ADL. To wartościowy sposób projektowania symetrycznych operatorów i ograniczania przypadkowych kandydatów.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Namespaces, visibility i ADL”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz odnalezienie deklaracji, przetworzenie zależności, utworzenie plików obiektowych, rozwiązanie symboli i złożenie końcowego artefaktu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel zależność źródłową, wymaganie użycia biblioteki, szczegół ABI oraz ustawienie prywatne konkretnego targetu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź graf targetów, pełne komendy kompilacji, tablicę symboli, kolejność linkowania i zawartość pakietu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projekt C++ jest grafem jednostek translacji, modułów, bibliotek i artefaktów. Kompilator analizuje jednostki osobno, linker łączy definicje, a system budowania musi odtworzyć zależności i opcje w sposób powtarzalny. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- ADL dodaje do wyszukiwania funkcje z przestrzeni skojarzonych z typami argumentów. Hidden friend wykorzystuje tę regułę, udostępniając operację tylko wtedy, gdy uczestniczy odpowiedni typ.
- Vtable i key function są elementami ABI implementacji, nie normatywną reprezentacją standardu. Ukryta visibility zmniejsza publiczną powierzchnię symboli i umożliwia optymalizacje, ale musi być spójna z eksportowanym API.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Namespaces, visibility i ADL” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Namespaces, visibility i ADL
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Namespaces, visibility i ADL”, oceniaj hermetyczność, szybkość przebudowy, przenośność konfiguracji, kontrola publicznych zależności i zgodność ABI. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Overload resolution i ADL](../zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)
- [Linkowanie i ODR](02_linkowanie_odr_i_inline.md)
- [API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
