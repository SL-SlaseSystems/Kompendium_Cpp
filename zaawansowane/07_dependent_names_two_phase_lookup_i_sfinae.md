[← Spis treści](../README.md)

# Dependent names, two-phase lookup i SFINAE

W definicji szablonu część nazw zależy od parametrów. Nazwy niezależne są wyszukiwane przy definicji, a zależne dodatkowo podczas instancjacji według reguł two-phase lookup. To zapobiega przypadkowemu uzależnieniu szablonu od deklaracji pojawiających się później.

`typename` informuje parser, że zależna kwalifikowana nazwa oznacza typ. Słowo `template` informuje, że zależna składowa jest szablonem. Brak tych disambiguators jest częstym źródłem diagnostyki.

~~~cpp
#include <cassert>
#include <vector>

template<class Container>
typename Container::value_type first_or_default(const Container& values) {
    using Value = typename Container::value_type;
    return values.empty() ? Value{} : values.front();
}

template<class T>
struct Wrapper {
    template<class U>
    static U convert(T value) { return static_cast<U>(value); }
};

template<class T>
double convert_to_double(T value) {
    return Wrapper<T>::template convert<double>(value);
}

int main() {
    assert(first_or_default(std::vector<int>{}) == 0);
    assert(convert_to_double(21) == 21.0);
}
~~~

ADL przy instancjacji może znaleźć funkcje w przestrzeniach powiązanych z zależnymi argumentami, ale zwykły lookup nie zbiera dowolnych późniejszych deklaracji. Różnice implementacji two-phase lookup były historycznym źródłem nieprzenośnego kodu, szczególnie w starszym MSVC.

SFINAE działa tylko dla niepoprawności w immediate context podstawienia. Błąd głęboko w instancjowanym ciele może być twardym błędem. Requires-expressions lepiej lokalizują badane wyrażenie i dają czytelniejszy kontrakt, choć zrozumienie dependent names nadal jest konieczne.

## Jak to działa krok po kroku

Parser odczytujący `first_or_default` nie zna konkretnego `Container`. `Container::value_type` jest nazwą zależną, więc w pokazanym miejscu `typename` rozstrzyga, że chodzi o typ. Po podstawieniu `std::vector<int>` nazwa oznacza `int`, a obie gałęzie operatora warunkowego zwracają zgodną wartość. Dla typu bez `value_type` funkcja nie spełni warunków podstawienia potrzebnych do utworzenia kandydata.

W `Wrapper<T>::template convert<double>` słowo `template` informuje parser, że znak `<` rozpoczyna listę argumentów szablonu, zamiast operatora porównania. Dopiero po podstawieniu `T` kompilator sprawdzi, czy składowa istnieje i czy wywołanie jest poprawne. Słowa `typename` i `template` nie tworzą deklaracji ani nie obiecują, że instancjacja się powiedzie; rozwiązują niejednoznaczność gramatyczną.

## Pogłębienie mechanizmu

Niezależne nazwy są wiązane przy definicji szablonu. Jeżeli szablon wywołuje `helper(0)`, późniejsze dopisanie przeciążenia `helper` przed instancjacją nie powinno dowolnie zmienić znaczenia tego wywołania. W przypadku `helper(value)` z zależnym typem argumentu reguły są bardziej złożone: lookup zachowuje kontekst definicji, a ADL może uwzględnić powiązane deklaracje. Stąd idiom funkcji dostosowującej umieszczonej w przestrzeni typu, zamiast polegania na kolejności dołączania przypadkowych nagłówków.

Składowe zależnej klasy bazowej nie są automatycznie odnajdywane przez zwykły niezależny lookup w definicji klasy pochodnej. Zapis `this->member` nadaje zależność potrzebną do późniejszego wyszukiwania, a kwalifikacja `Base<T>::member` wskazuje bazę jawnie. Nie jest to tylko wymóg „bardziej gadatliwego kompilatora”: baza może mieć specjalizacje dostarczające różne składowe, więc jej zawartość nie jest znana dla wszystkich `T`.

SFINAE oznacza, że określona niepoprawność podstawienia w bezpośrednim kontekście deklaracji usuwa kandydata. Nie osłania dowolnego kodu uruchomionego przez instancjację. Jeśli typ wyniku zależy od `typename Inner<T>::type`, a utworzenie `Inner<T>` powoduje błąd wewnątrz jego definicji, może to być błąd twardy. Tak samo `static_assert` w ciele wybranej funkcji nie staje się podstawą wyboru innego przeciążenia.

Requires-expression pozwala umieścić test bliżej badanej operacji. Zwykłe wymaganie `t.size();` sprawdza poprawność wyrażenia, compound requirement może dodatkowo badać typ wyniku i `noexcept`, a nested requirement wymaga prawdziwości constraint. Wymagania nie wykonują tych operacji runtime. Poza zależnym kontekstem niepoprawna składnia lub nazwa nadal może być zwykłym błędem programu; `requires` nie jest ogólnym mechanizmem przechwytywania diagnostyki kompilatora.

