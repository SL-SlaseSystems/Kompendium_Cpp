[← Spis treści](../README.md)

# Silne typy, znaczenie porównań i kontrakt hash

**Wymagania wstępne:** konstruktory, `explicit`, przeciążanie operatorów, podstawy kontenerów asocjacyjnych. Przykłady używają C++23.

Funkcja przyjmująca dwie liczby nie mówi, która oznacza metry, a która sekundy. Nazwy parametrów pomagają czytelnikowi, lecz nie blokują zamiany argumentów. Silny typ przenosi to rozróżnienie do systemu typów. Jego wartość polega na ograniczeniu zbioru legalnych operacji: kompilacja ma odrzucać programy, które nie mają sensu w domenie, nawet gdy ich reprezentacja maszynowa jest identyczna.

Projekt zaczyna się jednak przed napisaniem konstruktora. Trzeba określić jednostkę, dopuszczalny zakres, politykę przepełnienia oraz znaczenie równości. Dwa identyfikatory mogą oznaczać tę samą encję mimo różnych etykiet. Dwa pomiary mogą być nieporównywalne. Domyślne porównanie wszystkich pól nie rozstrzyga tych pytań za autora interfejsu.

## Jak to działa krok po kroku

Poniższy typ przechowuje nieujemne wielkości o ograniczonym zakresie. Znacznik szablonu odróżnia jednostki, ale nie zajmuje miejsca w obiekcie. Granica miliona upraszcza także analizę dodawania: suma dwóch reprezentacji mieści się w `int` o zakresie jawnie sprawdzonym w przykładzie.

~~~cpp
#include <cassert>
#include <compare>
#include <limits>
#include <stdexcept>
#include <type_traits>

static_assert(std::numeric_limits<int>::max() >= 2'000'000);

template<class Unit>
class Quantity {
    int value_;
public:
    explicit Quantity(int value) : value_{value} {
        if (value < 0 || value > 1'000'000) {
            throw std::out_of_range{"quantity"};
        }
    }
    int count() const noexcept { return value_; }
    auto operator<=>(const Quantity&) const = default;

    friend Quantity operator+(Quantity a, Quantity b) {
        return Quantity{a.value_ + b.value_};
    }
};

struct Metre {};
struct Second {};
using Distance = Quantity<Metre>;
using Duration = Quantity<Second>;

double metres_per_second(Distance distance, Duration duration) {
    if (duration.count() == 0) {
        throw std::invalid_argument{"zero duration"};
    }
    return static_cast<double>(distance.count()) / duration.count();
}

int main() {
    static_assert(!std::is_convertible_v<int, Distance>);
    static_assert(!std::is_constructible_v<Distance, Duration>);
    assert(Distance{3} + Distance{4} == Distance{7});
    assert(Distance{3} < Distance{4});
    assert(metres_per_second(Distance{100}, Duration{20}) == 5.0);
    bool rejected = false;
    try {
        const auto too_far = Distance{900'000} + Distance{200'000};
        (void)too_far;
    } catch (const std::out_of_range&) {
        rejected = true;
    }
    assert(rejected);
}
~~~

`explicit` blokuje niejawne przejście z `int`, ale pozwala na świadome `Distance{100}`. Nie nadaje liczbie jednostki samodzielnie: odpowiada za to odrębna specjalizacja `Quantity`. Alias `using Distance = int` nie zapewniłby takiej ochrony. Jednocześnie nie udostępniamy konwersji do `int`; wydobycie reprezentacji przez `count()` jest widoczną decyzją na granicy API.

Dodawanie działa wyłącznie w obrębie tej samej jednostki. Suma przechodzi ponowną walidację, więc nie tworzy wartości naruszającej niezmiennik. Dzielenie odległości przez czas ma osobną nazwę i jawny warunek niezerowego mianownika. W większym systemie wynik powinien otrzymać własny typ prędkości. Tutaj `double` pokazuje jedynie miejsce świadomego wyjścia poza dwa zaprojektowane typy.

Nie dopisuj automatycznie całej arytmetyki. Dodawanie dwóch identyfikatorów klienta zwykle nie ma znaczenia, choć ich reprezentacją również może być liczba. Konwersja kilometrów na metry wymaga sprawdzenia zakresu po skalowaniu; samo rzutowanie nie jest walidacją. Biblioteka jednostek powinna dodatkowo określać zachowanie przy zmianie precyzji i przy operacjach mieszających reprezentacje.

