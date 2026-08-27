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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Storage duration i lifetime”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz rozpoczęcie lifetime, ustanowienie inwariantu, przekazywanie własności lub widoku oraz zakończenie lifetime w dokładnie określonym miejscu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel storage od obiektu, właściciela od obserwatora oraz semantykę przeniesienia od zwykłego kopiowania bitów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź miejsce konstrukcji i destrukcji, graf właścicieli, ważność referencji oraz zachowanie sanitizerów. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Poprawność pamięci w C++ wynika z czasu życia obiektów i własności zasobów. Adres jest tylko reprezentacją położenia; nie dowodzi, że obiekt nadal istnieje ani że wolno uzyskać przez niego dostęp do przechowywanej wartości. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Storage duration opisuje dostępność pamięci, a lifetime istnienie konkretnego obiektu w tej pamięci. Ponowne użycie storage przez placement new może zakończyć jeden lifetime i rozpocząć drugi bez zmiany adresu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Storage duration i lifetime” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Storage duration i lifetime
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Storage duration i lifetime”, oceniaj jednoznaczna własność, automatyczne sprzątanie, brak dangling i możliwie mała liczba ręcznych operacji na pamięci. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Ograniczaj zakres i czas życia. Preferuj lokalne obiekty wartościowe oraz function-local statics dla bezpiecznej inicjalizacji singletonów, jeśli są naprawdę potrzebne. Nie przechowuj referencji do obiektu krócej żyjącego niż właściciel referencji.

## Powiązane tematy

- [Stos, sterta i pamięć dynamiczna](02_stos_sterta_i_dynamiczna_pamiec.md)
- [RAII](03_raii_i_destruktory.md)
- [Lifetime i provenance](../zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)

