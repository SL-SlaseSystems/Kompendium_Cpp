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

Wywołanie `two_steps(state)` tworzy stan korutyny, umieszcza w nim potrzebne kopie parametrów i konstruuje promise. `get_return_object` buduje `Task`, który przejmuje odpowiedzialność za ramkę. `initial_suspend` zwraca `suspend_always`, dlatego samo wywołanie funkcji nie wykonuje jeszcze przypisania `state = 1`. To model lazy start, niezależny od uruchamiania wątków.

Pierwsze `resume` przechodzi przez początkowe zawieszenie i wykonuje kod do kolejnego `co_await`. `state` staje się `1`, a ramka zachowuje punkt wznowienia. Drugie `resume` wykonuje dalszą część, ustawia `2` i dochodzi do końca funkcji, równoważnego odpowiedniemu `co_return`. Promise obsługuje zakończenie, a `final_suspend` pozostawia ramkę istniejącą. Dopiero destruktor `Task` wywołuje `destroy` i zwalnia jej zasoby.

## Pogłębienie mechanizmu

`coroutine_handle` jest lekkim uchwytem do ramki, nie jej automatycznym właścicielem. Skopiowanie uchwytu nie liczy referencji i nie zabezpiecza przed podwójnym `destroy`. Wrapper powinien definiować własność, przenoszenie i zachowanie pustego stanu. W pokazanym `Task` wolno badać `done` i wznawiać tylko niepusty, odpowiednio zawieszony uchwyt; wznowienie korutyny na final suspend narusza kontrakt. Bezpieczniejszy interfejs produkcyjny sprawdza stan lub ukrywa ręczne `resume` przed klientem.

Transformacja `co_await` może najpierw przejść przez `promise.await_transform`, następnie odpowiedni `operator co_await`, a dopiero potem otrzymuje awaiter. `await_ready` zwracające `true` pomija zawieszenie i prowadzi do `await_resume`. Gdy potrzebne jest zawieszenie, `await_suspend` otrzymuje uchwyt już zawieszonej korutyny. Może zwrócić `void`, wartość logiczną albo inny coroutine handle, określając sposób przekazania sterowania.

Publikacja uchwytu innemu wątkowi wewnątrz `await_suspend` wymaga synchronizacji. Inny wątek może wznowić korutynę, zanim `await_suspend` zakończy działanie, a awaiter może zostać już zniszczony. Po publikacji nie wolno bez odpowiedniego dowodu dalej korzystać z jego pól. To jedna z przyczyn, dla których poprawny awaiter sieciowy wymaga znacznie więcej niż zapisania callbacka.

Parametr przez wartość zostaje przeniesiony lub skopiowany do stanu według reguł korutyny. Parametr przez referencję zachowuje referencję. Również przechwycenia korutynowej lambdy należą do obiektu domknięcia i nie stają się automatycznie bezpiecznymi kopiami w ramce. Tymczasowa lambda znikająca po wywołaniu może pozostawić korutynę z odwołaniem do zniszczonych przechwyceń. Często lepiej przekazać potrzebne wartości jako jawne parametry korutyny.

## Drugi przykład

~~~cpp
#include <cassert>
#include <coroutine>
#include <exception>

struct ReadyTask {
    struct promise_type {
        ReadyTask get_return_object() { return {}; }
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };
};
struct Immediate {
    int value;
    bool await_ready() const noexcept { return true; }
    void await_suspend(std::coroutine_handle<>) const noexcept {}
    int await_resume() const noexcept { return value; }
};
ReadyTask compute(int& result) {
    result = co_await Immediate{42};
}
int main() {
    int result = 0;
    compute(result);
    assert(result == 42);
}
~~~

