[← Spis treści](../README.md)

# Referencje, wskaźniki i tablice

Referencja `T&` jest aliasem istniejącego obiektu i musi zostać zainicjalizowana. Wskaźnik `T*` przechowuje adres, może być równy `nullptr` i może zmienić cel. Ani referencja, ani surowy wskaźnik nie oznaczają automatycznie własności. Kontrakt API powinien wyjaśniać nullowalność oraz wymagany czas życia.

~~~cpp
#include <array>
#include <cassert>
#include <span>

int sum(std::span<const int> values) {
    int total = 0;
    for (int value : values) {
        total += value;
    }
    return total;
}

int main() {
    std::array data{1, 2, 3};
    int& first = data[0];
    int* pointer = &data[1];
    first = 4;
    *pointer = 5;

    assert(sum(data) == 12);
}
~~~

Wbudowana tablica `T[N]` ma stały rozmiar będący częścią typu. W większości wyrażeń ulega konwersji do wskaźnika na pierwszy element, tracąc informację o długości. `std::array<T, N>` zachowuje semantykę wartości i integruje się z biblioteką, a `std::span<T>` jest niewłaścicielskim widokiem na ciągły zakres.

Arytmetyka wskaźników jest dozwolona tylko w obrębie jednej tablicy oraz na pozycję one-past-the-end, której nie wolno dereferencjonować. Odejmowanie niepowiązanych wskaźników, dereferencja `nullptr`, użycie adresu po końcu lifetime obiektu i naruszenie alignment mogą być undefined behavior.

`const int*` wskazuje na niemodyfikowalny `int`, `int* const` jest stałym wskaźnikiem do modyfikowalnego `int`, a `const int* const` łączy oba ograniczenia. Czytaj deklarację od nazwy na zewnątrz lub w złożonych interfejsach używaj aliasów typów.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Referencje, wskaźniki i tablice”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie deklaracji, ustalenie typu, wybór operacji i ocenę wyrażenia zgodnie z regułami języka. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba sprawdź, które informacje istnieją w czasie kompilacji, a które zależą od danych i stanu programu podczas wykonania. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ wyrażenia, wybrany overload, zakres nazwy, wartość wyniku i ewentualną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Podstawowe konstrukcje C++ trzeba czytać jako operacje na typach, wartościach i zakresach, a nie tylko jako składnię. Istotne są konwersje, kategorie wartości, kolejność ewaluacji oraz to, czy dana nazwa oznacza obiekt, funkcję czy typ. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Referencja musi być związana z obiektem i nie może zostać później przepięta, natomiast wskaźnik jest wartością, może być pusty i podlega arytmetyce tylko wewnątrz odpowiedniej tablicy. Żaden z nich sam nie określa własności.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Referencje, wskaźniki i tablice” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Referencje, wskaźniki i tablice
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Referencje, wskaźniki i tablice”, oceniaj jawność intencji, brak niebezpiecznych konwersji, minimalny zakres nazw i możliwość wykrycia błędu podczas kompilacji. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Przekazuj obowiązkowo istniejący obiekt przez referencję, opcjonalny niewłaścicielski dostęp przez wskaźnik, ciągły zakres przez `span`, a własność przez typ wartościowy lub smart pointer. Unikaj wskaźnika i osobnego rozmiaru, jeśli może je spiąć widok.

## Powiązane tematy

- [Smart pointery](../03_pamiec_i_czas_zycia/05_smart_pointery.md)
- [Widoki i dangling](../03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)
- [Pointer provenance](../zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

