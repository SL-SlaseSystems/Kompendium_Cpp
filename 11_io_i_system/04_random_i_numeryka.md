[← Spis treści](../README.md)

# random i numeryka

Biblioteka `<random>` rozdziela silnik generujący pseudolosowe bity od rozkładu mapującego je na wartości. `std::mt19937` jest deterministycznym silnikiem o dobrych właściwościach do symulacji, ale nie jest kryptograficznie bezpieczny. `std::random_device` może dostarczać entropię albo zachowywać się zależnie od implementacji.

~~~cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <random>

int main() {
    std::mt19937 engine{12345};
    std::uniform_int_distribution<int> die{1, 6};
    const int roll = die(engine);
    assert(roll >= 1 && roll <= 6);

    std::array values{1, 2, 3, 4};
    std::shuffle(values.begin(), values.end(), engine);
    std::ranges::sort(values);
    assert((values == std::array{1, 2, 3, 4}));
}
~~~

Stały seed pomaga odtworzyć test przy zachowaniu silnika, implementacji rozkładu i kolejności wywołań. W aplikacji można seedować z `random_device` lub kontrolowanego źródła, ale zapisuj seed symulacji, aby odtworzyć błąd. Nie generuj zakresu przez `engine() % n`, bo modulo może wprowadzać bias; użyj odpowiedniego distribution.

Nagłówek `<numeric>` oferuje `accumulate`, `inner_product`, `iota` oraz algorytmy skanowania. C++17 dodał warianty umożliwiające przestawianie działań, dlatego wyniki floating point mogą różnić się kolejnością zaokrągleń. `std::reduce` ma inne wymagania niż sekwencyjne `accumulate`.

Overflow signed integer pozostaje UB także w obliczeniach numerycznych. Sprawdzaj zakres przed działaniem albo używaj typu i biblioteki odpowiadającej domenie. Dla kryptografii, statystyki i dużych liczb wybierz zweryfikowaną bibliotekę; standardowe prymitywy nie tworzą kompletnego rozwiązania domenowego.

## Jak to działa krok po kroku

Silnik przechowuje stan. Każde jego wywołanie produkuje liczbę i przesuwa stan do następnego kroku. Rozkład pobiera tyle wyników silnika, ile potrzebuje do skonstruowania wartości z wybranej przestrzeni. Jeden rzut kostką nie musi odpowiadać dokładnie jednemu wywołaniu silnika. Dlatego dopisanie losowania w innym miejscu może zmienić wszystkie późniejsze wyniki symulacji.

Rozpocznij test od stałego seeda, zapisz dane wejściowe i oczekiwane własności. Sprawdź zakres i inwarianty, a nie tylko pojedynczą „losową” wartość. Dla debugowania długiej symulacji potrzebujesz także wersji algorytmu i informacji o strumieniach losowych. Sam seed nie odtworzy programu, w którym zmieniła się kolejność wywołań generatora.

## Pogłębienie mechanizmu

Standaryzowany silnik, taki jak `mt19937`, ma zdefiniowaną transformację stanu. Algorytm mapowania wielu rozkładów nie jest identycznie określony dla wszystkich implementacji biblioteki. Ten sam seed i silnik nie gwarantują więc identycznej sekwencji wyników `uniform_int_distribution` między różnymi bibliotekami. Dla bitowej reprodukowalności określ również metodę mapowania, wersję i format stanu.

Bias modulo wynika z nierównej liczby reprezentantów reszt. Jeżeli źródło daje równomiernie liczby od 0 do 7, reszty modulo 3 to `0,1,2,0,1,2,0,1`: zero i jeden występują po trzy razy, a dwa tylko dwa razy. Poprawny rozkład może odrzucać część wyników, aby wyrównać prawdopodobieństwa. Dodanie bardziej złożonego wyrażenia modulo nie usuwa tego problemu.

Zmiennoprzecinkowe dodawanie nie jest łączne ze względu na zaokrąglenia. Zmiana kolejności sumowania może zmienić wynik bez błędu kompilatora. `accumulate` definiuje sekwencyjne narastanie akumulatora; `reduce` dopuszcza przegrupowania także bez równoległej polityki. Typ wartości początkowej wpływa na typ akumulatora: `0` i `0.0` nie są zamiennymi argumentami dla sumy wartości ułamkowych.

## Drugi przykład

~~~cpp
#include <array>
#include <cassert>
#include <numeric>
#include <random>

int main() {
    const std::array values{0.5, 0.5, 0.5};
    const int truncated = std::accumulate(values.begin(), values.end(), 0);
    const double exact_here = std::accumulate(values.begin(), values.end(), 0.0);
    assert(truncated == 0);
    assert(exact_here == 1.5);

    std::mt19937 a{123u};
    auto b = a;
    for (int i = 0; i < 10; ++i) {
        const auto x = a();
        const auto y = b();
        assert(x == y);
    }
}
~~~

Akumulator typu `int` przy każdej iteracji traci część ułamkową; to nie jednorazowe zaokrąglenie ostatecznego wyniku. Wartości połówkowe wybrano celowo, aby przykład nie zależał od subtelności dziesiętnych ułamków binarnych. Kopia silnika zawiera kopię stanu, więc dalsze identyczne wywołania dają identyczne wyniki. Nie jest to utworzenie niezależnego strumienia losowego.

## Porównanie i decyzje

Do zwykłych symulacji wybierz silnik i rozkład dostosowane do modelu, z jawną polityką seedowania. Do tokenów uwierzytelniających używaj kryptograficznego generatora zapewnianego przez sprawdzoną bibliotekę lub system. Duży okres `mt19937` nie oznacza odporności na przewidywanie. `random_device` ma kontrakt zależny od implementacji i może też zgłosić błąd.

W wielowątkowości unikaj równoczesnych niesynchronizowanych wywołań tego samego silnika. Osobne silniki rozwiązują data race, ale sposób doboru ich strumieni pozostaje problemem statystycznym. W obliczeniach numerycznych określ tolerancję błędu, obsługę NaN i nieskończoności oraz wymagany zakres; zwykłe „wyniki są prawie równe” nie jest pełnym kontraktem.

## Ćwiczenie z odpowiedzią

Czy skopiowanie generatora na początku każdego zadania daje niezależne losowania? Nie, zadania startują z tego samego stanu i mogą otrzymywać identyczne sekwencje. Czy zastąpienie zera przez `0.0` naprawia każdy błąd sumy? Nie: usuwa konkretną utratę ułamków przez typ akumulatora, lecz nie znosi zaokrągleń ani problemów kondycjonowania obliczeń.

Źródło kontraktów silników i rozkładów: [C++23, random number generation requirements](https://timsong-cpp.github.io/cppwp/n4950/rand.req).

## Powiązane tematy

- [Typy podstawowe](../02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
- [Algorytmy](../06_biblioteka_standardowa/05_algorytmy_i_lambdy.md)
- [Testy i fuzzing](../09_testowanie_i_jakosc/05_fuzzing_i_property_based_testing.md)

