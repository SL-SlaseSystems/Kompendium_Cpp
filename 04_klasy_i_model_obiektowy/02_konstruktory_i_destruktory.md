[← Spis treści](../README.md)

# Konstruktory i destruktory

Konstruktor rozpoczyna życie kompletnego obiektu po skonstruowaniu klas bazowych i pól. Elementy są inicjalizowane w kolejności deklaracji w klasie, nie w kolejności listy inicjalizacyjnej. Destrukcja zachodzi odwrotnie: najpierw ciało destruktora, potem pola i klasy bazowe.

~~~cpp
#include <cassert>
#include <string>
#include <utility>

class Account {
public:
    Account(std::string owner, int balance = 0)
        : owner_{std::move(owner)}, balance_{balance} {}

    Account() : Account{"anonymous", 0} {}

    [[nodiscard]] const std::string& owner() const noexcept { return owner_; }
    [[nodiscard]] int balance() const noexcept { return balance_; }

private:
    std::string owner_;
    int balance_{};
};

int main() {
    const Account named{"Ada", 100};
    const Account guest;
    assert(named.balance() == 100);
    assert(guest.owner() == "anonymous");
}
~~~

Delegating constructor pozwala jednej wersji wywołać inną, ograniczając powtarzanie inwariantów. In-class member initializers zapewniają wartości domyślne. Konstruktor jednoargumentowy powinien zwykle być `explicit`, chyba że konwersja jest naturalną i bezpieczną częścią semantyki typu.

Obiekt nie jest jeszcze kompletnym obiektem najbardziej pochodnej klasy podczas budowania bazy. Wywołania wirtualne w konstruktorze lub destruktorze nie dispatchują do nieistniejącej już części pochodnej. Nie publikuj `this` przed zakończeniem konstrukcji.

Destruktor jest generowany automatycznie, jeśli nie trzeba specjalnego zachowania. W hierarchii usuwanej polimorficznie destruktor klasy bazowej musi być public virtual albo należy uniemożliwić takie usuwanie, np. przez chroniony niewirtualny destruktor.

## Jak to działa krok po kroku

Przy konstrukcji najbardziej pochodnego obiektu najpierw inicjalizowane są bazy wirtualne, potem bezpośrednie bazy w kolejności deklaracji, następnie niestatyczne pola w kolejności deklaracji i wreszcie wykonywane jest ciało konstruktora. Kolejność wpisów po dwukropku nie zmienia tej sekwencji. Dlatego pole zależne od innego musi być zadeklarowane po nim, a nie jedynie później wymienione na liście inicjalizacyjnej.

W `Account` najpierw powstaje `owner_`, potem `balance_`, a ciało konstruktora jest puste. Konstruktor delegujący `Account()` wybiera drugi konstruktor tej samej klasy. Konstruktor docelowy odpowiada za wszystkie bazy i pola, a ciało delegującego wykonuje się później. Nie można równocześnie delegować i osobno wymieniać kolejnych inicjalizatorów pól.

Inicjalizacja pola różni się od przypisania w ciele. Jeśli napis najpierw zostanie domyślnie skonstruowany, a potem otrzyma wartość przez przypisanie, są to dwie operacje na jego życiu. Bezpośrednia inicjalizacja od razu buduje właściwą wartość. Pola referencyjne i stałe wymagają inicjalizacji; zwykłe przypisanie w ciele nie może zastąpić ich utworzenia.

## Pogłębienie mechanizmu

Inicjalizator domyślny pola jest używany, gdy dany konstruktor nie poda własnego inicjalizatora tego pola. Ułatwia wspólną wartość domyślną, lecz nie zmienia kolejności. `int count{};` zapewnia zero przy takim użyciu, podczas gdy nieinicjalizowany zwykły `int` może mieć wartość indeterminate. Nie należy liczyć na przypadkowe wyzerowanie miejsca przez system operacyjny.

Jeżeli inicjalizacja drugiego pola rzuci, pierwsze w pełni skonstruowane pole jest niszczone. Ciało konstruktora nie rozpoczyna się, a destruktor całej klasy nie wykonuje się. Gdy wyjątek pochodzi z ciała, wszystkie wcześniej skonstruowane pola i bazy również są sprzątane. To powód, dla którego zasoby należy od razu umieszczać w polach RAII.

