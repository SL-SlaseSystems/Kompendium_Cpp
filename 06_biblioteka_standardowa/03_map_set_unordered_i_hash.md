[← Spis treści](../README.md)

# map, set, unordered i hash

Kontenery uporządkowane `std::map` i `std::set` utrzymują porządek według komparatora i zwykle oferują operacje logarytmiczne. `std::unordered_map` i `std::unordered_set` używają hashowania, oferując oczekiwaną złożoność stałą przy dobrym rozkładzie, lecz bez uporządkowanej iteracji. `multimap` i `multiset` dopuszczają powtarzające się klucze.

~~~cpp
#include <cassert>
#include <map>
#include <string>
#include <unordered_map>

int main() {
    std::map<std::string, int, std::less<>> ordered;
    ordered.try_emplace("Ada", 1);
    ordered.insert_or_assign("Ada", 2);

    std::unordered_map<std::string, int> counts;
    for (const std::string word : {"C++", "Rust", "C++"}) {
        ++counts[word];
    }

    assert(ordered.at("Ada") == 2);
    assert(counts.at("C++") == 2);
}
~~~

`operator[]` mapy tworzy brakującą wartość przez konstrukcję domyślną. Do samego odczytu użyj `at`, `find` albo `contains`. `try_emplace` nie konstruuje wartości, jeśli klucz już istnieje, a `insert_or_assign` jasno komunikuje nadpisanie.

Komparator kontenera uporządkowanego musi ustanawiać strict weak ordering. Równość kluczy oznacza, że żaden nie jest mniejszy od drugiego. W kontenerze haszowanym, jeśli `a == b`, wartości hash muszą być równe. Zmiana pola klucza wpływającego na porządek lub hash po wstawieniu złamałaby inwariant, dlatego klucze są udostępniane jako const.

Transparent comparator, np. `std::less<>`, może umożliwić heterogeniczne wyszukiwanie bez konstruowania tymczasowego `std::string`. Dla unordered potrzebne są transparentne hash i equality oraz wsparcie odpowiednich operacji w wybranym standardzie.

## Jak to działa krok po kroku

Pierwsze `try_emplace("Ada", 1)` wyszukuje klucz i konstruuje parę tylko wtedy, gdy go nie ma. Zwrócona para zawiera iterator oraz informację, czy rzeczywiście wstawiono element. Drugie wywołanie z tym samym kluczem nie nadpisuje wartości. `insert_or_assign` wybiera inną semantykę: tworzy element albo przypisuje nową wartość do istniejącej. Rozdzielenie tych operacji pozwala uniknąć sekwencji „sprawdź, a potem ponownie szukaj”.

W liczeniu słów `counts[word]` celowo tworzy brakujący licznik z wartością zero. Taki sam zapis w funkcji rzekomo tylko odczytującej konfigurację byłby błędem projektu: odczyt zmieniałby zawartość mapy. `at` rzuca przy braku klucza, `find` zwraca iterator końcowy, a `contains` daje samą odpowiedź logiczną. Jeśli później potrzebujesz wartości, zachowaj wynik `find`, zamiast wykonywać drugie wyszukiwanie.

Zwróć uwagę na argumenty `try_emplace`: wyrażenia argumentów funkcji są obliczane przed jej wykonaniem. `try_emplace(key, expensive())` nadal uruchamia `expensive()`, także przy istniejącym kluczu. Oszczędność dotyczy konstrukcji przechowywanej wartości z dostarczonych argumentów. Jeżeli samo ich przygotowanie jest kosztowne, potrzebujesz wcześniejszego wyszukania albo innej organizacji API.

## Pogłębienie mechanizmu

Komparator określa równoważność przez `!comp(a,b) && !comp(b,a)`, a nie przez `operator==`. Mapa z porównywaniem bez rozróżniania wielkości liter może uznawać dwa różne napisy za ten sam klucz. Komparator nie może zmieniać odpowiedzi po zmianie zewnętrznego stanu. Liczby zmiennoprzecinkowe z NaN wymagają szczególnej uwagi: zwykłe `<` na całej takiej dziedzinie nie dostarcza wymaganego porządku słabego.

