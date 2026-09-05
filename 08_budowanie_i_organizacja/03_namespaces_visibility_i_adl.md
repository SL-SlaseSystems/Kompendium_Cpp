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

W wywołaniu `swap(first, second)` nazwa jest niekwalifikowana. Zwykłe wyszukiwanie znajduje deklaracje wprowadzone przez `using std::swap`. ADL dodaje kandydatów z przestrzeni powiązanej z typem `geometry::Point`, więc znajduje również `geometry::swap`. Następnie rozstrzyganie przeciążeń wybiera najlepszą funkcję. Wewnątrz własnego swap pola są liczbami, dlatego standardowy wariant stanowi odpowiedni fallback.

Zapis `std::swap(first, second)` jest kwalifikowany i nie uruchamia tego samego wyszukiwania ADL. Może użyć generycznych operacji przeniesienia zamiast wyspecjalizowanej funkcji obok typu. Różnica bywa istotna dla kosztu i gwarancji wyjątków. Z kolei `using namespace geometry` nie jest potrzebne do ADL: mechanizm opiera się na typach argumentów, a nie na wcześniejszym imporcie nazw przez klienta.

Wyszukiwanie nazwy i wybór przeciążenia to dwa różne etapy. Najpierw powstaje zbiór kandydatów, a dopiero potem porównuje się dopasowania. Dostęp `private` nie jest wygodnym filtrem usuwającym niepożądane przeciążenia na początku całego procesu. Również eksport symbolu z biblioteki dynamicznej nie ma wpływu na to, którą funkcję znajdzie semantyczne wyszukiwanie w kodzie źródłowym.

## Pogłębienie mechanizmu

Powiązane encje dla klasy szablonowej mogą obejmować typy argumentów szablonu. Dlatego argument `std::vector<geometry::Point>` może wciągnąć do ADL więcej przestrzeni niż sam zapis nazwy wektora sugeruje. Typy fundamentalne nie dodają własnych przestrzeni. Mechanizm ma też reguły blokujące, np. zwykłe wyszukiwanie znajdujące odpowiedni obiekt niebędący funkcją może wyłączyć ADL. Nie traktuj go jako bezwarunkowego „przeszukaj wszystkie namespace”.

Hidden friend zdefiniowany w klasie jest funkcją niezależną, choć ma dostęp do prywatnych składowych. Należy do otaczającej przestrzeni nazw, ale bez dodatkowej deklaracji zwykle nie jest widoczny przez zwykłe kwalifikowane wyszukiwanie. ADL udostępnia go wtedy, gdy argument powiązuje wywołanie z klasą. Ogranicza to przypadkowe kandydatury i dobrze działa dla symetrycznych operatorów.

Alias przestrzeni nazw nie tworzy nowego zestawu encji: `namespace geo = geometry;` daje drugą nazwę tej samej przestrzeni. `inline namespace` pozwala kontrolować wersjonowanie źródłowego interfejsu i lookup, ale samo nie gwarantuje zgodności ABI starych binariów. Anonimowa przestrzeń nazw w nagłówku tworzy oddzielne encje w każdej jednostce, co może być niepożądane dla typów używanych w publicznym interfejsie.

W szablonach zależne wywołania funkcji podlegają zasadom wyszukiwania w dwóch fazach. Część informacji jest ustalana przy definicji szablonu, a ADL może uwzględnić powiązane deklaracje przy instancjacji. Dopisywanie przypadkowej funkcji później do globalnego zakresu nie jest niezawodnym sposobem dostosowania istniejącego szablonu. Umieszczaj legalne punkty dostosowania w przestrzeni typu albo korzystaj z konkretnego protokołu biblioteki.

## Drugi przykład

Operator porównania jako hidden friend otrzymuje dostęp do prywatnej reprezentacji, a klient używa zwykłej składni wartościowej.

~~~cpp
#include <cassert>
#include <utility>

namespace billing {
class Amount {
    int cents_;
public:
    explicit Amount(int cents) : cents_(cents) {}
    int cents() const noexcept { return cents_; }
    friend bool operator==(const Amount&, const Amount&) = default;
    friend void swap(Amount& a, Amount& b) noexcept {
        using std::swap;
        swap(a.cents_, b.cents_);
    }
};
}

template<class T>
void exchange_values(T& a, T& b) {
    using std::swap;
    swap(a, b);
}

int main() {
    billing::Amount a{100}, b{250};
    exchange_values(a, b);
    assert(a == billing::Amount{250});
    assert(b.cents() == 100);
}
~~~

Szablon nie zna nazwy `billing`, lecz typ argumentów wystarcza do znalezienia właściwej funkcji. `explicit` zapobiega niejawnej zamianie dowolnej liczby na kwotę. Nie potrzebujemy otwierać `namespace std`, aby zapewnić poprawne dostosowanie `swap`. Rozszerzanie przestrzeni standardowej jest silnie ograniczone i należy robić je tylko tam, gdzie specyfikacja wyraźnie na to pozwala.

## Porównanie i decyzje

Używaj kwalifikowanych nazw, gdy chcesz jednoznacznie wskazać konkretną funkcję. Używaj niekwalifikowanego wywołania z kontrolowanym fallbackiem, gdy projektujesz punkt dostosowania przez ADL. W publicznym nagłówku unikaj globalnych dyrektyw `using namespace`; decyzja o skróceniu nazw powinna należeć do użytkownika nagłówka. Dla nowoczesnych bibliotek ranges warto poznać ich obiekty punktów dostosowania, które mają własny uporządkowany protokół wyboru.

**Ćwiczenie.** Czy `namespace internal` ukrywa symbole przed użytkownikiem biblioteki? **Odpowiedź:** nie. To nazwa i konwencja organizacyjna. Ukrycie na poziomie kompilacji wymaga odpowiedniego interfejsu i linkage, a eksport binarny zależy od narzędzi platformy. Klient mający widoczną deklarację może odwołać się do takiej przestrzeni.

Źródła reguł: [C++23: ADL](https://timsong-cpp.github.io/cppwp/n4950/basic.lookup.argdep), [przestrzenie nazw](https://timsong-cpp.github.io/cppwp/n4950/namespace.def), [wyszukiwanie nazw zależnych](https://timsong-cpp.github.io/cppwp/n4950/temp.dep.candidate).

## Powiązane tematy

- [Overload resolution i ADL](../zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)
- [Linkowanie i ODR](02_linkowanie_odr_i_inline.md)
- [API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
