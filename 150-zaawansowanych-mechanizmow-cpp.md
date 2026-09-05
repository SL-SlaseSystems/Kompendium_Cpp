[← Spis treści](README.md)

# 150 zaawansowanych mechanizmów języka C++

Praktyczny katalog nowoczesnego C++: zarządzanie zasobami, system typów, templates i concepts, ranges, coroutines, współbieżność, niskopoziomowa optymalizacja, metaprogramowanie, biblioteka standardowa, ABI, moduły oraz wybrane mechanizmy C++26.

Lista nie jest zamkniętą specyfikacją całego języka i biblioteki — C++ ma jeszcze więcej wyspecjalizowanych obszarów — ale 150 pozycji daje szeroki przekrój mechanizmów użytecznych w zaawansowanym i produkcyjnym kodzie.

> Stan standardu sprawdzony 2026-09-05. Bazą materiału jest **C++23** i stabilny draft N4950. Prace WG21 nad C++26 ukończono w marcu 2026 ([P3850R0](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p3850r0.pdf)); nie oznacza to pełnego wsparcia narzędzi. Punkty 97–100 są oznaczone jako C++26. Bloki `cpp` sprawdzamy jako niezależne jednostki C++23; `cpp,notest` wskazują jawnie opisany brak lokalnego API, przykład wieloplikowy lub rozszerzenie. Przejście kontroli składni nie zastępuje analizy lifetime, kontraktów i zachowania runtime.

## Spis treści