Tabela haszująca najpierw wybiera kubełek przez hash, a następnie rozstrzyga równość kluczy. Kolizje są legalne, dlatego sam hash nie jest identyfikatorem ani dowodem równości. Równoważne klucze muszą mieć jednak ten sam hash. Zły rozkład powoduje długie łańcuchy poszukiwania i pesymistyczne O(n). `std::hash` nie gwarantuje odporności kryptograficznej ani trwałego numeru nadającego się do zapisu w pliku.

`load_factor` opisuje średnią liczbę elementów na kubełek. `reserve(n)` w kontenerze unordered przygotowuje kubełki dla n elementów przy obowiązującym maksymalnym współczynniku zapełnienia. Rehash unieważnia iteratory, ale nie wskaźniki i referencje do zachowanych elementów. Kolejność iteracji może się zmienić. Nie opieraj deterministycznej serializacji na tej kolejności; posortuj klucze albo użyj kontenera uporządkowanego.

Heterogeniczne wyszukiwanie wymaga spójnego porównywania całej obsługiwanej rodziny argumentów. Jeżeli kluczem jest string, a zapytaniem string_view, relacja musi porównywać zawartość w obu kierunkach tak samo jak dwa właściwe klucze. W unordered samo dodanie `is_transparent` do hasha nie wystarcza: potrzebny jest również transparentny predykat równości z odpowiednimi wywołaniami. To znacznik udostępniający przeciążenia, a nie automatyczny generator poprawnych konwersji i spójnych reguł porównania.

## Drugi przykład

Node handle pozwala legalnie zmienić klucz poza kontenerem i następnie ponownie włączyć węzeł. Wstawienie może się nie udać, jeśli nowy klucz już istnieje.

~~~cpp
#include <cassert>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> ports{{"http", 80}, {"https", 443}};
    auto node = ports.extract("http");
    assert(!node.empty());
    node.key() = "web";
    auto inserted = ports.insert(std::move(node));
    assert(inserted.inserted);
    assert(ports.at("web") == 80);
    assert(!ports.contains("http"));

    auto conflict = ports.extract("web");
    conflict.key() = "https";
    auto rejected = ports.insert(std::move(conflict));
    assert(!rejected.inserted && !rejected.node.empty());
    rejected.node.key() = "web";
    ports.insert(std::move(rejected.node));
    assert(ports.size() == 2);
}
~~~

Nieudane wstawienie nie gubi węzła: wynik zawiera go w polu `node`. Gdybyśmy porzucili ten wynik, jego destruktor zwolniłby przechowywany element. To przykład, w którym obsługa wyniku jest częścią zachowania danych, a nie tylko diagnostyką sukcesu.

## Porównanie i decyzje

Wybieraj mapę uporządkowaną, gdy potrzebujesz zakresów kluczy, `lower_bound`, przewidywalnego O(log n) albo uporządkowanego przejścia. Unordered pasuje do wyszukiwania dokładnej równości, lecz wymaga właściwej funkcji hash. Dla małego, rzadko zmienianego zbioru posortowany wektor może być tańszy pamięciowo. C++23 dodaje `flat_map` i `flat_set`; ich stabilność iteratorów i koszt wstawiania różnią się od kontenerów węzłowych.

**Ćwiczenie.** Hash ignoruje wielkość liter, a equality porównuje dokładne bajty. Czy to samo w sobie łamie kontrakt? **Odpowiedź:** nie, powoduje tylko dodatkowe kolizje. Odwrotna konfiguracja byłaby błędna: equality uznawałoby napisy za równe, a hash mógłby skierować je do różnych kubełków.

Źródła reguł: [C++23: kontenery asocjacyjne](https://timsong-cpp.github.io/cppwp/n4950/associative.reqmts), [unordered](https://timsong-cpp.github.io/cppwp/n4950/unord.req), [uchwyty węzłów](https://timsong-cpp.github.io/cppwp/n4950/container.node).

## Powiązane tematy

- [Algorytmy i lambdy](05_algorytmy_i_lambdy.md)
- [Specialization i SFINAE](../05_szablony_i_generycznosc/03_specialization_i_sfinAE.md)
- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)
