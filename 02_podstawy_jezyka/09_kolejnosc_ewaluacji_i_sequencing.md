[← Spis treści](../README.md)

# Kolejność ewaluacji i sequencing

## Wymagania wstępne

Potrzebujesz znajomości operatorów, argumentów funkcji, efektów ubocznych oraz obiektów tymczasowych. Przyjmujemy C++23 i wskazujemy istotne gwarancje wprowadzone w C++17. Analizujemy wykonanie jednego wątku; relacja *sequenced before* nie zastępuje synchronizacji między wątkami. Przykłady uczą rozpoznawać zbiór dozwolonych wyników, a nie przewidywać preferencje konkretnego kompilatora.

Priorytet i łączność operatorów opisują drzewo składni. Kolejność ewaluacji opisuje wykonanie obliczeń i efektów ubocznych. Zapis `a() + b() * c()` grupuje się jako `a() + (b() * c())`, lecz nie nakazuje zaczynać od `b()`. Wartość mnożenia musi być znana przed końcowym dodawaniem, ale wywołanie `a()` może nastąpić wcześniej. Dodatkowe nawiasy zmieniają grupowanie; same nie tworzą nowej gwarancji czasowej.

## Jak to działa krok po kroku

Rozbij analizę na obliczenia wartości i efekty uboczne. Dla `i++` wartością wyrażenia jest stara wartość `i`, a efektem ubocznym zwiększenie obiektu. Nie zakładaj, że każde użycie tej składni oznacza jedną niepodzielną operację widzianą identycznie przez wszystkie otaczające wyrażenia. Standard określa relacje między zdarzeniami; dopiero z tych relacji wynika poprawność wspólnego użycia zmiennej.

