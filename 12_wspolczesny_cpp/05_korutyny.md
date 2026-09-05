[← Spis treści](../README.md)

# Korutyny

Korutyna może zawiesić wykonanie i później je wznowić, zachowując stan w coroutine frame. Słowa `co_await`, `co_yield` i `co_return` uruchamiają transformację kompilatora. C++20 dostarcza mechanikę, ale nie standardowy typ `task`, event loop ani model I/O async.

Minimalny generator wymaga własnego `promise_type`, zarządzania uchwytem i iteratora, dlatego pełny przykład jest dłuższy niż zwykła funkcja. Poniższy szkic pokazuje kształt API biblioteki, nie samowystarczalny C++23:

~~~cpp,notest
generator<int> sequence() {
    for (int value = 0; value < 3; ++value) {
        co_yield value;
    }
}

task<Response> fetch(Client& client) {
    Response response = co_await client.get("/status");
    co_return response;
}
~~~

Typ zwracany wybiera `promise_type`. Kompilator tworzy frame, wywołuje `get_return_object`, `initial_suspend`, a przy końcu `final_suspend`. Wyrażenie `co_await` jest przekształcane do awaitera z metodami `await_ready`, `await_suspend` i `await_resume`. Szczegóły są opisane w dziale zaawansowanym.

Zawieszenie nie tworzy automatycznie nowego wątku. To awaiter/executor decyduje, kiedy i gdzie nastąpi wznowienie. Dane referencyjne przechowywane w frame muszą żyć wystarczająco długo. Właściciel ramki odpowiada za jej zniszczenie przez `destroy()` w legalnym stanie zawieszenia; destruktor samego `std::coroutine_handle` nie zwalnia ramki. Biblioteka musi precyzyjnie określić własność.

Anulowanie jest kooperacyjne i wymaga kontraktu cancellation safety. Operacja przerwana w połowie nie może zgubić odpowiedzi, blokady lub bajtów protokołu w sposób mylący kolejne wywołanie.

## Jak to działa krok po kroku

Wywołanie korutyny przygotowuje jej stan i obiekt zwrotny. Parametry przekazane przez wartość mogą znaleźć się w ramce jako posiadane wartości; referencje nadal odnoszą się do cudzych obiektów. `initial_suspend` decyduje, czy ciało zacznie działać od razu. Jeżeli zwraca `suspend_always`, użytkownik otrzymuje korutynę oczekującą na pierwsze wznowienie.

Gdy wykonanie dociera do `co_await`, awaiter odpowiada, czy wynik jest już gotowy. Jeśli tak, zawieszenie może nie nastąpić. W przeciwnym przypadku mechanizm zawieszenia pozwala przekazać sterowanie i ustalić dalsze wznowienie. Po wznowieniu `await_resume` dostarcza wynik albo zgłasza błąd zgodnie z własnym kontraktem. Samo wystąpienie słowa `co_await` nie oznacza utworzenia wątku.

Po `co_return` korutyna dochodzi do `final_suspend`. Jeżeli pozostaje tam zawieszona, jej ramka nadal istnieje, mimo że ciało zakończyło obliczenia. Właściciel musi ją później zniszczyć. Zakończenie obliczeń, wznowienie i zniszczenie ramki to trzy różne operacje.

## Pogłębienie mechanizmu

`std::coroutine_handle` jest niskopoziomowym uchwytem, którego destruktor sam nie zwalnia ramki. Potrzebny jest typ RAII kodujący własność. Skopiowanie uchwytu nie tworzy drugiej korutyny; tworzy kolejną drogę dostępu do tej samej ramki. Dwóch właścicieli wywołujących `destroy()` doprowadzi do błędu.

Ramka może zawierać parametry, lokalne obiekty potrzebne po zawieszeniu, promise i informację o miejscu wznowienia. Często wymaga alokacji, choć implementacja może ją eliminować w określonych warunkach. Nie należy oceniać kosztu korutyny wyłącznie na podstawie krótkiego ciała funkcji. Długo żyjący bufor lokalny może zwiększyć rozmiar każdej jednocześnie istniejącej operacji.

