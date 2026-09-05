[← Spis treści](../README.md)

# Storage duration i lifetime

*Storage duration* określa, jak długo istnieje pamięć przeznaczona dla obiektu. *Lifetime* określa okres, w którym w tej pamięci rzeczywiście istnieje obiekt danego typu. To różne pojęcia: pamięć może już być przydzielona, zanim rozpocznie się lifetime obiektu, albo pozostać dostępna po jego zakończeniu.

C++ wyróżnia automatic, static, thread i dynamic storage duration. Zwykłe zmienne lokalne mają automatic duration, obiekty namespace scope i lokalne `static` — static duration, `thread_local` — thread duration, a pamięć przydzielona dynamicznie trwa do zwolnienia. Słowa „stos” i „sterta” są przydatnym modelem implementacyjnym, ale standard formułuje reguły przez storage duration.

~~~cpp
#include <cassert>

int global_counter = 0; // static storage duration

int next_id() {
    static int local_counter = 0;
    ++global_counter;
    return ++local_counter;
}

int main() {
    const int first = next_id();
    const int second = next_id();
    assert(first == 1 && second == 2);
    assert(global_counter == 2);
}
~~~

Inicjalizacja lokalnej zmiennej statycznej od C++11 jest bezpieczna wobec równoczesnego pierwszego wejścia wielu wątków. Późniejszy dostęp do modyfikowalnego obiektu nadal wymaga synchronizacji. Destrukcja obiektów statycznych zachodzi podczas kończenia programu, lecz zależności między obiektami z różnych jednostek translacji mogą prowadzić do *static initialization order fiasco*.

Lifetime obiektu klasy zaczyna się po uzyskaniu odpowiednio wyrównanej pamięci i zakończeniu właściwej inicjalizacji, a kończy przy rozpoczęciu destruktora lub ponownym użyciu miejsca przez inny obiekt. Wskaźnik do pamięci nie jest dowodem, że żyje tam obiekt oczekiwanego typu.

## Jak to działa krok po kroku

Dla zwykłego lokalnego obiektu klasy rozpatrz trzy etapy: dostępność miejsca, wykonanie inicjalizacji i późniejsze zniszczenie. Kompilator może zarezerwować miejsce wcześniej, ale nie daje to prawa do używania jeszcze nieskonstruowanego obiektu. Konstruktor buduje najpierw bazy i pola. Po ukończeniu inicjalizacji istnieje kompletny obiekt z ustanowionym inwariantem, a przy wyjściu z zakresu uruchamiany jest destruktor.

Formalne zakończenie lifetime obiektu klasy następuje już przy rozpoczęciu wywołania destruktora. Nie oznacza to, że ciało destruktora nie może korzystać z pól: okres konstrukcji i destrukcji ma specjalne reguły. Pola są niszczone dopiero po wykonaniu ciała destruktora, w odwrotnej kolejności do inicjalizacji. Uproszczenie „każdy dostęp po końcu lifetime jest zawsze taki sam” pomija te szczególne fazy.

W pierwszym przykładzie nazwa `local_counter` jest widoczna tylko w funkcji, ale licznik nie powstaje na nowo przy każdym wejściu. Jego wartość jest zachowywana. Inicjalizacja lokalnego statyka z dynamicznym inicjalizatorem następuje przy pierwszym dojściu do deklaracji; jeśli rzuci wyjątek, kolejna próba wejścia może ją powtórzyć. Bezpieczeństwo tej inicjalizacji nie obejmuje późniejszego inkrementowania licznika.

## Pogłębienie mechanizmu

Obiekty tymczasowe zwykle są niszczone na końcu pełnego wyrażenia, najczęściej przy średniku. Lokalne związanie odpowiedniej referencji z temporary może przedłużyć jego życie. `const std::string& s = std::string{"abc"};` zachowuje napis do końca życia tej lokalnej referencji. Utworzenie następnej referencji z `s` nie przyznaje nowego, dłuższego okresu życia. Przedłużenie nie jest przekazywane jak własność.

