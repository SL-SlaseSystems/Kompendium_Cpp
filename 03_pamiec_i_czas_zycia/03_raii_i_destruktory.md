[← Spis treści](../README.md)

# RAII i destruktory

RAII (*Resource Acquisition Is Initialization*) wiąże ważność zasobu z lifetime obiektu. Konstruktor ustanawia inwariant, a destruktor go bezwarunkowo sprząta. Zasobem może być pamięć, plik, blokada, gniazdo, uchwyt systemowy albo tymczasowa zmiana stanu.

~~~cpp
#include <cassert>
#include <utility>

class CounterGuard {
public:
    explicit CounterGuard(int& counter) : counter_{counter} {
        ++counter_;
    }

    ~CounterGuard() {
        --counter_;
    }

    CounterGuard(const CounterGuard&) = delete;
    CounterGuard& operator=(const CounterGuard&) = delete;

private:
    int& counter_;
};

int main() {
    int active = 0;
    {
        CounterGuard guard{active};
        assert(active == 1);
    }
    assert(active == 0);
}
~~~

Destruktory obiektów automatycznych są wywoływane w odwrotnej kolejności pełnego skonstruowania, również podczas rozwijania stosu przez wyjątek. Dlatego RAII daje jednolity mechanizm sprzątania bez ręcznych bloków `finally`. Destruktor powinien być praktycznie `noexcept`; wyjątek opuszczający destruktor podczas obsługi innego wyjątku kończy program przez `std::terminate`.

Konstruktor nie może zwrócić błędu zwykłą wartością. Jeśli nie potrafi ustanowić inwariantu, może rzucić wyjątek; podobiekty już skonstruowane zostaną posprzątane. Alternatywą jest fabryka zwracająca `std::expected` lub inny typ wyniku. Dwufazowa inicjalizacja, w której obiekt przez pewien czas jest nieważny, zwykle komplikuje wszystkie metody.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „RAII i destruktory”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz rozpoczęcie lifetime, ustanowienie inwariantu, przekazywanie własności lub widoku oraz zakończenie lifetime w dokładnie określonym miejscu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel storage od obiektu, właściciela od obserwatora oraz semantykę przeniesienia od zwykłego kopiowania bitów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź miejsce konstrukcji i destrukcji, graf właścicieli, ważność referencji oraz zachowanie sanitizerów. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Poprawność pamięci w C++ wynika z czasu życia obiektów i własności zasobów. Adres jest tylko reprezentacją położenia; nie dowodzi, że obiekt nadal istnieje ani że wolno uzyskać przez niego dostęp do przechowywanej wartości. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- RAII wiąże zwolnienie zasobu z destruktorem obiektu posiadającego. Podczas stack unwinding niszczone są w pełni skonstruowane podobiekty, dlatego częściowo nieudany konstruktor nie wymaga ręcznego odwijania wcześniej utworzonych członów.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „RAII i destruktory” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: RAII i destruktory
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „RAII i destruktory”, oceniaj jednoznaczna własność, automatyczne sprzątanie, brak dangling i możliwie mała liczba ręcznych operacji na pamięci. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Pułapki

RAII nie oznacza, że każdy destruktor może zakładać pełne istnienie innych globalnych obiektów. Uważaj też na cykle `shared_ptr`. Jeśli zasób ma dedykowany typ standardowy, użyj go zamiast pisać własną otoczkę.

## Powiązane tematy

- [Konstruktory i destruktory](../04_klasy_i_model_obiektowy/02_konstruktory_i_destruktory.md)
- [Exception safety](../07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md)
- [Rule of zero](04_copy_move_i_rule_of_zero.md)