Wyjątki pochodzące z ciała trafiają do `unhandled_exception`. Biblioteka może zachować `exception_ptr` i przekazać błąd odbiorcy albo zakończyć proces według własnej polityki. Sam język nie wybiera za autora aplikacji uniwersalnego kanału błędów. Anulowanie również wymaga umowy: trzeba wiedzieć, co dzieje się z rozpoczętym I/O i kto jeszcze może wznowić korutynę.

## Drugi przykład

~~~cpp
#include <cassert>
#include <coroutine>
#include <exception>
#include <utility>

class StepTask {
public:
    struct promise_type {
        std::exception_ptr error;
        StepTask get_return_object() {
            return StepTask{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_always initial_suspend() noexcept { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_void() noexcept {}
        void unhandled_exception() noexcept { error = std::current_exception(); }
    };
    using Handle = std::coroutine_handle<promise_type>;
    explicit StepTask(Handle handle) noexcept : handle_{handle} {}
    StepTask(const StepTask&) = delete;
    StepTask& operator=(const StepTask&) = delete;
    StepTask(StepTask&& other) noexcept : handle_{std::exchange(other.handle_, {})} {}
    ~StepTask() { if (handle_) handle_.destroy(); }

    bool resume() {
        if (!handle_ || handle_.done()) return false;
        handle_.resume();
        if (handle_.promise().error) std::rethrow_exception(handle_.promise().error);
        return !handle_.done();
    }
private:
    Handle handle_;
};

StepTask stages(int& state) {
    state = 1;
    co_await std::suspend_always{};
    state = 2;
}

int main() {
    int state = 0;
    auto task = stages(state);
    assert(state == 0);
    const bool paused = task.resume();
    assert(paused && state == 1);
    const bool more = task.resume();
    assert(!more && state == 2);
    assert(!task.resume());
}
~~~

Pierwsze wywołanie `resume` dochodzi do jawnego zawieszenia. Drugie kończy ciało i zatrzymuje korutynę na `final_suspend`. Destruktor `task` usuwa ramkę. `state` zostało utworzone wcześniej, więc żyje przez całe użycie korutyny. Przykład jest sterowany ręcznie w jednym wątku; równoczesne wywołania `resume` lub `destroy` nie są obsługiwane przez ten typ.

## Porównanie i decyzje

Do prostego synchronicznego przetwarzania pętla bywa wystarczająca. Korutyna pomaga, gdy naturalny opis algorytmu musi zachować lokalny stan pomiędzy kolejnymi żądaniami wyniku lub etapami oczekiwania. C++23 dodaje `std::generator` dla określonego modelu synchronicznego generowania wartości; nie jest on uniwersalnym typem asynchronicznego zadania.

Dla aplikacji sieciowej zwykle wybierz bibliotekę określającą scheduler, anulowanie i własność operacji. Samodzielny typ zadania jest dobrym ćwiczeniem mechaniki, ale wymaga znacznie szerszego projektu, zanim stanie się podstawą wykonania aplikacji. Szczególnie ważne jest, by callback nie próbował wznowić ramki już zniszczonej przy anulowaniu.

## Ćwiczenie z odpowiedzią

Co stanie się po zniszczeniu `task` tuż po pierwszym wznowieniu? Ramka zostanie zwolniona bez wykonania pozostałej części ciała, więc `state` pozostanie równe 1. Dlaczego nie można potem użyć zachowanej kopii surowego uchwytu? Wskazywałaby na ramkę, która już nie istnieje. `done()` także nie jest metodą sprawdzania ważności dowolnego wiszącego uchwytu.

Podstawa transformacji: [C++23, coroutine definitions](https://timsong-cpp.github.io/cppwp/n4950/dcl.fct.def.coroutine).

## Powiązane tematy

- [Mechanika korutyn](../zaawansowane/12_korutyny_promise_awaitery_i_frame.md)
- [future i async](../10_wspolbieznosc/03_future_promise_async.md)
- [Sieć i serializacja](../11_io_i_system/05_siec_serializacja_i_granice_std.md)

