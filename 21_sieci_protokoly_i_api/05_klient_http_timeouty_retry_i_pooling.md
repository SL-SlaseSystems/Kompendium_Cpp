[← Spis treści](../README.md)

# Klient HTTP: timeouty, retry i pooling

Klient HTTP zarządza jednocześnie czasem, niepewnością wyniku i czasem życia połączeń. Timeout oznacza, że klient nie otrzymał wyniku w terminie. Nie dowodzi, że serwer nie wykonał operacji. Jeżeli wysyłasz zlecenie obciążenia karty, utrata odpowiedzi po zatwierdzeniu płatności jest zupełnie inną sytuacją niż błąd DNS przed otwarciem połączenia. Typ błędu powinien zachować tę różnicę, zamiast sprowadzać wszystko do `false`.

C++23 nie zawiera kompletnego klienta HTTP. Poniższe programy są wykonywalnymi modelami polityki czasu i własności zasobów. Nie implementują DNS, TCP, TLS, parsera HTTP ani integracji z pętlą zdarzeń. Ich rolą jest pokazanie kontraktu, który następnie trzeba odwzorować na konkretne API sieciowe.

## Jak to działa krok po kroku

Najpierw ustal deadline całej operacji przy użyciu zegara monotonicznego. Obejmuje on oczekiwanie w kolejce, pobranie połączenia z puli, rozwiązywanie nazwy, zestawienie transportu, TLS, wysłanie danych, odczyt odpowiedzi i ewentualną przerwę przed ponowieniem. Timeout pojedynczej próby ogranicza tylko tę próbę. Nadanie każdej próbie pełnego budżetu operacji wydłuża żądanie wraz z liczbą ponowień.

Dla każdej próby wyznacz granicę `min(global_deadline, now + attempt_timeout)`. Wewnątrz próby poszczególne fazy także mogą mieć limity, ale muszą dziedziczyć pozostały czas. Timer bezczynności odświeżany przy każdym bajcie nie zastępuje deadline: serwer wysyłający bajt co sekundę może utrzymywać transfer bez końca. Osobno ogranicz rozmiar nagłówków i treści, aby szybki transfer nie wyczerpał pamięci.

Pierwszy program ma zegar logiczny w milisekundach. Koszty faz są danymi wejściowymi; nie usypiamy procesu. Dwie próby mają limit 500 ms, natomiast cała operacja 800 ms. Przerwa 100 ms też zużywa budżet. Druga próba otrzymuje zaledwie 250 ms i kończy się na globalnym deadline.

~~~cpp
#include <algorithm>
#include <cassert>
#include <chrono>
#include <iostream>
#include <vector>

using namespace std::chrono_literals;
using Ms = std::chrono::milliseconds;

enum class Outcome { success, transient_failure, timeout };
struct Attempt { std::vector<Ms> phases; Outcome result; };

Outcome execute(Ms& now, Ms limit, const Attempt& attempt) {
    for (Ms cost : attempt.phases) {
        assert(cost >= 0ms);
        if (cost >= limit - now) {
            now = limit;
            return Outcome::timeout;
        }
        now += cost;
    }
    return attempt.result;
}

int main() {
    Ms now = 0ms;
    const Ms deadline = 800ms;
    const Ms per_attempt = 500ms;
    const std::vector<Attempt> script{
        {{100ms, 150ms, 200ms}, Outcome::transient_failure},
        {{50ms, 250ms}, Outcome::success}
    };
    Outcome result = Outcome::timeout;
    for (std::size_t i = 0; i < script.size(); ++i) {
        if (now >= deadline) break;
        // Najpierw odejmowanie: brak now + nieograniczony timeout.
        const Ms allowance = std::min(per_attempt, deadline - now);
        result = execute(now, now + allowance, script[i]);
        if (result == Outcome::success) break;
        if (i + 1 == script.size() || now >= deadline) break;
        const Ms pause = 100ms;
        if (pause >= deadline - now) { now = deadline; break; }
        now += pause;
    }
    assert(result == Outcome::timeout && now == 800ms);
    std::cout << "elapsed_ms=" << now.count() << '\n';
}
~~~

W prawdziwym adapterze ustawiasz timer przed rozpoczęciem asynchronicznej operacji. Gdy timer wygra wyścig, anulujesz operację i odbierasz jej zakończenie. Samo zwrócenie błędu timeout z wyższej warstwy nie daje prawa zwolnienia bufora, który nadal wykorzystuje transport. Do czasu potwierdzenia zakończenia potrzebny jest właściciel stanu operacji.