Destrukcja zaczyna się od ciała destruktora najbardziej pochodnej klasy. W tym momencie jej pola jeszcze istnieją. Następnie niszczone są pola w odwrotnej kolejności i bazy; bazy wirtualne na końcu obsługuje najbardziej pochodny obiekt. Gdy trwa konstruktor albo destruktor bazy, wywołania wirtualne dotyczą odpowiedniego etapu hierarchii, nie kompletnej przyszłej lub już rozebranej klasy pochodnej.

Konstruktor nie ma typu zwracanego i nie może być wirtualny. Wybór konkretnego typu obiektu musi poprzedzać rozpoczęcie konstrukcji. Polimorficzne tworzenie zwykle realizuje fabryka zwracająca właściciela interfejsu. Destruktor może być wirtualny, ponieważ typ dynamiczny już istniejącego obiektu pozwala dobrać prawidłowe sprzątanie.

Deklaracja zwykłego konstruktora może wyłączyć automatyczne dostarczenie konstruktora domyślnego. `= default` przywraca żądaną operację tylko wtedy, gdy pola i bazy pozwalają ją wykonać. Referencja bez inicjalizatora może spowodować, że domyślna konstrukcja będzie usunięta. Ponadto `T object();` jest deklaracją funkcji, nie tworzeniem obiektu; zapis `T object{};` unika tej niejednoznaczności.

## Drugi przykład

Stała tablica dziennika umożliwia prześledzenie zdarzeń bez dodatkowych alokacji. Program potwierdza, że pola kończą życie dopiero po ciele destruktora właściciela.

~~~cpp
#include <array>
#include <cassert>
#include <cstddef>

struct Log {
    std::array<int, 5> events{};
    std::size_t size{};
    void push(int event) noexcept { events[size++] = event; }
};
struct Part {
    Log& log;
    int id;
    Part(Log& output, int number) : log{output}, id{number} { log.push(id); }
    ~Part() { log.push(-id); }
};
struct Whole {
    Log& log;
    Part first;
    Part second;
    explicit Whole(Log& output) : log{output}, first{output, 1}, second{output, 2} {}
    ~Whole() { log.push(0); }
};

int main() {
    Log log;
    { Whole object{log}; }
    assert((log.events == std::array{1, 2, 0, -2, -1}));
}
~~~

Zero oznacza ciało destruktora `Whole`, a ujemne identyfikatory destruktory pól. `Log` żyje dłużej od wszystkich rejestrujących obiektów, więc odwołania używane podczas sprzątania pozostają ważne. Gdyby logger był polem deklarowanym po elementach, kolejność jego życia wymagałaby innego projektu.

## Porównanie i decyzje

Umieszczaj reprezentację od elementów niezależnych do zależnych, a listę inicjalizacyjną zapisuj w kolejności deklaracji. Pozwala to łatwo porównać kod z rzeczywistym przebiegiem. Wspólne wartości początkowe wpisuj przy polach, wspólną walidację skupiaj w konstruktorze docelowym lub fabryce. Nie publikuj `this` odbiorcom, którzy mogą użyć obiektu przed ukończeniem inwariantu.

**Ćwiczenie.** W klasie zadeklarowano `int second_; int first_;`, a konstruktor ma listę `first_{7}, second_{first_}`. Czy kolejność zapisu zapewnia siedem w obu polach?

**Odpowiedź.** Nie. `second_` inicjalizuje się pierwsze i próbuje czytać jeszcze niezainicjalizowane `first_`. Należy zmienić kolejność deklaracji albo uniezależnić inicjalizatory. Ostrzeżenie o kolejności inicjalizacji wskazuje realny problem semantyczny.

Źródła: [inicjalizacja baz i pól](https://timsong-cpp.github.io/cppwp/n4950/class.base.init), [destruktory](https://timsong-cpp.github.io/cppwp/n4950/class.dtor), [konstruktory](https://timsong-cpp.github.io/cppwp/n4950/class.ctor).

## Powiązane tematy

- [RAII i destruktory](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
- [Funkcje specjalne](03_funkcje_specjalne_i_operatory.md)
- [Dziedziczenie i polimorfizm](04_dziedziczenie_i_polimorfizm.md)

