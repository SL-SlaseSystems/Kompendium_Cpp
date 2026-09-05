[← Spis treści](../README.md)

# Undefined behavior i model maszyny

Standard opisuje program względem C++ abstract machine. Implementacja musi zachować obserwowalne zachowanie poprawnego programu zgodnie z regułą as-if, ale może dowolnie przekształcać kod. Gdy wykonanie ma undefined behavior, standard nie nakłada wymagań na całość tego wykonania; optimizer może wykorzystać założenie, że poprawny program nie trafia w UB.

Typowe źródła UB to signed overflow, wyjście poza zakres, use-after-lifetime, dereferencja nieważnego lub źle wyrównanego wskaźnika, data race, naruszenie aliasingu, dzielenie całkowite przez zero i złamanie precondition oznaczonego w standardzie jako UB.

~~~cpp,notest
int overflow(int value) {
    return value + 1; // UB, gdy value == INT_MAX
}

int use_after_free() {
    int* pointer = new int{42};
    delete pointer;
    return *pointer; // UB
}
~~~

Nie każdy błąd to UB. Wyjątek z `vector::at`, niepowodzenie `dynamic_cast` do wskaźnika mają określone konsekwencje. Brak postępu trzeba analizować według kontraktu synchronizacji: nie każdy deadlock jest UB, lecz ponowne blokowanie niewłaściwego mutexa może naruszać wymagania API. Zachowanie implementation-defined wymaga dokumentacji wyboru, unspecified dopuszcza kilka wyników, a ill-formed program wymaga diagnostyki, o ile nie zaznaczono inaczej.

~~~cpp
#include <cassert>
#include <limits>
#include <optional>

std::optional<int> checked_add(int left, int right) {
    if (right > 0 && left > std::numeric_limits<int>::max() - right) return std::nullopt;
    if (right < 0 && left < std::numeric_limits<int>::min() - right) return std::nullopt;
    return left + right;
}

int main() {
    assert(checked_add(20, 22) == 42);
    assert(!checked_add(std::numeric_limits<int>::max(), 1));
}
~~~

Sanitizery wykrywają część naruszeń w wykonanych ścieżkach. Analiza statyczna i testy uzupełniają obraz. Najważniejsza jest konstrukcja API: span zamiast wskaźnika z rozmiarem, RAII zamiast ręcznego cleanup i synchronizacja zamiast nadziei na kolejność.

## Jak to działa krok po kroku

W `checked_add` warunki są sprawdzane **przed** dodawaniem. Dla dodatniego `right` odejmowanie od maksimum nie przepełnia typu, a nierówność rozpoznaje wartości `left`, dla których suma byłaby za duża. Dla ujemnego `right` odejmowanie od minimum daje reprezentowalny próg. Dopiero po odrzuceniu obu przypadków funkcja wykonuje dodawanie. Kod nie próbuje wykrywać przepełnienia na podstawie już przepełnionego wyniku; taka kontrola przyszłaby za późno.

Przykładowo dla `left = INT_MAX`, `right = 1` pierwsza nierówność jest prawdziwa i funkcja zwraca pusty `optional`. Dla `left = INT_MIN`, `right = -1` działa druga gałąź. Dla liczb przeciwnych znaków przekroczenie skrajnej wartości nie nastąpi, więc nie potrzeba szerszego typu. To rozumowanie działa także wtedy, gdy `long long` nie jest szerszy od badanego typu; samo rzutowanie do domniemanego większego typu nie jest uniwersalnym zabezpieczeniem.

## Pogłębienie mechanizmu

Reguła as-if opisuje równoważność obserwowalnego zachowania, a nie liczbę instrukcji procesora. Kompilator może usunąć zapis do lokalnej zmiennej, zwinąć pętlę albo obliczyć wynik wcześniej. Dla `int x` wyrażenie `x + 1 > x` jest prawdziwe dla wszystkich wartości, dla których dodawanie jest zdefiniowane. Optymalizator może więc zwrócić `true` bez wykonywania dodawania. Procesor posiadający instrukcję dodawania modulo nie zmienia semantyki signed overflow w źródłowym C++.

Zachowanie unspecified nie daje podobnej swobody. Przy `f(g(), h())` implementacja może wybrać kolejność argumentów, ale od C++17 ich ewaluacje są indeterminately sequenced: nie przeplatają się. Program musi tolerować dozwolone kolejności, lecz nie staje się przez sam brak ustalonej kolejności programem z UB. Natomiast niezsekwencjonowana modyfikacja i odczyt tego samego skalara może już naruszać reguły języka.

