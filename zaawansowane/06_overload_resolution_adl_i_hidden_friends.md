[← Spis treści](../README.md)

# Overload resolution, ADL i hidden friends

Overload resolution buduje zbiór kandydatów przez lookup, dodaje kandydatów znalezionych przez ADL, sprawdza viability, szereguje implicit conversion sequences i wybiera najlepszą funkcję. Templates przechodzą dedukcję i constraints. Jeśli nie ma jednego najlepszego kandydata, wywołanie jest niejednoznaczne.

~~~cpp
#include <cassert>

namespace units {
class Meter {
public:
    explicit constexpr Meter(int value) : value_{value} {}
    friend constexpr Meter operator+(Meter left, Meter right) {
        return Meter{left.value_ + right.value_};
    }
    friend constexpr bool operator==(Meter, Meter) = default;

private:
    int value_;
};
} // namespace units

int main() {
    using units::Meter;
    constexpr Meter total = Meter{20} + Meter{22};
    static_assert(total == Meter{42});
}
~~~

Operatory są hidden friends: nie są zwykle odnajdywane przez zwykły lookup bez argumentu powiązanego z `Meter`, lecz ADL je znajduje. Zmniejsza to liczbę kandydatów i wiąże customization z typem.

Konwersja exact match wygrywa z promotion, promotion z conversion, ale istnieją dodatkowe reguły dla referencji, initializer lists, templates i rewritten candidates operatorów porównania. `explicit` usuwa konstruktor lub conversion function z kontekstów wymagających niejawnej konwersji.

Customization point pattern często wykonuje niekwalifikowane wywołanie po wprowadzeniu standardowego fallbacku. Należy unikać niekontrolowanej rekurencji i przypadkowego ADL dla typów zależnych. C++20 customization point objects w ranges używają bardziej złożonych reguł niż zwykła funkcja.

## Jak to działa krok po kroku

W wyrażeniu `Meter{20} + Meter{22}` typy argumentów wyznaczają powiązane klasy i przestrzenie nazw. ADL odnajduje funkcję zaprzyjaźnioną z `Meter`, choć nie została wprowadzona osobną deklaracją dostępną przez zwykłe wyszukiwanie. Funkcja otrzymuje dwie wartości, dodaje ich prywatne pola i konstruuje wynik. Przyjaźń nadaje dostęp do pól; ADL odpowiada za odnalezienie funkcji. Są to dwa odrębne mechanizmy.

Po zbudowaniu zbioru kandydatów kompilator sprawdza liczbę argumentów, dedukcję szablonów, constraints oraz możliwość niejawnych konwersji. Wybór najlepszego przeciążenia porównuje sekwencje konwersji dla poszczególnych argumentów. Kandydat powinien nie być gorszy dla żadnego argumentu i wygrać zgodnie z dalszymi regułami rozstrzygania. Nie oblicza się sumy „kosztów konwersji”; funkcja lepsza dla pierwszego argumentu, lecz gorsza dla drugiego może prowadzić do niejednoznaczności.

## Pogłębienie mechanizmu

Lookup poprzedza overload resolution. Prywatna funkcja składowa może uczestniczyć w wyborze, a dopiero wybranie niedostępnego kandydata kończy się błędem dostępu. Podobnie funkcja `= delete` jest kandydatem, który może wygrać i celowo zabronić określonej konwersji. Kompilator nie usuwa takich funkcji, aby spróbować mniej dopasowanego publicznego przeciążenia. To pozwala projektować precyzyjne ograniczenia interfejsu.

Standardowa sekwencja konwersji ma pierwszeństwo przed konwersją użytkownika, lecz „funkcja nieszablonowa wygrywa” działa dopiero przy spełnieniu odpowiednich warunków porównania. Szablon z dokładnym dopasowaniem może wygrać z funkcją nieszablonową wymagającą konwersji. List-initialization wprowadza preferencję dla konstruktorów `initializer_list`, dlatego `vector<int>{3, 7}` i `vector<int>(3, 7)` mają różną treść, mimo identycznych liczb.

Niekwalifikowane wywołanie `swap(a, b)` po `using std::swap` łączy standardowy fallback z możliwością odnalezienia specjalizowanej funkcji przez ADL. Bez fallbacku typ podstawowy może nie zapewnić żadnej funkcji do odnalezienia. Przy `std::swap(a, b)` kwalifikacja wyłącza ten mechanizm dostosowania. Obiekty punktów dostosowania biblioteki ranges mają własne dokładne reguły i nie są po prostu dowolnym zestawem przeciążeń funkcji o identycznej nazwie.

Hidden friend ogranicza przypadkowe konwersje: co najmniej jeden argument musi już wnosić właściwy powiązany typ do ADL. Dwa zupełnie obce argumenty nie spowodują odnalezienia operatora tylko dlatego, że oba mogłyby zostać przekonwertowane do `Meter`. Natomiast po odnalezieniu funkcji zwykłe reguły konwersji nadal obowiązują. `explicit` na konstruktorze zapobiega tu automatycznemu mieszaniu metrów z liczbami.