Istnieją trzy istotne sytuacje. *Sequenced before* narzuca kierunek: A przed B. *Indeterminately sequenced* oznacza, że całe A poprzedza całe B albo odwrotnie, ale wybór jest nieokreślony. *Unsequenced* oznacza brak obu takich relacji. W ostatnim przypadku konflikt modyfikacji z modyfikacją lub odczytem tej samej lokalizacji pamięci może powodować UB. Rozróżnienie oraz dokładne warunki podaje [N4950, intro.execution](https://timsong-cpp.github.io/cppwp/n4950/intro.execution).

Od C++17 inicjalizacje parametrów wywołania są względem siebie *indeterminately sequenced*. Wyrażenie `f(i++, i++)` nie powoduje z samego tego powodu UB, ale funkcja może otrzymać wcześniejszą wartość jako pierwszy albo drugi argument. Nie oznacza to, że oba argumenty otrzymują dowolne wartości. Przy początkowym zerze i parametrach `int` dozwolone pary to zero i jeden albo jeden i zero. Wszystkie efekty obliczenia argumentów kończą się przed wejściem do funkcji; zobacz [N4950, expr.call](https://timsong-cpp.github.io/cppwp/n4950/expr.call).

~~~cpp
#include <array>
#include <cassert>
#include <utility>

std::pair<int, int> collect(int first, int second) {
    return {first, second};
}

int main() {
    int counter = 0;
    auto next = [&counter] { return counter++; };

    const auto result = collect(next(), next());
    assert(counter == 2);
    assert((result == std::pair{0, 1} || result == std::pair{1, 0}));

    counter = 0;
    const std::array ordered{next(), next(), next()};
    assert((ordered == std::array{0, 1, 2}));

    counter = 0;
    const int first = next();
    const int second = next();
    assert((collect(first, second) == std::pair{0, 1}));
}
~~~

Pierwsze wywołanie celowo akceptuje oba porządki. Asercja wymagająca wyłącznie pary `{0, 1}` testowałaby przypadkowy wybór implementacji. Klamrowa lista inicjalizacyjna działa inaczej: jej elementy są ewaluowane w kolejności zapisu, wraz z efektami ubocznymi. Gwarancja obejmuje również listę używaną do wywołania konstruktora, a nie tylko agregaty. Osobne instrukcje dają jeszcze bardziej bezpośredni sposób utrwalenia wymaganej kolejności. Regułę klamer opisuje [N4950, dcl.init.list](https://timsong-cpp.github.io/cppwp/n4950/dcl.init.list).

## Pogłębienie mechanizmu

Nie przenoś gwarancji wywołania na dowolny operator. Wbudowane dodawanie nie sekwencjonuje lewego operandu przed prawym. Poniższy program zawiera niezsekwencjonowane modyfikacje tego samego `int`, więc ma UB. Jest oznaczony `cpp,notest`, ponieważ jego uruchomienie nie sprawdza żadnego legalnego wyniku i mogłoby jedynie utrwalić mylące obserwacje.

~~~cpp,notest
int main() {
    int i = 0;
    return i++ + i++; // UB: brak wymaganej relacji między modyfikacjami.
}
~~~

Dwa niezsekwencjonowane odczyty tej samej liczby nie stanowią analogicznego konfliktu. Również modyfikacje niezależnych obiektów nie powodują automatycznie tego rodzaju UB. Trzeba wskazać konkretną lokalizację i konfliktujące działania. Osobno sprawdza się inne warunki poprawności, takie jak zakres liczb, ważność wskaźnika i czas życia. Usunięcie problemu kolejności nie dowodzi poprawności całego wyrażenia.

Wbudowane `&&` i `||` obliczają lewy operand przed ewentualnym prawym i stosują krótkie spięcie. W `condition ? yes() : no()` najpierw oblicza się warunek, następnie tylko wybraną gałąź. Wbudowany operator przecinka sekwencjonuje lewy operand przed prawym, ale przecinek między argumentami funkcji jest separatorem składniowym. Nie należy uzasadniać nim kolejności argumentów. Te lokalne reguły opisują [expr.log.and](https://timsong-cpp.github.io/cppwp/n4950/expr.log.and), [expr.cond](https://timsong-cpp.github.io/cppwp/n4950/expr.cond) i [expr.comma](https://timsong-cpp.github.io/cppwp/n4950/expr.comma).

Od C++17 prawy operand przypisania jest sekwencjonowany przed lewym. Dlatego przy prawidłowej tablicy i indeksie `a[i++] = i` zapisuje starą wartość `i` do elementu o starym indeksie, a następnie pozostawia zwiększone `i`. Ta gwarancja nie działa przez samą prawostronną łączność przypisania: wynika z osobnego przepisu. Dla przesunięcia `left() << right()` lewa strona poprzedza prawą. Źródłami są [N4950, expr.ass](https://timsong-cpp.github.io/cppwp/n4950/expr.ass) i [expr.shift](https://timsong-cpp.github.io/cppwp/n4950/expr.shift).

## Drugi przykład

Składnia przeciążonego operatora zachowuje odpowiednie reguły sekwencjonowania operatora wbudowanego. Jawne wywołanie tej samej funkcji przez nazwę `operator<<` podlega regułom zwykłego wywołania. Można więc uzyskać te same wartości zwracane, lecz odmienne gwarancje kolejności argumentów. To istotna różnica podczas refaktoryzacji kodu bibliotecznego i generatorów wyrażeń; zobacz [N4950, over.match.oper](https://timsong-cpp.github.io/cppwp/n4950/over.match.oper).

~~~cpp
#include <cassert>
#include <vector>

struct Token {
    int value;
};

Token left(std::vector<int>& trace) {
    trace.push_back(1);
    return {10};
}

int right(std::vector<int>& trace) {
    trace.push_back(2);
    return 20;
}

int operator<<(Token token, int value) {
    return token.value + value;
}

int main() {
    std::vector<int> trace;
    const int first = left(trace) << right(trace);
    assert(first == 30);
    assert((trace == std::vector{1, 2}));

    trace.clear();
    const int second = operator<<(left(trace), right(trace));
    assert(second == 30);
    assert((trace == std::vector{1, 2} || trace == std::vector{2, 1}));
}
~~~

Nie wyciągaj stąd wniosku, że przeciążony `operator&&` zachowuje krótkie spięcie. Wywołanie funkcji wymaga przygotowania obu operandów. Składnia operatorowa zapewnia właściwą relację kolejności, lecz nie pominięcie drugiego argumentu. Jeśli druga operacja dereferencjonuje wskaźnik, przeciążenie nie może zastąpić wbudowanej ochrony `pointer && condition`. Kolejność i warunkowe wykonanie są odrębnymi własnościami.

Wyrażenie identyfikujące wywoływaną funkcję jest sekwencjonowane przed argumentami. W `get_object().method(make_argument())` najpierw oblicza się `get_object()`. Nadal nie ustala to kierunku między kilkoma argumentami metody. Tak samo łańcuch wywołań może zapewniać istotne zależności bez narzucania globalnej zasady „zawsze od lewej do prawej”. Analizuj konkretny zapis, zamiast przypisywać całemu językowi jeden porządek.

## Porównanie i decyzje

Pełne wyrażenie obejmuje także niszczenie obiektów tymczasowych, zwykle następujące przy kończącym je średniku. Jeśli rozdzielisz jedno wyrażenie na kilka instrukcji, możesz zmienić moment zwolnienia blokady, bufora lub uchwytu. Utrwalając kolejność, nadaj nazwy również właścicielom zasobów, które mają przetrwać do późniejszego wywołania. Samo wyjęcie wartości z tymczasowego właściciela może pozostawić wiszący wskaźnik.

Wybierz osobne instrukcje, gdy kolejność jest wymaganiem biznesowym: najpierw pobranie identyfikatora, potem zapis dziennika, następnie wysłanie żądania. Pozostaw nieokreśloną kolejność argumentów, gdy działania są niezależne i oba porządki są poprawne. W testach dokumentuj cały dopuszczalny zbiór wyników. Ostrzeżenia i sanitizery pomagają znaleźć podejrzane fragmenty, lecz udane uruchomienie nie zamienia nieokreślonej kolejności w gwarancję standardu ani nie legalizuje UB.

Przy przeglądzie kodu najpierw zaznacz wszystkie miejsca zmieniające stan. Potem połącz je z odczytami tych samych obiektów i sprawdź regułę otaczającego operatora albo wywołania. Ta procedura jest skuteczniejsza niż zapamiętywanie listy „dziwnych przykładów”. Pozwala również odróżnić nieszkodliwą swobodę kolejności od zależności, która musi zostać jawnie zapisana w programie.

**Ćwiczenie 1.** Czy `consume((read_header()), (read_body()))` gwarantuje odczyt nagłówka przed treścią?

<details>
<summary>Rozwiązanie</summary>

Nie. Nawiasy otaczają argumenty, a przecinek je oddziela. Oblicz nagłówek i treść w kolejnych instrukcjach, przechowaj wyniki, a dopiero potem wywołaj `consume`.

</details>

**Ćwiczenie 2.** Czy nieokreślona kolejność `collect(next(), next())` oznacza UB? Czy kompilator musi wybierać ten sam porządek przy każdym wywołaniu?

<details>
<summary>Rozwiązanie</summary>

W przedstawionym programie nie ma z tego powodu UB: inicjalizacje parametrów są nieokreślenie sekwencjonowane. Wybór kierunku nie musi być stały między wywołaniami. Poprawny test dopuszcza obie pary i sprawdza końcową wartość licznika.

</details>

## Powiązane tematy

- [Operatory i konwersje](04_operatory_i_konwersje.md)
- [Inicjalizacja i initializer_list](08_inicjalizacja_i_initializer_list.md)
- [Storage duration i lifetime](../03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md)
- [Atomiki i model pamięci](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md)