## Pogłębienie mechanizmu

Bezpieczne ponowienie wymaga dwóch niezależnych warunków: awaria ma szansę ustąpić oraz powtórzenie nie zepsuje znaczenia operacji. Błąd walidacji certyfikatu nie powinien rozpoczynać burzy prób. Kod 503 może uzasadniać odczekanie, ale nie rozstrzyga, czy wcześniej wykonano efekt biznesowy. Decyzję wiąż z kontraktem endpointu, a nie wyłącznie z kategorią błędu biblioteki.

RFC rozróżnia bezpieczeństwo metody od idempotencji. GET ma semantykę bezpieczną; PUT i DELETE są idempotentne, choć zmieniają stan. Idempotencja dotyczy zamierzonego efektu, a nie identycznej odpowiedzi. Ponawianie POST po utracie odpowiedzi wymaga wiedzy o jego kontrakcie albo dowodu, że pierwsza próba nie została zastosowana. [RFC 9110, §9.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2).

Praktyczny kontrakt tworzenia zamówienia może przyjmować stabilny klucz idempotencji. Ta sama operacja zachowuje klucz przez wszystkie próby, a serwer atomowo zapamiętuje wynik i odrzuca użycie klucza z innym żądaniem. Sama obecność dowolnego nagłówka niczego nie gwarantuje. Musisz znać zakres klucza, okres przechowywania i zachowanie żądań równoległych. Strumieniowaną treść trzeba dodatkowo umieć odtworzyć; idempotentny endpoint nie odtworzy zużytego lokalnego strumienia.

`Retry-After` może wskazywać czas oczekiwania jako liczbę sekund albo datę HTTP. Oczekiwanie musi mieścić się w pozostałym budżecie; długa wskazówka serwera może oznaczać zakończenie żądania lokalnie. [RFC 9110, §10.2.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-10.2.3). Dla API stosuj ograniczoną liczbę prób i jawny kontrakt ponowień; RFC dodatkowo odradza automatyczne ponawianie nieudanej automatycznej próby.

## Drugi przykład

Pooling jest protokołem wypożyczenia, a nie tylko wektorem uchwytów. Połączenie wraca do puli dopiero wtedy, gdy można je bezpiecznie użyć ponownie. Dla HTTP/1.1 nieprzeczytana treść odpowiedzi może pozostawić bajty, które kolejny parser uzna za nową odpowiedź. Adapter powinien doczytać treść w dozwolonym budżecie albo zamknąć transport. Szczegóły ponownego użycia zależą od wersji protokołu i biblioteki.

Model poniżej jest jednowątkowy. `Lease` utrzymuje stan puli przez `shared_ptr`, więc fasada puli nie musi żyć dłużej niż każde wypożyczenie. Stan `closing` zabrania kolejnego pobrania i zwrotu do zbioru bezczynnych połączeń. Bez jawnego potwierdzenia zużycia treści wypożyczony zasób jest odrzucany. Numer zastępuje tutaj prawdziwy socket.

~~~cpp
#include <cassert>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <utility>
#include <vector>

struct State { bool closing = false; std::vector<int> idle{41}; };

class Lease {
    std::shared_ptr<State> state_;
    int socket_;
    bool reusable_ = false;
public:
    Lease(std::shared_ptr<State> s, int socket)
        : state_(std::move(s)), socket_(socket) {}
    Lease(const Lease&) = delete;
    Lease& operator=(const Lease&) = delete;
    Lease(Lease&& other) noexcept
        : state_(std::move(other.state_)), socket_(other.socket_),
          reusable_(other.reusable_) {}
    Lease& operator=(Lease&&) = delete;
    void body_consumed() noexcept { reusable_ = true; }
    ~Lease() {
        if (!state_) return;
        // Model ma jeden slot i zachowaną pojemność vectora.
        if (reusable_ && !state_->closing) state_->idle.push_back(socket_);
        else std::cout << "close " << socket_ << '\n';
    }
};

class Pool {
    std::shared_ptr<State> state_ = std::make_shared<State>();
public:
    Lease acquire() {
        if (state_->closing || state_->idle.empty())
            throw std::runtime_error("pool unavailable");
        const int socket = state_->idle.back();
        state_->idle.pop_back();
        return Lease(state_, socket);
    }
    std::weak_ptr<State> inspect() const { return state_; }
    void close() noexcept { state_->closing = true; state_->idle.clear(); }
    ~Pool() { close(); }
};

