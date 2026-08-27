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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „map, set, unordered i hash”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie zakresu, wykonanie operacji zgodnie z wymaganiami iteratora i aktualizację stanu kontenera wraz z regułami invalidacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij właściciela elementów od widoku, kolejność logiczną od fizycznego układu i gwarancję złożoności od konkretnego czasu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź rozmiar i capacity, ważność iteratorów, liczbę alokacji, kolejność elementów oraz klasę złożoności. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Kontenery i algorytmy biblioteki standardowej mają kontrakty dotyczące złożoności, invalidacji, własności oraz zakresów. Poprawny wybór wynika z wymaganych operacji i stabilności adresów, nie z przyzwyczajenia do jednego kontenera. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Kontenery uporządkowane wymagają ścisłego słabego porządku i oferują operacje logarytmiczne. Kontenery unordered wymagają spójności hash i równości; rehash invaliduje iteratory, choć nie referencje do elementów.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „map, set, unordered i hash” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: map, set, unordered i hash
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „map, set, unordered i hash”, oceniaj wzorzec dostępu, lokalność danych, stabilność referencji, koszt modyfikacji i możliwość użycia gotowego algorytmu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Algorytmy i lambdy](05_algorytmy_i_lambdy.md)
- [Specialization i SFINAE](../05_szablony_i_generycznosc/03_specialization_i_sfinAE.md)
- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)

