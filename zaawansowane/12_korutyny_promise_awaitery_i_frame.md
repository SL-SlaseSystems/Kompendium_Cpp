[← Spis treści](../README.md)

# Korutyny: promise, awaitery i frame

Kompilator przekształca funkcję korutynową w maszynę stanów z coroutine frame. Frame przechowuje parametry, lokalne wartości żyjące przez zawieszenie, promise object i bookkeeping. Alokacja frame może zostać zoptymalizowana lub dostosowana przez `promise_type::operator new`, ale nie należy zakładać konkretnej lokalizacji.

~~~cpp
#include <cassert>
#include <coroutine>
#include <exception>
#include <utility>

class Task {
public:
    struct promise_type {
        Task get_return_object() {
            return Task{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_always initial_suspend() noexcept { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };

    explicit Task(std::coroutine_handle<promise_type> handle) : handle_{handle} {}
    Task(const Task&) = delete;
    Task(Task&& other) noexcept : handle_{std::exchange(other.handle_, {})} {}
    ~Task() { if (handle_) handle_.destroy(); }
    void resume() { handle_.resume(); }
    bool done() const { return handle_.done(); }

private:
    std::coroutine_handle<promise_type> handle_;
};

Task two_steps(int& state) {
    state = 1;
    co_await std::suspend_always{};
    state = 2;
}

int main() {
    int state = 0;
    Task task = two_steps(state);
    task.resume();
    assert(state == 1 && !task.done());
    task.resume();
    assert(state == 2 && task.done());
}
~~~

`initial_suspend` decyduje, czy wykonanie zaczyna się od razu. `final_suspend` musi pozostawić frame w stanie zgodnym z modelem właściciela; zniszczenie uchwytu przed końcem kończy frame bez zwykłego „return”. Double destroy lub resume po done to poważny błąd kontraktu.

`co_await expr` uzyskuje awaiter, pyta `await_ready`, a jeśli trzeba zawiesić, wywołuje `await_suspend` z uchwytem. `await_resume` produkuje wynik po wznowieniu. Awaiter może wznowić inną korutynę, zapisać continuation lub zorganizować symmetric transfer.

Parametry referencyjne nie są automatycznie kopiowane do bezpiecznej własności. `two_steps` wymaga, by `state` przeżył task. Produkcyjny task musi także określić propagację wyjątku, cancellation, executor i structured lifetime.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Korutyny: promise, awaitery i frame”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Promise zapisuje wynik współdzielonego stanu, a future pobiera go najwyżej zgodnie z kontraktem danego typu. Polityka `std::async` może dopuścić wykonanie deferred, więc jawna polityka jest potrzebna, gdy wymagany jest osobny wątek.
- Korutyna jest transformowana do maszyny stanów z ramką przechowującą parametry i lokale żyjące przez zawieszenie. Typ zwracany oraz `promise_type` definiują protokół, a sam język nie dostarcza schedulera.
- `co_await` jest rozwijane przez protokół `await_ready`, `await_suspend` i `await_resume`. Ownership coroutine handle oraz chwila zniszczenia frame muszą być jawne, szczególnie przy wyjątkach i anulowaniu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Korutyny: promise, awaitery i frame” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Korutyny: promise, awaitery i frame
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Korutyny: promise, awaitery i frame”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Wprowadzenie do korutyn](../12_wspolczesny_cpp/05_korutyny.md)
- [future, promise i async](../10_wspolbieznosc/03_future_promise_async.md)
- [Lifetime](02_lifetime_aliasing_i_pointer_provenance.md)
