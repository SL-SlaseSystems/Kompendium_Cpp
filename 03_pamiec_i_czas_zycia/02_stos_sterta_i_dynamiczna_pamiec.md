[← Spis treści](../README.md)

# Stos, sterta i dynamiczna pamięć

Obiekty automatyczne są zwykle umieszczane na stosie, a dynamiczne w obszarze nazywanym stertą. Standard nie wymaga takiej fizycznej implementacji, ale model pomaga rozumieć koszty. Automatyczny obiekt jest niszczony przy wyjściu z zakresu. Dynamiczny trwa do jawnego `delete` albo do zwolnienia przez obiekt zarządzający.

Surowe `new` tworzy obiekt i zwraca wskaźnik; `delete` kończy lifetime i zwalnia pamięć. Pary `new[]`/`delete[]` są odrębne. Błędne dopasowanie, podwójne zwolnienie, użycie po zwolnieniu oraz utrata ostatniego adresu prowadzą do UB lub wycieku.

~~~cpp
#include <cassert>
#include <memory>
#include <vector>

int main() {
    auto number = std::make_unique<int>(42);
    auto values = std::vector<int>(1'000, 7);

    assert(*number == 42);
    assert(values.size() == 1'000);
}
~~~

Przykład przydziela pamięć dynamicznie, ale nie wykonuje ręcznego `delete`. `std::unique_ptr` i `std::vector` zwalniają zasoby w destruktorach. To podstawowa technika współczesnego C++: bezpośrednie operacje alokatora ukrywa się za typami przestrzegającymi RAII.

Dynamiczna alokacja ma koszt czasu, może fragmentować pamięć i pogarszać lokalność cache. Nie każda wartość musi trafiać na stertę. Kontenery mogą jednak realokować, gdy rosną; wskaźniki i referencje do ich elementów mogą wtedy zostać unieważnione. `reserve` pomaga, gdy przewidywany rozmiar jest znany, ale nie powinien być stosowany bez zrozumienia profilu danych.

## Kiedy ręczne zarządzanie jest uzasadnione

Własne kontenery, alokatory, interoperacyjność z C i kod embedded czasem wymagają pracy na surowej pamięci. Oddziel wtedy uzyskanie storage od konstruowania obiektu, udokumentuj alignment i exception safety, a niskopoziomową część zamknij w małym typie RAII.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Stos, sterta i dynamiczna pamięć”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz rozpoczęcie lifetime, ustanowienie inwariantu, przekazywanie własności lub widoku oraz zakończenie lifetime w dokładnie określonym miejscu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel storage od obiektu, właściciela od obserwatora oraz semantykę przeniesienia od zwykłego kopiowania bitów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź miejsce konstrukcji i destrukcji, graf właścicieli, ważność referencji oraz zachowanie sanitizerów. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Poprawność pamięci w C++ wynika z czasu życia obiektów i własności zasobów. Adres jest tylko reprezentacją położenia; nie dowodzi, że obiekt nadal istnieje ani że wolno uzyskać przez niego dostęp do przechowywanej wartości. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Stos i sterta są popularnymi opisami implementacji, podczas gdy standard definiuje storage duration i mechanizmy alokacji. `new` najpierw uzyskuje storage, potem konstruuje obiekt; `delete` niszczy obiekt i zwalnia odpowiednią alokację.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Stos, sterta i dynamiczna pamięć” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Stos, sterta i dynamiczna pamięć
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Stos, sterta i dynamiczna pamięć”, oceniaj jednoznaczna własność, automatyczne sprzątanie, brak dangling i możliwie mała liczba ręcznych operacji na pamięci. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Smart pointery](05_smart_pointery.md)
- [Kontenery sekwencyjne](../06_biblioteka_standardowa/02_vector_array_deque_list.md)
- [Alokatory i PMR](../zaawansowane/04_allocatory_pmr_i_new_delete.md)