int main() {
    auto pool = std::make_unique<Pool>();
    auto state = pool->inspect();
    { auto lease = pool->acquire(); lease.body_consumed(); }
    assert(state.lock()->idle.size() == 1);
    {
        auto lease = pool->acquire();
        pool.reset();
        assert(!state.expired());
        lease.body_consumed(); // Zamknięta pula i tak odrzuci transport.
    }
    assert(state.expired());
}
~~~

Produkcyjny zwrot zasobu w destruktorze musi być niezgłaszający i niealokujący. Tutaj zachowana pojemność jednego slotu zapewnia miejsce, ale ogólny pool potrzebuje z góry przydzielonych węzłów lub innego mechanizmu. Dostęp wielowątkowy wymaga synchronizacji; `shared_ptr` chroni czas życia, nie pola obiektu. Pula także potrzebuje limitu aktywnych połączeń i kolejki oczekujących z deadline.

## Porównanie i decyzje

Krótki czas connect pomaga szybko zmienić niedostępny adres, lecz nie powinien skracać wszystkich transferów dużych plików. Globalny deadline chroni opóźnienie widziane przez użytkownika; limity faz pomagają zdiagnozować i przerwać konkretny rodzaj zastoju. Wspólne przekazywanie deadline przez warstwy utrzymuje te decyzje spójne.

Pooling oszczędza zestawianie połączeń i TLS, ale zatrzymuje pamięć, deskryptory i stan uwierzytelnienia. Klucz puli musi uwzględniać odpowiedni origin, konfigurację proxy i kontekst bezpieczeństwa. Nie mieszaj klientów wymagających różnych certyfikatów klienta. Dodaj maksymalny czas bezczynności i życia połączenia; zdalny koniec może je zamknąć niezależnie od lokalnej polityki.

Mierz osobno czas oczekiwania na pool, czas próby i czas całej operacji. Jeden histogram „HTTP latency” ukryje przeciążenie lokalnej puli pod pozorem wolnego serwera. Zapisuj liczbę prób i przyczynę końcową, a identyfikator konkretnego żądania umieszczaj w śladzie lub logu.

Przed odczekaniem zwolnij wypożyczony zasób, jeżeli dana próba już się zakończyła. Trzymanie połączeń podczas backoff może wyczerpać pulę właśnie wtedy, gdy zależność ma kłopoty. Z drugiej strony zwrot do puli przed potwierdzeniem anulowania aktywnego odczytu pozwoliłby dwóm operacjom używać tego samego transportu. Kolejność brzmi: zakończenie transportu, rozstrzygnięcie ponownego użycia, zwolnienie wypożyczenia, oczekiwanie.

Przekierowania również zużywają globalny budżet i potrzebują limitu liczby przejść. Nowy origin może oznaczać nowy klucz puli, rozwiązywanie nazwy i TLS. Adapter powinien świadomie zdecydować o przekazywaniu uwierzytelnienia oraz o odtwarzaniu treści. Pętla przekierowań nie może dostawać nieograniczonego czasu tylko dlatego, że każda pojedyncza odpowiedź przyszła szybko. W teście polityki warto osobno zasymulować wyczerpanie budżetu przez oczekiwanie na połączenie i przez odczyt treści.

## Ćwiczenia

1. Operacja ma 900 ms budżetu. Pierwsza próba zużyła 500 ms, a wymagane oczekiwanie wynosi 450 ms. Czy uruchomić drugą próbę z timeoutem 500 ms?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Nie. Już samo oczekiwanie przekroczyłoby pozostałe 400 ms. Zakończ operację odpowiednim błędem budżetu; przydzielenie nowego timeoutu utworzyłoby inny kontrakt czasu niż zaakceptowany na wejściu.

</details>

2. Odpowiedź została odebrana częściowo, a klient przestał jej potrzebować. Czy destruktor odpowiedzi powinien bezwarunkowo zwrócić HTTP/1.1 socket do puli?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Nie. Adapter musi ustalić granicę wiadomości i zużyć pozostałą treść albo odrzucić połączenie. RAII rozstrzyga własność, lecz poprawne ponowne użycie wymaga również zachowania stanu protokołu.

</details>

## Powiązane tematy

- [HTTP i REST](02_http_i_rest.md)
- [TLS, certyfikaty i zaufanie](03_tls_certyfikaty_i_zaufanie.md)
- [Retry, backoff i idempotencja](../24_messaging_i_systemy_rozproszone/02_retry_backoff_i_idempotencja.md)