Odczyt niezainicjalizowanego zwykłego `int` w C++23 zasadniczo prowadzi do UB. Nie wolno przenosić tu opisu **erroneous behavior z C++26** bez wskazania wersji i dokładnej kategorii pamięci. Podobnie „kompilator nie ostrzegł” nie oznacza defined behavior: wielu naruszeń wykonania implementacja nie musi diagnozować. Program ill-formed no diagnostic required, na przykład wskutek pewnych naruszeń ODR, stanowi jeszcze inną kategorię niż błąd składni wymagający komunikatu.

## Drugi przykład

~~~cpp
#include <cassert>
#include <limits>
#include <optional>

std::optional<int> quotient(int a, int b) {
    if (b == 0) return std::nullopt;
    if (a == std::numeric_limits<int>::min() && b == -1)
        return std::nullopt;
    return a / b;
}
int main() {
    assert(quotient(-7, 3) == -2);
    assert(!quotient(1, 0));
    assert(!quotient(std::numeric_limits<int>::min(), -1));
}
~~~

Dzielenie całkowite obcina wynik w stronę zera, więc pierwsze sprawdzenie daje `-2`. Sam test dzielnika nie wystarcza: iloraz minimum przez `-1` nie mieści się w `int`. Ten sam szczególny przypadek trzeba rozważyć przy operatorze reszty `%`. Zamiana tych operatorów na funkcję opakowującą pozwala skupić dowód poprawności w jednym miejscu i zwracać błąd należący do domeny aplikacji.

## Porównanie i decyzje

Typ unsigned wybieraj, kiedy potrzebujesz arytmetyki modulo, masek bitowych lub reprezentacji nieujemnej o dobrze rozumianych konwersjach. Nie traktuj go jako automatycznej ochrony przed błędami liczbowymi: odejmowanie `0u - 1u` jest zdefiniowane, ale może zamienić brak elementu w ogromny indeks. Sanitizer UB nie musi zgłosić logicznego błędu w poprawnej arytmetyce unsigned.

ASan wykrywa wiele błędów adresowania, UBSan wybrane naruszenia semantyki, a TSan wyścigi danych. Każdy wymaga uruchomienia odpowiednich ścieżek; żaden nie jest pełnym dowodem. W analizie porównuj wersję z optymalizacją i diagnostyką, lecz nie „naprawiaj” programu samym obniżeniem poziomu optymalizacji. Wyłączenie strict aliasing jest rozszerzeniem konfiguracji kompilatora, a nie zmianą przenośnego kontraktu C++.

**Ćwiczenie.** Dlaczego `if (a + b < a)` nie sprawdza niezawodnie przepełnienia signed? **Odpowiedź:** wyrażenie warunku samo może już wykonać UB; optymalizator rozumuje przy założeniu, że poprawne wykonanie go nie zawiera. Dlaczego `assert(pointer)` nie sprawdza lifetime? Niezerowy adres może wskazywać zwolnioną pamięć lub obiekt innego typu. Sprawdzenie wartości wskaźnika i legalności dereferencji to różne obowiązki.

Źródło reguł: [N4950: abstract machine](https://timsong-cpp.github.io/cppwp/n4950/intro.abstract) i [ewaluacja wyrażeń](https://timsong-cpp.github.io/cppwp/n4950/intro.execution).

### Granica obietnic dla optymalizatora

`volatile` nie jest uniwersalnym hamulcem optymalizacji i nie wprowadza atomowości między wątkami. Ma szczególne znaczenie dla obserwowalnych dostępów i interfejsów określonych przez implementację, na przykład pamięci mapowanej na urządzenia. Użycie go na współdzielonym liczniku nie usuwa data race. Podobnie kompilatorowa bariera asemblerowa nie jest automatycznie odpowiednikiem relacji happens-before w standardowym C++.

Precondition biblioteki może być równie ważny jak reguła operatora. `vector::operator[]` wymaga poprawnego indeksu; po przekroczeniu `size()` nie wolno usprawiedliwiać dostępu tym, że pamięć mieści się w przydzielonej pojemności. `at()` oferuje kontrolowany wyjątek dla błędnego indeksu, lecz nadal nie chroni przed użyciem już zniszczonego wektora. Kolejne warstwy API rozwiązują określone klasy problemów, nie wszystkie problemy pamięci jednocześnie.

Przy badaniu podejrzanej optymalizacji najpierw zmniejsz przykład, zachowując wymagania dotyczące typów, lifetime i kolejności. Następnie określ zbiór dozwolonych wyników niezależnie od obserwacji jednego uruchomienia. Jeśli kod maszynowy nie odpowiada temu zbiorowi dla poprawnego programu, masz podstawę do zgłoszenia błędu kompilatora. Jeżeli wcześniejsza instrukcja narusza semantykę, nietypowy wynik może być konsekwencją tego naruszenia.

## Powiązane tematy

- [Lifetime i provenance](02_lifetime_aliasing_i_pointer_provenance.md)
- [Sanitizery](../09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)
- [Memory ordering](11_memory_ordering_lock_free_aba_i_reclamation.md)