Tutaj korutyna wykonuje się od razu, awaiter nigdy jej nie zawiesza, a końcowe `suspend_never` pozwala automatycznie zniszczyć ramkę. Obiekt wyniku nie przechowuje uchwytu, więc nie próbuje ponownie niszczyć zakończonego stanu. `await_suspend` istnieje dla kompletności protokołu, ale na tej ścieżce nie jest wywołane. Kontrast z pierwszym przykładem pokazuje, że wybór final suspend musi pasować do strategii własności.

## Porównanie i decyzje

Korutyna opisuje zawieszalne obliczenie; executor, pętla zdarzeń, wątek i operacje wejścia/wyjścia są osobnymi elementami biblioteki. Generator synchroniczny może nie potrzebować żadnej synchronizacji. Zadanie asynchroniczne potrzebuje natomiast propagacji wyjątków, reguł anulowania i zachowania po porzuceniu wyniku. `destroy` nie jest uniwersalną operacją anulowania zewnętrznego żądania: callback nadal posiadający uchwyt mógłby później odwołać się do zwolnionej ramki.

**Ćwiczenie.** Czy `Task task = two_steps(local)` może przeżyć `local`? **Odpowiedź:** nie, funkcja używa referencji. Czy `done()` oznacza, że pamięć ramki jest już zwolniona? Nie, przy `suspend_always` w final suspend ramka czeka na właściciela. Czy `co_await` sam tworzy wątek? Nie; przebieg wynika z awaitera i infrastruktury wykonania.

Źródła: [N4950: definicja korutyny](https://timsong-cpp.github.io/cppwp/n4950/dcl.fct.def.coroutine) i [await expression](https://timsong-cpp.github.io/cppwp/n4950/expr.await).

### Wyjątki i niszczenie zawieszonego stanu

Wyjątki z ciała korutyny są kierowane do `unhandled_exception` według transformacji języka. W przykładach wybrano jawne `terminate`, aby nie udawać pełnego transportu błędów. Produkcyjny typ zadania często zapisuje `exception_ptr` w promise, a odbiorca wyniku ponownie zgłasza wyjątek. Błędy tworzenia ramki i początkowych kopii parametrów mają odrębne miejsca wystąpienia; nie wszystkie awarie zadania pojawiają się dopiero przy odbiorze wyniku.

Zniszczenie zawieszonej ramki uruchamia destruktory żywych obiektów przechowywanych w jej stanie. Kod znajdujący się po punkcie zawieszenia nie zostaje jednak zwyczajnie wykonany. Jeżeli sprzątanie zapisano jako instrukcję na końcu ciała zamiast w RAII, porzucenie korutyny może je pominąć. To ten sam argument za destruktorami, który obowiązuje dla wyjątków, zastosowany do dodatkowej drogi kończenia obliczenia.

Rozmiar ramki zależy od wartości, które muszą przetrwać zawieszenie, oraz decyzji optymalizatora. Duży bufor lokalny może zwiększać koszt każdego zadania nawet wtedy, gdy nie jest osobno alokowany przez programistę. Przeniesienie go do krótszego zakresu przed zawieszeniem może pomóc, ale należy sprawdzić faktyczny wynik kompilacji i nie opisywać konkretnego layoutu ramki jako gwarancji języka.

Symmetric transfer przekazuje sterowanie przez zwrócenie uchwytu z await_suspend, zamiast ręcznie wywoływać kolejne resume na zagnieżdżonym stosie wywołań. Może ograniczać narastanie stosu przy łańcuchach zadań, lecz nadal potrzebuje prawidłowej własności obu ramek. Kontynuacja musi pozostać dostępna, a stan zakończonego zadania nie może zostać zniszczony przed odczytaniem wyniku. Nie jest to osobna gwarancja synchronizacji pamięci między wątkami.

## Powiązane tematy

- [Wprowadzenie do korutyn](../12_wspolczesny_cpp/05_korutyny.md)
- [future, promise i async](../10_wspolbieznosc/03_future_promise_async.md)
- [Lifetime](02_lifetime_aliasing_i_pointer_provenance.md)
