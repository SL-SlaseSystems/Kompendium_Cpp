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

Wyrażenie `new T(args)` obejmuje znalezienie funkcji alokującej, uzyskanie odpowiedniego miejsca i inicjalizację obiektu. Zwrócony wskaźnik odnosi się do gotowego obiektu, jeżeli całość się powiedzie. Zwykła rzucająca alokacja sygnalizuje brak pamięci wyjątkiem `std::bad_alloc`. Wersja `new (std::nothrow)` może zwrócić pusty wskaźnik przy niepowodzeniu alokacji, lecz konstruktor `T` nadal może rzucić własny wyjątek.

Jeśli konstruktor rzuci po uzyskaniu pamięci przez zwykłe `new`, odpowiednio dopasowana funkcja zwalniająca sprząta tę pamięć. Destruktor kompletnego `T` nie jest wtedy uruchamiany, ponieważ obiekt nie został w pełni skonstruowany. Sprzątane są już zbudowane podobiekty. To nie ochroni jednak surowego zasobu, który konstruktor przejął do zwykłego pola wskaźnikowego przed późniejszą porażką.

`delete p` wywołuje destruktor, a następnie zwalnia miejsce zgodnie z właściwą operacją dealokacji. Dla pustego wskaźnika nie niszczy obiektu. Nie ustawia automatycznie wszystkich kopii wskaźnika na `nullptr`. Po zwolnieniu stare aliasy stają się niebezpieczne. `delete[]` dodatkowo odpowiada za wszystkie elementy tablicy; nie można zastępować go pojedynczym `delete`.

## Pogłębienie mechanizmu

Lokalny `std::vector<int>` jest automatycznym obiektem zarządzającym, ale jego elementy zwykle znajdują się w osobnym dynamicznym buforze. Zniszczenie lokalnego wektora wywołuje destrukcję elementów i zwolnienie tego bufora. Dlatego pytanie „czy wektor jest na stosie?” jest zbyt mało precyzyjne: należy osobno wskazać obiekt zarządzający i przechowywane dane.

`reserve(n)` zapewnia pojemność co najmniej `n`, ale nie zmienia rozmiaru. `resize(n)` tworzy lub niszczy elementy, a w razie potrzeby także alokuje. Gdy `reserve` rzeczywiście powoduje realokację, wszystkie wskaźniki, referencje i iteratory do elementów zostają unieważnione. Bez realokacji pozostają ważne. Nie wolno przewidywać dokładnego mnożnika wzrostu pojemności jako przenośnej gwarancji.

`malloc` i `free` pochodzą z biblioteki C i nie wykonują konstruktorów ani destruktorów C++. Współczesny model dopuszcza pewne niejawne tworzenie obiektów typów implicit-lifetime w przydzielonym miejscu, ale nie czyni z `malloc` zamiennika konstrukcji dowolnej klasy, takiej jak `std::string`. Nie mieszaj rodzin alokacji i zwalniania. Umowa z biblioteką C powinna wskazywać dokładnie funkcję zwalniającą jej wynik.

Nawet poprawny model własności może być kosztowny, jeśli wykonuje jedną alokację dla każdej małej wartości. Ciągły bufor zwykle poprawia lokalność danych, lecz jego realokacja zmienia adresy. Oddzielne obiekty zarządzane przez `unique_ptr` stabilizują adresy samych wartości kosztem wielu alokacji i pośrednich dostępów. Wybór wynika z wymagania stabilności adresów oraz pomiaru rzeczywistego obciążenia.

## Drugi przykład

Alokator pozwala osobno uzyskać miejsce i rozpocząć życie obiektu. Przykład edukacyjny zawiera sprzątanie zarówno po udanej konstrukcji, jak i po wyjątku konstruktora.

~~~cpp
#include <cassert>
#include <memory>
#include <string>

int main() {
    std::allocator<std::string> allocator;
    std::string* storage = allocator.allocate(1);
    std::string* object = nullptr;
    try {
        object = std::construct_at(storage, "C++");
    } catch (...) {
        allocator.deallocate(storage, 1);
        throw;
    }
    assert(*object == "C++");
    std::destroy_at(object);
    allocator.deallocate(storage, 1);
}
~~~

Pomiędzy `allocate` a `construct_at` nie ma jeszcze skonstruowanego napisu, którego metody można wywoływać. Po `destroy_at` napis przestaje istnieć, ale miejsce jest nadal przydzielone aż do `deallocate`. W kodzie aplikacyjnym te operacje powinien wykonywać kontener albo mały obiekt RAII. Przykład celowo ujawnia etapy, które zwykle pozostają ukryte.

## Porównanie i decyzje

Wybieraj zwykłą wartość, gdy czas życia odpowiada zakresowi i nie potrzebujesz dynamicznego rozmiaru ani stabilnej niezależnej tożsamości. Dla sekwencji używaj kontenera. Dynamiczny pojedynczy obiekt najczęściej powinien od razu trafić do `unique_ptr`. Sam fakt, że wartość jest duża, nie uzasadnia rozproszenia wszystkich jej części w osobnych alokacjach.

**Ćwiczenie.** Czy po `auto p = std::make_unique<int>(7); int* raw = p.get(); p.reset();` przypisanie `raw = nullptr` naprawia wcześniejsze użycie `*raw` wykonane po `reset`?

**Odpowiedź.** Nie. `reset` zniszczył obiekt i zwolnił pamięć. Późniejsze wyzerowanie obserwatora może zapobiec następnym pomyłkom, lecz nie cofa już wykonanego użycia po zwolnieniu. Obserwator powinien przestać być używany najpóźniej przed zakończeniem własności.

Źródła: [wyrażenie new](https://timsong-cpp.github.io/cppwp/n4950/expr.new), [wyrażenie delete](https://timsong-cpp.github.io/cppwp/n4950/expr.delete), [zarządzanie pojemnością vector](https://timsong-cpp.github.io/cppwp/n4950/vector.capacity).

## Powiązane tematy

- [Smart pointery](05_smart_pointery.md)
- [Kontenery sekwencyjne](../06_biblioteka_standardowa/02_vector_array_deque_list.md)
- [Alokatory i PMR](../zaawansowane/04_allocatory_pmr_i_new_delete.md)

