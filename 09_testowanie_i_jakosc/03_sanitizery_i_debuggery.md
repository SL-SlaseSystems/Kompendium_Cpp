[← Spis treści](../README.md)

# Sanitizery i debuggery

Sanitizery instrumentują program, aby wykrywać klasy błędów podczas wykonania. AddressSanitizer znajduje wiele use-after-free, buffer overflow i błędów stosu. UndefinedBehaviorSanitizer wykrywa wybrane przypadki UB. ThreadSanitizer szuka data races. MemorySanitizer śledzi niezainicjalizowane odczyty, lecz ma bardziej wymagające środowisko. Dostępność i łączenie sanitizerów zależy od platformy.

~~~text
clang++ -std=c++23 -g -O1 -fno-omit-frame-pointer \
  -fsanitize=address,undefined main.cpp -o app
./app
~~~

Instrumentowane powinny być zarówno kompilacja, jak i linkowanie. `-g` umożliwia symbolizację, `-O1` zachowuje realistyczniejszy kod niż całkowity brak optymalizacji, a frame pointers pomagają stosom wywołań. Sanitizery nie dowodzą braku UB — obserwują tylko wykonane ścieżki i wspierane klasy problemów.

~~~cpp
#include <cassert>
#include <vector>

int checked_at(const std::vector<int>& values, std::size_t index) {
    return values.at(index);
}

int main() {
    const std::vector values{10, 20};
    assert(checked_at(values, 1) == 20);
}
~~~

Debugger, np. GDB, LLDB albo debugger Visual Studio, pozwala zatrzymać program, badać stos, zmienne, pamięć i wątki. Watchpoint reaguje na zmianę pamięci. Core dump zachowuje stan po awarii. Przy optymalizacji zmienne mogą być usunięte lub przemieszczone, dlatego debug i release trzeba analizować świadomie.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Sanitizery i debuggery”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz sformułowanie hipotezy, przygotowanie kontrolowanego wejścia, zebranie wyniku, porównanie z oczekiwaniem i zachowanie reprodukcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd funkcjonalny, undefined behavior, problem przenośności i regresję wydajności, ponieważ wymagają innych narzędzi. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przypadek, kod wyjścia, raport sanitizera, statystyczny rozkład pomiarów i konfigurację kompilacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Żadne pojedyncze narzędzie nie dowodzi poprawności programu C++. Test sprawdza zachowanie dla danych, analiza statyczna szuka wzorców, sanitizer obserwuje wykonanie, a profiler mierzy koszt; wiarygodność daje dopiero połączenie niezależnych dowodów. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- ASan wykrywa wiele naruszeń pamięci, UBSan instrumentuje wybrane UB, a TSan szuka data races. Instrumentacje zmieniają timing i nie pokrywają wszystkich błędów, ale raport z reprodukcją jest silniejszy niż sam crash.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Sanitizery i debuggery” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Sanitizery i debuggery
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Sanitizery i debuggery”, oceniaj zdolność wykrycia realnej regresji, powtarzalność, koszt utrzymania testu i reprezentatywność środowiska. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Uruchamiaj sanitizer build w CI na rozbudowanych testach. TSan zwykle działa osobno od ASan. Nie ignoruj raportu tylko dlatego, że program „jeszcze nie crashuje”. Minimalizuj reprodukcję i najpierw napraw źródło naruszenia lifetime lub synchronizacji.

## Powiązane tematy

- [Undefined behavior](../zaawansowane/01_undefined_behavior_i_model_maszyny.md)
- [Atomiki i model pamięci](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md)
- [Fuzzing](05_fuzzing_i_property_based_testing.md)