## Pogłębienie mechanizmu

Równość semantyczna odpowiada na pytanie, czy wartości są takie same w przyjętym modelu. Kolejność odpowiada na inne pytanie: jak ustawić je względem siebie. Kontener uporządkowany rozpoznaje równoważne klucze przez swój komparator, czyli brak mniejszości w obu kierunkach. Nie wywołuje w tym celu koniecznie `operator==`. Sortowanie rekordów wyłącznie według priorytetu może więc celowo grupować różne rekordy w jedną klasę równoważności.

Kategorie wyniku `<=>` informują odbiorcę, jak silny kontrakt proponuje porównanie. Nie są tylko wygodnymi odpowiednikami trzech wartości liczbowych.

| Kategoria | Znaczenie w projekcie typu | Typowy przykład |
|---|---|---|
| `strong_ordering` | Pełny porządek; równość wspiera zastępowalność w stanie istotnym dla porównania | Całkowita liczba metrów |
| `weak_ordering` | Pełny porządek klas równoważności; równoważne wartości mogą zachowywać obserwowalne różnice | Klucz encji z różnymi etykietami |
| `partial_ordering` | Dopuszcza dodatkowo nieporównywalność | Zmiennoprzecinkowy pomiar z NaN |

Wbudowane porównanie zmiennoprzecinkowe zwraca `partial_ordering`. Przy NaN wyniki `<`, `>`, `<=`, `>=` oraz `==` nie zachowują się jak dla zwykłej liczby. W szczególności brak `a < b` i brak `b < a` nie dowodzi wtedy równości. Próba potraktowania wszystkich takich par jako równoważnych psuje przechodniość równoważności wymaganej przez ścisły słaby porządek. Dlatego sortowanie zbioru zawierającego NaN wymaga osobnej polityki, na przykład odrzucenia NaN albo umieszczenia wszystkich NaN za liczbami. [Reguły kategorii porównań](https://timsong-cpp.github.io/cppwp/n4950/cmp.categories) i [wbudowanego `<=>`](https://timsong-cpp.github.io/cppwp/n4950/expr.spaceship) opisują te różnice.

Domyślne `<=>` porównuje podobiekty w ustalonej kolejności. To dobry wybór dla reprezentacji dokładnie odpowiadającej wartości, ale zły dla rekordu z cache, etykietą diagnostyczną albo adresem alokacji. Ręcznie napisane `<=>` nie dostarcza automatycznie własnej definicji `==`; obie operacje trzeba zaprojektować spójnie. W pierwszym przykładzie specjalna reguła dotyczy porównania domyślnego.

## Drugi przykład

Klucz encji zachowuje etykietę do prezentacji, lecz tożsamość określa wyłącznie numer. Słaby porządek uczciwie komunikuje, że dwie równoważne wartości mogą mieć różny publicznie dostępny opis. Funkcja hash korzysta z tego samego numeru co równość.

~~~cpp
#include <cassert>
#include <compare>
#include <cstddef>
#include <functional>
#include <limits>
#include <string>
#include <unordered_set>

struct EntityKey {
    int id;
    std::string label;

    bool operator==(const EntityKey& other) const noexcept {
        return id == other.id;
    }
    std::weak_ordering operator<=>(const EntityKey& other) const noexcept {
        return id <=> other.id;
    }
};

struct EntityHash {
    std::size_t operator()(const EntityKey& key) const noexcept {
        return std::hash<int>{}(key.id);
    }
};

int main() {
    const EntityKey a{7, "Ada"};
    const EntityKey b{7, "Administrator"};
    assert(a == b);
    assert((a <=> b) == std::weak_ordering::equivalent);
    assert(EntityHash{}(a) == EntityHash{}(b));
    std::unordered_set<EntityKey, EntityHash> keys;
    keys.insert(a);
    keys.insert(b);
    assert(keys.size() == 1);

    if constexpr (std::numeric_limits<double>::has_quiet_NaN) {
        const double nan = std::numeric_limits<double>::quiet_NaN();
        const auto relation = nan <=> 1.0;
        assert(relation == std::partial_ordering::unordered);
        assert(!(relation < 0) && !(relation > 0) && !(relation == 0));
    }
}
~~~

Kontrakt wymaga, aby klucze równe według predykatu kontenera dawały ten sam hash. Odwrotna implikacja nie obowiązuje: kolizja jest legalna, a kontener rozstrzyga ją przez porównanie kluczy. Haszowanie etykiety przy równości opartej na numerze naruszyłoby wymaganie, nawet jeżeli przypadkowe testy wyszukiwania początkowo by przechodziły. [Wymagania kontenerów nieuporządkowanych](https://timsong-cpp.github.io/cppwp/n4950/unord.req) wiążą obie operacje.

Wartości hash nie są trwałym identyfikatorem pliku ani protokołu. Biblioteka nie obiecuje zgodności między uruchomieniami, wersjami implementacji czy platformami; kontrakt dotyczy określonego wykonania programu. Do zapisu trwałego potrzebujesz osobno zdefiniowanego algorytmu, kodowania i wersjonowania. Hash przeznaczony do tablicy nie daje też automatycznie własności kryptograficznych. [Wymagania `Cpp17Hash`](https://timsong-cpp.github.io/cppwp/n4950/hash.requirements) określają właściwy zakres gwarancji.

Stan wyznaczający równość i hash musi pozostawać stabilny podczas przechowywania klucza. Stałość samego obiektu w kontenerze nie zabezpiecza danych osiągalnych przez wskaźnik albo widok. Jeśli haszujesz zawartość cudzego napisu, jego właściciel nie może jej później zmienić bez wyjęcia i ponownego umieszczenia klucza. Podobne wymaganie dotyczy komparatora korzystającego z globalnego trybu sortowania. Zmiana trybu nie przebuduje istniejącego drzewa ani tablicy. Preferuj klucze przechowujące niezależną, niezmienną reprezentację tożsamości; etykieta prezentacyjna może natomiast pozostać informacją poboczną, jeśli konsekwentnie pomijają ją wszystkie operacje klucza.

## Porównanie i decyzje

Wybieraj najmocniejsze ograniczenia odpowiadające rzeczywistej domenie. Dla odległości przechowywanej jako liczba całkowita silny porządek jest naturalny. Dla pomiaru dopuszczającego NaN częściowy porządek ujawnia ważną informację. Zamiana kategorii na silniejszą bez zmiany reprezentacji i polityki danych jedynie ukrywa problem przed konsumentem API.

Przed dodaniem pola do klasy sprawdź jego wpływ na porównania i hash. Przed zmianą równości sprawdź wszystkie kontenery przechowujące ten typ. Ustalenie tożsamości jest decyzją o modelu danych, a nie szczegółem składni operatora. Oddzielny komparator do konkretnego widoku pozwala zmienić sposób prezentacji bez zmiany globalnej równości wartości.

**Ćwiczenie 1.** Rekordy mają identyfikator i priorytet. Czy `std::set` z komparatorem porównującym wyłącznie priorytet przechowa dwa rekordy o tym samym priorytecie?

<details>
<summary>Rozwiązanie</summary>

Nie jako dwa odrębne klucze. Komparator uznaje je za równoważne niezależnie od identyfikatora i `operator==`. Jeśli potrzebujesz obu rekordów, porównuj najpierw priorytet, a następnie identyfikator, albo świadomie użyj kontenera wielokrotnego.

</details>

**Ćwiczenie 2.** Typ odległości wprowadza równość z tolerancją: różnica mniejsza od jednego metra oznacza równość. Czy to dobry predykat kluczy?

<details>
<summary>Rozwiązanie</summary>

Zwykle nie: relacja może nie być przechodnia. Wartości 0,0 i 0,6 są bliskie, podobnie 0,6 i 1,2, lecz 0,0 i 1,2 już nie. Użyj jawnego testu bliskości do pomiarów albo dobrze zdefiniowanej kwantyzacji, jeżeli domena rzeczywiście potrzebuje klas równoważności.

</details>

Źródło uzupełniające: [N4950: porównania domyślne](https://timsong-cpp.github.io/cppwp/n4950/class.compare). Wszystkie odwołania do standardu dotyczą C++23.

## Powiązane tematy

- [Funkcje specjalne i operatory](03_funkcje_specjalne_i_operatory.md)
- [Kontenery i hash](../06_biblioteka_standardowa/03_map_set_unordered_i_hash.md)
- [Projektowanie API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
