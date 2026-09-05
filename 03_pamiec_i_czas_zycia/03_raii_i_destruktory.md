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

Strażnik RAII nabywa odpowiedzialność w konstruktorze i zachowuje ją tak długo, jak istnieje. W pierwszym programie udana konstrukcja `CounterGuard` zwiększa licznik. Po opuszczeniu bloku destruktor zmniejsza ten sam licznik, ponieważ pole referencyjne nadal wskazuje `active`. Obiekt `active` zadeklarowano wcześniej, więc żyje wystarczająco długo, aby destruktor strażnika mógł go zmienić.

Usunięcie kopiowania jest częścią poprawności przykładu. Gdyby domyślna kopia skopiowała referencję bez ponownego zwiększenia licznika, dwa destruktory wykonałyby dwa zmniejszenia po jednym nabyciu. Właściciel zasobu nie może przypadkiem powielać odpowiedzialności. Jeśli strażnik ma być przenoszalny, operacja ruchu musi przekazać obowiązek sprzątania i rozbroić źródło. Samo skopiowanie adresu w dwóch właścicielach nie wystarcza.

Przy wyjątku niszczone są w odwrotnej kolejności lokalne obiekty, których konstrukcja zakończyła się poprawnie, o ile następuje rozwijanie stosu. Najnowsza blokada może zostać zwolniona przed wcześniejszym buforem i plikiem. Kod sprzątający nie musi znać miejsca, z którego przyszedł wyjątek. Zależności między zasobami powinny być odzwierciedlone kolejnością ich nabywania.

## Pogłębienie mechanizmu

Jeśli konstruktor nie dokończy działania, destruktor całego obiektu nie zostanie wywołany. Dokończone pola i bazy są jednak niszczone. Dlatego zasób nabyty w konstruktorze powinien natychmiast otrzymać własnego właściciela RAII, na przykład pole `unique_ptr`, zanim następna operacja może rzucić. Trzymanie go w surowym wskaźniku do końca konstruktora tworzy lukę w ochronie.

Destruktor zwykle ma niezgłaszający specyfikator wyjątków wyprowadzony z destruktorów baz i pól. Jawne `noexcept` dokumentuje ten kontrakt. Jeżeli operacja zwalniania może zawieść, potrzebna jest polityka: osobna metoda `close` lub `commit` raportuje błąd wtedy, gdy wywołujący może zareagować, a destruktor wykonuje bezpieczne sprzątanie końcowe. Ciche ignorowanie błędu zapisu pliku w destruktorze nie gwarantuje, że dane zostały utrwalone.

RAII nie oznacza automatycznie cofnięcia wszystkich zmian. Zamknięcie pliku zwalnia uchwyt, ale nie usuwa wcześniej zapisanych bajtów. Silna gwarancja wyjątków wymaga, aby niepowodzenie nie zmieniało obserwowalnego stanu operacji. Można ją budować przez przygotowanie nowej wartości osobno i bezpieczne zatwierdzenie. RAII dostarcza sprzątania częściowo przygotowanego stanu, nie wymyśla transakcji za projektanta.

Nie każdy sposób zakończenia programu rozwija stos. `std::abort`, zakończenie procesu przez system oraz część ścieżek kończących się `std::terminate` nie dają zwykłej gwarancji zniszczenia wszystkich obiektów lokalnych. Także `std::exit` nie niszczy automatycznych obiektów aktywnych funkcji. Krytyczna trwałość danych wymaga odpowiedniego protokołu zapisu, a nie założenia, że każdy destruktor zawsze się wykona.

## Drugi przykład

Dwa strażniki ustawiają tymczasowe wartości tej samej zmiennej. Wyjątek opuszcza ich zakres, a odwrotna kolejność destrukcji przywraca najpierw wartość pośrednią i na końcu pierwotną.

~~~cpp
#include <cassert>
#include <stdexcept>

class RestoreInt {
    int& target_;
    int previous_;
public:
    RestoreInt(int& target, int next) noexcept
        : target_{target}, previous_{target} { target_ = next; }
    ~RestoreInt() noexcept { target_ = previous_; }
    RestoreInt(const RestoreInt&) = delete;
    RestoreInt& operator=(const RestoreInt&) = delete;
};

int main() {
    int mode = 1;
    try {
        RestoreInt outer{mode, 2};
        RestoreInt inner{mode, 3};
        assert(mode == 3);
        throw std::runtime_error{"operation failed"};
    } catch (const std::runtime_error&) {
        assert(mode == 1);
    }
}
~~~

Przypisanie `int` nie rzuca, więc sprzątanie rzeczywiście spełnia `noexcept`. Uogólnienie strażnika na dowolne `T` wymaga ponownej analizy: przywracające przypisanie dla takiego typu mogłoby samo rzucać. Prosty przykład nie jest automatycznie poprawnym uniwersalnym mechanizmem transakcyjnym.

## Porównanie i decyzje

Nazwij lokalny obiekt blokady lub strażnika. Wyrażenie tworzące tylko temporary, na przykład `Guard{resource};`, niszczy strażnika już przy kończącym je średniku. Kolejne instrukcje nie są chronione, mimo że konstruktor poprawnie nabył zasób. Deklaracja `Guard guard{resource};` wiąże odpowiedzialność z całym zakresem nazwanego obiektu. Czas życia strażnika jest więc równie istotny jak poprawność jego destruktora.

Preferuj istniejących właścicieli: `unique_ptr` dla obiektu, `lock_guard` dla blokady i klasy strumieni dla plików. Własny strażnik ma sens, gdy zasób lub przywracany stan nie ma odpowiednika bibliotecznego. Jego interfejs powinien jasno określać kopiowanie, przenoszenie, możliwość zwolnienia odpowiedzialności oraz wymagany czas życia obserwowanych obiektów.

**Ćwiczenie.** Konstruktor klasy najpierw otwiera zasób i zapisuje surowy uchwyt, a potem tworzy napis, którego alokacja rzuca. Czy destruktor tej klasy zamknie uchwyt?

**Odpowiedź.** Nie, bo konstrukcja klasy nie została ukończona. Zasób musi już należeć do skonstruowanego pola RAII lub lokalnego strażnika. Wtedy jego własny destruktor wykona sprzątanie podczas obsługi niepowodzenia konstruktora.

Źródła: [destruktory](https://timsong-cpp.github.io/cppwp/n4950/class.dtor), [obsługa wyjątków w konstrukcji](https://timsong-cpp.github.io/cppwp/n4950/except.ctor), [zakończenie przez terminate](https://timsong-cpp.github.io/cppwp/n4950/except.terminate).

## Powiązane tematy

- [Konstruktory i destruktory](../04_klasy_i_model_obiektowy/02_konstruktory_i_destruktory.md)
- [Exception safety](../07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md)
- [Rule of zero](04_copy_move_i_rule_of_zero.md)