Istnieją istotne wyjątki. Temporary związane z parametrem referencyjnym trwa do końca pełnego wyrażenia zawierającego wywołanie. Jeżeli funkcja zwróci ten alias i odbiorca zachowa go dłużej, powstanie dangling. Zwracanie referencji do lokalnego obiektu nie jest naprawiane przez `const` po stronie odbiorcy. Referencja jest opisem dostępu, a nie automatycznym właścicielem.

Biblioteka może oddzielać zajęte miejsce od aktywnych obiektów. `vector::reserve` zwiększa pojemność bez tworzenia dodatkowych elementów, dlatego indeks mniejszy od `capacity()`, ale nie od `size()`, nadal nie wskazuje legalnego elementu do zwykłego użycia. `optional::reset` niszczy zawartą wartość, chociaż miejsce wewnątrz samego `optional` nadal istnieje.

Ponowne użycie miejsca przez placement new wymaga odpowiedniego rozmiaru i wyrównania oraz prawidłowego zarządzania poprzednim obiektem. Reguły przezroczystego zastąpienia czasem pozwalają istniejącym nazwom i wskaźnikom odnosić się do następcy, lecz nie w każdym układzie podobiektów. Najbezpieczniej korzystać ze wskaźnika zwróconego przez operację konstrukcji; `std::launder` nie tworzy brakującego obiektu i nie legalizuje dowolnego rzutowania.

## Drugi przykład

`optional` pozwala pokazać koniec jednego życia i początek następnego bez ręcznego operowania na bajtach. Licznik mierzy aktywne obiekty, a nie liczbę istniejących miejsc na nie.

~~~cpp
#include <cassert>
#include <optional>

struct Tracked {
    static inline int alive = 0;
    int value;
    explicit Tracked(int number) : value{number} { ++alive; }
    ~Tracked() { --alive; }
    Tracked(const Tracked&) = delete;
    Tracked& operator=(const Tracked&) = delete;
};

int main() {
    std::optional<Tracked> slot;
    assert(Tracked::alive == 0);
    slot.emplace(7);
    assert(slot->value == 7 && Tracked::alive == 1);
    slot.reset();
    assert(!slot && Tracked::alive == 0);
    slot.emplace(9);
    assert(slot->value == 9 && Tracked::alive == 1);
}
~~~

`reset` kończy życie pierwszego `Tracked`, ale nie niszczy `slot`. Kolejne `emplace` konstruuje nową wartość. Nie należy zakładać, że wcześniejszy obserwator automatycznie jest właściwym uchwytem do nowego stanu; kod po zmianie powinien ponownie uzyskać dostęp przez właściciela.

## Porównanie i decyzje

Projektuj długość życia od właściciela w stronę obserwatorów. Gdy zadanie musi zachować dane po powrocie z funkcji, potrzebuje własnej wartości lub jawnego udziału we własności. Wskaźnik do lokalnej zmiennej nie spełni tego wymagania, nawet jeśli test chwilowo odczytuje spod niego oczekiwane bajty. Sanitizery mogą wykrywać część naruszeń, lecz brak raportu nie dowodzi istnienia obiektu.

**Ćwiczenie.** Czy rezerwacja stu elementów przez `std::vector<int> v; v.reserve(100);` pozwala wykonać `v[0] = 5`?

**Odpowiedź.** Nie. Rozmiar nadal wynosi zero. Potrzebne jest utworzenie elementu, na przykład przez `push_back(5)` lub `resize`. Pojemność określa możliwość wzrostu bez realokacji, a nie aktualny zakres żywych elementów dostępnych przez interfejs kontenera.

Źródła: [czas życia obiektów](https://timsong-cpp.github.io/cppwp/n4950/basic.life), [obiekty tymczasowe](https://timsong-cpp.github.io/cppwp/n4950/class.temporary), [konstrukcja i destrukcja](https://timsong-cpp.github.io/cppwp/n4950/class.cdtor).

## Powiązane tematy

- [Stos, sterta i pamięć dynamiczna](02_stos_sterta_i_dynamiczna_pamiec.md)
- [RAII](03_raii_i_destruktory.md)
- [Lifetime i provenance](../zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