## Drugi przykład

~~~cpp
#include <cassert>
#include <utility>

namespace app {
struct Pair {
    int first, second;
    friend void swap(Pair& a, Pair& b) noexcept {
        using std::swap;
        swap(a.first, b.first);
        swap(a.second, b.second);
    }
};
}
template<class T>
void exchange_values(T& a, T& b) noexcept(noexcept(swap(a, b))) {
    swap(a, b);
}
int main() {
    app::Pair a{1, 2}, b{3, 4};
    exchange_values(a, b);
    assert(a.first == 3 && b.second == 2);
}
~~~

W tym celowo ograniczonym adapterze wywołanie zależne odnajduje wyłącznie swap dostarczony przez ADL; dlatego przykład instancjuje go dla `app::Pair`. Wewnątrz hidden friend używamy standardowego fallbacku dla pól `int`. Gdyby adapter miał obsługiwać także `int`, należałoby zapewnić fallback również dla jego wywołania i spójnie zbudować warunek `noexcept`, albo użyć `std::ranges::swap`. Wyrażenie w specyfikacji wyjątku także podlega regułom lookup.

## Porównanie i decyzje

Metoda składowa pasuje do operacji mającej wyraźny obiekt odbiorcy. Symetryczny operator arytmetyczny często czytelniej wyraża funkcja nieskładowa. Hidden friend daje dostęp do reprezentacji i kontroluje zakres wyszukiwania bez publicznych getterów. Nie dodawaj przeciążeń do `std`, poza szczególnymi dozwolonymi przez standard przypadkami specjalizacji; dostosowanie przez własną przestrzeń nazw jest właściwym punktem wyjścia.

**Ćwiczenie.** Dla `f(long)` i `template<class T> f(T)`, który kandydat przyjmie `int`? **Odpowiedź:** szablon, bo daje exact match zamiast konwersji do `long`. Czy `f(int)=delete` spowoduje wybór `f(long)` dla argumentu `int`? Nie; najlepsza funkcja pozostaje usunięta, więc wywołanie jest błędne. Tak odróżnisz brak kandydata od zakazanego najlepszego dopasowania.

Źródła: [N4950: ADL](https://timsong-cpp.github.io/cppwp/n4950/basic.lookup.argdep) i [najlepsza funkcja](https://timsong-cpp.github.io/cppwp/n4950/over.match.best).

### Ewolucja zbioru przeciążeń

Dodanie przeciążenia może zmienić znaczenie istniejącego wywołania, choć wszystkie wcześniejsze funkcje pozostały dostępne. Szczególnie wrażliwe są argumenty literałowe, `nullptr`, konstrukcje listowe i szablony z szeroką dedukcją. Testy interfejsu powinny obejmować typy argumentów rzeczywiście używane przez klientów, nie tylko wywołanie z dokładnie zadeklarowanym typem parametru. `0` ma historyczną rolę null pointer constant, której nie zachowuje automatycznie po dedukcji jako zwykły `int` w wrapperze.

Wywołanie funkcji składowej uwzględnia także obiekt odbiorcy. Kwalifikatory `const`, `&` i `&&` decydują, które metody są dostępne oraz jak dobrze pasują. Pozwala to zwracać widok z trwałego obiektu i wartość z obiektu tymczasowego. Różnice te należą do publicznego kontraktu, więc dopisanie pozornie wygodnego przeciążenia bez kwalifikatora referencyjnego może osłabić ochronę przed wiszącymi widokami.

Operatory porównania w C++20 i późniejszych standardach dodają rewritten candidates, między innymi związane z odwróceniem argumentów oraz wykorzystaniem `<=>`. Projektując mieszane porównania dwóch typów, sprawdzaj oba porządki operandów. Nie zakładaj, że analiza zwykłej nazwanej funkcji wyczerpuje wszystkie reguły dla operatorów.

ADL może zostać powstrzymane przez wynik zwykłego lookup, na przykład znalezienie określonej składowej klasy lub deklaracji niebędącej funkcją. Dlatego lokalna zmienna o nazwie punktu dostosowania potrafi zmienić znaczenie niekwalifikowanego wywołania. Podczas diagnozy sprawdź deklaracje widoczne w bieżącym zakresie, zanim uznasz, że funkcja z przestrzeni argumentu powinna zawsze uczestniczyć w wyborze. Oczekiwane przez bibliotekę miejsce dostosowania powinno być wyraźnie udokumentowane.

## Powiązane tematy

- [Funkcje i przeciążanie](../02_podstawy_jezyka/05_funkcje_i_przeciazanie.md)
- [Namespaces i ADL](../08_budowanie_i_organizacja/03_namespaces_visibility_i_adl.md)
- [Concept subsumption](08_concepts_normalization_i_subsumption.md)

