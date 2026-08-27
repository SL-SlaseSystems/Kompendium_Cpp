[← Spis treści](../README.md)

# chrono i czas

Biblioteka `<chrono>` rozdziela zegar, punkt czasu i duration. `steady_clock` jest monotoniczny i nadaje się do mierzenia odstępów. `system_clock` wiąże się z czasem kalendarzowym i może zostać skorygowany. `high_resolution_clock` jest aliasem zależnym od implementacji i nie gwarantuje monotoniczności.

~~~cpp
#include <cassert>
#include <chrono>

using namespace std::chrono_literals;

int main() {
    constexpr auto timeout = 250ms;
    constexpr auto interval = 2s + 500ms;
    static_assert(timeout.count() == 250);
    static_assert(std::chrono::duration_cast<std::chrono::milliseconds>(interval).count() == 2500);

    const auto start = std::chrono::steady_clock::now();
    const auto end = std::chrono::steady_clock::now();
    assert(end >= start);
}
~~~

Duration ma reprezentację i period. Dodawanie różnych jednostek wykorzystuje wspólny typ, a `duration_cast` wykonuje jawną konwersję, potencjalnie obcinając część ułamkową. Literały `ms`, `s`, `min` poprawiają czytelność i zapobiegają przekazywaniu „gołej liczby” o niejasnej jednostce.

C++20 rozszerzył chrono o calendar i time zones. Dostępność bazy stref, jej aktualizacja i wsparcie biblioteki zależą od środowiska. Czas lokalny może być niejednoznaczny lub nieistniejący przy zmianie DST; przechowuj zdarzenia jako jednoznaczny punkt czasu i konwertuj do strefy na granicy prezentacji.

Timeouty powinny używać deadline opartego o steady clock, aby spurious wakeup i kolejne pętle nie wydłużały limitu. Nie zakładaj dokładności harmonogramu równej rozdzielczości typu; system może wznowić wątek później.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „chrono i czas”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz normalizację wejścia, wykonanie operacji systemowej lub bibliotecznej, sprawdzenie wyniku i zamknięcie zasobu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel format danych od obiektu domenowego, czas monotoniczny od kalendarzowego oraz API standardowe od zależności platformowej. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź kod błędu, liczbę przetworzonych bajtów, stan strumienia, jednostkę pomiaru i wynik dla przerwanej operacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: I/O przekracza granicę procesu i dlatego jest częściowe, opóźnione oraz zależne od reprezentacji. Każda operacja potrzebuje modelu błędów, limitu danych, kodowania lub jednostki oraz zasad własności uchwytu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `steady_clock` nadaje się do mierzenia odstępów, ponieważ nie cofa się wraz z korektą zegara kalendarzowego. Typowane duration chronią jednostki, ale jawne cast jest potrzebne, gdy konwersja może utracić precyzję.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „chrono i czas” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: chrono i czas
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „chrono i czas”, oceniaj jawne kodowanie, kontrolowane limity, odporność na częściowy odczyt, bezpieczne ścieżki i deterministyczne sprzątanie. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Benchmarki](../09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md)
- [condition_variable](../10_wspolbieznosc/02_mutex_lock_i_condition_variable.md)
- [C++20](../12_wspolczesny_cpp/03_cpp20.md)