## Drugi przykład

~~~cpp
#include <cassert>
#include <cstddef>
#include <vector>

template<class T>
concept Sized = requires(const T& t) { t.size(); };

template<class T>
std::size_t count(const T&) { return 1; }

template<Sized T>
std::size_t count(const T& t) { return t.size(); }

int main() {
    assert(count(42) == 1);
    assert(count(std::vector<int>{1, 2, 3}) == 3);
}
~~~

Dla `int` wymaganie próbuje utworzyć wyrażenie `t.size()`, otrzymuje wynik niespełniony i eliminuje ograniczone przeciążenie. Nie powstaje błąd ciała, bo ciało tego kandydata nie jest instancjowane. Dla wektora obie funkcje pasują, a bardziej ograniczona wygrywa. Ten concept celowo sprawdza jedynie obecność wyrażenia; interfejs produkcyjny powinien doprecyzować konwertowalność wyniku do oczekiwanego rozmiaru, jeżeli dopuszcza nieznane typy użytkownika.

## Porównanie i decyzje

Nowe ograniczenia interfejsów zwykle zapisuj przez concepts, a SFINAE zachowuj przy utrzymywaniu starszych bibliotek lub specjalizowanych strukturach metaprogramowania. `if constexpr` wybiera implementację dopiero wewnątrz instancjowanego szablonu; nie zastępuje constraints w publicznym zbiorze przeciążeń. Dobre API odrzuca nieobsługiwany typ na granicy wywołania, dzięki czemu komunikat wskazuje naruszone wymaganie, zamiast setek błędów w ciele.

**Ćwiczenie.** Dlaczego usunięcie `this->` przed składową zależnej bazy może zmienić poprawność szablonu? **Odpowiedź:** nazwa przestaje być traktowana jako zależne odszukanie składowej i musi zostać rozstrzygnięta wcześniej. Dlaczego fallback nie ratuje błędu w ciele wybranej funkcji? Ponieważ overload resolution już się zakończyło; instancjacja ciała nie uruchamia go ponownie.

Źródła: [N4950: zależne nazwy](https://timsong-cpp.github.io/cppwp/n4950/temp.dep) oraz [dedukcja i immediate context](https://timsong-cpp.github.io/cppwp/n4950/temp.deduct).

### Moment instancjacji jest częścią diagnozy

Instancjacja klasy szablonowej nie musi od razu instancjować wszystkich ciał jej metod. Dlatego kontener pewnego typu może istnieć, dopóki klient nie wywoła operacji wymagającej niedostępnego konstruktora lub porównania. Ta odroczona kontrola jest użyteczna, ale potrafi mylić podczas testów: samo zadeklarowanie `Box<Unusual>` nie dowodzi poprawności `Box<Unusual>::copy_all()`. Minimalny przykład powinien wywołać dokładnie operację, której wymagania chcesz zbadać.

`decltype` i `declval` działają w kontekstach niewartościowanych. Można nimi opisać wynik wywołania bez tworzenia rzeczywistego obiektu, również dla typu bez konstruktora domyślnego. Nie uprawnia to jednak do wywołania `declval` w runtime; funkcja służy wyłącznie do takich analiz typów. Użycie `T{}` zamiast `declval<T>()` przypadkowo dodałoby wymaganie konstrukcji domyślnej do badanego interfejsu.

W komunikacie kompilatora szukaj pierwszego miejsca, w którym wymagana stała się konkretna specjalizacja. Dalsze błędy mogą być tylko skutkiem nieudanego wcześniejszego podstawienia. Ograniczenie przykładu do jednego szablonu, jednego typu i jednego wywołania zwykle pozwala ustalić, czy problem dotyczy parsowania nazwy, lookup, dedukcji, constraints czy ciała instancjowanej funkcji.

W przypadku zależnego wywołania funkcji o nieograniczonej nazwie ważna jest także widoczność deklaracji w kontekście definicji szablonu. Przeniesienie pomocniczej funkcji pod definicję szablonu może spowodować błąd nawet wtedy, gdy nadal znajduje się przed miejscem wywołania w main. Najprostsza naprawa to wcześniejsza deklaracja właściwego helpera lub umieszczenie dostosowania w przestrzeni typu odnajdywanej przez ADL. Nie warto rozwiązywać takiego problemu przypadkowymi zmianami kolejności include w każdym kliencie.

## Powiązane tematy

- [Specialization i SFINAE](../05_szablony_i_generycznosc/03_specialization_i_sfinAE.md)
- [Concepts](../05_szablony_i_generycznosc/04_concepts_i_requires.md)
- [Overload resolution](06_overload_resolution_adl_i_hidden_friends.md)