- [RAII, lifetime i pamięć — 1–20](#raii-lifetime-i-pamięć--120)
- [System typów, templates i concepts — 21–45](#system-typów-templates-i-concepts--2145)
- [Type erasure, ranges i coroutines — 46–65](#type-erasure-ranges-i-coroutines--4665)
- [Współbieżność i atomiki — 66–82](#współbieżność-i-atomiki--6682)
- [Low-level, diagnostyka, moduły i C++26 — 83–100](#low-level-diagnostyka-moduły-i-c26--83100)
- [Metaprogramowanie i produkcyjne C++ — 101–150](#dodatkowe-mechanizmy-metaprogramowania-i-produkcyjnego--101150)
- [Źródła](#źródła)

---

## RAII, lifetime i pamięć — 1–20

### 1. RAII — zasób związany z lifetime obiektu

Konstruktor przejmuje zasób, a destruktor zwalnia go deterministycznie. Dzięki temu wyjście przez wyjątek nie omija sprzątania.

```cpp
#include <cstdio>
#include <stdexcept>

class File {
    std::FILE* handle_{};
public:
    explicit File(const char* path) : handle_(std::fopen(path, "rb")) {
        if (!handle_) throw std::runtime_error("fopen failed");
    }
    ~File() { std::fclose(handle_); }

    File(const File&) = delete;
    File& operator=(const File&) = delete;
};
```

**Zastosowanie:** pliki, sockety, mutexy, transakcje, uchwyty GPU i zasoby systemowe.

**Dlaczego i jak:** W konstruktorze otwarcie pliku albo kończy się poprawnym uchwytem, albo zgłasza wyjątek. Po udanej konstrukcji destructor zostanie wywołany przy zwykłym wyjściu z zakresu i podczas rozwijania stosu. Usunięcie kopiowania zapobiega sytuacji, w której dwa obiekty próbują zamknąć ten sam plik. Klasa jest tutaj także nieprzenoszalna, ponieważ jawny destructor hamuje niejawne generowanie move; należy to traktować jako świadomy kontrakt, a nie pełny uniwersalny wrapper.

**Pułapka:** Destructor nie powinien rzucać, zwłaszcza gdy trwa obsługa innego wyjątku. Błędy końcowego zapisu wymagające reakcji klienta lepiej zgłaszać przez jawną metodę zamknięcia. RAII nie gwarantuje wykonania cleanup po nagłym zakończeniu procesu ani `std::terminate`; jego gwarancja dotyczy odpowiednich ścieżek semantyki C++.

**Dalej:** [Lifetime i reprezentacja](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 2. Rule of Zero

Jeżeli pola klasy same poprawnie zarządzają zasobami, nie deklaruj destruktora ani operacji kopiowania i przenoszenia.

```cpp
#include <string>
#include <type_traits>
#include <vector>

struct User {
    std::string name;
    std::vector<int> permissions;
};

static_assert(std::is_move_constructible_v<User>);
```

**Zastosowanie:** preferowany model większości klas domenowych i aplikacyjnych.

**Dlaczego i jak:** Każde pole `User` ma własne poprawne operacje specjalne. Kompilator składa z nich kopiowanie, przenoszenie i niszczenie obiektu, dzięki czemu dodanie kolejnego pola nie wymaga ręcznej aktualizacji pięciu metod. Skopiowanie wektora tworzy jego niezależne elementy, a przeniesienie korzysta z możliwości poszczególnych pól. Trait `is_move_constructible` sprawdza poprawność konstrukcji z rvalue; sam w sobie nie dowodzi, że istnieje specjalny move constructor ani że operacja nie kopiuje.

**Pułapka:** Dopisanie pozornie niewinnego destructora do logowania może wyłączyć niejawne generowanie przenoszenia. Rule of Zero nie oznacza, że każda kompozycja jest kopiowalna: pole `unique_ptr` spowoduje usunięcie kopiowania całej klasy. To pożądany wynik, jeśli reprezentuje wyłączną własność.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 3. Rule of Five

Klasa ręcznie posiadająca zasób powinna świadomie zdefiniować albo usunąć destruktor, copy constructor, copy assignment, move constructor i move assignment.

```cpp
#include <algorithm>
#include <cstddef>
#include <utility>

class Buffer {
    std::byte* data_{};
    std::size_t size_{};
public:
    explicit Buffer(std::size_t n) : data_(new std::byte[n]), size_(n) {}
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer& other) : Buffer(other.size_) {
        if (size_ != 0) std::copy_n(other.data_, size_, data_);
    }
    Buffer& operator=(const Buffer& other) {
        if (this != &other) { Buffer copy(other); swap(copy); }
        return *this;
    }
    Buffer(Buffer&& other) noexcept { swap(other); }
    Buffer& operator=(Buffer&& other) noexcept { swap(other); return *this; }
    void swap(Buffer& other) noexcept {
        std::swap(data_, other.data_); std::swap(size_, other.size_);
    }
};
```

**Zastosowanie:** własne kontenery i wrappery niskopoziomowych zasobów.

**Dlaczego i jak:** Copy constructor przygotowuje nowy bufor i kopiuje bajty, więc kopie mają niezależne przydziały. Copy assignment najpierw tworzy kopię tymczasową, a dopiero po sukcesie zamienia stan, zachowując oryginalny obiekt przy błędzie alokacji. Move constructor zamienia pusty stan własny ze stanem źródła. Pokazane move assignment również wykonuje swap: źródło przejmuje dawny bufor celu, zamiast koniecznie stać się puste. Taki stan po przeniesieniu jest dopuszczalny i musi zostać opisany.

**Pułapka:** Rule of Five jest wskazówką projektową, nie nakazem implementowania pięciu rozbudowanych funkcji. Dla rzeczywistego bufora łatwiej użyć `vector<std::byte>` i Rule of Zero. Ręczna wersja wymaga także uwagi na pusty stan, samoprzypisanie oraz poprawność operacji dla zerowej długości.

**Dalej:** [Lifetime i reprezentacja](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 4. `noexcept` w operacjach przenoszenia

Kontenery mogą przenosić elementy podczas realokacji tylko wtedy, gdy jest to bezpieczne dla gwarancji wyjątków. Dlatego move constructor zasobu zwykle powinien być `noexcept`.

```cpp
#include <utility>
#include <type_traits>

struct Handle {
    int value{-1};

    Handle() = default;
    Handle(Handle&& other) noexcept
        : value(std::exchange(other.value, -1)) {}
    Handle& operator=(Handle&& other) noexcept {
        value = std::exchange(other.value, -1);
        return *this;
    }
};

static_assert(std::is_nothrow_move_constructible_v<Handle>);
```

**Zastosowanie:** wydajne elementy `std::vector` i zasoby o wyłącznym ownershipie.

**Dlaczego i jak:** Podczas realokacji vector musi zbudować elementy w nowym storage, zanim zrezygnuje z poprzedniej reprezentacji. Jeśli move może rzucać i pozostawia źródła zmienione, nie zawsze da się odtworzyć stan sprzed niepowodzenia. Gdy kopiowanie jest dostępne, kontener może wybrać kopię, aby zachować silną gwarancję. `noexcept` na przenoszeniu uchwytu opisuje obietnicę, że samo przekazanie reprezentacji i unieważnienie źródła nie zawiedzie.

**Pułapka:** Jeżeli typ jest wyłącznie przenoszalny i jego move może rzucać, kontener nadal może potrzebować takiej operacji, lecz gwarancja wyjątków może być słabsza. Nie dodawaj `noexcept` dla szybkości, jeśli ciało może wypuścić wyjątek: złamanie obietnicy prowadzi do `terminate`. W prawdziwym uchwycie assignment musi również zwolnić dotychczasowy zasób.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 5. Wyłączny ownership przez `std::unique_ptr`

`unique_ptr` jest move-only i koduje jednoznacznego właściciela obiektu.

```cpp
#include <memory>

struct Engine { void start() {} };

std::unique_ptr<Engine> make_engine() {
    return std::make_unique<Engine>();
}

void use() {
    auto engine = make_engine();
    engine->start();
    auto transferred = std::move(engine);
}
```

**Zastosowanie:** drzewa obiektów, PIMPL i bezpieczne zastąpienie ręcznego `new/delete`.

**Dlaczego i jak:** `make_unique` konstruuje obiekt i od razu umieszcza jego adres w właścicielu. Przeniesienie zmienia obiekt odpowiedzialny za późniejsze zniszczenie `Engine`; silnik nie musi być kopiowany ani przenoszony. Po przeniesieniu źródłowy `unique_ptr` jest pusty. Parametr `unique_ptr<T>` przyjmowany przez wartość jasno komunikuje konsumpcję własności, podczas gdy `T&` lub `T*` zwykle opisuje tylko chwilowe korzystanie z silnika.

**Pułapka:** Wywołanie `get()` nie przekazuje własności, a `release()` ją oddaje bez niszczenia obiektu. Pomylenie tych operacji prowadzi odpowiednio do podwójnego właściciela albo wycieku. Przy konwersji `unique_ptr<Derived>` do `unique_ptr<Base>` domyślne usuwanie wymaga poprawnego modelu destrukcji przez bazę, zwykle virtual destructora.

**Dalej:** [Lifetime i reprezentacja](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 6. Współdzielony ownership przez `shared_ptr` i `weak_ptr`

`shared_ptr` używa control blocka z licznikami. `weak_ptr` obserwuje obiekt bez przedłużania jego lifetime i przerywa cykle.

```cpp
#include <memory>

struct Parent;
struct Child { std::weak_ptr<Parent> parent; };
struct Parent { std::shared_ptr<Child> child; };

void example() {
    auto parent = std::make_shared<Parent>();
    parent->child = std::make_shared<Child>();
    parent->child->parent = parent;

    if (auto locked = parent->child->parent.lock()) {
        (void)locked;
    }
}
```

**Zastosowanie:** grafy obiektów i callbacki, w których obserwator nie powinien utrzymywać właściciela.

**Dlaczego i jak:** Control block przechowuje informacje potrzebne do wspólnego zarządzania obiektem i jego zasobami. Ostatni silny udział kończy życie obiektu, natomiast słabe udziały mogą jeszcze utrzymywać sam blok kontrolny. W przykładzie rodzic posiada dziecko, a dziecko jedynie obserwuje rodzica. `lock()` atomowo próbuje uzyskać silny udział: jeśli się powiedzie, lokalny `locked` zabezpiecza lifetime rodzica na czas wykorzystania.

**Pułapka:** Sprawdzenie `expired()`, a następnie osobne korzystanie z surowego wskaźnika nie zastępuje `lock()`, ponieważ stan może się zmienić pomiędzy operacjami. Współbieżna kontrola udziałów nie chroni pól obiektu przed data race. Dwa osobne `shared_ptr` skonstruowane z tego samego surowego adresu utworzą niezależnych właścicieli i mogą podwójnie usunąć obiekt.

**Dalej:** [Lifetime i reprezentacja](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 7. Aliasing constructor `shared_ptr`

Nowy `shared_ptr` może współdzielić control block właściciela, ale wskazywać na jego podobiekt.

```cpp
#include <memory>
#include <string>

struct User { std::string name; };

std::shared_ptr<std::string> user_name(std::shared_ptr<User> user) {
    auto* name = &user->name;
    return {std::move(user), name};
}

void example() {
    auto user = std::make_shared<User>(User{"Ada"});
    auto name = user_name(user);
    user.reset();
    // `name` nadal utrzymuje cały obiekt User przy życiu.
}
```

**Zastosowanie:** bezpieczne udostępnianie widoku na pole obiektu posiadającego.

**Dlaczego i jak:** Aliasing constructor oddziela przechowywany wskaźnik od obiektu utrzymywanego przy życiu przez control block. `name.get()` wskazuje pole napisu, ale zniszczenie ostatniego udziału niszczy całego `User`, nie osobno jego pole. Adres pola pobieramy przed przeniesieniem `user`, aby kolejność obliczeń nie próbowała odczytać właściciela już opróżnionego przez move. Technika pozwala zwracać podwidok z odpowiednią własnością bazowego obiektu.

**Pułapka:** Wspólna własność zabezpiecza właściciela, lecz nie dowodzi stabilności wskazywanego elementu. Alias do elementu vectora może wisieć po realokacji, choć zawierający vector obiekt nadal żyje. Pole `name` w pokazanym `User` ma stabilną tożsamość przez życie tego obiektu; wskaźnik do jego znaków miałby słabszą gwarancję.

**Dalej:** [Lifetime i reprezentacja](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 8. Własny deleter smart pointera

Deleter pozwala opakować zasób, którego nie zwalnia się przez `delete`.

```cpp
#include <cstdio>
#include <memory>

struct FileCloser {
    void operator()(std::FILE* file) const noexcept {
        if (file) std::fclose(file);
    }
};

using FilePtr = std::unique_ptr<std::FILE, FileCloser>;

FilePtr open_file(const char* path) {
    return FilePtr{std::fopen(path, "rb")};
}
```

**Zastosowanie:** `FILE*`, uchwyty systemowe, biblioteki C i obiekty wymagające specjalnej funkcji zwalniającej.

**Dlaczego i jak:** Typ deletera stanowi część typu `unique_ptr`, więc wybór sposobu zwalniania jest sprawdzany razem z właścicielem. `FileCloser` przekazuje uchwyt do właściwego API C, a nie do operatora delete. Pusty wskaźnik reprezentuje nieudane otwarcie, które klient musi jawnie sprawdzić. Deleter jest tutaj bezstanowy; implementacja może kompresować takie pole, choć konkretny rozmiar smart pointera należy do implementacji.

**Pułapka:** Funkcja zwalniająca musi odpowiadać funkcji tworzącej zasób. Nie wolno mieszać `fopen/fclose`, `malloc/free` i `new/delete`. Jeżeli zamknięcie zwraca istotny błąd zapisu, nie da się wygodnie przekazać go przez destructor; potrzebny jest dodatkowy jawny etap finalizacji, a deleter pozostaje zabezpieczeniem sprzątania.

**Dalej:** [Alokatory i PMR](zaawansowane/04_allocatory_pmr_i_new_delete.md)

### 9. `make_shared` i pojedyncza alokacja

`make_shared` zwykle alokuje obiekt i control block razem, zmniejszając liczbę alokacji i poprawiając locality.

```cpp
#include <memory>
#include <string>
#include <utility>

struct Session {
    explicit Session(std::string id) : id(std::move(id)) {}
    std::string id;
};

auto session = std::make_shared<Session>("acq-42");
```

**Zastosowanie:** często tworzone obiekty współdzielone. Pamiętaj, że pamięć obiektu może pozostać do zniszczenia ostatniego `weak_ptr`.

**Dlaczego i jak:** Fabryka konstruuje `Session` w pamięci zarządzanej razem z control blockiem, co zwykle redukuje liczbę przydziałów względem osobnego `new` i konstruktora shared pointera. Destructor `Session` uruchamia się po wygaśnięciu ostatniego silnego udziału. Jeżeli pozostały weak pointers, ich `lock()` już się nie powiedzie, ale implementacja może jeszcze przechowywać wspólny przydział aż do usunięcia słabych udziałów.

**Pułapka:** Dla bardzo dużego obiektu i długo żyjących weak pointers wspólna alokacja może opóźniać odzyskanie znacznej ilości pamięci, mimo zakończonego lifetime obiektu. `make_shared` nie przyjmuje dowolnego własnego deletera tak jak odpowiedni konstruktor `shared_ptr`. Zmiana sposobu tworzenia wymaga więc uwzględnienia strategii zwalniania.

**Dalej:** [Alokatory i PMR](zaawansowane/04_allocatory_pmr_i_new_delete.md)

### 10. PIMPL i niepełny typ

Implementacja jest ukryta w pliku `.cpp`, co ogranicza zależności nagłówka i stabilizuje ABI. Destruktor musi być zdefiniowany tam, gdzie `Impl` jest kompletny.

```cpp
// widget.hpp
#include <memory>

class Widget {
    struct Impl;
    std::unique_ptr<Impl> impl_;
public:
    Widget();
    ~Widget();
    Widget(Widget&&) noexcept;
    Widget& operator=(Widget&&) noexcept;
};

// widget.cpp
struct Widget::Impl { int state{}; };
Widget::Widget() : impl_(std::make_unique<Impl>()) {}
Widget::~Widget() = default;
Widget::Widget(Widget&&) noexcept = default;
Widget& Widget::operator=(Widget&&) noexcept = default;
```

**Zastosowanie:** biblioteki binarne, szybsze buildy i izolacja prywatnych zależności.

**Dlaczego i jak:** Nagłówek zna jedynie nazwę `Impl` i reprezentację właściciela. Pełne pola implementacji są potrzebne przy konstrukcji, dostępie i usuwaniu, dlatego odpowiednie operacje definiuje się w pliku z kompletnym `Impl`. Klient nie musi ponownie analizować wszystkich prywatnych nagłówków biblioteki. Jawne move operations są potrzebne, ponieważ deklaracja destructora zmienia reguły ich niejawnego generowania. Pokazanie obu części w jednym bloku służy demonstracji; w projekcie są to oddzielne pliki.

**Pułapka:** PIMPL ogranicza zmiany layoutu, ale nie gwarantuje zgodności ABI różnych bibliotek standardowych i kompilatorów. Domyślne zdefiniowanie operacji usuwającej `Impl` w nagłówku może wymusić kompletny typ w niewłaściwym miejscu. Copy semantics trzeba zaprojektować osobno: usunąć kopiowanie albo utworzyć głęboką kopię implementacji.

**Dalej:** [Type erasure i ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

### 11. Nieposiadający widok `std::span`

`span<T>` opisuje ciągły zakres pamięci bez ownershipu. Może mieć dynamiczny lub statyczny extent.

```cpp
#include <array>
#include <span>

constexpr int sum(std::span<const int> values) {
    int result{};
    for (int value : values) result += value;
    return result;
}

static_assert(sum(std::array{1, 2, 3}) == 6);
```

**Zastosowanie:** jedno API dla tablic, `std::array`, `std::vector` i buforów C.

**Dlaczego i jak:** Span przekazuje adres pierwszego elementu i informację o długości albo długość zakodowaną w typie. Dzięki ciągłości storage ta sama funkcja może czytać tablicę lub vector bez zmiany reprezentacji danych. `span<const int>` zabrania modyfikacji elementów przez widok, lecz nie nadaje wyłączności i nie blokuje zmian przez właściciela. W przykładzie tymczasowa array pozostaje żywa do końca pełnego wyrażenia, więc synchroniczne sumowanie jest poprawne.

**Pułapka:** Span nie kontroluje całego lifetime i w C++23 nie wykonuje automatycznej kontroli każdego indeksu. Zapisanie widoku na tymczasową kolekcję do późniejszego użycia byłoby błędem. Sama suma może przepełnić `int` dla innych danych; wygodny widok nie usuwa obowiązku kontroli arytmetyki.

**Dalej:** [Lifetime i reprezentacja](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 12. Tekstowy widok `std::string_view`

`string_view` nie posiada znaków. Wywołujący musi zagwarantować, że źródło żyje dłużej niż widok.

```cpp
#include <string_view>

constexpr std::string_view extension(std::string_view path) {
    auto position = path.rfind('.');
    return position == path.npos ? std::string_view{} : path.substr(position + 1);
}

static_assert(extension("report.csv") == "csv");
```

**Zastosowanie:** parsery zero-copy i parametry tekstowe bez alokacji.

**Dlaczego i jak:** `rfind` wyszukuje ostatnią kropkę, a `substr` tworzy kolejny widok na istniejące znaki. Nie powstaje nowy napis ani przydział pamięci. Wynik dziedziczy zależność od lifetime źródła: literał z asercji żyje przez cały program, natomiast wynik dotyczący lokalnego `string` byłby bezpieczny tylko tak długo, jak jego bufor pozostaje ważny. Funkcja nie przechowuje źródła za klienta.

**Pułapka:** `string_view::data()` nie gwarantuje terminatora zera na końcu widoku. Przekazanie podwidoku do funkcji C oczekującej C-string może odczytać za dużo. Parser rozszerzenia jest celowo uproszczony: kropka w nazwie katalogu lub nazwa pliku ukrytego wymaga reguł domenowych, których sam widok nie dostarcza.

**Dalej:** [Lifetime i reprezentacja](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 13. Stan opcjonalny przez `std::optional`

`optional<T>` przechowuje zero lub jeden obiekt `T` bez osobnej alokacji.

```cpp
#include <optional>
#include <string_view>

std::optional<int> parse_port(std::string_view text) {
    int value{};
    for (char c : text) {
        if (c < '0' || c > '9') return std::nullopt;
        const int digit = c - '0';
        if (value > (65535 - digit) / 10) return std::nullopt;
        value = value * 10 + digit;
    }
    return value > 0 && value <= 65535 ? std::optional{value} : std::nullopt;
}
```

**Zastosowanie:** jawny brak wyniku zamiast wartości wartowniczej albo nullable pointera.

**Dlaczego i jak:** Optional oddziela obecność wyniku od jego wartości, więc port zero nie musi pełnić roli ukrytego kodu błędu. Parser powinien kontrolować zakres przed mnożeniem i dodawaniem kolejnej cyfry. W poprawionej wersji próg wyznaczamy z maksymalnego dozwolonego portu, dlatego bardzo długi napis zostanie odrzucony, zanim signed arithmetic może się przepełnić. `has_value()` lub kontekst logiczny rozstrzyga, czy wolno odczytać przechowywany port.

**Pułapka:** `operator*` wymaga obecnej wartości; nie jest automatycznie bezpieczniejszy od dereferencji wskaźnika. `value()` zgłasza wyjątek przy pustce. Optional nie wyjaśnia przyczyny błędu: jeśli klient ma odróżnić pusty tekst, niedozwolony znak i przekroczony zakres, lepszy będzie `expected` z odpowiednim typem błędu.

**Dalej:** [Optional i expected](07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)

### 14. Typowany sukces lub błąd przez `std::expected` — C++23

`expected<T,E>` przechowuje wartość albo błąd jako część typu wyniku.

```cpp
#include <expected>
#include <string>

enum class ParseError { empty, invalid };

std::expected<int, ParseError> parse_digit(std::string text) {
    if (text.empty()) return std::unexpected(ParseError::empty);
    if (text.size() != 1 || text[0] < '0' || text[0] > '9')
        return std::unexpected(ParseError::invalid);
    return text[0] - '0';
}
```

**Zastosowanie:** przewidywalne błędy domenowe bez wyjątków i bez utraty informacji o przyczynie.

**Dlaczego i jak:** Wartość `expected<int, ParseError>` ma jeden z dwóch stanów: sukces z cyfrą lub błąd z konkretną przyczyną. Zwrócenie liczby konstruuje stronę wartości, a `unexpected` jawnie wybiera stronę błędu. Dzięki temu te same reprezentacje wartości nie muszą kodować dwóch znaczeń. Rozróżnienie empty i invalid pozwala klientowi pokazać właściwy komunikat lub podjąć inną decyzję bez parsowania treści tekstowego wyjątku.

**Pułapka:** Expected nie gwarantuje, że całe wywołanie nie rzuca: utworzenie parametru `std::string` lub konstrukcja `T` i `E` mogą zgłosić wyjątek. `operator*` wymaga sukcesu, a `error()` wymaga stanu błędu. Sprawdzanie tylko dostępności nagłówka nie zastępuje weryfikacji potrzebnej rewizji biblioteki C++23.

**Dalej:** [Modele błędów](07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)

### 15. Sum type przez `std::variant`

`variant` zwykle przechowuje jeden z wyszczególnionych typów (z wyjątkiem możliwego stanu `valueless_by_exception`) i jest bezpieczniejszą alternatywą dla ręcznego unionu z tagiem.

```cpp
#include <string>
#include <variant>

struct Idle {};
struct Running { std::size_t samples; };
struct Failed { std::string message; };

using AcquisitionState = std::variant<Idle, Running, Failed>;

bool active(const AcquisitionState& state) {
    return std::holds_alternative<Running>(state);
}
```

**Zastosowanie:** maszyny stanów i modelowanie zamkniętej rodziny rezultatów.

**Dlaczego i jak:** Variant przechowuje alternatywę w swoim storage wraz z informacją, która jest aktywna. Typ stanu wymienia zamknięty zestaw możliwości, więc visitor może obsłużyć każdą z nich podczas kompilacji. `holds_alternative<Running>` bada aktywny typ bez wymuszania dostępu do niewłaściwego pola. Domyślna konstrukcja wybiera pierwszą alternatywę, o ile jest domyślnie konstruowalna; tutaj odpowiada to stanowi Idle.

**Pułapka:** Po niektórych rzucających zmianach alternatywy variant może stać się `valueless_by_exception`, więc skrót „zawsze dokładnie jedna wartość” wymaga tego zastrzeżenia. `get` niewłaściwej alternatywy rzuca, a `get_if` pozwala sprawdzić ją wskaźnikiem. Kolejność alternatyw wpływa na indeksy i nie powinna być bezpośrednim stabilnym formatem serializacji.

**Dalej:** [Type erasure i ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

### 16. Type erasure wartości przez `std::any`

`any` przechowuje kopiowalną wartość dowolnego typu i udostępnia bezpieczne, sprawdzane rzutowanie.

```cpp
#include <any>
#include <string>

std::any metadata = std::string{"calibrated"};

void inspect_metadata() {
    if (const auto* value = std::any_cast<std::string>(&metadata)) {
        (void)value->size();
    }
}
```

**Zastosowanie:** heterogeniczne metadane i granice pluginów. W silnie typowanej domenie zwykle lepszy jest `variant`.

**Dlaczego i jak:** Any zachowuje konkretny obiekt wraz z operacjami potrzebnymi do jego kopiowania i niszczenia, lecz usuwa jego typ z interfejsu. Wskaźnikowa postać `any_cast` zwraca null przy niedopasowaniu, dzięki czemu kontrola nie wymaga wyjątku. Dopasowanie dotyczy właściwego typu, a nie dowolnej konwersji: zapisanie `int` nie umożliwia odczytania `double`, mimo że zwykła konwersja liczby byłaby dopuszczalna.

**Pułapka:** Wymazanie typu przenosi część kontroli na runtime i wymaga uzgodnionego schematu metadanych. Any nie ustanawia stabilnego ABI dla pluginów różnych toolchainów; mogą różnić się layout, RTTI i biblioteka standardowa. Przechowanie dużej wartości może alokować, a mały bufor optymalizacyjny pozostaje szczegółem implementacji.

**Dalej:** [Type erasure i ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

### 17. Polymorphic allocators i `std::pmr`

Kontener PMR oddziela typ danych od strategii alokacji wybieranej w runtime.

```cpp
#include <array>
#include <cstddef>
#include <memory_resource>
#include <vector>

void process_frame() {
    std::array<std::byte, 4096> storage{};
    std::pmr::monotonic_buffer_resource arena{storage.data(), storage.size()};
    std::pmr::vector<int> values{&arena};

    values.reserve(100);
    values.push_back(42);
}
```

**Zastosowanie:** ograniczanie alokacji w gorącej ścieżce, przetwarzanie klatkowe i request-scoped arenas.

**Dlaczego i jak:** Polymorphic allocator pyta wskazany resource o pamięć, dzięki czemu wybór areny nie zmienia typu PMR-wektora. Bufor, arena i vector są deklarowane w kolejności zapewniającej bezpieczną destrukcję odwrotną. `reserve(100)` ogranicza potrzebę kolejnych realokacji. Arena monotoniczna nadaje się do danych kończących życie razem, bo nie odzyskuje każdego bloku osobno, lecz zwalnia przydziały grupowo.

**Pułapka:** Domyślna arena może przejść na upstream allocator po wyczerpaniu lokalnej tablicy, więc przykład nie dowodzi braku alokacji dynamicznych. Vector nie posiada areny i nie może jej przeżyć. `clear()` niszczy elementy, ale nie oddaje automatycznie całej pamięci monotonicznego zasobu do ponownego wykorzystania.

**Dalej:** [Alokatory i PMR](zaawansowane/04_allocatory_pmr_i_new_delete.md)

### 18. Własny `memory_resource`

Dziedziczenie po `std::pmr::memory_resource` pozwala instrumentować lub delegować alokacje bez zmiany typu kontenera.

```cpp
#include <cstddef>
#include <memory_resource>

class CountingResource final : public std::pmr::memory_resource {
    std::pmr::memory_resource* upstream_ = std::pmr::get_default_resource();
public:
    std::size_t allocated{};
private:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override {
        void* result = upstream_->allocate(bytes, alignment);
        allocated += bytes;
        return result;
    }
    void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) override {
        upstream_->deallocate(p, bytes, alignment);
    }
    bool do_is_equal(const memory_resource& other) const noexcept override {
        return this == &other;
    }
};
```

**Zastosowanie:** telemetryka pamięci, pule, regiony NUMA i specjalne alokatory.

**Dlaczego i jak:** Interfejs `memory_resource` rozdziela publiczny protokół od trzech wirtualnych operacji implementacyjnych. Własny zasób musi przekazać wymagane alignment zarówno przy alokacji, jak i dealokacji. Równość `this == &other` zachowawczo uznaje za wymienny tylko ten sam obiekt zasobu. Poprawiony licznik zwiększamy po udanym przydziale, więc oznacza sumę bajtów udanych żądań, a nie liczbę prób ani bieżące zużycie.

**Pułapka:** Ten licznik nie jest atomowy, dlatego równoczesne alokacje wymagają synchronizacji. Suma może również osiągnąć granicę `size_t` w długim działaniu; jeśli telemetria ma być dokładna, potrzebuje strategii przepełnienia. Zwrócenie równości dla niezamiennych zasobów może pozwolić kontenerowi zwolnić pamięć niewłaściwą drogą.

**Dalej:** [Alokatory i PMR](zaawansowane/04_allocatory_pmr_i_new_delete.md)

### 19. `construct_at`, `destroy_at` i placement lifetime

Surowa pamięć i lifetime obiektu to osobne pojęcia. `construct_at` rozpoczyna lifetime w przygotowanym miejscu, a `destroy_at` go kończy.

```cpp
#include <memory>
#include <new>
#include <string>

void construct_in_place() {
    alignas(std::string) std::byte storage[sizeof(std::string)];
    auto* pointer = reinterpret_cast<std::string*>(storage);

    pointer = std::construct_at(pointer, "in-place");
    auto size = pointer->size();
    std::destroy_at(pointer);

    (void)size;
}
```

**Zastosowanie:** własne kontenery, small-buffer optimization i pule obiektów.

**Dlaczego i jak:** Tablica zapewnia surowe bajty o odpowiednim rozmiarze i alignment. `construct_at` używa w tym miejscu konstruktora stringa, a zwrócony wskaźnik odnosi się do utworzonego obiektu. Dopiero potem legalne jest wywołanie `size()`. `destroy_at` kończy życie napisu i zwalnia jego wewnętrzne zasoby, lecz nie niszczy ani nie dealokuje zewnętrznej tablicy bajtów. To dwa osobne poziomy zarządzania pamięcią.

**Pułapka:** Samo `reinterpret_cast` nie konstruuje stringa. Jeśli między udaną konstrukcją a `destroy_at` pojawi się rzucająca operacja, przykład będzie potrzebował strażnika cleanup. Nie używaj tutaj `delete pointer`, ponieważ zewnętrzne storage nie pochodzi z odpowiadającego mu new-expression. Zapis wyniku `construct_at` upraszcza dowód tożsamości obiektu.

**Dalej:** [Lifetime i reprezentacja](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 20. `std::start_lifetime_as` — C++23

Funkcja rozpoczyna lifetime implicit-lifetime type w istniejącym regionie bajtów bez kopiowania. Wsparcie bibliotek standardowych nadal zależy od toolchainu.

> **C++23; poza lokalną weryfikacją Apple Clang 17/libc++.** Wymagana biblioteka implementująca `std::start_lifetime_as` w `<memory>`; w lokalnej konfiguracji tej funkcji brakuje.

```cpp,notest
#include <cstring>
#include <memory>

struct Header { unsigned kind; unsigned length; };

Header decode(const unsigned char* bytes) {
    alignas(Header) unsigned char storage[sizeof(Header)];
    std::memcpy(storage, bytes, sizeof(Header));
    auto* header = std::start_lifetime_as<Header>(storage);
    return *header;
}
```

**Zastosowanie:** jawne rozpoczynanie lifetime w bajtach reprezentacji zgodnej z lokalną implementacją; bezkopiowe warianty wymagają odpowiednio przygotowanego storage.

**Dlaczego i jak:** `start_lifetime_as` pozwala rozpocząć życie odpowiedniego implicit-lifetime type w istniejącym storage, zachowując reprezentację według reguł biblioteki. W przykładzie bajty najpierw kopiujemy do właściwie wyrównanej tablicy, więc jest to demonstracja lifetime, a nie całkowicie bezkopiowy parser. Wywołujący musi zapewnić co najmniej `sizeof(Header)` dostępnych bajtów oraz reprezentację odpowiadającą bieżącemu ABI i wymaganiom typu.

**Pułapka:** Mechanizm nie zamienia dowolnej ramki sieciowej w przenośny obiekt. Rozmiar unsigned, padding i kolejność bajtów nadal zależą od implementacji. Nie uruchamia zwykłego konstruktora klasy zarządzającej zasobem. Przykład oznaczono jako zależny od biblioteki, ponieważ lokalny zestaw Apple Clang i libc++ nie udostępnia tej funkcji C++23.

**Dalej:** [Lifetime i reprezentacja](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

---

## System typów, templates i concepts — 21–45

### 21. Kategorie wartości: lvalue, xvalue i prvalue

Kategoria wyrażenia wpływa na wybór przeciążenia, lifetime temporary i możliwość przenoszenia.

```cpp
#include <utility>

void inspect(const int&) {} // lvalue i const rvalue
void inspect(int&&) {}      // xvalue/prvalue

void inspect_categories() {
    int value = 1;
    inspect(value);
    inspect(2);
    inspect(std::move(value));
}
```

**Zastosowanie:** projektowanie przeciążeń i zrozumienie move semantics.

**Dlaczego i jak:** Wyrażenie `value` ma tożsamość istniejącej zmiennej i jest lvalue. Literał `2` jest prvalue, z którego przy wiązaniu referencji materializuje się obiekt tymczasowy. `std::move(value)` jest xvalue wskazującym tę samą zmienną; nie tworzy nowej liczby. Dwa ostatnie wywołania wybierają parametr `int&&`, lecz samo związanie referencji nie wykonuje żadnego przeniesienia zasobów. Warto odróżniać typ parametru od kategorii wyrażenia używanego wewnątrz funkcji.

**Pułapka:** Nazwany parametr `int&& argument` jest lvalue jako wyrażenie `argument`. Ponowne przekazanie go bez `move` lub właściwego `forward` może wybrać inne przeciążenie. Kategoria wartości nie opisuje też lifetime: xvalue może wskazywać długo żyjącą zmienną, a referencja lvalue może już wisieć.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 22. `std::move` jako rzutowanie kategorii

`std::move` niczego sam nie przenosi — zamienia wyrażenie na xvalue, umożliwiając wybranie operacji przenoszącej.

```cpp
#include <string>
#include <utility>

std::string transfer_payload() {
    std::string source = "payload";
    std::string destination = std::move(source);

    // `source` pozostaje poprawny, ale jego stan jest nieokreślony.
    source.clear();
    return destination;
}
```

**Zastosowanie:** jawne przekazanie zasobów z obiektu, który nie będzie już potrzebny w dotychczasowym stanie.

**Dlaczego i jak:** Rzutowanie usuwa z typu wyrażenia referencję i tworzy odpowiednią rvalue reference, zachowując kwalifikatory const. Konstruktor destination może wtedy przejąć zasoby stringa. Dla standardowego stringa źródło pozostaje w stanie valid but unspecified, więc można je zniszczyć, przypisać mu nową wartość albo wykonać operację bez dodatkowego warunku wstępnego, taką jak clear. Nie trzeba sprawdzać jego dawnej zawartości.

**Pułapka:** Nie uogólniaj tego na każdą klasę użytkownika: jej move powinien jawnie definiować dozwolony stan źródła. Move z const stringa zwykle wybierze kopiowanie. Dodanie `std::move(destination)` w return może wyłączyć NRVO; zwykły powrót nazwanej lokalnej wartości korzysta z reguł języka bez takiej podpowiedzi.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 23. Forwarding reference

Parametr `T&&` jest forwarding reference, gdy `T` jest cv-niekwalifikowanym parametrem typu dedukowanym dla danego wywołania. Może wtedy związać zarówno lvalue, jak i rvalue.

```cpp
#include <type_traits>

template<class T>
constexpr bool received_lvalue(T&&) {
    return std::is_lvalue_reference_v<T>;
}

int value{};
static_assert(received_lvalue(value));
static_assert(!received_lvalue(42));
```

**Zastosowanie:** generyczne fabryki, adaptery i wrappery wywołań.

**Dlaczego i jak:** Dla argumentu lvalue dedukcja ustala `T` jako referencję lvalue, a reference collapsing tworzy parametr zdolny ją przyjąć. Dla liczby tymczasowej `T` jest zwykłym `int`, więc parametr ma typ `int&&`. Trait bada tu wydedukowany parametr typu, nie wykonuje odczytu wartości argumentu. Dlatego asercja może analizować przekazanie istniejącej globalnej zmiennej bez potrzeby traktowania jej wartości jako stałego wyrażenia.

**Pułapka:** Nie każdy zapis `T&&` jest forwarding reference. `const T&&` oraz metoda używająca już ustalonego parametru klasy nie spełniają odpowiednich warunków dedukcji. Jeżeli funkcja ma wyłącznie konsumować konkretny typ, zwykłe `Widget&&` jest czytelniejszym kontraktem i nie należy nazywać go forwarding reference.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 24. Perfect forwarding przez `std::forward`

`std::forward<T>` zachowuje kategorię wartości przekazaną do forwarding reference.

```cpp
#include <memory>
#include <utility>

template<class T, class... Args>
std::unique_ptr<T> factory(Args&&... args) {
    return std::unique_ptr<T>{new T(std::forward<Args>(args)...)};
}

struct Job {
    Job(int priority, const char* name) {}
};

auto job = factory<Job>(5, "correlator");
```

**Zastosowanie:** emplace, fabryki i dekoratory bez zbędnych kopii.

**Dlaczego i jak:** Fabryka dedukuje każdy argument oddzielnie, a `forward<Args>` przywraca jego kategorię przy konstrukcji T. Lvalue pozostaje lvalue, natomiast argument rvalue może uruchomić konstruktor przenoszący. Jeżeli konstrukcja T rzuci po alokacji, new-expression zwolni odpowiednie storage. Powstały unique pointer przejmuje następnie odpowiedzialność za zniszczenie udanego obiektu. Standardowe `make_unique` realizuje ten podstawowy przypadek bez potrzeby własnej fabryki.

**Pułapka:** Forwarding nie rozstrzyga sam typu nieopisanej listy `{...}` ani nazwy przeciążonej funkcji. Dwukrotne przekazanie tego samego argumentu jako rvalue może skonsumować go przed drugim użyciem. Fabryka nie przedłuża życia referencji zapisanych przez konstruktor T; utworzony obiekt może nadal pożyczać dane od wywołującego.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 25. Reference collapsing

Podczas podstawiania template wszystkie kombinacje zawierające `&` zapadają się do `&`; tylko `&&` z `&&` pozostaje rvalue reference.

```cpp
#include <type_traits>

using L = int&;
using R = int&&;

static_assert(std::is_same_v<L&, int&>);
static_assert(std::is_same_v<L&&, int&>);
static_assert(std::is_same_v<R&, int&>);
static_assert(std::is_same_v<R&&, int&&>);
```

**Zastosowanie:** fundament perfect forwardingu i dedukcji `auto&&`.

**Dlaczego i jak:** Referencje do referencji nie są bezpośrednio zapisywalnym zwykłym typem deklaracji, ale mogą powstać po podstawieniu aliasów i parametrów szablonu. Reguły collapsing normalizują te kombinacje. Obecność choć jednego `&` daje referencję lvalue, co chroni kategorię argumentu lvalue przekazanego do generycznego `T&&`. Dopiero para referencji rvalue pozostaje `&&`. Statyczne asercje pokazują wszystkie cztery kombinacje bez zależności od zachowania runtime.

**Pułapka:** Collapsing nie usuwa automatycznie const obiektu ani nie zamienia referencji w własność. Alias `const int&` po dalszym składaniu nadal opisuje niemodyfikowalny obiekt. Jeżeli wynik ma być niezależną przechowywaną wartością, użyj odpowiedniej transformacji typu, na przykład `remove_cvref_t`, i świadomie skonstruuj nowy obiekt.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 26. `decltype` i `decltype(auto)`

`decltype(auto)` zachowuje dokładny typ wyrażenia, włącznie z referencją. Nawiasy wokół nazwy mogą zmienić wynik `decltype`.

```cpp
#include <type_traits>

int value = 42;

decltype(auto) by_reference() { return (value); }
decltype(auto) by_value() { return value; }

static_assert(std::is_same_v<decltype(by_reference()), int&>);
static_assert(std::is_same_v<decltype(by_value()), int>);
```

**Zastosowanie:** wrappery zachowujące typ wyniku i metaprogramowanie zależne od wyrażeń.

**Dlaczego i jak:** Dla nieujętej w nawiasy nazwy `value` specjalna reguła decltype zwraca deklarowany typ, tutaj int. Dla `(value)` analizowana jest kategoria wyrażenia, więc wynik stanowi int&. `decltype(auto)` stosuje właśnie te reguły do wyrażenia return, zamiast zwykłej dedukcji auto usuwającej referencję. Drobna zmiana nawiasów jest zatem zmianą publicznego typu wyniku, a nie jedynie formatowaniem kodu.

**Pułapka:** Zwrócenie `(local)` z funkcji o wyniku decltype(auto) może oddać referencję do zniszczonej zmiennej lokalnej. Również dostęp do pola ma specjalną regułę bez nawiasów. Wrapper zachowujący referencję powinien jawnie ustalić lifetime właściciela; zachowanie dokładnego typu nie jest samo w sobie gwarancją bezpiecznego API.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 27. CTAD i deduction guides

Class Template Argument Deduction pozwala wyprowadzić argumenty szablonu z konstruktora. Deduction guide koryguje reguły dedukcji.

```cpp
#include <string>
#include <string_view>
#include <type_traits>

template<class T>
struct Box {
    T value;
};

Box(const char*) -> Box<std::string>;

Box box{"text"};
static_assert(std::is_same_v<decltype(box), Box<std::string>>);
```

**Zastosowanie:** ergonomiczne tworzenie typów generycznych bez jawnych parametrów.

**Dlaczego i jak:** Deduction guide wskazuje, że argument typu const char* ma prowadzić do Box<string>, mimo że bez tej wskazówki łatwo otrzymać pudełko przechowujące tylko wskaźnik. Po wyborze typu zachodzi zwykła inicjalizacja odpowiedniej specjalizacji, więc napis zostaje skopiowany do własnego stringa. Guide nie jest wykonywaną funkcją i nie może dowolnie przekształcać argumentów; wybiera typ, którego konstrukcja nadal musi być poprawna.

**Pułapka:** Zmiana reguł CTAD może zmienić ownership, koszt alokacji i czas życia danych. Pudełko wskaźnika oraz pudełko stringa mogą wyglądać tak samo w miejscu użycia, ale zachowują się inaczej po zniknięciu źródła. Guides nie służą do wnioskowania argumentów każdej funkcji ani nie zastępują dedukcji szablonów funkcji.

**Dalej:** [Auto, decltype i CTAD](05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md)

### 28. Non-type template parameters (NTTP)

Parametrem template może być wartość znana w compile time, w C++20 również odpowiedni structural class type.

```cpp
#include <array>
#include <cstddef>

template<class T, std::size_t Rows, std::size_t Columns>
struct Matrix {
    std::array<T, Rows * Columns> data{};
};

constexpr Matrix<float, 4, 4> transform;
static_assert(transform.data.size() == 16);
```

**Zastosowanie:** macierze, bufory i protokoły z rozmiarem w typie.

**Dlaczego i jak:** Wymiary macierzy są wartościami należącymi do jej typu. Dzięki temu niezgodne rozmiary mogą zostać odrzucone przy kompilacji, a storage array ma znaną pojemność bez osobnej alokacji. Różne pary wymiarów tworzą różne specjalizacje, nawet jeśli ich iloczyn jest taki sam. Parametry wartościowe mogą też sterować wyborem implementacji, ale zwiększają liczbę typów i instancjacji obecnych w projekcie.

**Pułapka:** Iloczyn Rows * Columns ma typ size_t i może zawinąć modulo przed utworzeniem array. Produkcyjna klasa potrzebuje ograniczenia sprawdzającego iloczyn bez przepełnienia. Structural class type dla NTTP ma szczególne wymagania; dowolny string z dynamiczną pamięcią nie staje się parametrem szablonu tylko dlatego, że jego treść jest znana.

**Dalej:** [Stała ewaluacja](zaawansowane/09_constexpr_consteval_i_compile_time.md)

### 29. Variadic templates i parameter packs

Pack reprezentuje dowolną liczbę typów lub wartości i może być rozwijany w wielu kontekstach.

```cpp
#include <tuple>
#include <utility>

template<class... Ts>
auto make_references(Ts&... values) {
    return std::tuple<Ts&...>{values...};
}

int number{};
double ratio{};
auto references = make_references(number, ratio);
```

**Zastosowanie:** tuple, delegowanie konstruktorów i generyczne API o zmiennej arności.

**Dlaczego i jak:** Parametr Ts&... dedukuje osobny typ dla każdej przekazanej zmiennej. Rozwinięcie w `tuple<Ts&...>` tworzy strukturę zawierającą referencje, więc zmiana elementu tuple zmienia oryginalny obiekt. Rozwinięcie values... dostarcza inicjalizatory w odpowiadającej kolejności. Paczka nie jest kontenerem runtime i nie ma jednej metody push_back; jej liczba elementów i zestaw typów są częścią instancjacji funkcji.

**Pułapka:** Zwrócenie tuple referencji nie przedłuża lifetime zmiennych. Parametry lvalue reference świadomie odrzucają obiekty tymczasowe, ograniczając część błędów, lecz klient nadal może zachować tuple po zniszczeniu źródeł. Gdy potrzebna jest własność, fabryka powinna budować tuple wartości z odpowiednią semantyką kopiowania lub przenoszenia.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 30. Fold expressions

Fold redukuje pack przy użyciu operatora bez rekurencyjnej specjalizacji template.

```cpp
#include <concepts>

template<std::integral... Ts>
constexpr auto sum(Ts... values) {
    return (values + ... + 0);
}

static_assert(sum(1, 2, 3, 4) == 10);
```

**Zastosowanie:** agregowanie parametrów, logowanie i sprawdzanie całej listy constraints.

**Dlaczego i jak:** Zapis `(values + ... + 0)` jest binarnym foldem z początkową wartością zapewniającą wynik również dla pustej paczki. Kompilator rozwija operator według kierunku złożenia określonego składnią; przy operatorach niełącznych kierunek wpływa na wynik. Końcowe zero ma typ int i uczestniczy w zwykłych konwersjach arytmetycznych, dlatego wynik nie musi zachować typu najmniejszego argumentu. Constraints sprawdzają typy całkowite każdego elementu.

**Pułapka:** Łączność matematyczna nie gwarantuje identyczności obliczeń maszynowych. Signed overflow nadal jest UB, a mieszanie signed i unsigned może dać nieoczekiwany typ wyniku. Dla wykonywania efektów ubocznych w ustalonej kolejności często używa się foldu po operatorze przecinka; fold z plusem nie daje automatycznie takiego samego sekwencjonowania.

**Dalej:** [Constraints i subsumption](zaawansowane/08_concepts_normalization_i_subsumption.md)

### 31. Własne concepts

Concept nadaje nazwę predykatowi compile-time i uczestniczy w wyborze przeciążeń.

```cpp
#include <concepts>

template<class T>
concept Arithmetic = std::integral<T> || std::floating_point<T>;

template<Arithmetic T>
constexpr T square(T value) {
    return value * value;
}

static_assert(square(4) == 16);
```

**Zastosowanie:** czytelne kontrakty szablonów i lepsze diagnostyki niż klasyczne SFINAE.

**Dlaczego i jak:** Concept Arithmetic nazywa alternatywę dwóch kategorii typów i jest sprawdzany przed wyborem specjalizacji square. Int spełnia integral, a double spełnia floating_point. Typ posiadający operator mnożenia, ale nienależący do tych kategorii, zostanie odrzucony, nawet jeśli samo ciało mogłoby się skompilować. Concept powinien więc wyrażać zamierzony zakres domeny, a nie przypadkowo bardziej wąską listę niż potrzebuje algorytm.

**Pułapka:** Sprawdzenie typu nie kontroluje wszystkich wartości. Square dla dużego int może przepełnić typ, mimo spełnionego conceptu. Dla typu bool integral również jest prawdziwe, co może zaskoczyć projektanta. Jeżeli potrzebujesz wyłącznie możliwości mnożenia i odpowiedniego wyniku, zapisz structural requirement zamiast kategorii arytmetycznej.

**Dalej:** [Constraints i subsumption](zaawansowane/08_concepts_normalization_i_subsumption.md)

### 32. Requires expressions

Requires expression sprawdza, czy typ wspiera konkretne operacje, ich wynik i właściwości `noexcept`.

```cpp
#include <concepts>
#include <cstddef>
#include <vector>

template<class T>
concept Reservable = requires(T container, std::size_t size) {
    { container.reserve(size) } -> std::same_as<void>;
    { container.capacity() } -> std::convertible_to<std::size_t>;
};

static_assert(Reservable<std::vector<int>>);
```

**Zastosowanie:** structural interfaces bez wymagania dziedziczenia po wspólnej klasie.

**Dlaczego i jak:** Parametry requires-expression służą do opisu hipotetycznych wyrażeń; nie tworzą kontenera ani nie wywołują reserve w runtime. Pierwsze wymaganie bada dokładny wynik void, a drugie dopuszcza konwersję capacity do size_t. Typ może spełnić taki interfejs bez dziedziczenia po wspólnej bazie. Kompilator uzyskuje czytelniejszy warunek przy przeciążeniu, zamiast dowiadywać się o braku metody dopiero wewnątrz ciała.

**Pułapka:** Sama obecność metod nie gwarantuje ich semantyki. Niestandardowy reserve może niczego nie rezerwować albo mieć odmienny kontrakt invalidacji. Wymaganie na const obiekcie różni się od wymagania na obiekcie modyfikowalnym. Dodatkowe noexcept należy sprawdzać tylko wtedy, gdy algorytm rzeczywiście potrzebuje braku wyjątków, a nie dla pozornej surowości interfejsu.

**Dalej:** [Constraints i subsumption](zaawansowane/08_concepts_normalization_i_subsumption.md)

### 33. Constraint subsumption

Jeśli jeden concept logicznie zawiera drugi przez wspólne atomic constraints, bardziej ograniczone przeciążenie jest preferowane.

```cpp
#include <concepts>

template<class T>
concept Number = std::integral<T> || std::floating_point<T>;

template<class T>
concept SignedNumber = Number<T> && std::signed_integral<T>;

constexpr int rank(Number auto) { return 1; }
constexpr int rank(SignedNumber auto) { return 2; }

static_assert(rank(42) == 2);
static_assert(rank(42.0) == 1);
```

**Zastosowanie:** hierarchie generycznych przeciążeń bez ręcznego sterowania priorytetem.

**Dlaczego i jak:** SignedNumber ponownie używa Number, więc normalizacja zachowuje wspólne atomic constraints. Dla int oba przeciążenia pasują, a drugie jest bardziej ograniczone i zwraca dwa. Double spełnia Number, lecz nie signed_integral, dlatego wybiera pierwszą wersję. Mechanizm porządkuje zestaw pasujących funkcji; nie jest ogólnym solverem dowodzącym dowolnych zależności matematycznych pomiędzy predykatami.

**Pułapka:** Powtórzenie identycznie wyglądającego wyrażenia w oddzielnej definicji może utworzyć inny atom i wywołać niejednoznaczność. Nazwa SignedNumber nie obejmuje tutaj liczb zmiennoprzecinkowych, choć mogą być ujemne. Dla przewidywalnej hierarchii buduj węższe concepts przez ponowne użycie publicznych concepts bazowych i testuj wybór przeciążeń.

**Dalej:** [Constraints i subsumption](zaawansowane/08_concepts_normalization_i_subsumption.md)

### 34. Abbreviated function templates

`auto` lub concept w parametrze funkcji tworzy ukryty parametr template.

```cpp
#include <array>
#include <ranges>

constexpr auto first(const std::ranges::forward_range auto& range) {
    return *std::ranges::begin(range);
}

static_assert(first(std::array{4, 5, 6}) == 4);
```

**Zastosowanie:** krótsze API generyczne bez utraty constraintów.

**Dlaczego i jak:** Skrócony zapis z conceptem tworzy ukryty parametr szablonu i ogranicza go do odpowiedniego zakresu. Osobne auto w dwóch parametrach zasadniczo oznaczają osobne dedukowane typy, a nie wymaganie ich identyczności. Funkcja first zwraca auto, więc otrzymany element jest kopiowany do wartości wyniku, zamiast automatycznie zwracać referencję. To wybór ownership, który może być korzystny dla bezpieczeństwa tymczasowych źródeł.

**Pułapka:** Forward range może być pusty, a dereferencja begin wymaga niepustości. Dodatkowo const zakres powinien sam spełniać wymagania używane w ciele; nie każdy view ma const begin. Jeśli potrzebujesz obsługi takich widoków, dopasuj parametr i constraint do rzeczywistego wyrażenia, zamiast zakładać, że const nie wpływa na iterację.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)

### 35. `if constexpr`

Niewybrana gałąź nie jest instancjonowana, więc może zawierać kod niepoprawny dla pozostałych typów.

```cpp
#include <string>
#include <type_traits>

template<class T>
std::string stringify(const T& value) {
    if constexpr (std::is_same_v<T, std::string>) {
        return value;
    } else {
        return std::to_string(value);
    }
}
```

**Zastosowanie:** statyczny dispatch i ograniczenie liczby specjalizacji.

**Dlaczego i jak:** Kompilator ocenia warunek zależny od T podczas instancjacji i odrzuca niewybraną gałąź. Dla stringa nie próbuje instancjować wywołania to_string(string), które nie istnieje; dla liczby wybiera konwersję liczbową. Nadal analizuje składnię definicji i nazwy niezależne od T. Mechanizm eliminuje niepotrzebną część implementacji, ale nie jest odpowiednikiem preprocesora ukrywającego dowolne tokeny.

**Pułapka:** Typ niebędący stringiem ani obsługiwaną liczbą trafi do wybranej gałęzi i spowoduje twardy błąd ciała. Jeśli API ma odrzucać taki typ podczas wyboru przeciążeń, dodaj constraint. Poza kontekstem szablonu if constexpr nie służy do maskowania dowolnego niepoprawnego kodu w niewykonywanej gałęzi.

**Dalej:** [Lookup i SFINAE](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)

### 36. Natychmiastowe funkcje `consteval`

Każde potencjalnie ewaluowane wywołanie `consteval` musi zostać wykonane podczas kompilacji.

```cpp
#include <cstdint>

consteval std::uint32_t hash(const char* text) {
    std::uint32_t value = 2166136261u;
    while (*text) value = (value ^ static_cast<unsigned char>(*text++)) * 16777619u;
    return value;
}

constexpr auto message_id = hash("acquisition.started");
```

**Zastosowanie:** identyfikatory, walidacja i generowanie wartości, które nie mogą przejść do runtime.

**Dlaczego i jak:** Natychmiastowa funkcja przetwarza literał podczas wymaganej stałej ewaluacji i zwraca gotowy identyfikator. Każdy odczyt znaku dotyczy znanej tablicy zakończonej zerem, a arytmetyka unsigned ma zdefiniowane zawijanie. Klient nie może zwyczajnie przekazać bufora wypełnionego dopiero w runtime. Użycie consteval koduje tę granicę faz języka w interfejsie, zamiast polegać na optymalizatorze.

**Pułapka:** Skończona liczba bitów daje możliwość kolizji, niezależnie od czasu obliczenia. Funkcja wymaga poprawnego, zakończonego zerem tekstu i nie przyjmuje bezpiecznie null. Jeżeli identyfikatory mają znaczenie trwałe, ustal kodowanie i stabilność algorytmu; nie traktuj prostego hasha jako funkcji kryptograficznej ani gwarancji unikalności.

**Dalej:** [Stała ewaluacja](zaawansowane/09_constexpr_consteval_i_compile_time.md)

### 37. Rozgałęzienie `if consteval` — C++23

Kod może wykonać inną implementację podczas constant evaluation i inną w runtime.

```cpp
#include <cmath>
#include <stdexcept>

// Demonstracja dla value == 0 lub 1 <= value <= 16.
constexpr double square_root(double value) {
    if (!(value == 0.0 || (value >= 1.0 && value <= 16.0)))
        throw std::domain_error("outside demonstration domain");
    if (value == 0.0) return 0.0;
    if consteval {
        double guess = value;
        for (int i = 0; i < 20; ++i) guess = (guess + value / guess) / 2.0;
        return guess;
    } else {
        return std::sqrt(value);
    }
}

static_assert(square_root(0.0) == 0.0);
static_assert(square_root(16.0) > 3.99 && square_root(16.0) < 4.01);
```

**Zastosowanie:** compile-time fallback dla algorytmu wykorzystującego zoptymalizowaną funkcję runtime.

**Dlaczego i jak:** Gałąź consteval może używać implementacji złożonej z operacji dostępnych przy stałej ewaluacji, a ścieżka runtime deleguje do bibliotecznego sqrt. Metoda Newtona iteracyjnie poprawia przybliżenie, lecz potrzebuje sensownego punktu startowego i kryterium zakończenia. Pokazany ograniczony przykład jawnie obsługuje zero oraz odrzuca wartości spoza małej, określonej domeny, aby nie udawać pełnego odpowiednika standardowej funkcji numerycznej.

**Pułapka:** Stała liczba iteracji nie daje jednakowej dokładności dla całego zakresu double. Pierwotne guess równe zero powodowałoby dzielenie zero przez zero. Zbieżność, NaN, nieskończoności i liczby ujemne wymagają osobnego kontraktu. Testowanie jedynie dolnej granicy 3.99 nie wystarcza; sprawdzaj także górną granicę wyniku.

**Dalej:** [Stała ewaluacja](zaawansowane/09_constexpr_consteval_i_compile_time.md)

### 38. Bezpieczna inicjalizacja statyczna przez `constinit`

`constinit` wymusza static initialization, ale nie czyni zmiennej stałą.

```cpp
constinit thread_local unsigned request_counter = 0;

void on_request() {
    ++request_counter;
}
```

**Zastosowanie:** unikanie problemu kolejności dynamicznej inicjalizacji i ukrytych guardów runtime.

**Dlaczego i jak:** Constinit wymaga inicjalizacji statycznej obiektu o odpowiednim storage duration, więc wykrywa przypadkowe wprowadzenie dynamicznego inicjalizatora. Thread_local daje oddzielny licznik dla każdego wątku; zwiększenie jednej kopii nie konkuruje ze zwiększeniem kopii innego wątku. Zmienna pozostaje modyfikowalna, ponieważ constinit nie dodaje const. Ma to inne znaczenie niż constexpr, które wymaga stałego inicjalizatora i niezmienności obiektu.

**Pułapka:** Oddzielne kopie nie tworzą automatycznie globalnej sumy żądań. Odczyt liczników z innych wątków wymaga dodatkowego modelu lifetime i synchronizacji. Constinit rozwiązuje inicjalizację, ale nie wszystkie zależności destrukcji obiektów statycznych. Zawijanie unsigned jest zdefiniowane, lecz aplikacja musi ustalić, czy utrata zliczonych żądań jest dopuszczalna.

**Dalej:** [Stała ewaluacja](zaawansowane/09_constexpr_consteval_i_compile_time.md)

### 39. Dynamiczna alokacja w `constexpr`

C++20 pozwala używać `new` i wielu kontenerów w constant evaluation, jeśli pamięć zostanie zwolniona przed jej końcem.

```cpp
#include <vector>

consteval int compile_time_sum() {
    std::vector<int> values{1, 2, 3, 4};
    int sum{};
    for (int value : values) sum += value;
    return sum;
}

static_assert(compile_time_sum() == 10);
```

**Zastosowanie:** bardziej naturalne metaprogramy operujące na dynamicznych strukturach tymczasowych.

**Dlaczego i jak:** Wektor istnieje jako obiekt przejściowy w wykonywanym przez kompilator obliczeniu. Jego przydziały są zwalniane przy wyjściu z funkcji, a na zewnątrz trafia tylko zwykła liczba. Dzięki temu rezultat nie zawiera wskaźnika do pamięci używanej przez evaluator. Taki warsztat pozwala pisać algorytmy bardziej podobne do zwykłego C++, zamiast reprezentować każdą operację przez rekurencję typów.

**Pułapka:** Nie wolno wnioskować, że dowolny dynamiczny vector może zostać zachowany jako trwała zmienna constexpr. Pamięć nie może wyciec poza dozwoloną ewaluację. Duże obliczenia zużywają czas i pamięć kompilatora oraz mogą przekroczyć jego limity. Compile-time nie oznacza zerowego kosztu dla całego procesu budowania.

**Dalej:** [Stała ewaluacja](zaawansowane/09_constexpr_consteval_i_compile_time.md)

### 40. Type traits i transformacje typów

`<type_traits>` pozwala pytać o właściwości typu i tworzyć nowy typ na podstawie starego.

```cpp
#include <memory>
#include <type_traits>

template<class T>
using Value = std::remove_cvref_t<T>;

static_assert(std::is_same_v<Value<const int&>, int>);
static_assert(std::is_trivially_copyable_v<int>);
static_assert(!std::is_copy_constructible_v<std::unique_ptr<int>>);
```

**Zastosowanie:** metaprogramowanie, serializacja i dobór zoptymalizowanej ścieżki.

**Dlaczego i jak:** Remove_cvref usuwa referencję oraz najwyższe kwalifikatory cv, tworząc typ nadający się często do przechowywania własnej wartości. Nie wykonuje przy tym konstrukcji ani kopiowania obiektu. Traits udostępniają informacje wymagane przy wyborze ścieżki implementacji; na przykład brak kopiowalności unique pointera wynika z jego modelu własności. Wyniki są stałymi, więc można ich używać w static_assert, constraints i if constexpr.

**Pułapka:** Nie każdy trait wolno bezwarunkowo stosować do niekompletnego typu; sprawdzaj jego wymagania. Trivially copyable nie oznacza przenośnej serializacji, a move constructible nie dowodzi braku kopii. Remove_cvref różni się od decay: nie zamienia automatycznie tablic i funkcji na wskaźniki. Wybierz transformację odpowiadającą kontraktowi przechowywania.

**Dalej:** [Lookup i SFINAE](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)

### 41. SFINAE przez `std::enable_if`

Błąd podstawienia w bezpośrednim kontekście usuwa kandydata z overload set zamiast przerywać kompilację.

```cpp
#include <type_traits>

template<class T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
constexpr T twice(T value) {
    return value * 2;
}

static_assert(twice(21) == 42);
```

**Zastosowanie:** starsze API i biblioteki wspierające standard sprzed concepts.

**Dlaczego i jak:** Enable_if_t udostępnia żądany typ tylko wtedy, gdy predykat jest prawdziwy. Dla typu całkowitego powstaje dodatkowy parametr szablonu typu int z wartością domyślną, więc funkcja jest kandydatem. Dla innego typu podstawienie nie tworzy poprawnej deklaracji w bezpośrednim kontekście i kandydat zostaje usunięty. Mechanizm poprzedza instancjację ciała oraz może współpracować z innym przeciążeniem ogólnym.

**Pułapka:** Błąd mnożenia wewnątrz wybranej funkcji nie staje się SFINAE. Nie myl też różniących się argumentów domyślnych z osobnymi sygnaturami szablonów; niektóre popularne warianty enable_if przypadkowo redeklarują tę samą funkcję. W nowym kodzie requires zwykle lepiej pokazuje kontrakt i ułatwia diagnostykę.

**Dalej:** [Lookup i SFINAE](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)

### 42. Detection idiom przez `std::void_t`

Specjalizacja jest wybierana tylko wtedy, gdy badane wyrażenie tworzy poprawny typ.

```cpp
#include <type_traits>
#include <utility>
#include <vector>

template<class, class = void>
struct has_size : std::false_type {};

template<class T>
struct has_size<T, std::void_t<decltype(std::declval<const T&>().size())>>
    : std::true_type {};

static_assert(has_size<std::vector<int>>::value);
static_assert(!has_size<int>::value);
```

**Zastosowanie:** kompatybilne wstecz wykrywanie capabilities typu.

**Dlaczego i jak:** Szablon podstawowy odpowiada false. Podczas dopasowania częściowej specjalizacji kompilator próbuje utworzyć typ wyniku wyrażenia size na const obiekcie. Jeżeli się uda, void_t zamienia dowolny taki poprawny typ na void, zgodny z drugim parametrem szablonu. Declval pozwala opisać hipotetyczną referencję bez wymogu konstrukcji rzeczywistego T. Dla int wyrażenie jest niepoprawne, więc pozostaje szablon podstawowy.

**Pułapka:** Wykrycie metody nie sprawdza jej złożoności ani zgodności znaczenia z oczekiwaną liczbą elementów. Metoda dostępna wyłącznie na obiekcie nieconst zostanie tutaj odrzucona. Declval nie jest funkcją do wywołania runtime. Błędy powstałe głębiej w innych instancjowanych definicjach nadal mogą wykraczać poza ochronę immediate context.

**Dalej:** [Lookup i SFINAE](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)

### 43. CRTP — statyczny polimorfizm

Klasa bazowa zna konkretny typ pochodny jako parametr template i deleguje bez vtable.

```cpp
template<class Derived>
struct Logger {
    void log() const {
        static_cast<const Derived&>(*this).write();
    }
};

struct ConsoleLogger : Logger<ConsoleLogger> {
    void write() const {}
};

void example() {
    ConsoleLogger logger;
    logger.log();
}
```

**Zastosowanie:** policies, expression templates i compile-time mixins.

**Dlaczego i jak:** Podstawienie ConsoleLogger do Logger tworzy bazę znającą konkretny typ odbiorcy. Rzutowanie jest poprawne, ponieważ używany podobiekt Logger rzeczywiście należy do ConsoleLogger, a write jest dostępne. Kompilator może rozwiązać wywołanie statycznie i włączyć jego ciało. Nie powstaje wspólny dynamiczny typ umożliwiający dowolne przechowywanie wszystkich Logger<T> w jednej kolekcji bez dodatkowej abstrakcji.

**Pułapka:** Samodzielny obiekt Logger<ConsoleLogger> nie jest pełnym ConsoleLogger; wywołanie log na nim naruszałoby założenie downcastu. Wzorzec można ograniczyć dostępnością konstrukcji bazy. CRTP nie dodaje automatycznie wirtualnego destructora i nie uprawnia do usuwania obiektu pochodnego przez niewirtualną bazę. Wywołania podczas konstrukcji wymagają uwagi na niegotowy stan pochodny.

**Dalej:** [Type erasure i ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

### 44. Hidden friends i Argument-Dependent Lookup

Funkcja zdefiniowana jako friend wewnątrz klasy jest znajdowana przez ADL tylko dla argumentów powiązanego typu.

```cpp
#include <compare>

struct StrongId {
    unsigned value;

    friend constexpr bool operator==(StrongId, StrongId) = default;
    friend constexpr auto operator<=>(StrongId, StrongId) = default;
};

static_assert(StrongId{1} < StrongId{2});
```

**Zastosowanie:** symetryczne operatory i ograniczanie zanieczyszczenia namespace.

**Dlaczego i jak:** Funkcje friend zdefiniowane w StrongId są nieskładowymi operatorami powiązanymi z klasą. ADL odnajduje je dzięki typom operandów, a domyślne definicje porównują odpowiednie składowe. Rewritten candidates operatorów porównania pozwalają użyć zapisu mniejsze-niż na podstawie dostępnego porównania trójkierunkowego. Funkcje pozostają blisko reprezentacji typu i nie wymagają dodawania publicznych metod ujawniających pola.

**Pułapka:** Hidden friend nie zostanie zwyczajnie odnaleziony dla dwóch obcych argumentów tylko dlatego, że mogłyby konwertować się do StrongId. Dodanie nowego pola może zmienić domyślną semantykę porównania. Jeżeli identyczność domenowa zależy jedynie od części reprezentacji, defaulted comparison niekoniecznie odpowiada właściwemu kontraktowi.

**Dalej:** [Overload resolution i ADL](zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)

### 45. Explicit object parameter — C++23

„Deducing this” pozwala modelować odbiorcę metody jako jawny parametr i zachować jego kategorię wartości. Wymaga odpowiednio nowego kompilatora.

```cpp
#include <utility>
#include <type_traits>

struct Buffer {
    int value{};

    template<class Self>
    decltype(auto) get(this Self&& self) {
        return (std::forward<Self>(self).value);
    }
};

static_assert(std::is_same_v<decltype(std::declval<Buffer&>().get()), int&>);
static_assert(std::is_same_v<decltype(std::declval<const Buffer&>().get()), const int&>);
static_assert(std::is_same_v<decltype(std::declval<Buffer&&>().get()), int&&>);
```

**Zastosowanie:** eliminowanie duplikacji przeciążeń `const`, `&` i `&&` oraz nowoczesny CRTP bez rzutowania.

**Dlaczego i jak:** Jawny parametr obiektu pozwala dedukować const i kategorię odbiorcy tak jak przy zwykłym forwarding reference. Zapis `forward<Self>(self)` odtwarza właściwy sposób dostępu do pola. Aby decltype(auto) zachowało referencję do tego pola, wyrażenie return musi być ujęte w nawiasy. Bez nich działa szczególna reguła dla dostępu do składowej i wynik ma deklarowany typ pola, czyli int przez wartość.

**Pułapka:** Referencja zwrócona z tymczasowego Buffer może wisieć po końcu pełnego wyrażenia. Jedna metoda obsługująca wszystkie kategorie nie eliminuje potrzeby różnych kontraktów własności. Często dla odbiorcy rvalue lepiej zwrócić wartość. Funkcja z explicit object parameter ma też ograniczenia składni i nie jest zwykłą metodą z ukrytym this.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

---

## Type erasure, ranges i coroutines — 46–65

### 46. Move-only type erasure przez `std::move_only_function` — C++23

Wrapper przechowuje dowolny callable o zadanej sygnaturze, również taki, którego nie można kopiować.

> **C++23; poza lokalną weryfikacją Apple Clang 17/libc++.** Wymagana implementacja `std::move_only_function` w `<functional>`; lokalna biblioteka jej nie udostępnia.

```cpp,notest
#include <functional>
#include <memory>

std::move_only_function<int()> task = [value = std::make_unique<int>(42)] {
    return *value;
};

int result = task();
```

**Zastosowanie:** kolejki zadań posiadających move-only stan i callbacki bez wymogu kopiowania.

**Dlaczego i jak:** Callable zawiera unique pointer, więc nie można go skopiować, ale można przekazać jego własność do wrappera. Move-only function wymazuje konkretny typ lambdy, zachowując wymaganie przenoszenia zamiast kopiowania. Sygnatura może dodatkowo kodować odpowiednie kwalifikatory wywołania oraz noexcept, co pozwala lepiej dopasować kontrakt odbiorcy. Po uruchomieniu zadania wynik pochodzi z obiektu utrzymywanego przez sam callable.

**Pułapka:** Wywołanie pustego move_only_function narusza warunek wstępny; nie należy oczekiwać tego samego bad_function_call co dla std::function. Przeniesione źródło trzeba traktować zgodnie z jego stanem. Lokalna biblioteka nie implementuje tego elementu C++23, dlatego przykład wymaga osobnej walidacji na toolchainie z odpowiednim wsparciem.

**Dalej:** [Type erasure i ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

### 47. Algorytmy `std::ranges`

Algorytmy przyjmują cały range, zwracają bogatsze typy wyników i współpracują z projections.

```cpp
#include <algorithm>
#include <array>
#include <ranges>

std::array values{4, 1, 3, 2};

bool sort_and_find() {
    std::ranges::sort(values);
    auto found = std::ranges::find(values, 3);
    return found != values.end();
}
```

**Zastosowanie:** krótszy i bezpieczniejszy kod algorytmiczny bez ręcznych par iteratorów.

**Dlaczego i jak:** Sort przyjmuje cały zakres, wyznaczając begin i end według bibliotecznego protokołu dostępu. Constraints odrzucają zakres bez wymaganych iteratorów random access lub możliwości sortowania. Find może przyjąć słabszą kategorię iteratora i zwraca wynik powiązany z lifetime przekazanego zakresu. Tutaj array jest trwałym obiektem, więc zwrócony iterator można porównać z jej end i użyć przed kolejną zmianą reprezentacji.

**Pułapka:** Ranges nie czynią każdego algorytmu leniwym; sort wykonuje pracę i modyfikuje wejście od razu. Komparator nadal musi spełniać prawa semantyczne strict weak ordering. Przekazanie tymczasowego posiadającego kontenera do algorytmu zwracającego iterator może dać typ dangling, ale ta ochrona nie wykrywa wszystkich wiszących widoków.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)

### 48. Kompozycja views operatorem `|`

View adaptors tworzą leniwy pipeline bez materializowania kolekcji pośrednich.

```cpp
#include <ranges>
#include <vector>

void consume_pipeline() {
    std::vector values{1, 2, 3, 4, 5, 6};
    auto pipeline = values
        | std::views::filter([](int value) { return value % 2 == 0; })
        | std::views::transform([](int value) { return value * value; });

    for (int value : pipeline) { (void)value; }
}
```

**Zastosowanie:** strumieniowa transformacja dużych zbiorów z minimalną liczbą alokacji.

**Dlaczego i jak:** Pipeline przechowuje adapter filtrowania i przekształcenia oraz widok na vector. Przy iteracji filter wyszukuje następny parzysty element, a transform oblicza jego kwadrat podczas dostępu do wartości. Nie powstają dwa pośrednie vectory. Kolejność adapterów ma znaczenie: najpierw filtrowanie oszczędza obliczeń transformacji dla odrzuconych elementów, o ile semantyka obu funkcji pozostaje zgodna z kontraktem.

**Pułapka:** Widok nad lvalue vectorem zwykle pożycza źródło, więc nie wolno zwracać go z funkcji wraz ze znikającym lokalnym vectorem. Kolejne przejście może ponownie wykonywać transformację. Zapis do źródła lub realokacja mogą unieważnić iteratory albo założenia filtracji. Leniwość nie jest memoizacją wyników.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)

### 49. Leniwość `filter_view` i `transform_view`

Pipeline przechowuje funkcje i źródło; element jest filtrowany i przekształcany dopiero podczas iteracji.

```cpp
#include <ranges>

int count_consumed() {
    int consumed{};
    auto values = std::views::iota(0, 100)
        | std::views::filter([](int value) { return value % 10 == 0; })
        | std::views::take(3);

    for (int value : values) { (void)value; ++consumed; }
    return consumed; // 3; nie zakładamy dokładnej liczby wywołań predykatu.
}
```

**Zastosowanie:** praca ze źródłami potencjalnie nieskończonymi lub kosztownymi.

**Dlaczego i jak:** Utworzenie adapterów nie przetwarza od razu stu liczb. Dopiero żądanie begin i kolejne zwiększenia iteratora wyszukują elementy spełniające predykat. Take ogranicza liczbę oddanych elementów, ale iterator bazowy może zostać przesunięty dalej przy sprawdzaniu końca. Nie należy zatem wyprowadzać dokładnej liczby wywołań predykatu tylko z liczby widocznych rezultatów. Forward filter może także buforować początek, co wpływa na powtórne przejścia.

**Pułapka:** Predykaty ranges mają wymagania semantyczne dotyczące regularności wywołań. Instrumentacja zmieniająca zewnętrzny licznik w predykacie nie jest dobrym wzorcem przenośnego predykatu; przykład poprawiono na pomiar liczby skonsumowanych wyników przy czystym warunku filtracji. Nie opieraj poprawności programu na dokładnej liczbie ewaluacji leniwego adaptera.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)

### 50. `iota`, `take` i `drop`

Adaptery tworzą i wycinają sekwencje bez osobnego kontenera.

```cpp
#include <ranges>
#include <vector>

std::vector<int> make_page() {
    auto page = std::views::iota(0)
        | std::views::drop(20)
        | std::views::take(10);

    std::vector<int> materialized;
    for (int value : page) materialized.push_back(value);
    return materialized;
}
```

**Zastosowanie:** paginacja, indeksy i generowanie kontrolowanych fragmentów sekwencji.

**Dlaczego i jak:** Nieograniczone iota reprezentuje generowaną sekwencję wartości, bez alokowania nieskończonej tablicy. Drop pomija początek, a take ogranicza widoczny fragment do dziesięciu kolejnych elementów. Dopiero pętla push_back materializuje wybrane wartości w posiadającym vectorze. Dla random-access iota pominięcie początku może być tanie, podczas gdy dla źródła jednoprzejściowego wymaga rzeczywistego odczytania i odrzucenia elementów.

**Pułapka:** Nieograniczoność logiczna nie powiększa zakresu typu int; dostatecznie długie zwiększanie może osiągnąć jego granicę. Nie uruchamiaj pełnego algorytmu wymagającego końca na nieograniczonym źródle. Kolejność take i drop zmienia wynik paginacji, a ujemne lub nadmierne liczności wejściowe wymagają sprawdzenia kontraktów adapterów.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)

### 51. `split_view` i spłaszczanie zakresów

`views::split` zwraca range podzakresów bez kopiowania źródła. Fragmenty można przetworzyć jako osobne tokeny.

```cpp
#include <ranges>
#include <string_view>

void parse() {
    std::string_view text = "alpha,beta,gamma";
    for (auto token : text | std::views::split(',')) {
        std::string_view view{token.begin(), token.end()};
        (void)view;
    }
}
```

**Zastosowanie:** parsery zero-copy, tokenizacja i dzielenie ramek tekstowych.

**Dlaczego i jak:** Każdy element wyniku split jest podzakresem pomiędzy kolejnymi wystąpieniami separatora. Iterator zewnętrzny wyszukuje granice tokenu, a iterator wewnętrzny nadal wskazuje znaki źródła. Dla ciągłego źródła pokazanego w przykładzie można z tych granic utworzyć string_view bez alokacji. Adapter join służy do odwrotnego kroku strukturalnego: przechodzi po elementach kolejnych podzakresów, nie odtwarzając automatycznie usuniętych separatorów. Parsowanie może więc pozostawać leniwe, dopóki nie potrzebujesz niezależnego wyniku tekstowego.

**Pułapka:** Zachowanie tokenów po zniszczeniu źródłowego stringa tworzy wiszące widoki. Kolejne separatory mogą tworzyć puste fragmenty, więc parser musi określić ich znaczenie. Nie zakładaj, że split jednocześnie usuwa białe znaki albo rozpoznaje cytowanie CSV.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md); [Widoki i dangling](03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)

### 52. Własny view przez `std::ranges::view_interface`

`view_interface` dostarcza domyślne operacje, jeżeli typ pochodny udostępnia `begin` i `end`.

```cpp
#include <ranges>

class Integers : public std::ranges::view_interface<Integers> {
    int first_{};
    int last_{};
public:
    Integers() = default;
    Integers(int first, int last) : first_(first), last_(last) {}

    auto begin() const { return std::views::iota(first_, last_).begin(); }
    auto end() const { return std::views::iota(first_, last_).end(); }
};

static_assert(std::ranges::view<Integers>);
```

**Zastosowanie:** domenowe źródła danych zgodne z całym ekosystemem ranges.

**Dlaczego i jak:** view_interface stosuje CRTP: zna typ pochodny i buduje część interfejsu na jego begin oraz end. Dostępność metod takich jak empty, front czy indeksowanie zależy od kategorii i dodatkowych własności zakresu; samo dziedziczenie nie zapewnia ich wszystkich. W Integers iteratory iota przechowują własne wartości, dlatego nie potrzebują życia tymczasowego obiektu iota_view z funkcji begin. Taki widok opisuje sekwencję obliczaną, a nie bufor przechowywany wewnątrz klasy.

**Pułapka:** Koncept view nie dowodzi poprawnej semantyki iteratorów. Odwrócone granice tego przykładu mogą prowadzić do przejścia poza zakres liczb zamiast normalnego zakończenia. Konstruktor powinien wymagać first <= last albo jawnie odrzucać niewłaściwy przedział.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)

### 53. Iterator i sentinel o różnych typach

Koniec range nie musi być iteratorem tego samego typu. Sentinel może przechowywać tylko warunek zakończenia.

```cpp
#include <cstddef>
#include <ranges>

struct NullSentinel {};

constexpr bool operator==(const char* iterator, NullSentinel) {
    return *iterator == '\0';
}

struct CStrRange {
    const char* text;
    const char* begin() const { return text; }
    NullSentinel end() const { return {}; }
};

static_assert(std::ranges::range<CStrRange>);
```

**Zastosowanie:** strumienie, C strings i zakresy kończące się zdarzeniem zamiast znanej pozycji.

**Dlaczego i jak:** Algorytmy ranges rozdzielają operację przesunięcia iteratora od sprawdzenia końca. Sentinel nie musi umożliwiać dereferencji ani inkrementacji; wystarcza odpowiednia relacja porównania z iteratorem. W przykładzie porównanie odczytuje bieżący znak i kończy zakres na zerze. Nie oblicza wcześniej długości przez strlen, dzięki czemu można przejść po napisie jednokrotnie. Sentinel o innym typie jest szczególnie przydatny, gdy zakończenie określa stan źródła, a nie wcześniej znany adres ostatniego elementu.

**Pułapka:** Ten sentinel dereferencjonuje iterator już podczas porównania. Źródło musi więc być niepuste w sensie ważnego adresu i zawierać osiągalny terminator. Pusty wskaźnik lub bufor bez zera może spowodować UB, choć typ spełnia wymagania składniowe range.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)

### 54. `borrowed_range` i ochrona przed dangling

Algorytm ranges zwraca `std::ranges::dangling`, gdy iterator do tymczasowego, niepożyczalnego range byłby niebezpieczny.

```cpp
#include <algorithm>
#include <ranges>
#include <type_traits>
#include <vector>

using Result = decltype(std::ranges::find(std::vector{1, 2, 3}, 2));
static_assert(std::is_same_v<Result, std::ranges::dangling>);

using ViewResult = decltype(std::ranges::find(std::views::iota(0, 4), 2));
static_assert(!std::is_same_v<ViewResult, std::ranges::dangling>);
```

**Zastosowanie:** statyczne wykrywanie iteratorów, które przeżyłyby swoje źródło.

**Dlaczego i jak:** borrowed_range opisuje zależność iteratorów od życia samego obiektu zakresu. Iterator iota przechowuje licznik, dlatego może przetrwać zniszczenie tymczasowego widoku. Iterator wektora odnosi się do posiadanych elementów, które znikają z tymczasowym wektorem. Niektóre algorytmy ranges używają borrowed_iterator_t, zwracając wtedy dangling zamiast niebezpiecznego iteratora. Dla lvalue wektora wynik pozostaje zwykłym iteratorem, ponieważ wywołanie nie niszczy tego zewnętrznego właściciela. Nadal trzeba przestrzegać późniejszych reguł invalidacji kontenera.

**Pułapka:** borrowed_range nie gwarantuje życia zewnętrznych danych. string_view jest pożyczalny, ale może wskazywać już zniszczony string. Algorytm może zwrócić normalny iterator do takiego widoku i nie wykryje pierwotnego błędu własności; ochrona dotyczy konkretnej granicy życia.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md); [Widoki i dangling](03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)

### 55. Projections w algorytmach ranges

Projection wskazuje pole lub transformację używaną do porównania bez tworzenia osobnego iteratora.

```cpp
#include <algorithm>
#include <functional>
#include <string>
#include <vector>

struct User { int id; std::string name; };

void sort_users(std::vector<User>& users) {
    std::ranges::sort(users, std::less{}, &User::name);
}
```

**Zastosowanie:** sortowanie i wyszukiwanie struktur według pola bez pomocniczych lambd.

**Dlaczego i jak:** Projection jest wywoływana na elemencie przed komparatorem. W sortowaniu użytkowników komparator porównuje wyniki dostępu do name, a algorytm nadal przestawia całe obiekty User. Wskaźnik do pola działa dzięki regułom invoke, więc nie trzeba ręcznie rozpakowywać obiektu. Projekcje mogą też obliczać klucz, lecz algorytm może wywoływać je wielokrotnie. Jeżeli klucz jest kosztowny, warto wcześniej zapisać go w pomocniczej strukturze zamiast oczekiwać automatycznego buforowania każdej transformacji.

**Pułapka:** Komparator nadal musi wyznaczać wymagany ścisły słaby porządek. Projekcja zmieniająca stan lub dająca inne klucze przy kolejnych wywołaniach może złamać to wymaganie. Dodaj bezpośredni nagłówek functional dla std::less, zamiast polegać na pośrednich include biblioteki.

**Dalej:** [Algorytmy i lambdy](06_biblioteka_standardowa/05_algorytmy_i_lambdy.md)

### 56. Materializacja przez `std::ranges::to` — C++23

`ranges::to<Container>` kończy pipeline i konstruuje wskazany kontener. Wsparcie zależy od wersji biblioteki standardowej.

```cpp
#include <ranges>
#include <string>
#include <vector>

auto names = std::views::iota(1, 5)
    | std::views::transform([](int id) { return std::to_string(id); })
    | std::ranges::to<std::vector>();
```

**Zastosowanie:** zwięzłe przejście od leniwego view do posiadającej kolekcji.

**Dlaczego i jak:** Materializacja przechodzi po źródle i tworzy elementy docelowego kontenera. W przykładzie transform generuje napisy dopiero wtedy, gdy ranges::to ich potrzebuje. Wynikowy vector posiada własne obiekty string i może przeżyć pipeline. Wybór sposobu konstrukcji zależy od dostępnych konstruktorów kontenera i rodzaju zakresu, a rozmiar źródła może pomóc zarezerwować miejsce. Wywołanie nie oznacza automatycznie przenoszenia wszystkich wartości: kategorię przekazywanych elementów określa źródło i użyte adaptery.

**Pułapka:** Kontener widoków nadal może pożyczać znaki: vector<string_view> nie staje się właścicielem tekstu przez samą materializację. Dla nieskończonego iota bez ograniczenia operacja nie dojdzie do końca, a dla input_range zużyje jednorazowe źródło danych.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)

### 57. `zip`, `chunk` i `slide` views — C++23

Nowe adaptery łączą sekwencje, grupują je w porcje i tworzą przesuwne okna. Dostępność zależy od implementacji C++23.

> **C++23; poza lokalną weryfikacją Apple Clang 17/libc++.** Cały przykład wymaga `views::zip`, `views::chunk` i `views::slide`. Lokalny przebieg wykazał brak `views::slide`, mimo dostępności pozostałych użytych adapterów.

```cpp,notest
#include <array>
#include <ranges>

double weighted_samples() {
    std::array samples{1.0, 2.0, 3.0, 4.0};
    std::array weights{0.1, 0.2, 0.3, 0.4};

    double weighted{};
    for (auto [sample, weight] : std::views::zip(samples, weights)) {
        weighted += sample * weight;
    }

    auto windows = samples | std::views::slide(2);
    (void)windows;
    return weighted;
}
```

**Zastosowanie:** DSP, batch processing, synchronizowanie kanałów i sliding windows.

**Dlaczego i jak:** zip przechodzi po kilku zakresach równocześnie i kończy się wraz z najkrótszym z nich. Dereferencja udostępnia elementy odpowiadających pozycji, często jako krotkę referencji, dlatego zapis przez poprawnie odebrane referencje może zmieniać źródła. chunk tworzy kolejne niepokrywające się porcje, z możliwą krótszą porcją końcową. slide tworzy zachodzące na siebie okna zadanej długości. Te adaptery opisują strukturę dostępu; nie kopiują automatycznie wszystkich próbek do nowych tablic.

**Pułapka:** zip może ukryć niezgodne długości, bo nie zgłasza błędu dla niewykorzystanego ogona dłuższego źródła. Dla obliczeń wymagających parowania wszystkich próbek sprawdź długości wcześniej. Rozmiar chunk lub slide musi spełniać wymaganie dodatniości; zero nie jest pustą poprawną grupą.

**Dalej:** [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)

### 58. `std::generator` — C++23

Generator oparty na coroutine produkuje leniwą sekwencję wartości przez `co_yield`. Wymaga implementacji nagłówka `<generator>`.

> **C++23; poza lokalną weryfikacją Apple Clang 17/libc++.** Wymagany nagłówek `<generator>` i implementacja `std::generator`, niedostępne w lokalnej konfiguracji.

```cpp,notest
#include <generator>
#include <ranges>

std::generator<unsigned> fibonacci() {
    unsigned a = 0, b = 1;
    while (true) {
        co_yield a;
        auto next = a + b;
        a = b;
        b = next;
    }
}

void use() {
    for (unsigned value : fibonacci() | std::views::take(10)) {
        (void)value;
    }
}
```

**Zastosowanie:** leniwe parsery, generatory danych testowych i sekwencje bez ręcznej maszyny stanów.

**Dlaczego i jak:** Wywołanie generatora tworzy obiekt kontrolujący korutynę, a kolejne iteracje wznawiają ją do następnego co_yield. Lokalne a i b należą do stanu zachowywanego pomiędzy zawieszeniami. Wartość powstaje na żądanie, więc take(10) nie oblicza całej nieskończonej sekwencji. Generator odpowiada synchronicznemu pozyskiwaniu kolejnych elementów, nie automatycznej pracy w osobnym wątku. Zniszczenie właściciela zwalnia zawieszoną ramkę i jej żywe obiekty, jeśli iterację zakończono wcześniej.

**Pułapka:** Generator jest zakresem jednokrotnego przejścia; nie zakładaj niezależnych wielokrotnych iteratorów jak w vector. Fibonacci na unsigned po przekroczeniu zakresu zawija się modulo. Referencje do parametrów korutyny muszą pozostać ważne przez wszystkie późniejsze wznowienia.

**Dalej:** [Korutyny, awaitery i ramka](zaawansowane/12_korutyny_promise_awaitery_i_frame.md)

### 59. Własny `promise_type` coroutine

Typ wyniku coroutine definiuje zagnieżdżony `promise_type`, który kontroluje utworzenie obiektu, zawieszenia i rezultat.

```cpp
#include <coroutine>
#include <exception>

struct Task {
    struct promise_type {
        Task get_return_object() noexcept { return {}; }
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };
};

Task run() {
    co_return;
}
```

**Zastosowanie:** własne taski, generatory i integracja z event loop.

**Dlaczego i jak:** promise_type jest częścią protokołu kompilatorowego, mimo nazwy nie jest std::promise. Kompilator tworzy promise w ramce, uzyskuje obiekt wyniku przez get_return_object, a następnie respektuje initial_suspend. co_return przekazuje rezultat przez return_void lub return_value, po czym final_suspend określa końcowy stan ramki. W pokazanym minimalnym Task oba zawieszenia są pomijane, więc wywołanie wykonuje się do końca i nie zwraca właściciela zawieszonej pracy. Obsługa błędu celowo kończy cały proces.

**Pułapka:** Nie można dodać do takiego Task destruktora niszczącego zapamiętany handle bez zmiany protokołu końca. Przy suspend_never w final_suspend ramka może już zostać automatycznie zniszczona. Drugi destroy oznaczałby użycie nieaktualnego uchwytu i naruszenie czasu życia.

**Dalej:** [Korutyny, awaitery i ramka](zaawansowane/12_korutyny_promise_awaitery_i_frame.md)

### 60. Własny awaiter

Obiekt używany przez `co_await` definiuje `await_ready`, `await_suspend` i `await_resume`.

```cpp
#include <coroutine>

struct ResumeImmediately {
    bool await_ready() const noexcept { return false; }
    bool await_suspend(std::coroutine_handle<>) const noexcept {
        return false; // nie pozostawiaj coroutine zawieszonej
    }
    int await_resume() const noexcept { return 42; }
};

// Wewnątrz coroutine: int value = co_await ResumeImmediately{};
```

**Zastosowanie:** adaptery operacji I/O, timerów, callbacków i schedulerów.

**Dlaczego i jak:** await_ready decyduje, czy można od razu przejść do await_resume. Gdy zwraca fałsz, korutyna przygotowuje zawieszenie i wywołuje await_suspend z uchwytem do siebie. Wynik bool równy false oznacza kontynuowanie bez pozostawienia korutyny zawieszonej; dlatego przykład natychmiast otrzyma czterdzieści dwa. Inne dozwolone postacie await_suspend mogą pozostawić pracę schedulerowi albo przekazać sterowanie innej korutynie. await_resume dostarcza wartość wyrażenia co_await i może odtworzyć błąd zakończonej operacji.

**Pułapka:** Po opublikowaniu handle w innym wątku korutyna może zostać wznowiona jeszcze przed powrotem await_suspend. Awaiter może wtedy już nie istnieć. Nie odczytuj bez zabezpieczenia jego pól po przekazaniu uchwytu; ustal też synchronizację stanu przekazywanego odbiorcy.

**Dalej:** [Korutyny, awaitery i ramka](zaawansowane/12_korutyny_promise_awaitery_i_frame.md)

### 61. `std::coroutine_handle` i kontrola ramki

Handle jest nieposiadającym uchwytem do ramki coroutine. Właściciel musi dokładnie określić, kto wywołuje `destroy()`.

```cpp
#include <coroutine>
#include <utility>

class OwnedCoroutine {
    std::coroutine_handle<> handle_{};
public:
    explicit OwnedCoroutine(std::coroutine_handle<> h) : handle_(h) {}
    OwnedCoroutine(OwnedCoroutine&& other) noexcept
        : handle_(std::exchange(other.handle_, {})) {}
    ~OwnedCoroutine() { if (handle_) handle_.destroy(); }

    void resume() { if (handle_ && !handle_.done()) handle_.resume(); }
};
```

**Zastosowanie:** executory, task handles i jawny lifecycle coroutine frame.

**Dlaczego i jak:** coroutine_handle jest podobny do surowego wskaźnika: kopiowanie nie zwiększa licznika własności i nie przedłuża życia ramki. Pokazany wrapper przekazuje pojedynczą odpowiedzialność w konstruktorze ruchu przez exchange, pozostawiając źródło puste. resume kontynuuje zawieszoną pracę, a destroy niszczy ramkę bez wykonywania jej dalszego zwykłego kodu. Taki właściciel musi współpracować z final_suspend, które pozostawia ramkę dostępną do późniejszego zniszczenia. Sam typ uchwytu nie wymusza tego protokołu.

**Pułapka:** done można sprawdzać dla odpowiedniego zawieszonego stanu, a resume nie wolno wykonywać po końcowym zawieszeniu ani równocześnie z destroy. Wrapper nie jest bezpiecznym właścicielem korutyny, która sama niszczy ramkę na końcu; otrzymałby wiszący handle.

**Dalej:** [Korutyny, awaitery i ramka](zaawansowane/12_korutyny_promise_awaitery_i_frame.md)

### 62. Monadyczne operacje `optional` — C++23

`and_then`, `transform` i `or_else` tworzą pipeline bez ręcznego sprawdzania `has_value()`.

```cpp
#include <optional>
#include <string>
#include <utility>

std::optional<int> parse(std::string text);

std::optional<int> normalized(std::string text) {
    return parse(std::move(text))
        .transform([](int value) { return value * 2; })
        .and_then([](int value) -> std::optional<int> {
            return value < 100 ? std::optional{value} : std::nullopt;
        });
}
```

**Zastosowanie:** kompozycja opcjonalnych transformacji bez zagnieżdżonych instrukcji warunkowych.

**Dlaczego i jak:** transform uruchamia funkcję tylko dla obecnej wartości i opakowuje zwykły wynik w nowe optional. and_then oczekuje funkcji zwracającej optional, dzięki czemu nie tworzy zagnieżdżonego optional<optional<T>>. Brak wartości przepływa przez oba kroki bez wywoływania lambd. or_else pozwala zdefiniować działanie dla pustego stanu. Przeciążenia uwzględniają kwalifikację i kategorię optional, co ma znaczenie dla kopiowania lub przenoszenia jego zawartości, zwłaszcza gdy jest ona niekopiowalna.

**Pułapka:** Te operacje nie przechwytują automatycznie wyjątków rzucanych przez callable. Mnożenie int przez dwa nadal wymaga braku przepełnienia. Pusty optional nie wyjaśnia przyczyny odrzucenia; gdy odbiorca potrzebuje szczegółu błędu, wybierz expected z odpowiednim typem błędu.

**Dalej:** [Optional i expected](07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)

### 63. Monadyczne operacje `expected` — C++23

W pełnej implementacji C++23 `and_then`, `transform`, `transform_error` i `or_else` składają operacje zakończone błędem.

```cpp
#include <expected>
#include <string>

using Result = std::expected<int, std::string>;

Result load();
Result validate(int);

Result pipeline() {
    return load()
        .and_then(validate)
        .transform([](int value) { return value * 2; })
        .transform_error([](std::string error) { return "pipeline: " + error; });
}
```

**Zastosowanie:** kolejno wykonywane operacje domenowe z zachowaniem typowanego błędu.

**Dlaczego i jak:** expected rozdziela kanał sukcesu i błędu. and_then łączy operację zwracającą kolejny expected, transform zmienia poprawną wartość, a transform_error przekształca sam błąd. Po pierwszym niepowodzeniu kolejne operacje sukcesu są pomijane, lecz końcowe wzbogacenie błędu nadal może się wykonać. Zwykły brak wyniku i błąd nie muszą więc być zlewane w pusty optional. Typy błędów w połączonych krokach muszą spełniać wymagania odpowiednich przeciążeń; biblioteka nie dobiera dowolnych konwersji semantycznych.

**Pułapka:** Lambda rzucająca wyjątek nie zostaje automatycznie zamieniona na unexpected. Pipeline łączy jawny kanał błędu, a wyjątki mogą nadal go opuścić. Wsparcie podstawowego expected nie dowodzi dostępności wszystkich metod monadycznych; sprawdź właściwą wartość feature-test macro.

**Dalej:** [Optional i expected](07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)

### 64. Overload pattern dla `std::visit`

Zestaw lambd może zostać połączony przez variadic inheritance w jednego visitora.

```cpp
#include <string>
#include <variant>

template<class... Fs>
struct Overload : Fs... { using Fs::operator()...; };
template<class... Fs> Overload(Fs...) -> Overload<Fs...>;

using Value = std::variant<int, std::string>;

std::size_t size(Value value) {
    return std::visit(Overload{
        [](int) { return sizeof(int); },
        [](const std::string& text) { return text.size(); }
    }, value);
}
```

**Zastosowanie:** wyczerpująca obsługa sum types i maszyn stanów.

**Dlaczego i jak:** Każda lambda jest osobnym typem z operatorem wywołania. Overload dziedziczy po tych typach i wprowadza ich operator() do jednego zbioru przeciążeń. std::visit wybiera aktywną alternatywę wariantu i wywołuje najlepiej pasującą funkcję. Nie jest to ręczny switch po indeksie, ale zwykłe reguły przeciążania zastosowane do dostępnych typów. Wszystkie możliwe wywołania muszą być poprawne, a wyniki zwykłego visit mieć wymagany wspólny typ i kategorię.

**Pułapka:** Generyczna lambda może przechwycić przypadek, dla którego oczekiwałeś konwersji do argumentu konkretnej lambdy. Usunięcie alternatywnego overloadu nie zawsze daje błąd, jeśli inny przyjmuje wartość przez konwersję. Sprawdzaj rzeczywistą wyczerpującą obsługę typów, nie tylko liczbę lambd.

**Dalej:** [Variant i inne typy sumowe](06_biblioteka_standardowa/07_tuple_pair_variant_any.md)

### 65. Wielowymiarowy widok `std::mdspan` — C++23

`mdspan` opisuje wielowymiarowy układ nad istniejącą pamięcią i rozdziela extents, layout oraz accessor.

```cpp
#include <array>
#include <mdspan>

std::array<float, 12> storage{};
std::mdspan matrix{storage.data(), 3, 4};

void set_sample() { matrix[1, 2] = 42.0f; }
static_assert(decltype(matrix)::rank() == 2);
```

**Zastosowanie:** macierze, obrazy, bufory DSP i obliczenia numeryczne bez kopiowania.

**Dlaczego i jak:** mdspan łączy uchwyt do danych z rozmiarami wymiarów i odwzorowaniem indeksów. Dla domyślnego layout_right najbardziej prawy indeks zmienia się najszybciej, więc pozycja [1, 2] w macierzy trzy na cztery wskazuje element o przesunięciu sześć. Inny layout może opisywać kolumny lub jawne kroki bez przestawiania danych. Accessor określa sposób uzyskania elementu z uchwytu i przesunięcia. Właścicielem pozostaje zewnętrzny bufor, a utworzenie widoku nie sprawdza jego rzeczywistej pojemności.

**Pułapka:** Indeksy muszą mieścić się w odpowiednich extents, a bufor pomieścić wymagany obszar mappingu. Zmiana layoutu nie transponuje fizycznie pamięci. Pokazane przypisanie do matrix musi być instrukcją wewnątrz funkcji; nie jest legalną deklaracją w zakresie przestrzeni nazw.

**Dalej:** [Widoki i dangling](03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md); [Layout i wyrównanie](zaawansowane/03_layout_alignment_padding_i_triviality.md)

---

## Współbieżność i atomiki — 66–82

### 66. Zarządzany wątek `std::jthread`

`jthread` automatycznie żąda zatrzymania i wykonuje `join` w destruktorze.

```cpp
#include <chrono>
#include <stop_token>
#include <thread>

void run() {
    std::jthread worker([](std::stop_token token) {
        while (!token.stop_requested()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    });
} // request_stop + join
```

**Zastosowanie:** długowieczne workery bez ryzyka zapomnianego `join()`.

**Dlaczego i jak:** Destruktor jthread sprawdza, czy posiada dołączalny wątek, żąda zatrzymania i czeka przez join. Token może zostać automatycznie przekazany jako pierwszy argument funkcji, jeśli jej wywołanie w takiej postaci jest poprawne. W przykładzie worker okresowo odczytuje token i dobrowolnie wychodzi z pętli. Sama prośba nie przerywa instrukcji w dowolnym miejscu. Kolejność deklaracji właściciela wątku i obserwowanych danych powinna zapewniać, że dane przetrwają aż do ukończenia join.

**Pułapka:** Automatyczny join może blokować bez końca, jeśli worker nie reaguje na zatrzymanie lub czeka na zasób trzymany przez niszczący go wątek. sleep_for nie jest mechanizmem anulowania; token będzie zauważony dopiero po powrocie z oczekiwania.

**Dalej:** [Thread, jthread i stop_token](10_wspolbieznosc/01_thread_jthread_i_stop_token.md)

### 67. Kooperatywne anulowanie przez `stop_token`

`stop_source` rozsyła żądanie, token je obserwuje, a `stop_callback` reaguje synchronicznie na zmianę.

```cpp
#include <stop_token>

bool cancel_operation() {
    std::stop_source source;
    auto token = source.get_token();

    bool callback_called{};
    std::stop_callback callback{token, [&] { callback_called = true; }};
    source.request_stop();
    return callback_called;
}
```

**Zastosowanie:** wspólny protokół anulowania dla wątków i operacji blokujących.

**Dlaczego i jak:** stop_source oraz pochodzące od niego tokeny odnoszą się do wspólnego stanu zatrzymania. Pierwsze skuteczne request_stop zmienia ten stan nieodwracalnie i wykonuje zarejestrowane callbacki. Jeżeli callback rejestruje się po zgłoszeniu prośby, może zostać wykonany już w trakcie własnej konstrukcji. Mechanizm nadaje się do obudowy operacji blokujących i powiadomienia oczekujących, ale nie kończy za nie pracy. Każda operacja musi określić bezpieczny moment przerwania i stan pozostający po anulowaniu.

**Pułapka:** Callback nie działa automatycznie na osobnym wątku. Może wykonać się w request_stop i zakleszczyć program, jeśli próbuje przejąć mutex już trzymany przez wywołującego. Nie powinien też wypuszczać wyjątków ani zakładać dowolnego porządku pozostałych callbacków.

**Dalej:** [Thread, jthread i stop_token](10_wspolbieznosc/01_thread_jthread_i_stop_token.md)

### 68. `condition_variable_any` ze `stop_token`

Wersja C++20 może zakończyć oczekiwanie po spełnieniu predykatu albo żądaniu anulowania.

```cpp
#include <condition_variable>
#include <mutex>
#include <stop_token>

std::mutex mutex;
std::condition_variable_any changed;
bool ready{};

bool wait_for_data(std::stop_token token) {
    std::unique_lock lock{mutex};
    return changed.wait(lock, token, [] { return ready; });
}
```

**Zastosowanie:** anulowalne kolejki blokujące i graceful shutdown workerów.

**Dlaczego i jak:** Oczekiwanie czasowo zwalnia blokadę, umożliwiając producentowi zmianę ready, a przed powrotem odzyskuje ją i ponownie sprawdza predykat. Powiadomienie jest sygnałem do sprawdzenia stanu, nie samym stanem. Przeciążenie ze stop_token dodaje możliwość obudzenia wskutek prośby o zatrzymanie. Wynik bool opisuje spełnienie predykatu, dlatego może być prawdziwy także wtedy, gdy równocześnie zażądano anulowania. Wywołujący powinien zdecydować, czy priorytet ma dostępna praca, czy zakończenie.

**Pułapka:** Producent musi modyfikować ready pod tym samym mutexem; samo notify nie zastępuje synchronizacji. Fałszywy wynik po anulowaniu nie oznacza, że wolno czytać brakujące dane. Nie niszcz condition_variable ani chronionego stanu, dopóki ktoś nadal oczekuje.

**Dalej:** [Mutexy i condition variable](10_wspolbieznosc/02_mutex_lock_i_condition_variable.md)

### 69. Blokowanie wielu mutexów przez `std::scoped_lock`

Konstruktor blokuje kilka mutexów algorytmem unikającym deadlocka, a destruktor zwalnia wszystkie.

```cpp
#include <mutex>

struct Account { std::mutex mutex; int balance{}; };

void transfer(Account& from, Account& to, int amount) {
    if (&from == &to) return;
    std::scoped_lock lock{from.mutex, to.mutex};
    from.balance -= amount;
    to.balance += amount;
}
```

**Zastosowanie:** atomowe operacje na kilku chronionych obiektach.

**Dlaczego i jak:** scoped_lock przejmuje wszystkie przekazane mutexy przed wejściem do sekcji krytycznej i oddaje je przy każdym zwykłym wyjściu z zakresu. Mechanizm wielokrotnego blokowania unika klasycznej sytuacji, w której dwa wywołania trzymają przeciwne pierwsze blokady. Dzięki temu odczyt i aktualizacja obu sald mogą być jedną logiczną operacją wobec innych uczestników używających tych samych mutexów. Synchronizacja nie sprawdza jednak poprawności kwoty, dostępnych środków ani przepełnienia reprezentacji salda.

**Pułapka:** Jeżeli from i to oznaczają ten sam obiekt, przekazujesz ten sam nierekurencyjny mutex dwa razy i naruszasz wymagania blokowania. Obsłuż taki przypadek przed scoped_lock. Walidację sald przeprowadź po przejęciu blokad, aby nie oprzeć decyzji na nieaktualnym stanie.

**Dalej:** [Mutexy i condition variable](10_wspolbieznosc/02_mutex_lock_i_condition_variable.md)

### 70. Wielu czytelników przez `std::shared_mutex`

`shared_lock` dopuszcza wielu czytelników, a `unique_lock` zapewnia wyłączny zapis.

```cpp
#include <mutex>
#include <shared_mutex>
#include <string>
#include <utility>

class Config {
    mutable std::shared_mutex mutex_;
    std::string value_;
public:
    std::string read() const {
        std::shared_lock lock{mutex_};
        return value_;
    }
    void write(std::string value) {
        std::unique_lock lock{mutex_};
        value_ = std::move(value);
    }
};
```

**Zastosowanie:** cache i konfiguracja z dominującym odczytem.

**Dlaczego i jak:** shared_mutex udostępnia dwa tryby własności: wiele jednoczesnych blokad współdzielonych albo jedną wyłączną. Odczyt w przykładzie kopiuje napis przed oddaniem blokady, więc odbiorca dostaje niezależną wartość. Metoda const może blokować mutable mutex bez zmiany logicznej konfiguracji. Korzyść zależy od czasu odczytów, udziału zapisów i kosztu samej blokady; prosty mutex może być szybszy przy krótkich operacjach. Standard nie daje uniwersalnej polityki sprawiedliwości między czytelnikami a pisarzami.

**Pułapka:** Nie zwracaj referencji do value_ po zwolnieniu blokady, jeśli inny wątek może zmienić napis. Zmiana shared_lock na unique_lock nie stanowi automatycznej atomowej promocji. Po zwolnieniu odczytu i przejęciu zapisu trzeba ponownie sprawdzić zależny od stanu warunek.

**Dalej:** [Mutexy i condition variable](10_wspolbieznosc/02_mutex_lock_i_condition_variable.md)

### 71. Podstawowe operacje atomowe

`std::atomic<T>` wykonuje operacje bez data race dla wspieranego typu.

```cpp
#include <atomic>

std::atomic<unsigned> completed{};

void finish_job() {
    completed.fetch_add(1, std::memory_order_relaxed);
}

unsigned count() {
    return completed.load(std::memory_order_relaxed);
}
```

**Zastosowanie:** liczniki i flagi, które nie publikują innych danych.

**Dlaczego i jak:** fetch_add jest pojedynczą atomową operacją odczytu, modyfikacji i zapisu. Dwa równoczesne zwiększenia nie gubią aktualizacji, ponieważ odnoszą się do uporządkowanych modyfikacji jednego obiektu atomowego. memory_order_relaxed zachowuje tę atomowość, ale nie publikuje niezależnych danych zapisanych wcześniej przez worker. Licznik w przykładzie opisuje liczbę wykonanych zgłoszeń, a nie gotowość osobnego bufora. Dla większych typów atomowe operacje mogą wewnętrznie używać blokad, co sprawdza się przez odpowiednie własności lock-free.

**Pułapka:** Zapis completed = completed + 1 składa się z osobnego atomowego odczytu i zapisu; cała sekwencja nie jest jednym read-modify-write. Może gubić równoległe zwiększenia mimo braku data race na atomiku. Do wspólnego licznika użyj fetch_add lub operatora inkrementacji.

**Dalej:** [Model pamięci i reclamation](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)

### 72. Acquire–release memory ordering

Store-release publikuje wcześniejsze zapisy, a load-acquire, który odczyta tę wartość, udostępnia je w wątku konsumenta.

```cpp
#include <atomic>

int payload{};
std::atomic<bool> ready{};

void producer() {
    payload = 42;
    ready.store(true, std::memory_order_release);
}

int consumer() {
    while (!ready.load(std::memory_order_acquire)) {}
    return payload;
}
```

**Zastosowanie:** jednokrotna publikacja danych bez mutexa.

**Dlaczego i jak:** Zapis payload jest sekwencjonowany przed store-release. Gdy konsument odczyta opublikowaną wartość przez load-acquire, powstaje relacja synchronizes-with, która wraz z kolejnością instrukcji buduje happens-before do odczytu payload. Dzięki temu samo payload nie musi być atomowe w tym jednorazowym protokole. Acquire nie pobiera magicznie wszystkich najnowszych danych z każdego wątku: potrzebne jest powiązanie z właściwą publikacją. Relacja dotyczy konkretnych operacji, a nie ogólnej szybkości pamięci podręcznej.

**Pułapka:** Ponowny zapis payload po ustawieniu ready może ścigać się z odczytem konsumenta. Przykład jest protokołem jednej publikacji, nie wielokrotnego przesyłania wiadomości. Zastąpienie acquire przez relaxed usuwa potrzebną relację nawet wtedy, gdy test działa na danym procesorze.

**Dalej:** [Model pamięci i reclamation](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)

### 73. Pętla Compare-And-Exchange

CAS aktualizuje wartość tylko wtedy, gdy nadal jest równa oczekiwanej; po porażce nadpisuje `expected` aktualną wartością.

```cpp
#include <atomic>

std::atomic<unsigned> maximum{};

void observe(unsigned value) {
    auto current = maximum.load(std::memory_order_relaxed);
    while (current < value &&
           !maximum.compare_exchange_weak(
               current, value,
               std::memory_order_relaxed,
               std::memory_order_relaxed)) {}
}
```

**Zastosowanie:** lock-free aktualizacja maksimum, stanu i wskaźników.

**Dlaczego i jak:** CAS porównuje reprezentację przechowywanej wartości z expected i przy zgodności zapisuje desired jako jedną operację. Po rzeczywistej niezgodności aktualizuje expected, dzięki czemu kolejna iteracja może podjąć decyzję na nowszej wartości. W przykładzie pętla kończy się także wtedy, gdy konkurent opublikował już większe maksimum. weak może zgłosić pozorną porażkę, dlatego pasuje do ponawianej pętli. Użycie relaxed jest wystarczające dla niezależnej liczbowej statystyki, która nie służy publikowaniu innych obiektów.

**Pułapka:** Dla bardziej złożonej transformacji desired trzeba ponownie obliczać po zmianie expected. Sukces CAS na adresie nie dowodzi, że wskazywany obiekt nie został zwolniony i zastąpiony innym pod tym adresem. Algorytmy wskaźnikowe potrzebują rozwiązania ABA i odzyskiwania pamięci.

**Dalej:** [Model pamięci i reclamation](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)

### 74. Atomowe operacje na istniejącym obiekcie przez `atomic_ref`

`atomic_ref<T>` nakłada atomowy interfejs na poprawnie wyrównany obiekt o odpowiednim lifetime.

```cpp
#include <atomic>

alignas(std::atomic_ref<unsigned>::required_alignment)
unsigned shared_counter{};

void increment() {
    std::atomic_ref counter{shared_counter};
    counter.fetch_add(1, std::memory_order_relaxed);
}
```

**Zastosowanie:** struktury w pamięci współdzielonej i stopniowa integracja atomików z istniejącym layoutem.

**Dlaczego i jak:** atomic_ref umożliwia oddzielenie reprezentacji danych od sposobu ich aktualizacji. Wrapper odnosi się do istniejącego obiektu odpowiedniego trywialnie kopiowalnego typu i nie tworzy nowego licznika. Kilka takich wrapperów może wykonywać atomowe operacje na tym samym poprawnie wyrównanym obiekcie. required_alignment może być większe od zwykłego alignof(T), dlatego przykład wyraźnie zwiększa wyrównanie. Właściciel danych musi zapewnić, że obiekt nie zostanie przeniesiony ani zniszczony, dopóki aktywne odwołania nadal go używają.

**Pułapka:** Podczas życia odpowiednich atomic_ref dostęp do wskazanego obiektu musi respektować wymagany atomowy protokół; zwykły odczyt tego samego licznika nie staje się bezpieczny sam przez obecność wrappera. Przenoszenie kontenera z takim elementem może dodatkowo unieważnić jego adres.

**Dalej:** [Model pamięci i reclamation](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)

### 75. `atomic::wait` i `notify`

Wątek może oczekiwać bez aktywnego spinowania, aż wartość atomowa przestanie być równa oczekiwanej.

```cpp
#include <atomic>

std::atomic<int> state{};

void wait_until_ready() {
    int expected = 0;
    while (state.load(std::memory_order_acquire) == 0)
        state.wait(expected, std::memory_order_relaxed);
}

void publish() {
    state.store(1, std::memory_order_release);
    state.notify_all();
}
```

**Zastosowanie:** lekkie zdarzenia i lock-free state machines bez condition variable.

**Dlaczego i jak:** wait porównuje wartość atomika z przekazaną starą wartością i może blokować, dopóki porównanie nadal wskazuje równość. notify budzi oczekujących, ale nie zmienia samego atomika. W przykładzie producent najpierw publikuje stan przez release, a konsument używa acquire w warunku pętli, więc właściwy odczyt zapewnia widoczność danych. Oczekiwanie może korzystać z mechanizmów systemowych zamiast stale zajmować procesor. Pętla opisuje pożądany stan, niezależnie od szczegółu sposobu obudzenia.

**Pułapka:** Zmiana wartości i notify nie tworzą trwałej kolejki zdarzeń. Sekwencja A–B–A może pozostać niezauważona przez oczekującego na zmianę A. Jeżeli musisz odnotować każde zdarzenie, użyj licznika generacji lub kolejki, a nie przełączanej w obie strony flagi.

**Dalej:** [Model pamięci i reclamation](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)

### 76. Liczący semafor

`counting_semaphore` ogranicza liczbę równoczesnych użytkowników zasobu.

```cpp
#include <semaphore>

std::counting_semaphore<8> slots{4};

void use_gpu() {
    slots.acquire();
    try {
        // operacja wykorzystująca jeden z czterech slotów
    } catch (...) {
        slots.release();
        throw;
    }
    slots.release();
}
```

**Zastosowanie:** connection pool, rate limiting i ograniczenie równoległości.

**Dlaczego i jak:** Semafor przechowuje liczbę dostępnych pozwoleń. acquire czeka na dodatni licznik i atomowo go zmniejsza, a release oddaje pozwolenie. W przeciwieństwie do mutexa oddanie może wykonać inny wątek niż pobranie, co pozwala modelować dostępne elementy kolejki. Parametr szablonu określa wymagane minimum maksymalnej wartości licznika, a konstruktor ustawia liczbę początkowych pozwoleń. W przykładzie dostępne są cztery sloty, mimo parametru osiem. Protokół powinien dokładnie bilansować pobrania i zwroty pozwoleń.

**Pułapka:** Wyjątek pomiędzy acquire i release może na zawsze utracić pozwolenie, jeśli sprzątanie nie jest zagwarantowane. Użyj strażnika RAII w rzeczywistym kodzie. Semafor ogranicza równoczesność, ale sam nie określa limitu liczby operacji na sekundę ani czasu ich wykonania.

**Dalej:** [Latch, barrier i semaphore](10_wspolbieznosc/05_latch_barrier_semaphore.md)

### 77. Jednorazowa synchronizacja przez `std::latch`

Latch odlicza do zera i nie może zostać użyty ponownie.

```cpp
#include <latch>
#include <thread>
#include <vector>

void launch() {
    std::latch ready{3};
    std::vector<std::jthread> workers;
    for (int i = 0; i < 3; ++i) {
        workers.emplace_back([&] {
            ready.count_down();
            ready.wait();
        });
    }
}
```

**Zastosowanie:** oczekiwanie na inicjalizację grupy komponentów.

**Dlaczego i jak:** Latch reprezentuje jedną zależność od ustalonej liczby ukończonych czynności. count_down zmniejsza licznik, a wait blokuje do osiągnięcia zera. Oba działania są rozdzielone, więc worker może zgłosić gotowość i później poczekać na resztę grupy. Po otwarciu latch pozostaje otwarty; nie rozpoczyna nowej rundy. Synchronizacja pozwala użyć przygotowanych danych po zakończeniu oczekiwania, jeśli ich zapisy należały do właściwych zgłaszanych działań. W przykładzie właściciel latch żyje dłużej niż dołączane wątki.

**Pułapka:** Każda zaplanowana czynność musi ostatecznie zmniejszyć licznik. Jeżeli utworzenie któregoś wątku rzuci, już uruchomione wątki mogą czekać na zgłoszenie, które nigdy nie nastąpi. Destruktory jthread wtedy blokują na join, więc inicjalizacja grupy również potrzebuje przemyślanej ścieżki błędu.

**Dalej:** [Latch, barrier i semaphore](10_wspolbieznosc/05_latch_barrier_semaphore.md)

### 78. Wielofazowa synchronizacja przez `std::barrier`

Barrier może być używany cyklicznie, a completion function wykonuje się po każdej ukończonej fazie.

```cpp
#include <barrier>
#include <thread>

void phases() {
    std::barrier sync{2, []() noexcept { /* koniec fazy */ }};

    std::jthread first{[&] {
        // faza 1
        sync.arrive_and_wait();
        // faza 2
    }};
    std::jthread second{[&] {
        sync.arrive_and_wait();
    }};
}
```

**Zastosowanie:** symulacje, iteracyjne algorytmy równoległe i przetwarzanie klatkowe.

**Dlaczego i jak:** Bariera organizuje pracę w fazy. Uczestnik zgłasza dotarcie, a arrive_and_wait dodatkowo czeka, aż wymagana liczba uczestników zamknie fazę. Funkcja completion może przygotować wspólny stan następnej rundy, zanim oczekujący przejdą dalej. Po zakończeniu licznik przygotowuje się do kolejnej fazy. arrive_and_drop pozwala uczestnikowi trwale zrezygnować z kolejnych rund i odpowiednio zmienia liczbę oczekiwanych zgłoszeń. To mechanizm dla algorytmu o znanej strukturze uczestnictwa, nie ogólna kolejka niezależnych zadań.

**Pułapka:** Worker, który wychodzi z pętli bez odpowiedniego drop lub zgłoszenia, może zatrzymać wszystkich pozostałych. Nie wywołuj completion z operacją wymagającą postępu tych samych czekających wątków. Funkcja zakończenia fazy musi spełniać wymagany kontrakt niezgłaszania wyjątków.

**Dalej:** [Latch, barrier i semaphore](10_wspolbieznosc/05_latch_barrier_semaphore.md)

### 79. Ręczne połączenie `promise`–`future`

Producer ustawia wynik albo wyjątek w `promise`, a konsument odbiera go raz przez `future`.

```cpp
#include <future>
#include <thread>
#include <utility>

int calculate() {
    std::promise<int> promise;
    auto future = promise.get_future();

    std::jthread worker{[promise = std::move(promise)]() mutable {
        promise.set_value(42);
    }};

    return future.get();
}
```

**Zastosowanie:** adaptowanie callbacków i komunikacja jednorazowego wyniku między wątkami.

**Dlaczego i jak:** Promise i future współdzielą stan zawierający jeszcze niegotowy albo już dostarczony wynik. get_future pobiera uchwyt odbiorcy, a przeniesienie promise do lambdy przekazuje odpowiedzialność producentowi. set_value zapisuje rezultat i oznacza gotowość; get czeka w razie potrzeby, po czym odbiera wartość. Zamiast wartości producent może ustawić exception_ptr przez set_exception, a get odtworzy wyjątek. Samo posiadanie future nie uruchamia pracy; w przykładzie odpowiada za to osobno utworzony jthread.

**Pułapka:** Promise zwykle można zaspokoić tylko raz, a future::get konsumuje dostęp do wyniku. Porzucona niezaspokojona promise sygnalizuje broken_promise. Nieobsłużony wyjątek w funkcji wątku nie trafia automatycznie do promise; trzeba go przechwycić i jawnie przekazać przez set_exception.

**Dalej:** [Future, promise i async](10_wspolbieznosc/03_future_promise_async.md)

### 80. Odroczone zadanie przez `packaged_task`

`packaged_task` opakowuje callable i udostępnia jego wynik przez `future`.

```cpp
#include <future>
#include <thread>
#include <utility>

int run_task() {
    std::packaged_task<int(int)> task{[](int value) { return value * 2; }};
    auto result = task.get_future();
    std::jthread worker{std::move(task), 21};
    return result.get();
}
```

**Zastosowanie:** kolejki pracy i ręcznie implementowane thread poole.

**Dlaczego i jak:** packaged_task łączy callable z przyszłym współdzielonym stanem wyniku. Pobranie future nie wykonuje funkcji; dopiero operator wywołania task uruchamia obliczenie i zapisuje wartość albo przechwycony wyjątek. Przeniesienie do workera pozwala umieścić niekopiowalne zadanie w kolejce bez tworzenia nowego stanu odbiorcy. W odróżnieniu od ręcznej promise obsługa wyjątków z samego callable jest częścią adaptera. Nadal trzeba zapewnić faktyczne uruchomienie task oraz odpowiedni czas życia wszystkich przechwyconych przez niego danych.

**Pułapka:** packaged_task nie jest schedulerem ani automatyczną pulą wątków. Umieszczenie go w kolejce bez pracującego konsumenta pozostawia future niegotowe. Ponowne zwykłe wywołanie tego samego zaspokojonego task nie oznacza kolejnego wyniku dla poprzedniego future; potrzebny jest nowy cykl stanu.

**Dalej:** [Future, promise i async](10_wspolbieznosc/03_future_promise_async.md)

### 81. Polityka uruchomienia `std::async`

Jawna polityka `launch::async` wymusza asynchroniczne wykonanie; domyślna może wybrać również wykonanie odroczone.

```cpp
#include <future>

int calculate() {
    auto future = std::async(std::launch::async, [] { return 6 * 7; });
    return future.get();
}
```

**Zastosowanie:** proste, jednorazowe zadania z wynikiem. Dla wielu zadań lepsza jest kontrolowana pula.

**Dlaczego i jak:** Polityka async uruchamia obliczenie asynchronicznie, a future przechowuje wynik lub wyjątek. Polityka deferred odkłada wywołanie do odpowiedniego oczekiwania i może wykonać je w wątku oczekującego. Domyślne przeciążenie pozwala implementacji wybrać między tymi zachowaniami, więc kod nie może polegać na natychmiastowym rozpoczęciu pracy. Jawne async uściśla kontrakt, ale tworzenie wielu zadań nadal wymaga kontroli zasobów. get zaraz po uruchomieniu zapewnia wynik, lecz nie daje okazji wykonywać równoległej pracy po stronie wywołującego.

**Pułapka:** Tymczasowy future z async może blokować przy zniszczeniu, więc dwa pozornie równoległe wywołania bez zachowania uchwytów mogą wykonać się kolejno. Przechwycenie lokalnych zmiennych przez referencję jest bezpieczne tylko wtedy, gdy przeżyją całe zadanie, także na ścieżkach wyjątków.

**Dalej:** [Future, promise i async](10_wspolbieznosc/03_future_promise_async.md)

### 82. Parallel algorithms i execution policies

Execution policy pozwala bibliotece wykonać algorytm sekwencyjnie, równolegle albo wektorowo. Funkcja użytkownika nie może tworzyć data race.

> **C++17 i późniejsze; poza lokalną weryfikacją Apple Clang 17/libc++.** Wymagana implementacja algorytmów z polityką `std::execution::par_unseq` i jej zaplecze wykonania. Lokalna biblioteka nie udostępnia użytej polityki.

```cpp,notest
#include <algorithm>
#include <execution>
#include <vector>

void normalize(std::vector<float>& values) {
    std::transform(
        std::execution::par_unseq,
        values.begin(), values.end(), values.begin(),
        [](float value) noexcept { return value * 0.5f; }
    );
}
```

**Zastosowanie:** CPU-bound transformacje dużych, niezależnych zbiorów.

**Dlaczego i jak:** Polityka wykonania określa, jakie sposoby organizacji pracy są dozwolone implementacji. par dopuszcza równoległe wywołania, a par_unseq również nieuporządkowane wykonanie umożliwiające wektoryzację. Biblioteka może jednak wybrać wykonanie sekwencyjne; polityka nie jest obietnicą konkretnej liczby wątków. W pokazanej transformacji każdy element jest odczytywany i zastępowany własnym wynikiem, bez wspólnego modyfikowalnego licznika. Zysk zależy od rozmiaru danych, przepustowości pamięci i kosztu podziału pracy, a nie tylko liczby rdzeni.

**Pułapka:** Pod par_unseq nie wolno bezmyślnie używać operacji blokujących i funkcji niebezpiecznych dla wektoryzacji, nawet jeśli zapobiegłyby data race. Wyjątek opuszczający callable przy standardowych politykach może prowadzić do terminate. Algorytm redukcji może również zmienić kolejność obliczeń zmiennoprzecinkowych.

**Dalej:** [SIMD i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

---

## Low-level, diagnostyka, moduły i C++26 — 83–100

### 83. Three-way comparison (`<=>`)

Spaceship operator generuje wspólny wynik porządku i może umożliwić kompilatorowi utworzenie pozostałych operatorów relacyjnych.

```cpp
#include <compare>

struct Version {
    int major{};
    int minor{};
    int patch{};

    constexpr auto operator<=>(const Version&) const = default;
};

static_assert(Version{1, 2, 0} < Version{1, 3, 0});
```

**Zastosowanie:** spójne porównania value objects i struktur leksykograficznych.

**Dlaczego i jak:** Domyślne porównanie analizuje podobiekty w ustalonej kolejności i zatrzymuje się na pierwszej różnicy. Dla Version oznacza to najpierw major, potem minor i patch, czyli porządek leksykograficzny. Wynik spaceship należy do kategorii porządku, którą można porównywać z zerem; nie jest zwykłą odległością liczbową. Wyrażenia relacyjne korzystają z reguł przepisywania operatorów. Przy domyślnej deklaracji odpowiednio dostarczane jest także porównanie równości, ale własna implementacja spaceship wymaga osobnego rozważenia operatora ==.

**Pułapka:** Porządek pól musi odpowiadać znaczeniu typu. Dodanie pola cache może przypadkiem zmienić równość i sortowanie. Własność częściowego porządku, na przykład przy NaN w double, oznacza możliwość nieuporządkowania; nie wolno traktować każdego wyniku różnego od less jako greater.

**Dalej:** [Funkcje specjalne i operatory](04_klasy_i_model_obiektowy/03_funkcje_specjalne_i_operatory.md)

### 84. Bezpieczna reinterpretacja bitów przez `std::bit_cast`

`bit_cast` kopiuje reprezentację pomiędzy trivially copyable typami o tym samym rozmiarze, bez naruszania strict aliasing.

```cpp
#include <bit>
#include <cstdint>

constexpr float one = 1.0f;
constexpr auto bits = std::bit_cast<std::uint32_t>(one);
static_assert(bits == 0x3F80'0000u);
```

**Zastosowanie:** serializacja, formaty IEEE-754 i protokoły binarne.

**Dlaczego i jak:** bit_cast tworzy nową wartość docelowego typu z reprezentacji źródła, zamiast budować alias do tego samego obiektu pod innym typem. Równość rozmiarów i trywialna kopiowalność są wymaganiami sprawdzanymi dla typów. Operacja nadaje się do inspekcji reprezentacji, lecz znaczenie otrzymanych bitów nadal wynika z formatu źródła i celu. Asercja z jedynką zakłada konkretnie reprezentację float zgodną z IEEE binary32 oraz odpowiadające przyporządkowanie bitów do uint32_t; nie jest uniwersalną gwarancją samego języka.

**Pułapka:** Nie każda reprezentacja bajtów odpowiada poprawnej wartości dowolnego typu docelowego. Padding i wartości indeterminate mają dodatkowe reguły, których bit_cast nie usuwa. Nie serializuj w ten sposób klas z zasobami ani wskaźnikami, oczekując przenośnego odtworzenia ich znaczenia.

**Dalej:** [Lifetime i aliasing](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 85. `std::endian` i `std::byteswap`

Kod może jawnie dostosować byte order platformy do formatu wire. `byteswap` jest częścią C++23.

```cpp
#include <bit>
#include <cstdint>

static_assert(std::endian::native == std::endian::little ||
              std::endian::native == std::endian::big);

constexpr std::uint32_t to_big_endian(std::uint32_t value) {
    if constexpr (std::endian::native == std::endian::little)
        return std::byteswap(value);
    else
        return value;
}
```

**Zastosowanie:** sieć, pliki binarne i wymiana danych między architekturami.

**Dlaczego i jak:** endian opisuje kolejność bajtów reprezentacji typów skalarnych implementacji, a byteswap odwraca kolejność bajtów odpowiedniej wartości całkowitej. To rozróżnienie między wartością liczbową i jej reprezentacją ma znaczenie: po zamianie bajtów sama liczba zwykle się zmienia, lecz zapis jej reprezentacji może dać oczekiwany format transmisji. Funkcja z przykładu jest poprawna przy założeniu jednolicie little-endian albo big-endian. Standard dopuszcza również implementacje mieszane, dla których native nie jest równe żadnej z tych dwóch wartości.

**Pułapka:** Gałąź else nie powinna bez dowodu oznaczać big-endian. Dodaj jawne ograniczenie wspieranych architektur albo serializuj poszczególne bajty przez przesunięcia. byteswap nie rozwiązuje paddingu całej struktury, rozmiaru pól ani reprezentacji float w niezależnym protokole binarnym.

**Dalej:** [Layout, padding i alignment](zaawansowane/03_layout_alignment_padding_i_triviality.md)

### 86. Wyrównanie i linie cache

`alignas` steruje minimalnym wyrównaniem, a `hardware_destructive_interference_size` pomaga rozdzielić atomiki narażone na false sharing.

```cpp
#include <atomic>
#include <new>

struct Counters {
    alignas(std::hardware_destructive_interference_size)
    std::atomic<unsigned> producer{};

    alignas(std::hardware_destructive_interference_size)
    std::atomic<unsigned> consumer{};
};
```

**Zastosowanie:** ograniczanie cache-line contention w intensywnie aktualizowanych licznikach.

**Dlaczego i jak:** Fałszywe współdzielenie zachodzi, gdy niezależnie aktualizowane dane trafiają do tej samej jednostki spójności cache. Procesory mogą wtedy przekazywać sobie własność linii mimo braku logicznego współdzielenia licznika. Zwiększenie wyrównania i odstępu między polami pomaga oddzielić takie aktualizacje. hardware_destructive_interference_size jest stałą zależną od implementacji przeznaczoną do tego rodzaju decyzji. Nie zastępuje pomiaru na docelowym sprzęcie, a powiększenie każdego obiektu może pogorszyć wykorzystanie pamięci podręcznej w innych wzorcach odczytu.

**Pułapka:** alignas nie zapewnia atomowości ani synchronizacji zwykłych pól. Wartość stałej może zależeć od konfiguracji kompilacji, więc użycie jej w publicznym layoutcie wpływa na zgodność ABI. Sprawdź dostępność bibliotecznego makra i pomiary zamiast wpisywać rozmiar linii jako uniwersalny fakt.

**Dalej:** [SIMD, cache i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

### 87. Automatyczny kontekst przez `std::source_location`

Domyślny argument przechwytuje plik, linię i nazwę funkcji w miejscu wywołania.

```cpp
#include <source_location>
#include <string_view>

void log(
    std::string_view message,
    std::source_location location = std::source_location::current()
) {
    auto file = location.file_name();
    auto line = location.line();
    (void)message; (void)file; (void)line;
}
```

**Zastosowanie:** logowanie i asercje bez makr `__FILE__` oraz `__LINE__`.

**Dlaczego i jak:** source_location jest niewielką wartością opisującą kontekst źródła znany kompilatorowi. Szczególna reguła current w domyślnym argumencie pozwala uchwycić miejsce wywołania log, a nie linię implementacji loggera. Przekazanie gotowej lokalizacji przez kolejne warstwy zachowuje pierwotny kontekst zgłoszenia. Mechanizm nadaje się do funkcji kontrolujących preconditions i raportujących błędy bez rozszerzania każdej operacji makrem. Szczegóły nazwy funkcji i sposobu przedstawienia ścieżki zależą jednak od implementacji oraz konfiguracji budowania.

**Pułapka:** Wrapper wywołujący log bez przekazania własnego source_location zapisze lokalizację wewnętrznego wywołania, a nie użytkownika wrappera. Dodaj domyślny parametr również do wrappera i przekaż go dalej. Źródłowa ścieżka nie jest stabilnym identyfikatorem ani gwarancją istnienia pliku na komputerze odbiorcy.

**Dalej:** [Diagnostyka i debugowanie](09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)

### 88. Stack trace jako wartość — C++23

`std::stacktrace::current()` przechwytuje stos w punkcie wywołania. Wsparcie i wymagania linkera zależą od implementacji.

> **C++23; poza lokalną weryfikacją Apple Clang 17/libc++.** Wymagany nagłówek `<stacktrace>` oraz zaplecze przechwytywania stosu; lokalna konfiguracja nie dostarcza tego nagłówka.

```cpp,notest
#include <stacktrace>

struct ErrorContext {
    std::stacktrace trace = std::stacktrace::current();
};
```

**Zastosowanie:** diagnostyka błędów, crash reporting i kontekst wyjątków.

**Dlaczego i jak:** Stacktrace jest migawką aktywnego łańcucha wywołań w chwili przechwycenia. Utworzenie ErrorContext zapisuje więc drogę prowadzącą do konstrukcji tego obiektu. Jeśli kontekst zostanie później przeniesiony jako część błędu, zachowuje pierwotną informację zamiast stosu miejsca obsługi. Reprezentacja wpisów i możliwość uzyskania nazw zależą od implementacji, symboli debugowania oraz optymalizacji. Operacja może wymagać alokacji i dodatkowego wsparcia linkera, dlatego jej koszt należy uwzględnić w projekcie ścieżki diagnostycznej.

**Pułapka:** Stacktrace przechwycony dopiero w catch pokazuje stos po rozwinięciu wcześniejszych ramek, więc nie odtworzy automatycznie miejsca throw. Brak pełnych symboli może dać ograniczone nazwy. Nie zakładaj też, że dynamiczne przechwycenie stosu jest bezpieczne w sygnalizatorze awarii wymagającym async-signal-safety.

**Dalej:** [Diagnostyka i debugowanie](09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)

### 89. Bezpieczne formatowanie przez `std::format`

Format string jest typowany i może zostać sprawdzony podczas kompilacji.

```cpp
#include <format>
#include <string>

std::string describe(int id, double rate) {
    return std::format("session={} rate={:.2f} MHz", id, rate / 1'000'000.0);
}
```

**Zastosowanie:** czytelne formatowanie bez niebezpieczeństw rodziny `printf`.

**Dlaczego i jak:** Format string opisuje pozycje argumentów i sposób ich przedstawienia, a typy argumentów są przekazywane oddzielnie. Dla typowego literału interfejs std::format może zweryfikować zgodność specyfikatorów podczas kompilacji. W przykładzie precyzja dotyczy wartości po przeliczeniu herców na megaherce; formatowanie nie ustala jednostki samo. Wynikiem jest właścicielski string, który można zachować niezależnie. Własne typy mogą dostarczyć specjalizację formatter, definiując obsługiwany język specyfikatorów i sposób przedstawienia swojej wartości.

**Pułapka:** Dynamicznego formatu z pliku nie przekazuje się w C++23 dowolnie do sprawdzanego interfejsu literałowego. Użyj właściwego vformat i obsłuż format_error. Bezpieczna zgodność typów nie wyklucza kosztownych szerokości pól ani ujawnienia poufnej zawartości w samym wyniku.

**Dalej:** [Strumienie i formatowanie](11_io_i_system/01_strumienie_i_formatowanie.md)

### 90. `std::print` — C++23

`print` i `println` łączą typowane formatowanie z bezpośrednim wyjściem. Wsparcie zależy od biblioteki standardowej.

```cpp
#include <print>

void report(unsigned frames, double seconds) {
    std::println("frames={} duration={:.3f}s", frames, seconds);
}
```

**Zastosowanie:** narzędzia CLI, diagnostyka i zwięzłe raportowanie.

**Dlaczego i jak:** print łączy formatowanie z zapisem do wskazanego standardowego celu, a println dodatkowo dopisuje znak nowej linii. Nie trzeba najpierw tworzyć widocznego w kodzie stringa i osobno przekazywać go do strumienia. Mechanizm korzysta z tego samego systemu formatterów, więc własne typy mogą zachować spójną prezentację. Obsługa tekstu na terminalach uwzględnia szczegóły implementacji, a dostępność print jest osobną własnością biblioteki standardowej od samego rozpoznawania flagi językowej C++23.

**Pułapka:** Nowa linia nie jest ogólną gwarancją natychmiastowego flush do urządzenia. Formatowanie i zapis nadal mogą sygnalizować błędy; nie traktuj print jako niezawodnej operacji noexcept w destruktorze. Przy mieszaniu różnych systemów wyjścia uwzględnij ich buforowanie i wymaganą kolejność komunikatów.

**Dalej:** [Strumienie i formatowanie](11_io_i_system/01_strumienie_i_formatowanie.md)

### 91. Named modules

Moduł eksportuje interfejs semantycznie, bez tekstowego wklejania nagłówka. Konkretne polecenia builda zależą od toolchainu.

> **C++20 i późniejsze; przykład wieloplikowy poza pojedynczym przebiegiem walidatora.** Pliki należy budować w kolejności zależności modułu i importera, z konfiguracją BMI właściwą dla kompilatora. Każdy poniższy blok reprezentuje osobny plik.

```cpp,notest
// math.cppm
export module math;

export constexpr int square(int value) {
    return value * value;
}
```

```cpp,notest
// main.cpp
import math;
static_assert(square(6) == 36);
```

**Zastosowanie:** izolacja interfejsów, mniej zależności preprocesora i potencjalnie szybsze buildy.

**Dlaczego i jak:** Jednostka interfejsu deklaruje nazwę modułu i oznacza deklaracje dostępne importerom przez export. Import udostępnia informacje semantyczne, więc makra odbiorcy nie przepisują tekstu eksportowanej definicji tak jak przy include. System budowania musi znać zależności, wytworzyć odpowiedni artefakt interfejsu i udostępnić go konsumentom w poprawnej kolejności. Funkcja constexpr nadal potrzebuje odpowiedniej osiągalnej definicji do stałej ewaluacji. Moduł nie jest automatycznie oddzielną biblioteką dynamiczną ani granicą stabilnego binarnego interfejsu.

**Pułapka:** Artefakty BMI nie są przenośnym formatem wymiany między dowolnymi kompilatorami i flagami. Samo import nie eliminuje ODR ani nie ujawnia wszystkich wewnętrznych nazw. Nagłówki wymagające makr konfiguracyjnych potrzebują świadomej strategii integracji, często z użyciem global module fragment.

**Dalej:** [ODR, moduły i FFI](zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)

### 92. Module partitions

Duży moduł można rozbić na partycje interfejsu i implementacji, zachowując jedną logiczną jednostkę.

> **C++20 i późniejsze; przykład wieloplikowy poza pojedynczym przebiegiem walidatora.** Partycja interfejsu i główny interfejs modułu wymagają osobnych etapów budowania oraz prawidłowej konfiguracji zależności BMI.

```cpp,notest
// geometry-shapes.cppm
export module geometry:shapes;
export struct Circle { double radius; };
```

```cpp,notest
// geometry.cppm
export module geometry;
export import :shapes;
```

**Zastosowanie:** skalowanie modułów bez ujawniania wewnętrznej organizacji użytkownikowi.

**Dlaczego i jak:** Partycja należy do jednego nazwanego modułu i rozdziela jego implementację lub eksportowany interfejs na mniejsze jednostki. Główny interfejs może reexportować partycję interfejsu przez export import, dzięki czemu użytkownik nadal importuje geometry. Organizacja wewnętrzna nie staje się osobnym publicznym modułem geometry:shapes dostępnym dowolnym importerom. Narzędzia budowania muszą jednak uwzględnić zależności między partycjami. Podział może ograniczać zakres zmian i pracę kompilatora, ale źle zaprojektowany cykl zależności pozostaje problemem architektury.

**Pułapka:** Nie każda partycja implementacyjna może być reexportowana tak jak partycja interfejsu. Nie używaj nazw partycji jako zamiennika niezależnych modułów współdzielonych między projektami. Zmiana organizacji wymaga weryfikacji osiągalności deklaracji potrzebnych przez eksportowane szablony i funkcje inline.

**Dalej:** [ODR, moduły i FFI](zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)

### 93. Granica ABI przez `extern "C"`

Language linkage określa językowe powiązanie funkcji i ich nazw; typowe ABI C używa innego nazewnictwa symboli niż C++. Nie czyni to klas STL zgodnymi z ABI C.

```cpp
#include <cstddef>
#include <cstdint>

extern "C" {
    struct SampleI16 { std::int16_t real; std::int16_t imag; };

    std::size_t process_samples(const SampleI16* samples, std::size_t count);
}
```

**Zastosowanie:** integracja z C, Rust FFI, UHD i stabilne wejścia biblioteki współdzielonej.

**Dlaczego i jak:** Language linkage informuje implementację o sposobie wiązania nazw i typów odpowiednich funkcji z innym językiem. W praktycznym ABI C umożliwia uzgodnienie symbolu funkcji między kompilatorami wspierającymi tę samą platformową umowę. Nie przekształca automatycznie argumentów w uniwersalny format. Stabilne FFI powinno używać jasno określonych typów, rozmiarów i własności buforów oraz zapewniać funkcje zwalniające pamięć po właściwej stronie granicy. Pokazany zapis jest nagłówkiem C++; wspólny nagłówek dla C wymaga dodatkowych warunków i typów dostępnych w C.

**Pułapka:** Nie przepuszczaj wyjątków C++ przez nieuzgodnioną granicę C. std::size_t ma rozmiar zależny od platformy, a extern C nie określa pakowania struktur, calling convention ani zgodności bibliotek runtime. Nawet układ z dwóch int16_t trzeba uzgodnić z odbiorcą protokołu.

**Dalej:** [ODR, moduły i FFI](zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)

### 94. Przeciążanie `operator new/delete` i placement new

Klasa może kontrolować źródło pamięci; placement new konstruuje obiekt w przekazanym adresie i wymaga jawnego zniszczenia.

```cpp
#include <cstddef>
#include <memory>
#include <new>

struct Packet {
    int id;
    static void* operator new(std::size_t size) { return ::operator new(size); }
    static void operator delete(void* pointer) noexcept { ::operator delete(pointer); }
};

void create_packet_in_buffer() {
    alignas(Packet) std::byte storage[sizeof(Packet)];
    Packet* packet = std::construct_at(reinterpret_cast<Packet*>(storage), 42);
    std::destroy_at(packet);
}
```

**Zastosowanie:** pule, arenas, shared memory i specjalistyczne strategie alokacji.

**Dlaczego i jak:** Wyrażenie new i funkcja operator new pełnią różne role. Funkcja alokująca uzyskuje storage, a wyrażenie dodatkowo inicjalizuje obiekt. Analogicznie samo operator delete nie zastępuje wywołania destruktora. construct_at tworzy Packet w uprzednio przygotowanym, odpowiednio wyrównanym buforze i nie korzysta ze zwykłego klasowego alokatora pokazanej klasy. destroy_at kończy życie Packet, lecz nie zwalnia zewnętrznego bufora. Dzięki temu pula może wielokrotnie wykorzystywać miejsca bez utożsamiania liczby alokacji z liczbą konstruowanych obiektów.

**Pułapka:** Nie wywołuj zwykłego delete dla obiektu utworzonego wewnątrz automatycznego bufora. Funkcja zwalniająca oczekiwałaby pamięci ze zgodnej alokacji. Bufor musi zachować właściwy rozmiar, wyrównanie i czas życia, a częściowo nieudana konstrukcja wymaga osobnego rozliczenia nabytych zasobów.

**Dalej:** [Alokatory, PMR i new/delete](zaawansowane/04_allocatory_pmr_i_new_delete.md)

### 95. Intrinsics SIMD i runtime dispatch

Intrinsics dają bezpośredni dostęp do zestawu instrukcji. Kod musi mieć fallback i uruchamiać ścieżkę tylko na wspierającym CPU.

> **Rozszerzenie implementacji, x86 SIMD; poza lokalną weryfikacją ARM.** Przykład używa intrinsics AVX za bramką `__AVX2__`; pusta gałąź na ARM nie sprawdza ich poprawności. Wymagany zgodny cel kompilacji i procesor oraz osobny protokół wyboru ścieżki runtime.

```cpp,notest
#if defined(__AVX2__)
#include <immintrin.h>

__m256 add_eight(const float* left, const float* right) {
    auto a = _mm256_loadu_ps(left);
    auto b = _mm256_loadu_ps(right);
    return _mm256_add_ps(a, b);
}
#endif
```

**Zastosowanie:** DSP, korelacja, grafika i intensywne obliczenia numeryczne.

**Dlaczego i jak:** Intrinsic jest rozszerzeniem określonego kompilatora opisującym operację sprzętową, nie ogólną funkcją ISO C++. Instrukcje loadu pobierają osiem float bez wymagania szczególnego wyrównania adresu do granicy wektora, lecz nadal potrzebują ośmiu legalnych elementów. Dodawanie działa równolegle na odpowiadających sobie pozycjach. Makro AVX2 oznacza możliwość generowania instrukcji w tej kompilowanej wersji, a nie sprawdzenie aktualnego procesora. Runtime dispatch wymaga osobnej bezpiecznej detekcji i wyboru właściwie zbudowanej funkcji.

**Pułapka:** Kompilacja całego programu z AVX2 może wprowadzić te instrukcje także do rzekomego fallbacku. Ścieżkę bazową buduj z właściwym celem i uwzględnij wsparcie systemu dla stanu wektorowego. Load bez wymogu wyrównania nadal nie pozwala czytać za końcem tablicy.

**Dalej:** [SIMD i runtime dispatch](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

### 96. Feature-test macros

Makra SD-6 pozwalają warunkowo użyć mechanizmu na podstawie rzeczywistego wsparcia, zamiast zgadywać po wersji kompilatora.

```cpp
#include <version>

#if defined(__cpp_lib_expected) && __cpp_lib_expected >= 202202L
    #define HAS_STD_EXPECTED 1
#else
    #define HAS_STD_EXPECTED 0
#endif

static_assert(HAS_STD_EXPECTED == 0 || HAS_STD_EXPECTED == 1);
```

**Zastosowanie:** biblioteki przenośne i stopniowe wdrażanie C++23/C++26.

**Dlaczego i jak:** Feature-test macro określa obecność konkretnej funkcji i datowaną rewizję jej obsługi. Makra językowe zwykle zaczynają się od __cpp_, a biblioteczne od __cpp_lib_ i są udostępniane przez właściwy nagłówek lub version. Porównanie wartości pozwala odróżnić podstawową implementację od późniejszego rozszerzenia API. W expected próg z przykładu sprawdza podstawowy mechanizm, natomiast metody monadyczne mają późniejszą rewizję makra. Dzięki temu warunki konfiguracji odnoszą się do potrzebnego interfejsu, a nie samej nazwy producenta kompilatora.

**Pułapka:** Samo __cplusplus nie dowodzi, że biblioteka implementuje każdy element wybranego standardu. __has_include potwierdza istnienie pliku, nie pełną zawartość API. Gdy funkcja ma kilka rewizji, zbyt niski próg makra może włączyć kod wymagający niedostępnych jeszcze metod.

**Dalej:** [Nowości i wsparcie C++26](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)

### 97. `std::inplace_vector` — C++26

Kontener ma pojemność zakodowaną w typie i przechowuje elementy wewnątrz obiektu, ale zachowuje zmienny rozmiar.

> **C++26; stan sprawdzony 2026-09-05, poza lokalną weryfikacją C++23.** Wymagana implementacja `<inplace_vector>` odpowiadająca opisanej rewizji C++26.

```cpp,notest
// C++26 — wymaga implementacji <inplace_vector>
#include <inplace_vector>

void make_frame() {
    std::inplace_vector<float, 1024> frame;
    frame.push_back(0.5f);
    frame.resize(512);
}
```

**Zastosowanie:** systemy real-time i embedded, gdy heap allocation jest niedozwolona lub nieprzewidywalna.

**Dlaczego i jak:** W C++26 inplace_vector łączy zmienny rozmiar z miejscem na maksymalnie N elementów wewnątrz samego obiektu. Zwiększanie rozmiaru konstruuje nowe elementy bez przenoszenia całej zawartości do większego bufora. Nie oznacza to jednak, że wszystkie N elementów żyje od początku, jak w array. Zwykłe operacje powiększania przekraczające pojemność mogą zgłosić bad_alloc, mimo braku dynamicznej alokacji kontenera. Weryfikacja opisu: 2026-09-05, bieżący working draft; dostępność konkretnego API zależy od biblioteki.

**Pułapka:** Elementy T mogą same alokować pamięć, więc inplace_vector<string, N> nie oznacza pełnego zakazu heap. Przenoszenie całego kontenera przenosi elementy z jego wewnętrznego miejsca. Przypisania push_back i resize z przykładu muszą znajdować się wewnątrz funkcji.

**Dalej:** [Nowości C++26](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md); [Draft: inplace_vector](https://eel.is/c++draft/inplace.vector)

### 98. `std::simd` — C++26

Standardowy typ SIMD umożliwia przenośne operacje wektorowe, pozostawiając implementacji dobór instrukcji i ABI.

> **C++26; stan sprawdzony 2026-09-05, poza lokalną weryfikacją C++23.** Wymagana implementacja `<simd>` z użytymi nazwami z przestrzeni `std::simd`; wcześniejszy Parallelism TS i prototypy mogą mieć inne API.

```cpp,notest
// C++26 — API według bieżącego working draft.
#include <simd>

void add(const float* left, const float* right, float* output) {
    using V = std::simd::vec<float>;
    auto a = std::simd::unchecked_load<V>(left, V::size());
    auto b = std::simd::unchecked_load<V>(right, V::size());
    std::simd::unchecked_store(a + b, output, V::size());
}
```

**Zastosowanie:** przenośna wektoryzacja DSP, obrazu i algorytmów numerycznych.

**Dlaczego i jak:** Według working draft sprawdzonego 2026-09-05 biblioteka C++26 udostępnia rodzinę std::simd::vec w przestrzeni std::simd. Wartość reprezentuje kilka równoległych elementów, a operatory wykonują działania na odpowiadających pozycjach. Liczba elementów domyślnego wektora może zależeć od typu i wybranego celu kompilacji. Ładowanie i zapis jawnie łączą tę abstrakcję z ciągłym buforem. Kod przykładu przetwarza jeden blok szerokości V::size, więc pełny algorytm powinien dodać przejście przez wszystkie bloki i obsługę końcowej reszty.

**Pułapka:** Przekazanie V::size nie tworzy brakujących danych za końcem bufora. Dla niepełnej reszty potrzebny jest odpowiedni odczyt częściowy lub inna bezpieczna ścieżka. Standardowy interfejs nie gwarantuje jednej instrukcji ani stabilnego ABI między różnymi ustawieniami celu kompilacji.

**Dalej:** [Nowości C++26](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md); [Draft: nagłówek simd](https://eel.is/c++draft/simd.syn)

### 99. Senders/receivers w `std::execution` — C++26

Sender opisuje leniwą operację asynchroniczną, którą można kompozycyjnie łączyć i uruchomić na schedulerze.

> **C++26; stan sprawdzony 2026-09-05, poza lokalną weryfikacją C++23.** Wymagana implementacja modelu senders/receivers i `sync_wait`; sam starszy nagłówek `<execution>` z politykami algorytmów nie wystarcza.

```cpp,notest
// C++26 — API wymaga nowej implementacji <execution>.
#include <execution>
#include <utility>

namespace ex = std::execution;

int run_work() {
    auto work = ex::just(21)
        | ex::then([](int value) { return value * 2; });

    auto [result] = std::this_thread::sync_wait(std::move(work)).value();
    return result;
}
```

**Zastosowanie:** ujednolicony model async, executory, I/O i strukturalna współbieżność.

**Dlaczego i jak:** Sender opisuje operację i możliwe kanały zakończenia: wartości, błąd lub zatrzymanie. Połączenie z receiverem tworzy stan operacji, a start rozpoczyna jej wykonanie. Adapter then przekształca udany rezultat bez ręcznego przepisywania kanałów błędu. Pokazane just oraz then nie wybierają samodzielnie nowego wątku; sync_wait jest konsumentem uruchamiającym i oczekującym na wynik. Weryfikacja API C++26: 2026-09-05, working draft zawiera std::execution oraz std::this_thread::sync_wait. Scheduler i czas życia stanu wymagają osobnego świadomego projektu.

**Pułapka:** Sync_wait może zwrócić pusty optional dla kanału zatrzymania, więc bezwarunkowe value nie jest ogólnym wzorcem obsługi anulowania. Stan operacji i przechwycone referencje muszą przeżyć zakończenie. Sender sam w sobie nie gwarantuje pracy w tle ani użycia puli.

**Dalej:** [Nowości C++26](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md); [Draft: execution](https://eel.is/c++draft/exec); [Draft: sync_wait](https://eel.is/c++draft/exec.sync.wait)

### 100. Statyczna refleksja — C++26

Reflection tworzy compile-time wartości opisujące encje programu, a splicing pozwala wrócić od metadanych do kodu. Składnia wymaga kompilatora obsługującego przyjęty model C++26.

> **C++26; stan sprawdzony 2026-09-05, poza lokalną weryfikacją C++23.** Wymagany frontend obsługujący refleksję oraz zgodny nagłówek `<meta>`; lokalny toolchain nie zapewnia tego zestawu.

```cpp,notest
// C++26 — przykład ideowy według modelu P2996.
#include <meta>
#include <string_view>

struct User { int id; double score; };

consteval std::size_t field_count() {
    return std::meta::nonstatic_data_members_of(
        ^^User, std::meta::access_context::current()
    ).size();
}

static_assert(field_count() == 2);
```

**Zastosowanie:** serializacja, enum-to-string, bindingi, ORM i generowanie kodu bez zewnętrznego parsera.

**Dlaczego i jak:** Refleksja reprezentuje encję programu jako metadane dostępne w stałej ewaluacji. Operator ^^ tworzy odpowiednią informację, a biblioteka meta pozwala pytać o rodzaj encji i jej składowe. W przykładzie nonstatic_data_members_of zwraca informacje o dostępnych niestatycznych polach User, a rozmiar wyniku staje się stałą liczbą. access_context określa kontekst sprawdzania dostępu; refleksja nie powinna przypadkiem stać się niekontrolowanym eksportem całej reprezentacji. Weryfikacja nazw API C++26: 2026-09-05, bieżący working draft.

**Pułapka:** Metadane compile-time nie są automatycznie rejestrem typów runtime ani stabilnym schematem serializacji. Dodanie pola może zmienić generowany format. Oprócz introspekcji nadal trzeba zaprojektować wersjonowanie, obsługę prywatności i reguły kodowania danych; eksperymentalny kompilator może obsługiwać inną rewizję propozycji.

**Dalej:** [Nowości C++26](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md); [Draft: pytania o składowe](https://eel.is/c++draft/meta.reflection.member.queries)

---

## Dodatkowe mechanizmy metaprogramowania i produkcyjnego — 101–150

### 101. Częściowa specjalizacja template

Class template można specjalizować dla całej rodziny typów, np. wszystkich wskaźników.

```cpp
#include <type_traits>

template<class T>
struct IsPointer : std::false_type {};

template<class T>
struct IsPointer<T*> : std::true_type {};

static_assert(!IsPointer<int>::value);
static_assert(IsPointer<const int*>::value);
```

**Zastosowanie:** dobór reprezentacji lub algorytmu na podstawie struktury typu.

**Dlaczego i jak:** Specjalizacja częściowa dopasowuje wzorzec argumentów, a następnie wybiera implementację bardziej wyspecjalizowaną niż szablon główny. Dla `IsPointer<const int*>` parametr T specjalizacji staje się `const int`, więc dziedziczona wartość wynosi true. To wybór całej definicji klasy, a nie warunek wykonywany w programie. Można zmienić zestaw pól, metody i reprezentację. Przy kilku pasujących specjalizacjach działa porządkowanie częściowe; jeśli żadna nie jest jednoznacznie lepsza, instancjacja jest niepoprawna.

**Pułapka:** Szablonów funkcji nie można częściowo specjalizować tak jak klas. Użyj przeciążeń lub pomocniczej klasy. Pokazany trait nie obejmuje też `int* const`: kwalifikator const dotyczy samego wskaźnika, więc prosty wzorzec T* wymaga osobnego rozważenia tej postaci.

**Dalej:** [Nazwy zależne i metaprogramowanie](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)

### 102. Dependent names: `typename` i `template`

Kompilator nie wie, czy nazwa zależna od parametru oznacza typ albo template. Słowa `typename` i `template` usuwają tę niejednoznaczność.

```cpp
template<class Container>
typename Container::value_type first(const Container& container) {
    return *container.begin();
}

template<class Factory>
auto create(Factory& factory) {
    return factory.template make<int>();
}
```

**Zastosowanie:** poprawne parsowanie złożonych templates zależnych od innych typów.

**Dlaczego i jak:** Parser musi rozstrzygnąć składnię, zanim pozna konkretny typ argumentu szablonu. `typename` informuje, że zależna nazwa jest typem, a `template` pozwala odczytać kolejne nawiasy kątowe jako listę argumentów szablonu zamiast operatorów porównania. Nie sprawdzają one, czy członek rzeczywiście istnieje: to zostanie rozstrzygnięte przy odpowiedniej instancjacji. C++20 rozszerzył konteksty, w których typ jest zakładany bez dodatkowego typename, ale jawny zapis nadal pomaga wyjaśnić zależność.

**Pułapka:** Dodanie typename nie naprawia brakującej deklaracji ani nie zamienia wartości w typ. Funkcja first ma dodatkowo warunek niepustego kontenera; poprawne parsowanie szablonu nie zapobiega dereferencji iteratora końcowego po przekazaniu pustego zakresu przez klienta.

**Dalej:** [Nazwy zależne i metaprogramowanie](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)

### 103. Template template parameters

Parametrem template może być inny template, co pozwala wstrzyknąć rodzinę kontenerów lub strategii.

```cpp
#include <deque>
#include <vector>

template<class T, template<class...> class Container = std::vector>
struct Repository {
    Container<T> entities;
};

Repository<int> vector_repository;
Repository<int, std::deque> deque_repository;
```

**Zastosowanie:** konfigurowalne kontenery i policy-based libraries.

**Dlaczego i jak:** Parametr template template otrzymuje rodzinę typów, którą klasa może później instancjować własnym T. Repository nie dostaje gotowego `vector<int>`, lecz szablon vector, dlatego może konsekwentnie podstawić typ elementu. Wariant `template<class...> class` przyjmuje szablony parametrów typowych, w tym allocator używany przez vector i deque. Zgodność parametru szablonowego nie gwarantuje jednak zgodności interfejsu powstałego kontenera; metody Repository muszą wymagać konkretnych operacji przez constraints lub udokumentowany kontrakt.

**Pułapka:** `std::array` nie pasuje do tego samego interfejsu, ponieważ ma nietypowy parametr rozmiaru. Nie każdy szablon kontenera da się więc wymienić mechanicznie. Dodatkowo kontenery mogą różnić się invalidacją i kosztami, mimo identycznych nazw podstawowych metod.

**Dalej:** [Nazwy zależne i metaprogramowanie](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)

### 104. Compile-time string jako NTTP

Structural class type może przechowywać literał i zostać argumentem template.

```cpp
#include <algorithm>
#include <cstddef>

template<std::size_t N>
struct FixedString {
    char value[N];
    constexpr FixedString(const char (&text)[N]) {
        std::copy_n(text, N, value);
    }
};

template<FixedString Name>
struct Event {
    static constexpr auto name = Name;
};

using Started = Event<"acquisition.started">;
```

**Zastosowanie:** typowane nazwy eventów, compile-time routing i refleksja budowana bibliotekowo.

**Dlaczego i jak:** W C++20 i później odpowiedni strukturalny typ klasowy może być nietypowym argumentem szablonu. FixedString kopiuje znaki do publicznej tablicy będącej częścią wartości, zamiast przechowywać wskaźnik do osobnego bufora. Przy instancjacji Event tekst uczestniczy w identyfikacji specjalizacji, więc różne napisy oznaczają różne typy. Parametr N obejmuje końcowe zero literału. Ten model pozwala wiązać nazwy protokołu ze statycznym interfejsem bez wyszukiwania tekstu w runtime.

**Pułapka:** Zastąpienie tablicy zwykłym wskaźnikiem do literału nie zachowuje tych samych reguł dopuszczalności argumentu szablonu. Pola typu strukturalnego muszą spełniać ograniczenia, między innymi dotyczące publiczności i braku mutable; sam konstruktor constexpr nie wystarcza do uzyskania structural type.

**Dalej:** [Stała ewaluacja](zaawansowane/09_constexpr_consteval_i_compile_time.md)

### 105. User-defined literals

Operator literal tworzy domenową wartość bez runtime parsera dla literałów znanych kompilatorowi.

```cpp
#include <cstdint>
#include <limits>

struct Hertz { std::uint64_t value; };

consteval Hertz operator""_MHz(unsigned long long value) {
    if (value > std::numeric_limits<std::uint64_t>::max() / 1'000'000ULL)
        throw "frequency out of range";
    return Hertz{value * 1'000'000ULL};
}

constexpr auto center_frequency = 150_MHz;
static_assert(center_frequency.value == 150'000'000ULL);
```

**Zastosowanie:** jednostki fizyczne, identyfikatory i bezpieczne DSL-e.

**Dlaczego i jak:** Sufiks `_MHz` wybiera operator literałowy, który otrzymuje wartość i buduje odrębny typ jednostki. `consteval` wymaga wykonania tego wywołania podczas obliczania stałego wyrażenia; zwykły operator constexpr mógłby także uczestniczyć w obliczeniach runtime. Hertz pozostaje typem domenowym, więc można później zdefiniować tylko sensowne operacje między jednostkami. Sufiksy użytkownika zaczynające się podkreśleniem unikają przestrzeni nazw zarezerwowanej dla standardowych operatorów literałowych i przyszłych rozszerzeń języka.

**Pułapka:** Stała ewaluacja nie wykrywa automatycznie błędu domenowego przy zawinięciu unsigned. Przed pomnożeniem częstotliwości sprawdź reprezentowalność wyniku. Dopiero jawnie odrzucony przypadek czyni zbyt duży literał błędem kompilacji zamiast poprawną, lecz bezsensowną zawiniętą liczbą.

**Dalej:** [Stała ewaluacja](zaawansowane/09_constexpr_consteval_i_compile_time.md)

### 106. Tag dispatch

Pusty typ wybiera przeciążenie w compile time, zanim concepts i `if constexpr` stały się standardowym narzędziem.

```cpp
#include <iterator>

template<class Iterator>
void advance_impl(Iterator& it, int n, std::random_access_iterator_tag) {
    it += n;
}

template<class Iterator>
void advance_impl(Iterator& it, int n, std::input_iterator_tag) {
    while (n-- > 0) ++it;
}

template<class Iterator>
void advance(Iterator& it, int n) {
    advance_impl(it, n, typename std::iterator_traits<Iterator>::iterator_category{});
}
```

**Zastosowanie:** statyczny dispatch zależny od capabilities typu.

**Dlaczego i jak:** Typ znacznika jest dodatkowym argumentem przeciążenia, ale zwykle nie niesie danych. Dziedziczenie kategorii iteratorów pozwala wybrać najbardziej szczególną dostępną wersję, a dla iteratora słabszego zastosować pętlę. Koszt operacji różni się więc zgodnie z możliwościami typu: skok losowy jest stałoczasowy, a przejście input iteratora liniowe. Mechanizm nadal przydaje się do jawnego protokołu rozszerzeń, chociaż if constexpr często lepiej mieści niewielki wybór wewnątrz pojedynczej funkcji.

**Pułapka:** Wariant input w przykładzie nie obsługuje ujemnego n; milczące pominięcie pętli nie jest odpowiednikiem cofnięcia iteratora. Trzeba ograniczyć kontrakt do nieujemnych odległości albo dodać właściwe przeciążenie bidirectional, nadal pilnując granic rzeczywistego zakresu.

**Dalej:** [Nazwy zależne i metaprogramowanie](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)

### 107. Policy-based design

Zachowanie klasy jest składane z typów-strategii bez wirtualnego dispatchu.

```cpp
struct NoRetry {
    template<class F> static auto run(F&& operation) { return operation(); }
};

struct ThreeAttempts {
    template<class F> static auto run(F&& operation) {
        for (int attempt = 0; attempt < 2; ++attempt)
            if (auto result = operation()) return result;
        return operation();
    }
};

template<class RetryPolicy>
struct Client {
    auto send() { return RetryPolicy::run([] { return true; }); }
};
```

**Zastosowanie:** compile-time konfiguracja logowania, retry, alokacji i synchronizacji.

**Dlaczego i jak:** Policy jest parametrem typu, więc Client z różnymi strategiami tworzy różne specjalizacje znane kompilatorowi. Nie trzeba przechowywać wskaźnika do funkcji wirtualnej tylko po to, aby wybrać stałą konfigurację. Strategia może mieć własny stan, wymagania i niezgłaszające operacje, które powinny być widoczne w kontrakcie klienta. Kompozycja kilku polityk daje elastyczność, lecz powiększa liczbę instancjacji i wymaga sprawdzenia, czy ich kombinacje rzeczywiście mają sens domenowy.

**Pułapka:** Ponawiana operacja musi być bezpieczna do powtórzenia. Sam wynik false nie dowodzi, że poprzednia próba nie wykonała częściowego zapisu lub żądania sieciowego. Dla efektów zewnętrznych potrzebna jest idempotencja, identyfikator żądania albo jednoznaczny protokół kompensacji.

**Dalej:** [Type erasure i ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

### 108. Expression templates

Operatory budują drzewo lekkich proxy zamiast od razu materializować wynik każdego działania.

```cpp
template<class Left, class Right>
struct SumExpr {
    const Left& left;
    const Right& right;
    double operator[](int index) const { return left[index] + right[index]; }
};

template<class L, class R>
SumExpr<L, R> operator+(const L& left, const R& right) {
    return {left, right};
}
```

**Zastosowanie:** biblioteki macierzy i wektorów eliminujące obiekty tymczasowe.

**Dlaczego i jak:** Wynik operatora plus jest opisem obliczenia, a nie gotowym buforem. Odczyt elementu SumExpr wykonuje dodawanie odpowiadających elementów źródeł; docelowe przypisanie może przejść po całym drzewie w jednej pętli. Oszczędza to kolekcje pośrednie, ale zmienia czas ewaluacji i model własności. Dopracowana biblioteka rozróżnia referencje do trwałych operandów od posiadanych tymczasowych węzłów oraz analizuje aliasing między wynikiem i jego wejściami przed rozpoczęciem zapisu.

**Pułapka:** Zapisanie `auto expr = (a + b) + c` przy pokazanych samych referencjach może pozostawić referencję do zniszczonego tymczasowego SumExpr. Złożona składnia nie przedłuża automatycznie życia wewnętrznych operandów. Potrzebna jest własność odpowiednich węzłów lub natychmiastowa materializacja.

**Dalej:** [Czas życia i aliasing](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 109. Typelist i operacje na listach typów

Lista typów istnieje wyłącznie podczas kompilacji i może być transformowana specjalizacjami.

```cpp
#include <cstddef>

template<class... Ts>
struct TypeList {};

template<class List>
struct Size;

template<class... Ts>
struct Size<TypeList<Ts...>> {
    static constexpr std::size_t value = sizeof...(Ts);
};

static_assert(Size<TypeList<int, double, char>>::value == 3);
```

**Zastosowanie:** dependency injection, rejestry komponentów i compile-time pipelines.

**Dlaczego i jak:** Pakiet Ts jest informacją typową dostępną podczas kompilacji. Specjalizacja Size rozpakowuje TypeList i liczy parametry bez tworzenia obiektów tych typów. Inne operacje mogą transformować każdy typ, filtrować spełniające concept albo wyszukiwać pierwsze dopasowanie. Takie wyniki służą do generowania tuple, wariantu lub zestawu przeciążeń. Koszt przenosi się do instancjacji i diagnostyki kompilatora, więc duże rejestry warto projektować z ograniczeniem głębokości rekurencji i liczby pośrednich typów.

**Pułapka:** Lista typów nie przechowuje obiektów, ale instancjacje wygenerowane na jej podstawie mogą zawierać duże wartości i kosztowny kod. Nie myl braku samego runtime typelisty z brakiem kosztu rozwiązania. Powtarzające się typy także mogą wymagać rozstrzygnięcia tożsamości.

**Dalej:** [Nazwy zależne i metaprogramowanie](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)

### 110. Variadic mixins

Dziedziczenie po packu typów składa capabilities w jeden typ.

```cpp
struct Startable { void start() {} };
struct Stoppable { void stop() {} };
struct Resettable { void reset() {} };

template<class... Capabilities>
struct Device : Capabilities... {};

using SdrDevice = Device<Startable, Stoppable, Resettable>;

void use(SdrDevice& device) {
    device.start();
    device.reset();
}
```

**Zastosowanie:** compile-time composition zamiast głębokiej hierarchii klas.

**Dlaczego i jak:** Rozwinięcie pakietu w liście baz tworzy osobny podobiekt dla każdej capability. Dziedziczone metody stają się częścią interfejsu Device zgodnie z regułami dostępu i wyszukiwania nazw. Kompilator zna cały zestaw podczas instancjacji, więc nie potrzeba dynamicznego rejestru funkcjonalności. Capabilities mogą korzystać z CRTP, aby odwoływać się do konkretnego urządzenia, lecz wtedy trzeba jawnie określić wymagany interfejs oraz moment, kiedy kompletny obiekt nadaje się do użycia.

**Pułapka:** Dwa mixiny z metodą o tej samej nazwie mogą powodować niejednoznaczność, a dwukrotne podanie tego samego typu bazy jest niepoprawne. Dodatkowo stan poszczególnych baz jest realnym storage. Dziedziczenie pakietu nie gwarantuje automatycznej kompresji wszystkich składowych.

**Dalej:** [Układ i właściwości typów](zaawansowane/03_layout_alignment_padding_i_triviality.md)

### 111. Uniwersalne wywołanie przez `std::invoke`

`invoke` obsługuje zwykłe callables, funkcje członkowskie i wskaźniki do pól jednym interfejsem.

```cpp
#include <functional>

struct Sensor {
    double gain{30.0};
    double read(int channel) const { return gain + channel; }
};

Sensor sensor;
auto value = std::invoke(&Sensor::read, sensor, 1);
auto gain = std::invoke(&Sensor::gain, sensor);
```

**Zastosowanie:** generyczne executory, callback wrappers i algorytmy wyższego rzędu.

**Dlaczego i jak:** INVOKE opisuje wspólny protokół wywołania: zwykły callable otrzymuje argumenty, a wskaźnik do metody najpierw rozstrzyga obiekt docelowy. Obsługiwane są między innymi obiekty, wskaźniki i reference_wrapper. Wskaźnik do pola daje dostęp do składowej bez wywoływania funkcji. Dzięki temu generyczny adapter nie musi pisać własnego zestawu gałęzi dla każdej postaci callbacka, a traits takie jak is_invocable sprawdzają zgodność z tym samym modelem.

**Pułapka:** Wynik dostępu do pola może być referencją, lecz zwykłe `auto gain` w przykładzie tworzy kopię wartości. Jeśli chcesz zmieniać sensor przez wynik, zachowaj właściwą referencję. Invoke nie przedłuża także życia obiektu wskazywanego przez przechowywany callback.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 112. Rozpakowanie tuple przez `std::apply`

`apply` przekazuje elementy tuple-like object jako osobne argumenty funkcji.

```cpp
#include <tuple>

constexpr int multiply(int a, int b, int c) { return a * b * c; }

constexpr auto arguments = std::tuple{2, 3, 7};
static_assert(std::apply(multiply, arguments) == 42);
```

**Zastosowanie:** forwarding przechowywanych argumentów i metaprogramowanie tuple.

**Dlaczego i jak:** Apply tworzy koncepcyjnie sekwencję indeksów od zera do liczby elementów i przekazuje każdy get jako oddzielny argument do protokołu invoke. Kategoria wartości tuple wpływa na kategorie przekazywanych elementów, co umożliwia kopiowanie, wiązanie referencji lub przenoszenie zawartości. Nie jest to wywołanie funkcji z jednym argumentem tuple. W C++23 normatywny koncept tuple-like używany przez tę część biblioteki opisuje określone standardowe rodziny, a nie każdy typ wspierający structured bindings.

**Pułapka:** Przeciążona funkcja albo nierozstrzygnięty szablon funkcji może wymagać lambdy pośredniczącej, aby apply otrzymało konkretny callable. Samo dodanie tuple_size i własnego get do rekordu nie daje przenośnej gwarancji współpracy z każdym standardowym algorytmem tuple-like.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 113. Wskaźniki do składowych

Pointer-to-member nie jest zwykłym adresem; wymaga obiektu, względem którego zostanie zastosowany.

```cpp
struct Sample {
    float real;
    float imaginary;
};

float Sample::* component = &Sample::imaginary;
Sample sample{1.0f, 2.0f};

void update_component() {
    sample.*component = 3.0f;
}
```

**Zastosowanie:** projections, binding pól i generyczna serializacja.

**Dlaczego i jak:** Wartość `float Sample::*` opisuje składową obiektu Sample, ale nie wskazuje pojedynczego istniejącego float bez wybrania obiektu. Operator `.*` łączy ją z obiektem, a `->*` ze wskaźnikiem do obiektu. Reprezentacja może być bardziej złożona niż zwykły adres, szczególnie dla metod i dziedziczenia. Taki uchwyt jest przydatny jako projekcja, ponieważ pozwala kodowi generycznemu wskazać pole bez tworzenia osobnej lambdy dla każdego rekordu.

**Pułapka:** Nie serializuj surowej reprezentacji pointer-to-member jako przenośnego offsetu pola. Rozmiar i kodowanie zależą od ABI, a null member pointer nie musi mieć samych zer w pamięci. Do wywołania nadal potrzebny jest żywy obiekt właściwego typu.

**Dalej:** [Układ i właściwości typów](zaawansowane/03_layout_alignment_padding_i_triviality.md)

### 114. `bind_front` i `bind_back`

Bindery zachowują część argumentów callabla. `bind_back` jest dodatkiem C++23 i wymaga aktualnej biblioteki.

```cpp
#include <functional>

constexpr int clamp(int value, int minimum, int maximum) {
    return value < minimum ? minimum : value > maximum ? maximum : value;
}

constexpr int add_base(int base, int value) { return base + value; }

auto add_ten = std::bind_front(add_base, 10);
auto percentage = std::bind_back(clamp, 0, 100); // C++23
```

**Zastosowanie:** adaptery callbacków i częściowa aplikacja argumentów.

**Dlaczego i jak:** Binder tworzy nowy callable posiadający oryginalną funkcję oraz przekształcone kopie związanych argumentów. Bind_front umieszcza je przed argumentami przyszłego wywołania, a bind_back za nimi. Kwalifikatory obiektu bindera wpływają na przekazywanie jego stanu, co pomaga zachować przenoszenie przy użyciu jako rvalue. W porównaniu ze starszym bind nie trzeba rozpisywać placeholderów dla wszystkich niezwiązanych argumentów. Dla bardziej złożonych przekształceń jawna lambda bywa czytelniejszym interfejsem.

**Pułapka:** Związanie wskaźnika lub reference_wrapper nie przejmuje własności wskazywanego obiektu. Callback zachowany na później może więc użyć wygasłego celu. Bind_back nie jest dostępny w C++20 mimo podobieństwa do bind_front; trzeba sprawdzić poziom biblioteki standardowej.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 115. Ręczna type erasure

Interfejs, model template i owning wrapper ukrywają konkretny typ bez wymagania wspólnej klasy bazowej od użytkownika.

```cpp
#include <memory>
#include <utility>

class Command {
    struct Concept { virtual ~Concept() = default; virtual void run() = 0; };
    template<class F>
    struct Model final : Concept {
        F function;
        explicit Model(F f) : function(std::move(f)) {}
        void run() override { function(); }
    };
    std::unique_ptr<Concept> self_;
public:
    template<class F> Command(F f) : self_(std::make_unique<Model<F>>(std::move(f))) {}
    void run() { self_->run(); }
};
```

**Zastosowanie:** jednolity interfejs źródłowy oraz przechowywanie heterogenicznych typów spełniających kontrakt strukturalny; stabilność binarna wymaga oddzielnego projektu ABI.

**Dlaczego i jak:** Konstruktor szablonowy poznaje konkretny F i tworzy Model<F>, ale reszta programu przechowuje tylko jednolity Command. Wywołanie przechodzi przez wewnętrzny interfejs wirtualny, dzięki czemu użytkownik nie musi dziedziczyć po klasie bazowej biblioteki. Unique_ptr koduje wyłączną własność oraz domyślny zakaz kopiowania wrappera. Pełniejsza implementacja może dodać operację clone, mały bufor lub ograniczenia invocable, lecz każda z tych decyzji zmienia koszt i publiczną semantykę wartości.

**Pułapka:** Po przeniesieniu self_ może być pusty, więc run wymaga określonego kontraktu stanu źródłowego. Pokazany wrapper nie tworzy sam stabilnego ABI pluginów: zawiera zależne od kompilatora klasy, vtable i mechanikę niszczenia, które nadal wymagają zgodnego środowiska.

**Dalej:** [Type erasure i ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

### 116. `[[no_unique_address]]`

Puste pole może współdzielić adres z innym polem, dzięki czemu policy lub deleter nie zwiększa rozmiaru obiektu.

```cpp
#include <cstddef>

struct EmptyPolicy {};

struct CompressedValue {
    [[no_unique_address]] EmptyPolicy policy;
    std::size_t value;
};

static_assert(sizeof(CompressedValue) >= sizeof(std::size_t));
// Równość jest możliwą optymalizacją konkretnej implementacji.
```

**Zastosowanie:** kompresja pustych policies, iteratorów i smart pointerów.

**Dlaczego i jak:** Atrybut zezwala implementacji traktować pole jako potencjalnie nakładający się podobiekt. Pusta policy może dzięki temu nie zwiększyć rozmiaru otaczającej klasy, a dla niektórych niepustych pól możliwe jest wykorzystanie końcowego paddingu. Jest to pozwolenie dotyczące reprezentacji, a nie nakaz osiągnięcia określonego sizeof. Semantycznie pole nadal istnieje, ma swój typ, inicjalizację i destrukcję. Równość rozmiaru trzeba mierzyć osobno dla wybranego ABI, jeśli stanowi lokalne wymaganie projektu.

**Pułapka:** Nie przedstawiaj `sizeof(CompressedValue) == sizeof(size_t)` jako przenośnej gwarancji języka. Rozmiar, wyrównanie i decyzje implementacji mogą dać inny wynik. Pola tego samego typu podlegają też regułom tożsamości obiektów; atrybut nie pozwala dowolnie nakładać wszystkich adresów.

**Dalej:** [Układ i właściwości typów](zaawansowane/03_layout_alignment_padding_i_triviality.md)

### 117. Empty Base Optimization (EBO)

Pusta klasa bazowa zwykle nie zajmuje dodatkowej pamięci w klasie pochodnej.

```cpp
#include <type_traits>

struct EmptyAllocator {};

struct VectorStorage : private EmptyAllocator {
    void* data{};
    unsigned size{};
};

static_assert(std::is_empty_v<EmptyAllocator>);
// Rozmiar VectorStorage zależy także od paddingu i ABI.
```

**Zastosowanie:** starszy odpowiednik kompresji policies używany wewnątrz kontenerów.

**Dlaczego i jak:** Pusty kompletny obiekt musi mieć reprezentację pozwalającą odróżniać obiekty, ale pusty podobiekt bazowy może zostać skompresowany. Dziedziczenie po allocatorze było dlatego używane do przechowywania bezstanowych polityk bez dodatkowego bajtu powiększającego padding. Prywatne dziedziczenie w przykładzie jest detalem reprezentacji, nie publiczną relacją domenową. Dla nowego kodu pole z no_unique_address często czytelniej wyraża kompozycję, o ile dostępny standard i wymagania ABI pozwalają na zmianę układu.

**Pułapka:** Nie każdy układ dziedziczenia pozwala na dowolną kompresję, zwłaszcza gdy pojawiają się powiązane podobiekty tego samego typu. Prosty górny limit sizeof obliczony z rozmiarów pól może też ignorować implementacyjne wyrównanie i padding. Weryfikuj konkretną reprezentację osobno.

**Dalej:** [Układ i właściwości typów](zaawansowane/03_layout_alignment_padding_i_triviality.md)

### 118. Triviality i standard-layout

Type traits pozwalają sprawdzić, czy typ można bezpiecznie kopiować bajtowo oraz czy ma layout odpowiedni dla określonych granic ABI.

```cpp
#include <cstdint>
#include <type_traits>

struct SampleI16 {
    std::int16_t real;
    std::int16_t imaginary;
};

static_assert(std::is_trivially_copyable_v<SampleI16>);
static_assert(std::is_standard_layout_v<SampleI16>);
```

**Zastosowanie:** binarne I/O, shared memory i warstwa FFI.

**Dlaczego i jak:** Trivially copyable opisuje możliwość zachowania wartości przez odpowiednie kopiowanie reprezentacji bajtowej, z warunkami dotyczącymi obiektów i podobiektów. Standard-layout daje odrębne właściwości układu oraz relacji do pierwszej składowej, przydatne przy analizie interoperacyjności. Te cechy nie są równoważne: typ może spełniać jedną bez drugiej. Trait jest odpowiedzią kompilatora dla danego typu, więc warto sprawdzać konkretną właściwość potrzebną operacji zamiast używać ogólnego określenia prosty typ.

**Pułapka:** Żaden z tych traits nie gwarantuje przenośnego formatu pliku ani identycznego ABI na różnych maszynach. Padding, endianowość, reprezentacja liczb i szerokości typów nadal mają znaczenie. Surowy zapis pamięci może dodatkowo ujawniać nieistotne bajty wypełnienia obiektu.

**Dalej:** [Układ i właściwości typów](zaawansowane/03_layout_alignment_padding_i_triviality.md)

### 119. Aktywny member unionu

Union współdzieli pamięć między polami, ale program sam odpowiada za śledzenie aktywnego membera i jego lifetime.

```cpp
#include <memory>
#include <string>

union Storage {
    int number;
    std::string text;
    Storage() : number{} {}
    ~Storage() {}
};

void switch_active_member() {
    Storage storage;
    std::construct_at(&storage.text, "active");
    std::destroy_at(&storage.text);
}
```

**Zastosowanie:** wnętrze `variant`, small-object optimization i ręczne layouty.

**Dlaczego i jak:** Union zapewnia wspólne storage o rozmiarze i wyrównaniu wystarczającym dla jego pól, lecz zwykle aktywne jest tylko jedno z nich. Construct_at w przykładzie rozpoczyna życie string w miejscu, gdzie wcześniej aktywna była liczba. Ponieważ stary int nie wymaga sprzątania zasobów, można przejść do konstrukcji nowej alternatywy. Późniejsze destroy_at kończy życie napisu. Własny destruktor unionu nie zgaduje aktywnej alternatywy, dlatego kod musi utrzymywać tę informację zewnętrznie.

**Pułapka:** Odczyt nieaktywnego pola nie jest przenośnym odpowiednikiem bit_cast. Dla klas z zasobami pominięcie destruktora starej alternatywy może wyciec pamięć. Przy rzucającej konstrukcji nowej alternatywy trzeba również określić stan znacznika, aby późniejszy cleanup nie niszczył nieistniejącego obiektu.

**Dalej:** [Czas życia i aliasing](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 120. `std::launder`

Po utworzeniu nowego obiektu w tym samym storage istniejący wskaźnik nie zawsze może być użyty do dostępu. `launder` uzyskuje wskaźnik zgodny z nowym lifetime.

```cpp
#include <new>

struct Value { const int number; };

int replace_value() {
    Value value{1};
    auto* old_pointer = &value;
    new (&value) Value{2};
    auto* current = std::launder(old_pointer);
    return current->number;
}
```

**Zastosowanie:** szczególne przypadki ponownego wykorzystania storage, gdy reguły transparent replacement nie przenoszą automatycznie dawnych wskaźników na nowy obiekt.

**Dlaczego i jak:** Launder nie konstruuje obiektu ani nie przesuwa pamięci. Przy spełnionych wymaganiach uzyskuje wskaźnik do już istniejącego obiektu danego typu w określonym miejscu, gdy poprzedni wskaźnik nie daje wymaganej relacji do nowego czasu życia. Trzeba zachować między innymi ograniczenia osiągalności bajtów. W pokazanym przykładzie C++23 kompletny nieconst obiekt Value jest transparentnie zastępowalny przez drugi Value; samo pole const nie sprawia, że launder jest tutaj konieczne.

**Pułapka:** Launder nie legalizuje zapisu w pamięci rzeczywiście stałego kompletnego obiektu, błędnego wyrównania ani dostępu do storage po zwolnieniu. Często najprościej zachować wskaźnik bezpośrednio zwrócony przez placement new, zamiast próbować naprawiać dowolny dawny wskaźnik.

**Dalej:** [Czas życia i aliasing](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 121. Strict aliasing i dostęp do object representation

Dowolny trivially copyable obiekt można bezpiecznie skopiować do bajtów przez `memcpy` lub oglądać przez `as_bytes`.

```cpp
#include <array>
#include <cstddef>
#include <cstring>
#include <span>

void inspect_object_representation() {
    float value = 1.0f;
    std::array<std::byte, sizeof(value)> bytes{};
    std::memcpy(bytes.data(), &value, sizeof(value));

    auto representation = std::as_bytes(std::span{&value, 1});
    (void)representation;
}
```

**Zastosowanie:** serializacja bez undefined behavior wynikającego z niepoprawnego `reinterpret_cast`.

**Dlaczego i jak:** Reguły dostępu do obiektu przez typ ograniczają, jakimi glvalue można odczytywać przechowywaną wartość. Oglądanie reprezentacji przez char, unsigned char lub std::byte jest przewidzianym wyjątkiem, a as_bytes udostępnia taki niemodyfikowalny zakres. Memcpy kopiuje bajty bez tworzenia nieprawidłowej referencji do innego typu. To przydatne do diagnostyki i określonych operacji na typach trivially copyable, ale trzeba odróżniać reprezentację obiektu od semantycznie zdefiniowanego zewnętrznego kodowania danych.

**Pułapka:** Skopiowanie bajtów float do bufora nie daje automatycznie przenośnego protokołu binarnego. Reprezentacja i endianowość mogą się różnić. Odwrotna interpretacja dowolnych bajtów jako obiektu wymaga poprawnej reprezentacji wartości, właściwego czasu życia i spełnienia warunków konkretnej operacji.

**Dalej:** [Czas życia i aliasing](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

### 122. `std::assume_aligned`

Program przekazuje optymalizatorowi udowodnione założenie o wyrównaniu wskaźnika. Fałszywe założenie prowadzi do undefined behavior.

```cpp
#include <memory>

float sum_aligned(float* pointer, int count) {
    auto* aligned = std::assume_aligned<32>(pointer);
    float result{};
    for (int i = 0; i < count; ++i) result += aligned[i];
    return result;
}
```

**Zastosowanie:** umożliwienie wektoryzacji buforów z gwarantowanym alignmentem.

**Dlaczego i jak:** Assume_aligned zwraca wskaźnik, dla którego optymalizator może wykorzystać podane wyrównanie. Nie alokuje nowego bufora i nie poprawia liczbowego adresu argumentu. Obietnicę uzasadnia zwykle alignas, odpowiedni allocator lub kontrakt zewnętrznego API. Należy korzystać z otrzymanego wyniku, ponieważ to z nim narzędzie wiąże wiedzę optymalizacyjną. Wymagane wyrównanie musi być poprawną potęgą dwójki, a liczba elementów nadal musi mieścić się w rzeczywistym żyjącym zakresie.

**Pułapka:** Wyrównana początkowa tablica nie gwarantuje tego samego wyrównania dla dowolnego podzakresu. Przesunięcie o jeden float zwykle psuje obietnicę 32 bajtów. Fałszywe założenie jest UB również wtedy, gdy testowy procesor toleruje niewyrównany dostęp bez widocznej awarii.

**Dalej:** [Wektoryzacja i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

### 123. `std::unreachable` — C++23

Funkcja informuje kompilator, że dana ścieżka jest logicznie niemożliwa. Jej osiągnięcie stanowi undefined behavior.

```cpp
#include <utility>

enum class State { idle, running };

const char* name(State state) {
    switch (state) {
        case State::idle: return "idle";
        case State::running: return "running";
    }
    std::unreachable();
}
```

**Zastosowanie:** optymalizacja wyczerpujących przełączeń, gdy inwariant jest rzeczywiście udowodniony.

**Dlaczego i jak:** Unreachable jest deklaracją niemożliwości konkretnej ścieżki dla poprawnego programu, a nie funkcją raportującą błąd. Kompilator może na tej podstawie uprościć przepływ i zrezygnować z kodu odzyskiwania. Umieszcza się ją dopiero za wyczerpującą analizą stanów gwarantowanych przez kontrakt. Dla danych zewnętrznych walidacja musi nastąpić wcześniej. Jeśli brakujący przypadek może realnie wystąpić, odpowiednia jest jawna porażka, wyjątek lub zakończenie procesu o określonym zachowaniu.

**Pułapka:** Enum class może zawierać wartość nieodpowiadającą żadnemu nazwanemu enumeratorowi, na przykład po legalnej konwersji liczby w dziedzinie typu bazowego. Dwa case nie dowodzą więc, że każde możliwe wejście State zostało obsłużone. Wymagany jest rzeczywisty inwariant argumentu.

**Dalej:** [Undefined behavior](zaawansowane/01_undefined_behavior_i_model_maszyny.md)

### 124. `[[likely]]` i `[[unlikely]]`

Atrybuty przekazują heurystyczną informację o prawdopodobieństwie gałęzi. Nie zastępują profilowania.

```cpp
int process(int status) {
    if (status == 0) [[likely]] {
        return 1;
    }
    if (status < 0) [[unlikely]] {
        return -1;
    }
    return 0;
}
```

**Zastosowanie:** gorące ścieżki parserów i rzadkie przypadki błędów potwierdzone pomiarem.

**Dlaczego i jak:** Atrybuty pozwalają przekazać wskazówkę dotyczącą częstotliwości wykonania konkretnej instrukcji lub etykiety. Implementacja może wykorzystać ją do rozmieszczenia bloków kodu i innych heurystyk, ale nie zmienia ona poprawności ani dopuszczalnych wyników programu. Nie daje też gwarancji określonej instrukcji procesora. Najlepsze uzasadnienie pochodzi z reprezentatywnego profilu i stabilnej własności obciążenia. PGO potrafi dostarczyć bardziej szczegółową informację niż ręczne oznaczenie pojedynczej gałęzi danego programu.

**Pułapka:** Oznaczenie gałęzi jako unlikely nie pozwala pominąć jej testowania lub obsługi błędów. Jeśli rzeczywiste obciążenie się zmieni, wskazówka może pogorszyć układ gorącego kodu. Porównuj cały scenariusz przed i po zmianie, a nie sam wygląd asemblera.

**Dalej:** [Wektoryzacja i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

### 125. Scope guards: `scope_exit` — Library Fundamentals TS v3

Guard wykonuje callback przy każdym wyjściu z zakresu, bez potrzeby tworzenia osobnej klasy RAII.

> **Library Fundamentals TS v3, poza ISO C++23 i poza lokalną weryfikacją.** Wymagane `<experimental/scope>` oraz `std::experimental::scope_exit`, opisane w [N4948](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/n4948.html). Brak tej funkcji nie oznacza niepełnego wsparcia standardu C++23.

```cpp,notest
#include <experimental/scope> // Library Fundamentals TS v3; nie ISO C++23

void transaction() {
    bool committed = false;
    auto rollback = std::experimental::scope_exit([&] {
        if (!committed) { /* rollback */ }
    });

    // operacje
    committed = true;
}
```

**Zastosowanie:** rollback, przywracanie flag i sprzątanie złożonego kodu proceduralnego.

**Dlaczego i jak:** Scope guard wiąże funkcję sprzątającą z czasem życia nazwanego obiektu. Callback wykonuje się przy wyjściu normalnym, return i rozwijaniu stosu, jeśli strażnik nadal jest aktywny. Pozwala przywrócić flagę lub wykonać rollback bez definiowania oddzielnej klasy dla jednego miejsca. W odniesieniu do C++23 pokazany mechanizm pochodzi jednak z Library Fundamentals TS v3: właściwe nazwy to experimental/scope i std::experimental::scope_exit. Nie należy przedstawiać go jako standardowej biblioteki ISO C++23.

**Pułapka:** Strażnik musi żyć do właściwego końca zakresu i nie może przechwytywać referencji do wcześniej zniszczonych danych. Callback sprzątający powinien nie wypuszczać wyjątku, zwłaszcza podczas unwinding. Tymczasowy strażnik bez nazwy wykona cleanup już na końcu instrukcji.

**Dalej:** [Zasoby i zarządzanie pamięcią](zaawansowane/04_allocatory_pmr_i_new_delete.md); [Library Fundamentals TS v3: scope guards](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/n4948.html#scopeguard)

### 126. Adaptacja C API przez `out_ptr` i `inout_ptr` — C++23

Adapter umożliwia funkcji C zapisującej `T**` bezpieczne ustawienie smart pointera.

```cpp
#include <memory>

struct Resource;
extern "C" int create_resource(Resource** output);
extern "C" void destroy_resource(Resource* resource);

using ResourcePtr = std::unique_ptr<Resource, decltype(&destroy_resource)>;

ResourcePtr create() {
    ResourcePtr resource{nullptr, destroy_resource};
    if (create_resource(std::out_ptr(resource)) != 0) return {nullptr, destroy_resource};
    return resource;
}
```

**Zastosowanie:** bezpieczne przejmowanie ownershipu z legacy C API.

**Dlaczego i jak:** Out_ptr tworzy krótkotrwały adapter, który udostępnia funkcji C adres surowego wskaźnika i po zakończeniu wywołania przekazuje rezultat do smart pointera. Odpowiedni deleter określa sposób zwolnienia zasobu zgodny z obcym API. Inout_ptr obsługuje inny kontrakt: istniejący zasób może być przyjęty, zwolniony lub zastąpiony przez funkcję C. To rozróżnienie dotyczy własności, a nie wyłącznie składni T**. Adapter nie interpretuje automatycznie liczbowego kodu sukcesu funkcji.

**Pułapka:** Sprawdź, co C API zapisuje do output przy porażce i kto posiada stary zasób. Jeśli funkcja zostawia nieprawidłowy wskaźnik albo zwalnia go wbrew zakładanemu kontraktowi, adapter nie naprawi protokołu. Deleter musi odpowiadać właściwemu sposobowi alokacji.

**Dalej:** [Zasoby i zarządzanie pamięcią](zaawansowane/04_allocatory_pmr_i_new_delete.md)

### 127. Transparent comparator i heterogeniczne wyszukiwanie

Comparator z `is_transparent` pozwala wyszukać `std::string` przez `string_view` bez tworzenia tymczasowego klucza.

```cpp
#include <map>
#include <string>
#include <string_view>

std::map<std::string, int, std::less<>> users{{"alice", 1}};
std::string_view key = "alice";
auto iterator = users.find(key);
```

**Zastosowanie:** ograniczenie alokacji w często odpytywanych mapach.

**Dlaczego i jak:** Transparentny komparator udostępnia przeciążenia wyszukiwania przyjmujące typ zapytania odmienny od przechowywanego klucza. Less<void>, zapisywany jako less<>, może porównywać string i string_view bez obowiązkowego tworzenia nowego string. Oszczędność dotyczy konstrukcji klucza tymczasowego, nie samego kosztu porównania znaków. Relacja nadal musi być spójna i spełniać wymagany porządek dla wszystkich obsługiwanych kombinacji argumentów. Widok zapytania jest potrzebny tylko przez czas wykonywania synchronicznego wyszukiwania.

**Pułapka:** Samo zadeklarowanie is_transparent nie dowodzi, że porównania mieszanych typów są dostępne i zgodne. Dla unordered wymagane są odpowiednie transparentne hash i equality, a operacje heterogeniczne dodawano w różnych wersjach standardu. Sprawdzaj konkretną funkcję, nie tylko nazwę kontenera.

**Dalej:** [ADL i ukryte friend](zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)

### 128. Node handles: `extract` i `merge`

Node handle przenosi węzeł associative container bez kopiowania wartości i pozwala zmienić klucz poza kontenerem.

```cpp
#include <map>
#include <string>

void migrate_node() {
    std::map<std::string, int> source{{"old", 42}};
    std::map<std::string, int> destination;

    auto node = source.extract("old");
    node.key() = "new";
    destination.insert(std::move(node));
}
```

**Zastosowanie:** reorganizacja map i migracja elementów bez dodatkowych alokacji.

**Dlaczego i jak:** Extract oddziela węzeł od kontenera, pozostawiając uchwyt posiadający jego element i zasoby. Poza mapą klucz można legalnie zmienić, bo nie uczestniczy chwilowo w jej uporządkowaniu. Ponowne insert może przekazać węzeł do zgodnego kontenera bez kopiowania samej wartości. Merge próbuje przenieść wszystkie dopuszczalne elementy, lecz przy konflikcie unikalnego klucza pozostawia odpowiedni element w źródle. Model wymaga zgodności allocatorów i innych warunków wskazanego przeciążenia.

**Pułapka:** Po extract brakującego klucza uchwyt jest pusty i nie wolno od razu użyć key. Przy nieudanym insert wynik może zawierać nieprzekazany węzeł; porzucenie wyniku niszczy go. Nie zakładaj też, że każda dawna referencja jest legalna podczas posiadania przez node handle.

**Dalej:** [Zasoby i zarządzanie pamięcią](zaawansowane/04_allocatory_pmr_i_new_delete.md)

### 129. Płaskie kontenery `flat_map` i `flat_set` — C++23

Flat containers przechowują posortowane klucze i wartości w sekwencyjnych kontenerach, poprawiając locality kosztem droższego insertu w środku.

```cpp
#include <flat_map>
#include <string>

std::flat_map<int, std::string> labels{
    {1, "idle"},
    {2, "running"},
};

auto value = labels.at(2);
```

**Zastosowanie:** małe i średnie mapy często odczytywane, rzadko modyfikowane.

**Dlaczego i jak:** Flat_map jest adapterem nad sekwencjami kluczy i wartości, domyślnie osobnymi wektorami. Zachowuje uporządkowanie kluczy i zgodność odpowiadających sobie pozycji. Wyszukiwanie korzysta z uporządkowanego zakresu, a przeglądanie ma dobrą lokalność pamięci bez węzła alokowanego dla każdego elementu. Wstawienie w środku może wymagać przesunięcia wielu wartości i realokacji. Korzystny profil to dane przygotowywane zbiorczo i potem wielokrotnie odczytywane, z jasno określonym okresem zmian.

**Pułapka:** Iterator flat_map nie musi zwracać zwykłej referencji do trwałej pair przechowywanej w jednym buforze. Nie przenoś założeń mapy węzłowej o stabilności adresów. Tag sorted_unique wymaga naprawdę uporządkowanych, unikalnych danych; nie jest poleceniem automatycznej walidacji wejścia.

**Dalej:** [Układ i właściwości typów](zaawansowane/03_layout_alignment_padding_i_triviality.md)

### 130. Kontrola `unordered_map`

`reserve` i `max_load_factor` ograniczają rehashing, a własny hash może obsługiwać klucz domenowy.

```cpp
#include <cstddef>
#include <functional>
#include <unordered_map>

struct SessionId { unsigned value; friend bool operator==(SessionId, SessionId) = default; };
struct SessionHash {
    std::size_t operator()(SessionId id) const noexcept {
        return std::hash<unsigned>{}(id.value);
    }
};

void prepare_sessions() {
    std::unordered_map<SessionId, int, SessionHash> sessions;
    sessions.max_load_factor(0.75f);
    sessions.reserve(1'000);
}
```

**Zastosowanie:** przewidywalniejszy koszt budowania dużych hash maps.

**Dlaczego i jak:** Max_load_factor określa cel zapełnienia, a reserve wybiera liczbę kubełków potrzebną dla planowanej liczby elementów przy tym ustawieniu. Warto ustawić limit przed rezerwacją, aby kalkulacja odpowiadała rzeczywistemu protokołowi budowania tabeli. Własny hash wiąże klucz domenowy z mechanizmem kubełków, a equality rozstrzyga rzeczywistą równoważność po ewentualnej kolizji. Żadna dobra rezerwacja nie zastąpi odpowiedniego rozkładu hash dla danych charakterystycznych dla aplikacji i jej modelu zagrożeń.

**Pułapka:** Reserve nie gwarantuje konkretnej liczby kubełków ani porządku iteracji. Rehash unieważnia iteratory, choć referencje i wskaźniki do zachowanych elementów pozostają ważne. Hash nie jest trwałym identyfikatorem ani kryptograficznym zabezpieczeniem przed celowo dobranymi kolizjami na wejściu.

**Dalej:** [Wektoryzacja i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

### 131. Gwarancje wyjątków

Silna gwarancja oznacza, że nieudana operacja nie zmienia obserwowalnego stanu. Copy-and-swap naturalnie ją zapewnia.

```cpp
#include <utility>
#include <vector>

class Values {
    std::vector<int> data_;
public:
    Values& operator=(const Values& other) {
        Values copy(other);       // może rzucić; `*this` bez zmian
        data_.swap(copy.data_);   // noexcept
        return *this;
    }
};
```

**Zastosowanie:** API odporne na częściowo wykonane aktualizacje.

**Dlaczego i jak:** Copy-and-swap rozdziela przygotowanie nowego stanu od jego zatwierdzenia. Jeśli konstrukcja copy rzuci, oryginał pozostaje niezmieniony. Jeśli wymiana nie może rzucić, po jej zakończeniu stary stan należy do obiektu tymczasowego i jest sprzątany przez destruktor. Silna gwarancja dotyczy określonego obserwowalnego stanu, a nie wszystkich skutków ubocznych otoczenia. W przykładzie domyślny allocator wektora int pozwala łatwo uzasadnić niezgłaszający swap i poprawne usunięcie starej zawartości.

**Pułapka:** Copy-and-swap nie jest uniwersalnym dowodem, jeśli swap własnego typu rzuca albo kopia wykonuje nieodwracalne efekty zewnętrzne. Może też być kosztowniejsza od wyspecjalizowanego przypisania wykorzystującego istniejącą pojemność. Najpierw określ gwarancję, potem oceniaj potrzebne kopiowanie.

**Dalej:** [Zasoby i zarządzanie pamięcią](zaawansowane/04_allocatory_pmr_i_new_delete.md)

### 132. Warunkowy `noexcept`

Specyfikacja może zależeć od właściwości operacji wykonywanej przez template.

```cpp
#include <type_traits>
#include <utility>

template<class T>
void relocate(T& destination, T& source)
    noexcept(std::is_nothrow_move_assignable_v<T>)
{
    destination = std::move(source);
}

static_assert(noexcept(relocate(std::declval<int&>(), std::declval<int&>())));
```

**Zastosowanie:** zachowanie gwarancji wyjątków w generycznych kontenerach i algorytmach.

**Dlaczego i jak:** Specyfikacja noexcept jest częścią deklarowanego kontraktu funkcji i może zależeć od podstawionej operacji typu T. Trait w przykładzie bada przypisanie przenoszące, a nie konstruktor przenoszący; są to różne właściwości. Operator noexcept użyty w static_assert nie wykonuje relocate, tylko ocenia potencjalne zgłaszanie wyrażenia. Dzięki temu opakowanie może zachować informację potrzebną innym algorytmom, które dobierają strategię kopiowania lub przenoszenia na podstawie gwarancji dostępnych operacji.

**Pułapka:** Jeżeli do ciała relocate dodasz logowanie lub inną operację mogącą rzucić, sam trait T przestanie opisywać cały kontrakt. Wyjątek opuszczający funkcję z noexcept(true) wywoła terminate, zamiast automatycznie zostać obsłużony albo zamieniony w kod błędu.

**Dalej:** [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)

### 133. Transport wyjątku przez `exception_ptr`

Wyjątek można przechwycić w jednym wątku i ponownie rzucić w innym.

```cpp
#include <exception>

std::exception_ptr failure;

void worker() {
    try {
        throw 42;
    } catch (...) {
        failure = std::current_exception();
    }
}

void rethrow_if_failed() {
    if (failure) std::rethrow_exception(failure);
}
```

**Zastosowanie:** thread pools, futures i agregowanie błędów z zadań równoległych.

**Dlaczego i jak:** Current_exception przechowuje odwołanie do aktualnie obsługiwanego wyjątku, a rethrow_exception później ponownie przekazuje go do mechanizmu handlerów. Sam exception_ptr zarządza wymaganym czasem życia informacji o wyjątku, dzięki czemu nie trzeba zachowywać wiszącej referencji z catch. Transport między wątkami wymaga jednak kanału publikacji: join, promise/future albo mutex mogą ustanowić właściwy porządek. Wyjątek nie przeskakuje automatycznie ze stosu pracownika do handlera otaczającego utworzenie wątku.

**Pułapka:** Globalna zmienna failure z przykładu nie może być równocześnie przypisywana i odczytywana bez synchronizacji. Bezpieczny scenariusz to zapis w jedynym pracowniku, join, a potem rethrow_if_failed. Samo użycie exception_ptr nie czyni wspólnej zmiennej atomową ani odporną na data race.

**Dalej:** [Synchronizacja i model pamięci](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)

### 134. Własna domena `std::error_code`

`error_category` wiąże lekki kod liczbowy z komunikatem i porównywaniem warunków błędu.

```cpp
#include <string>
#include <system_error>

enum class SdrErrc { disconnected = 1, overflow };

class SdrCategory final : public std::error_category {
public:
    const char* name() const noexcept override { return "sdr"; }
    std::string message(int value) const override {
        switch (static_cast<SdrErrc>(value)) {
            case SdrErrc::disconnected: return "disconnected";
            case SdrErrc::overflow: return "overflow";
        }
        return "unknown sdr error";
    }
};

const std::error_category& sdr_category() {
    static SdrCategory category;
    return category;
}
```

**Zastosowanie:** integracja błędów systemowych i bibliotek C bez alokacji w samym kodzie błędu.

**Dlaczego i jak:** Kategoria nadaje znaczenie wartościom liczbowym i jest częścią tożsamości error_code. Dwa identyczne numery z różnych kategorii mogą oznaczać inne porażki. Funkcja zwracająca statyczny obiekt kategorii zapewnia odpowiedni czas życia i spójną tożsamość podczas zwykłego użycia biblioteki. Pełne API zwykle dodaje make_error_code dla enuma, a opcjonalnie dozwoloną specjalizację is_error_code_enum. Mapowanie do ogólnych error_condition pozwala klientom porównywać błędy z bardziej przenośnymi klasami przyczyn.

**Pułapka:** Message nie powinno klasyfikować każdej nieznanej liczby jako overflow. Kody mogą pochodzić z przyszłej wersji lub błędnego wejścia, więc zachowaj gałąź nieznanego błędu. Sam error_code jest lekki, lecz wygenerowanie string w message może alokować i rzucić.

**Dalej:** [Interoperacyjność i ABI](zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)

### 135. Własny `std::formatter`

Specjalizacja formattera integruje typ domenowy z `std::format` i `std::print`.

```cpp
#include <format>

struct Frequency { double hertz; };

template<>
struct std::formatter<Frequency> : std::formatter<double> {
    auto format(Frequency value, format_context& context) const {
        return std::formatter<double>::format(value.hertz / 1'000'000.0, context);
    }
};

auto text = std::format("{} MHz", Frequency{150'000'000.0});
```

**Zastosowanie:** spójne logowanie i diagnostyka value objects.

**Dlaczego i jak:** Formatter rozdziela parsowanie specyfikacji formatu od zapisania konkretnej wartości. Dziedziczenie po formatter<double> ponownie wykorzystuje obsługę takich parametrów jak precyzja, a własne format przelicza jednostkę domenową na MHz. Specjalizacja dotyczy typu zdefiniowanego przez program, zgodnie z przewidzianym punktem rozszerzenia biblioteki. Format powinno zapisać wynik przez kontekst i zwrócić odpowiednią pozycję wyjściową. Typ domenowy pozostaje niezależny od string tworzonego przez pojedyncze wywołanie std::format.

**Pułapka:** Pokazany formatter zawsze przelicza na MHz, ale sam nie dopisuje jednostki; klient robi to w szablonie formatu. Jeśli nazwa typu sugeruje herce, udokumentuj tę decyzję. Własne parse musi też przestrzegać składni i zgłaszać błędne formaty w odpowiedni sposób.

**Dalej:** [Type erasure i ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

### 136. `std::spanstream` — C++23

Span stream wykonuje formatowane I/O na zewnętrznym buforze o stałej pojemności.

> **C++23; poza lokalną weryfikacją Apple Clang 17/libc++.** Wymagany nagłówek `<spanstream>` i implementacja strumieni opartych na span; lokalna konfiguracja nie dostarcza tego nagłówka.

```cpp,notest
#include <array>
#include <spanstream>
#include <stdexcept>
#include <string>
#include <string_view>

std::string describe_sample_rate() {
    std::array<char, 128> buffer{};
    std::ospanstream stream{buffer};
    stream << "sample-rate=" << 20'000'000;

    if (!stream) throw std::runtime_error{"output buffer too small"};
    auto written = stream.span();
    return {written.data(), written.size()};
}
```

**Zastosowanie:** formatowanie do zewnętrznego bufora o stałej pojemności; pozostałe operacje funkcji nadal mogą alokować.

**Dlaczego i jak:** Spanstream korzysta z zewnętrznego ciągłego bufora i oferuje interfejs strumienia bez automatycznego powiększania tego bufora. Ospanstream::span zwraca zapisany zakres, więc można wykorzystać dokładną długość bez szukania terminatora. Właściciel pamięci musi żyć przez cały dostęp strumienia i uzyskanych widoków. Konwersja tego zakresu do string w przykładzie tworzy już nowego właściciela i może alokować; brak wzrostu bufora strumienia nie oznacza braku alokacji całej funkcji.

**Pułapka:** Po wyczerpaniu miejsca strumień sygnalizuje błąd stanu; zignorowanie go może zwrócić obcięty opis jako rzekomy sukces. Zapis nie obiecuje końcowego zera. Sprawdzaj stream przed użyciem wyniku i przekazuj odbiorcy długość albo jawnie utworzony string.

**Dalej:** [Zasoby i zarządzanie pamięcią](zaawansowane/04_allocatory_pmr_i_new_delete.md)

### 137. Atomowe wyjście tekstowe przez `osyncstream`

Każdy wrapper buforuje tekst lokalnie i publikuje go jako nieprzeplatający się fragment.

> **C++20 i późniejsze; poza lokalną weryfikacją Apple Clang 17/libc++.** Wymagana implementacja `std::osyncstream` z `<syncstream>`; lokalny nagłówek nie udostępnia używanego typu.

```cpp,notest
#include <iostream>
#include <syncstream>
#include <thread>

void log_from_worker(int id) {
    std::osyncstream{std::cout} << "worker=" << id << " finished\n";
}
```

**Zastosowanie:** czytelne logi z wielu wątków bez osobnego mutexa wokół każdej sekwencji `<<`.

**Dlaczego i jak:** Osyncstream gromadzi kolejne części komunikatu w swoim buforze, a następnie emituje je jako nieprzeplatany fragment do wspólnego bufora docelowego. Dzięki temu kilka operatorów strumieniowych tworzy logiczny komunikat, którego części nie mieszają się z komunikatem innego wrappera używającego tego samego celu. Publikacja następuje między innymi podczas destrukcji wrappera. To porządek na poziomie emitowanych fragmentów, a nie deterministyczna kolejność wszystkich wątków lub trwała transakcja systemu plików.

**Pułapka:** Gwarancja wymaga zgodnego korzystania z mechanizmu przez uczestniczące zapisy. Bezpośrednie cout wykonywane równolegle może przeplatać tekst z wrapperami. Osyncstream nie naprawia też data race podczas przygotowywania argumentów komunikatu ani nie gwarantuje braku alokacji w lokalnym buforze.

**Dalej:** [Synchronizacja i model pamięci](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)

### 138. Kalendarze w `std::chrono`

C++20 reprezentuje daty typami `year`, `month`, `day` i sprawdza ich poprawność.

```cpp
#include <chrono>

using namespace std::chrono;

constexpr year_month_day release = 2026y / August / 19d;
static_assert(release.ok());

constexpr sys_days release_day = release;
constexpr weekday week_day{release_day};
```

**Zastosowanie:** bezpieczne obliczenia kalendarzowe bez ręcznej arytmetyki timestampów.

**Dlaczego i jak:** Year_month_day opisuje datę kalendarzową, a ok sprawdza, czy jej pola razem tworzą poprawny dzień. Konstrukcja sama może przechowywać niepoprawne połączenie, na przykład trzydziesty pierwszy lutego. Sys_days reprezentuje punkt na osi dni zegara systemowego i pozwala wykonywać arytmetykę dni oraz wyznaczać weekday. Dodawanie miesięcy jest inną operacją niż dodawanie stałej liczby dni, ponieważ miesiące mają różne długości i trzeba określić zachowanie dla nieistniejącego dnia docelowego.

**Pułapka:** Nie utożsamiaj poprawności poszczególnych pól z poprawnością całej daty. Miesiąc luty i dzień trzydzieści jeden są osobno reprezentowalne, ale ich połączenie nie jest legalną datą. Po operacjach kalendarzowych sprawdzaj wynik i jawnie wybieraj politykę korekty.

**Dalej:** [Stała ewaluacja](zaawansowane/09_constexpr_consteval_i_compile_time.md)

### 139. Strefy czasowe i `zoned_time`

Baza IANA mapuje czas systemowy na lokalny z uwzględnieniem historycznych zmian i DST. Dostępność zależy od libstdc++/libc++.

> **C++20 i późniejsze; poza lokalną weryfikacją Apple Clang 17/libc++.** Wymagana implementacja stref czasowych chrono, `std::chrono::zoned_time` oraz dostępna baza stref. Lokalna biblioteka nie udostępnia użytego typu.

```cpp,notest
#include <chrono>

auto now = std::chrono::system_clock::now();
auto warsaw = std::chrono::zoned_time{"Europe/Warsaw", now};
auto local = warsaw.get_local_time();
```

**Zastosowanie:** harmonogramy i prezentacja czasu użytkownika bez stałych przesunięć UTC.

**Dlaczego i jak:** Zoned_time wiąże punkt czasowy z regułami wskazanej strefy. Konwersja z czasu systemowego do lokalnego jest jednoznaczna, ale odwrotna droga może napotkać godzinę nieistniejącą lub występującą dwukrotnie przy zmianie czasu. Wtedy potrzebna jest jawna decyzja wybierająca interpretację albo obsługa wyjątku. Nazwa IANA opisuje zestaw historycznych reguł, a nie stałą liczbę godzin przesunięcia. Aplikacja powinna także ustalić wersję i dostępność bazy danych na maszynie wykonującej obliczenia.

**Pułapka:** Zapisanie lokalnej godziny bez strefy i polityki niejednoznaczności może nie wystarczyć do odtworzenia chwili. Nie dodawaj na stałe jednej lub dwóch godzin do UTC dla Warszawy. Przepisy i baza stref mogą się zmieniać niezależnie od binarnej wersji programu.

**Dalej:** [Interoperacyjność i ABI](zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)

### 140. Rekurencyjne przechodzenie filesystemu

Iterator katalogu jest range'em, a `error_code` pozwala obsłużyć błędy bez wyjątków.

```cpp
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

std::error_code scan(const fs::path& root) {
    std::error_code error;
    fs::recursive_directory_iterator it{root, error}, end;
    if (error) return error;
    while (it != end) {
        const bool regular = it->is_regular_file(error);
        if (error) return error;
        if (regular) { /* process */ }
        it.increment(error);
        if (error) return error;
    }
    return {};
}
```

**Zastosowanie:** indeksowanie plików z kontrolą błędów uprawnień i usunięć w trakcie iteracji.

**Dlaczego i jak:** Recursive_directory_iterator przechodzi po drzewie katalogów w modelu pojedynczego przejścia. Tworzenie iteratora, pobieranie metadanych i przesuwanie pozycji są oddzielnymi operacjami mogącymi zawieść. Przeciążenia z error_code pozwalają jawnie sprawdzić błąd każdej z nich, zamiast zakładać, że pętla na pewno dotrze do następnego ciała. Kolejność odwiedzania nie jest stabilnym kontraktem. W trakcie skanowania pliki mogą zniknąć lub zostać podmienione, więc wynik jest obserwacją zmiennego systemu, nie niezmiennym snapshotem.

**Pułapka:** Sprawdzenie error dopiero wewnątrz for może zgubić błąd konstrukcji lub increment, jeśli iterator od razu stanie się końcowy. Sprawdź go po każdej operacji. Włączenie podążania za dowiązaniami do katalogów wymaga także świadomego rozwiązania ryzyka cykli.

**Dalej:** [Interoperacyjność i ABI](zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)

### 141. Operacje bitowe z `<bit>`

Standard dostarcza rotacje, zliczanie bitów oraz potęgi dwójki bez ręcznych, podatnych na UB trików.

```cpp
#include <bit>
#include <cstdint>

constexpr std::uint32_t mask = 0b1011'0000u;
static_assert(std::popcount(mask) == 3);
static_assert(std::rotl(std::uint32_t{1}, 4) == 16);
static_assert(std::bit_ceil(std::uint32_t{17}) == 32);
```

**Zastosowanie:** protokoły, hash functions i algorytmy niskopoziomowe.

**Dlaczego i jak:** Funkcje z bit opisują operacje na reprezentacji liczb bez ręcznego odtwarzania przesunięć i masek. Popcount liczy ustawione bity, rotacje zawijają przesuwane bity, a bit_ceil wyznacza najmniejszą reprezentowalną potęgę dwójki nie mniejszą od argumentu przy spełnionych wymaganiach. Większość tych interfejsów celowo przyjmuje odpowiednie typy bez znaku. Kompilator może wybrać instrukcję sprzętową albo przenośną implementację, więc zapis intencji nie wymaga ręcznej zależności od konkretnego ISA.

**Pułapka:** Bit_ceil ma warunek reprezentowalności wyniku; dla zbyt dużej wartości nie jest bezpieczną funkcją zwracającą automatycznie zero. Podobnie wynik potęgi dwójki używany jako rozmiar alokacji wymaga dalszej kontroli mnożenia przez rozmiar elementu i limitu zasobów.

**Dalej:** [Wektoryzacja i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

### 142. `transform_reduce`

Algorytm łączy mapowanie i redukcję i może korzystać z execution policy.

```cpp
#include <functional>
#include <numeric>
#include <stdexcept>
#include <vector>

double dot_product(const std::vector<double>& left, const std::vector<double>& right) {
    if (left.size() != right.size())
        throw std::invalid_argument{"different vector sizes"};
    return std::transform_reduce(
        left.begin(), left.end(), right.begin(), 0.0,
        std::plus{}, std::multiplies{}
    );
}
```

**Zastosowanie:** iloczyny skalarne, metryki i obliczenia map-reduce.

**Dlaczego i jak:** Transform_reduce może połączyć obliczenie iloczynów par z redukcją, ograniczając potrzebę kolekcji pośredniej. Wersja dwóch zakresów w przykładzie zna koniec pierwszego, ale dostaje tylko początek drugiego; poprawność wymaga wystarczającej liczby elementów po prawej. Redukcja może inaczej grupować i porządkować działania także bez jawnej polityki równoległej. To umożliwia optymalizacje, ale oznacza inny kontrakt niż sekwencyjny fold wykonywany dokładnie od lewej strony wejścia.

**Pułapka:** Dodawanie double nie jest łączne w arytmetyce maszyny, więc wynik może różnić się od zwykłej pętli. Krótszy prawy wektor dodatkowo narusza zakres. Sprawdzaj zgodność rozmiarów i określ tolerancję numeryczną, zanim porównasz wydajność alternatywnych implementacji.

**Dalej:** [Wektoryzacja i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

### 143. Własny tuple-like type i structured bindings

Implementacja `get` oraz specjalizacje `tuple_size` i `tuple_element` integrują typ ze structured bindings.

```cpp
#include <cstddef>
#include <tuple>

struct Point { double x, y; };

template<std::size_t I>
double& get(Point& point) {
    static_assert(I < 2);
    if constexpr (I == 0) return point.x;
    else return point.y;
}

namespace std {
    template<> struct tuple_size<Point> : integral_constant<size_t, 2> {};
    template<size_t I> struct tuple_element<I, Point> {
        static_assert(I < 2);
        using type = double;
    };
}
```

**Zastosowanie:** ergonomiczne destructuring własnych rekordów i wyników algorytmów.

**Dlaczego i jak:** Protokół structured bindings wybiera liczbę elementów z tuple_size, ich deklarowane typy z tuple_element i dostęp przez właściwe get. Funkcja get umieszczona obok typu może zostać znaleziona przez ADL. Pokazany wariant obsługuje tylko mutowalne lvalue, więc wystarcza dla wiązania referencyjnego z istniejącym Point. Pełny typ użytkowy powinien świadomie dostarczyć odmiany const oraz rvalue, zachowując odpowiednie referencje i kategorie wartości. To protokół destrukturyzacji, odrębny od każdego standardowego użycia pojęcia tuple-like.

**Pułapka:** Zwykłe `auto [x, y] = point` używa ukrytego obiektu i może potrzebować get dla rvalue; sam get(Point&) nie wystarcza. Dodaj także kontrolę I < 2, aby błędny indeks nie wskazywał po cichu pola y w każdej sytuacji.

**Dalej:** [ADL i ukryte friend](zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)

### 144. Designated initializers

Agregat można inicjalizować nazwanymi polami w kolejności deklaracji.

```cpp
struct DeviceConfig {
    double sample_rate;
    double center_frequency;
    double gain;
};

DeviceConfig config{
    .sample_rate = 20'000'000.0,
    .center_frequency = 150'000'000.0,
    .gain = 30.0,
};
```

**Zastosowanie:** czytelne obiekty konfiguracyjne bez buildera dla prostych agregatów.

**Dlaczego i jak:** Designatory odnoszą się do bezpośrednich niestatycznych pól agregatu i pozwalają powiązać wartość z nazwą już w miejscu inicjalizacji. Kolejność musi odpowiadać deklaracji pól, choć niektóre pola można pominąć. Pominięte elementy korzystają z domyślnych inicjalizatorów pól albo właściwej inicjalizacji wynikającej z reguł agregatu. Interfejs jest dzięki temu czytelny dla prostych konfiguracji. Jeśli typ ma wymuszać złożone inwarianty przez konstruktor, rezygnacja z agregatu może być celową i korzystną decyzją.

**Pułapka:** Składnia C++ nie jest pełnym odpowiednikiem designated initializers z C. Nie można dowolnie zmieniać kolejności ani mieszać wskazanych i pozycyjnych pól w tej samej liście. Dodanie konstruktora może pozbawić typ statusu agregatu i zmienić legalność dotychczasowych inicjalizacji.

**Dalej:** [Układ i właściwości typów](zaawansowane/03_layout_alignment_padding_i_triviality.md)

### 145. Dziedziczenie wirtualne

Virtual base gwarantuje jeden wspólny podobiekt bazy w strukturze diamentowej.

```cpp
struct Device { virtual ~Device() = default; int id{}; };
struct Receiver : virtual Device {};
struct Transmitter : virtual Device {};
struct Transceiver : Receiver, Transmitter {};

void configure(Transceiver& radio) {
    radio.id = 42; // jeden wspólny Device
}
```

**Zastosowanie:** rzadkie hierarchie wymagające współdzielonej bazy. Preferuj kompozycję, jeśli model nie wymaga takiej semantyki.

**Dlaczego i jak:** Dziedziczenie wirtualne sprawia, że różne ścieżki diamentu odwołują się do jednego wspólnego podobiektu bazy w najbardziej pochodnym obiekcie. To właśnie najbardziej pochodny konstruktor odpowiada za inicjalizację wirtualnej bazy, nawet jeśli pośrednie klasy mają własne inicjalizatory dla samodzielnych obiektów. Konwersje wskaźników mogą wymagać dostosowania adresu według układu konkretnego obiektu. Współdzielenie Device rozwiązuje duplikację stanu, ale nie usuwa wszystkich niejednoznaczności metod w pozostałych częściach hierarchii.

**Pułapka:** Słowo virtual przy dziedziczeniu nie ma tego samego znaczenia co virtual przy metodzie. Nie dodawaj wirtualnych baz wyłącznie dla usunięcia komunikatu o niejednoznaczności: zmieniają model stanu, inicjalizacji i reprezentację obiektu. Uzasadnij wspólną tożsamość domenową bazy.

**Dalej:** [Układ i właściwości typów](zaawansowane/03_layout_alignment_padding_i_triviality.md)

### 146. RTTI: `dynamic_cast` i `typeid`

RTTI umożliwia bezpieczne sprawdzenie konkretnego typu w hierarchii polimorficznej.

```cpp
#include <typeinfo>

struct Message { virtual ~Message() = default; };
struct DataMessage : Message { int value{}; };

int read(Message& message) {
    if (auto* data = dynamic_cast<DataMessage*>(&message)) return data->value;
    return 0;
}
```

**Zastosowanie:** granice pluginów i legacy hierarchie. Częste rzutowania zwykle wskazują na brakujący interfejs wirtualny.

**Dlaczego i jak:** Dynamic_cast w hierarchii polimorficznej sprawdza rzeczywisty układ i typ obiektu podczas wykonania. Odmiana wskaźnikowa zwraca null przy niedopasowaniu, a referencyjna zgłasza bad_cast. Mechanizm może obejmować zejście do pochodnej i przejście między gałęziami hierarchii przy spełnieniu reguł dostępności. Typeid dla odpowiedniej glvalue typu polimorficznego opisuje typ dynamiczny; dla innych wyrażeń często wystarcza informacja statyczna. To narzędzia obserwacji typu, a nie automatyczny model serializacji obiektów.

**Pułapka:** Wynik type_info::name jest zależny od implementacji i nie nadaje się na trwały identyfikator protokołu. RTTI może też być wyłączone opcjami toolchainu. Wielokrotne casty w każdej operacji mogą sygnalizować, że hierarchii brakuje właściwego interfejsu wirtualnego.

**Dalej:** [Type erasure i ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

### 147. Function multiversioning — rozszerzenie GCC/Clang

Kilka wersji funkcji może zostać skompilowanych dla różnych ISA, a runtime wybiera wariant zgodny z CPU.

> **Rozszerzenie GCC/Clang dla odpowiednich celów x86; poza lokalną weryfikacją ARM.** Wymagana obsługa `target_clones`, właściwego formatu binarnego i mechanizmu wyboru wariantu. Pominięcie całego kodu przez preprocesor nie stanowi walidacji rozszerzenia.

```cpp,notest
#if defined(__GNUC__) && defined(__x86_64__)
__attribute__((target_clones("avx2", "sse4.2", "default")))
float sum(const float* values, int count) {
    float result{};
    for (int i = 0; i < count; ++i) result += values[i];
    return result;
}
#endif
```

**Zastosowanie:** jedna binarka korzystająca z SIMD na nowych CPU i fallbacku na starszych.

**Dlaczego i jak:** Multiversioning kompiluje kilka implementacji funkcji i dodaje mechanizm wyboru zgodny z możliwościami procesora. Pozwala utrzymać podstawowy wariant dla starszego sprzętu oraz szybsze wersje korzystające z dodatkowych instrukcji. Sam atrybut jest rozszerzeniem konkretnego toolchainu i jego implementacja zależy także od systemu, formatu obiektów oraz linkera. Różne wersje powinny zachowywać zadeklarowaną semantykę, a testy obejmować wymuszony lub rzeczywisty wybór fallbacku, nie tylko najnowszą maszynę autora.

**Pułapka:** Makro `__GNUC__` bywa definiowane także przez Clang dla zgodności i nie dowodzi dostępności target_clones na danej platformie. Weryfikuj konkretny atrybut i środowisko. SIMD nie gwarantuje też identycznych wyników zmiennoprzecinkowych po zmianie grupowania operacji lub flag arytmetyki.

**Dalej:** [Wektoryzacja i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

### 148. Sanitizery kompilatora

ASan, UBSan i TSan instrumentują program, wykrywając klasy błędów niewidoczne dla zwykłych testów.

```bash
# Pamięć i wybrane przypadki undefined behavior
g++ -std=c++23 -O1 -g -fsanitize=address,undefined app.cpp

# Data races — uruchamiaj jako osobny wariant, nie razem z ASan
g++ -std=c++23 -O1 -g -fsanitize=thread app.cpp
```

**Zastosowanie:** CI i diagnostyka use-after-free, overflow, złego alignmentu oraz data races.

**Dlaczego i jak:** Sanitizer dodaje instrumentację w czasie kompilacji i korzysta z runtime podczas wykonania. ASan śledzi dostępność pamięci, UBSan wybrane naruszenia semantyki, a TSan konflikty dostępów i synchronizację. Aby uzyskać wartościowy wynik, trzeba uruchomić reprezentatywne testy instrumentowanego programu, nie tylko go zbudować. Raport czytaj od pierwszej przyczyny i zachowuj powiązane miejsca alokacji, zwolnienia lub drugiego dostępu. Konfiguracje muszą obejmować odpowiednie własne biblioteki, a nie jedynie plik główny.

**Pułapka:** Brak raportu nie jest dowodem braku UB ani wyścigów: narzędzie obejmuje wybrane klasy błędów i wykonane ścieżki. TSan uruchamiaj osobno od ASan. Instrumentacja zmienia harmonogram i koszty, więc nie używaj jej czasów jako pomiaru produkcyjnej wydajności.

**Dalej:** [Undefined behavior](zaawansowane/01_undefined_behavior_i_model_maszyny.md)

### 149. Link-Time Optimization i Profile-Guided Optimization

LTO optymalizuje między translation units, a PGO wykorzystuje profil rzeczywistych obciążeń.

```bash
# LTO
g++ -std=c++23 -O3 -flto app.cpp -o app

# PGO: instrumentacja → typowe obciążenie → rebuild
g++ -std=c++23 -O3 -fprofile-generate app.cpp -o app
./app workload.bin
g++ -std=c++23 -O3 -fprofile-use app.cpp -o app
```

**Zastosowanie:** optymalizacja całego programu na podstawie faktycznych hot paths.

**Dlaczego i jak:** LTO przekazuje dodatkową reprezentację programu do etapu linkowania, umożliwiając analizę i optymalizacje ponad granicami jednostek translacji. PGO dostarcza informacji o częstotliwości ścieżek z reprezentatywnego wykonania, aby kierować decyzjami optymalizatora. To niezależne mechanizmy, które można łączyć, jeśli toolchain je wspiera. Procedura PGO musi zapewnić odczyt rzeczywiście wygenerowanych danych profilu, zgodność nazw artefaktów i kontrolę diagnostyki brakujących lub niepasujących liczników. Samo dodanie flagi use nie dowodzi użycia profilu.

**Pułapka:** Przykład z inną nazwą pliku wykonywalnego przy zbieraniu i użyciu może zmienić nazwę oczekiwanego pliku profilu GCC. Zachowaj spójny układ albo jawnie skonfiguruj mapowanie profilu. Niereprezentatywne obciążenie może zoptymalizować rzadką ścieżkę kosztem właściwego zastosowania programu.

**Dalej:** [Wektoryzacja i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)

### 150. Widoczność symboli i kontrola ABI

Biblioteka współdzielona powinna domyślnie ukrywać symbole i eksportować tylko jawny interfejs.

> **Rozszerzenia ABI i narzędzi platformy; poza walidacją przenośnego ISO C++.** Atrybut visibility oraz `__declspec(dllexport)` zależą od kompilatora. Polecenie budowania pokazuje wariant biblioteki `.so`; inne systemy wymagają odpowiednich opcji i formatów.

```cpp,notest
#if defined(_WIN32)
  #define API_EXPORT __declspec(dllexport)
#else
  #define API_EXPORT __attribute__((visibility("default")))
#endif

extern "C" API_EXPORT int library_version() noexcept {
    return 1;
}
```

```bash
g++ -fPIC -fvisibility=hidden -shared library.cpp -o libexample.so
```

**Zastosowanie:** mniejsze tablice symboli, szybsze ładowanie i stabilniejsza granica ABI.

**Dlaczego i jak:** Kontrola visibility ogranicza eksportowany zestaw symboli, co zmniejsza przypadkowe zależności klientów od implementacji. Extern C wybiera językowe linkage, ale nie definiuje sam kompletnej przenośnej granicy binarnej. Stabilne ABI wymaga uzgodnienia typów, konwencji wywołań, wersjonowania, błędów i własności zasobów. Dla bibliotek z uchwytami warto dostarczać pary create/destroy z tego samego modułu. Noexcept pomaga utrzymać wyjątki wewnątrz granicy, jeśli implementacja rzeczywiście tłumaczy wszystkie możliwe porażki.

**Pułapka:** Makro z dllexport służy budowaniu biblioteki, lecz klient Windows zwykle potrzebuje odpowiedniego wariantu dllimport. Polecenie z -fPIC i .so dotyczy konkretnej rodziny środowisk, nie każdego systemu. Ukrycie symboli nie naprawia niezgodnych layoutów ani niezgodnych bibliotek runtime.

**Dalej:** [Interoperacyjność i ABI](zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)

---

## Źródła

- [N4950 — stabilny draft C++23](https://timsong-cpp.github.io/cppwp/n4950/)
- [P3850R0 — potwierdzenie zakończenia prac WG21 nad C++26 w marcu 2026](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p3850r0.pdf)
- [Clang — status funkcji języka](https://clang.llvm.org/cxx_status.html)
- [libc++ — status C++23](https://libcxx.llvm.org/Status/Cxx23.html)
- [libc++ — status C++26](https://libcxx.llvm.org/Status/Cxx26.html)
- [Standard C++ — aktualny opublikowany standard](https://isocpp.org/std/the-standard)
- [WG21 — dokumenty i working drafts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/)
- [N5046 — working draft C++ z maja 2026](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/n5046.pdf)
- [N5047 — raport edytorów working draft C++26](https://www9.open-std.org/JTC1/SC22/WG21/docs/papers/2026/n5047.html)
- [GCC — wsparcie standardów C++](https://gcc.gnu.org/projects/cxx-status.html)
- [GCC 13.3 — status libstdc++](https://gcc.gnu.org/onlinedocs/gcc-13.3.0/libstdc++/manual/status.html)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [P2300 — `std::execution`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2300r9.html)
- [P2996 — Reflection for C++26](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2025/p2996r13.html)

---

## Proponowana kolejność nauki

1. Najpierw opanuj RAII, Rule of Zero, move semantics i widoki nieposiadające — punkty 1–20.
2. Następnie przejdź od value categories i perfect forwardingu do concepts — punkty 21–45.
3. Ranges ćwicz jako leniwe pipeline'y, a coroutine zacznij od modelu `promise_type`/awaiter — punkty 46–65.
4. Przy atomikach nie kopiuj jedynie składni: udowodnij relację happens-before dla każdej pary operacji — punkty 66–82.
5. Moduły i C++26 wdrażaj dopiero po sprawdzeniu feature-test macros i wsparcia całego toolchainu.
6. Punkty 101–150 potraktuj jako warstwę produkcyjną: metaprogramowanie, ABI, allocatory, filesystem, chrono, narzędzia kompilatora i optymalizacja całego programu.

Dobrym projektem przekrojowym jest pipeline SDR: RAII dla uchwytu UHD, `span<const SampleI16>` na granicy bufora, `expected` dla błędów odbioru, ranges dla ramek, bounded queue z semaforem oraz SIMD dla korelacji próbek.

## Powiązane tematy

- [Rozdziały eksperckie](zaawansowane/README.md)
- [Zarządzanie czasem życia](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)
- [Kategorie wartości i forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)
- [Współbieżność i odzyskiwanie pamięci](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)
- [C++26: status i ograniczenia implementacji](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)
