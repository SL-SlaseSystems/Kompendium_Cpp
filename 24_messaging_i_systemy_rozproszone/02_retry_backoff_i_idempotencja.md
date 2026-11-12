[← Spis treści](../README.md)

# Retry, backoff i idempotencja

Ponowienie przekształca niepewność sieciową w dodatkową pracę. Jeżeli serwer nie odebrał żądania, kolejna próba może uratować operację. Jeżeli wykonał zmianę, lecz zgubiła się odpowiedź, ta sama próba może wykonać zmianę ponownie. Ograniczenie liczby prób chroni zasoby, ale nie zapewnia poprawności biznesowej. Idempotencja chroni znaczenie operacji, lecz nie ogranicza jej kosztu. Potrzebujesz obu mechanizmów.

Rozróżniaj próbę transportową od operacji logicznej. Operacja „dodaj środki do portfela” ma jeden identyfikator i może składać się z kilku połączeń lub dostarczeń komunikatu. Każda próba dostaje osobny identyfikator diagnostyczny, ale zachowuje identyfikator operacji. Utworzenie nowego klucza idempotencji po timeout niweczy możliwość rozpoznania powtórzenia.

## Jak to działa krok po kroku

Najpierw sklasyfikuj wynik. Błąd składni, odmowa autoryzacji i niespełniony warunek biznesowy zwykle nie poprawią się po odczekaniu. Przejściowe przeciążenie może uzasadniać kolejną próbę, o ile operację wolno powtórzyć. Nieznany wynik zmiany stanu wymaga kontraktu deduplikacji albo sprawdzenia stanu po stronie wykonawcy. Automatyczna pętla łapiąca wszystkie wyjątki nie ma takiej wiedzy.

Następnie wyznacz trzy ograniczenia: maksymalną liczbę prób, deadline całej operacji i timeout próby. Uwzględnij czas kolejki oraz oczekiwania pomiędzy próbami. Nie rozpoczynaj pracy, jeżeli pozostały czas nie pozwala już uzyskać przydatnego wyniku. Anulowanie powinno przerywać również backoff, aby zamykanie procesu nie czekało na koniec minutowego sleep.

Poniższy model używa zegara logicznego w milisekundach. Każda symulowana próba potrzebuje 90 ms; trzecia kończy się sukcesem. Nie ma tu transportu, prawdziwego oczekiwania ani samodzielnej oceny idempotencji. `again` oznacza wynik już zakwalifikowany przez warstwę znającą kontrakt operacji. Full jitter wybiera równomiernie czas od zera do aktualnego limitu.

~~~cpp
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>

using Tick = std::uint64_t;
enum class Status { success, again, permanent, budget };
struct Result { Status status; unsigned attempts; Tick elapsed; };

Tick grow(Tick value, Tick cap) {
    assert(value <= cap);
    return value > cap / 2 ? cap : std::min(cap, value * 2);
}

Result run(Tick budget, unsigned max_attempts, std::mt19937& rng) {
    Tick now = 0;
    Tick ceiling = 50;
    constexpr Tick cap = 160;
    unsigned attempts = 0;
    while (attempts < max_attempts && now < budget) {
        ++attempts;
        Tick allowance = std::min<Tick>(100, budget - now);
        constexpr Tick work = 90;
        if (work >= allowance) {
            now += allowance;
            return {Status::budget, attempts, now};
        }
        now += work;
        Status status = attempts == 3 ? Status::success : Status::again;
        if (status != Status::again) return {status, attempts, now};
        if (attempts == max_attempts) return {status, attempts, now};
        Tick delay = std::uniform_int_distribution<Tick>(0, ceiling)(rng);
        if (delay >= budget - now) return {Status::budget, attempts, now};
        now += delay;
        ceiling = grow(ceiling, cap);
    }
    return {Status::budget, attempts, now};
}

int main() {
    std::mt19937 rng(17); // Stałe ziarno służy odtwarzalności przykładu.
    auto ok = run(500, 4, rng);
    assert(ok.status == Status::success && ok.attempts == 3);
    auto short_budget = run(100, 4, rng);
    assert(short_budget.status == Status::budget);
    assert(short_budget.elapsed <= 100 && short_budget.attempts <= 2);
    assert(grow(UINT64_MAX - 1, UINT64_MAX) == UINT64_MAX);
    std::cout << "success after " << ok.attempts << " attempts\n";
}
~~~

Limit rośnie z nasyceniem, więc nie obliczamy nieograniczonego `base * (1 << attempt)`. Taka formuła może przepełnić mnożenie albo przesunięcie przed zastosowaniem minimum. Równie ważne jest odejmowanie pozostałego czasu przed dodawaniem opóźnienia. Dane konfiguracyjne muszą być dodatnie, przeliczone na wspólną jednostkę i sprawdzone przed uruchomieniem pętli.

## Pogłębienie mechanizmu

Stały backoff sprawia, że duża grupa klientów uderza ponownie w tych samych chwilach. Wzrost wykładniczy ogranicza częstotliwość kolejnych prób, a jitter rozprasza ich synchronizację. Nie zmniejsza jednak liczby klientów ani całkowitego kosztu operacji. Przy awarii potrzebne bywają także ograniczenie współbieżności, admission control i wspólny budżet ponowień na zależność.

Unikaj retry na każdej warstwie. Trzy próby klienta, trzy próby adaptera i trzy dostarczenia brokera mogą uruchomić aż 27 prób wykonania jednego efektu. Wybierz właściciela polityki, propaguj deadline i udostępnij niższym warstwom informację o numerze próby. Mierz próbę oddzielnie od operacji; udana trzecia próba nie oznacza, że zależność obsłużyła tylko jedno żądanie.

HTTP opisuje idempotencję przez zamierzony efekt wielokrotnego identycznego żądania, a nie przez brak jakichkolwiek zapisów czy identyczny status odpowiedzi. Klient nie powinien automatycznie ponawiać nieidempotentnej metody bez dodatkowej wiedzy o bezpieczeństwie powtórzenia lub niewykonaniu pierwszej próby. [RFC 9110, §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2). Reguła ta dobrze ujawnia ogólny problem messagingu: utrata potwierdzenia nie oznacza utraty skutku.

Rekord idempotencji powinien wiązać klucz, zakres uprawnień, kanoniczny opis żądania i wynik. Ten sam klucz z inną kwotą jest konfliktem, nie duplikatem sukcesu. Przy żądaniach równoległych potrzebujesz unikalności klucza i atomowego rozstrzygnięcia wyścigu. Stan `in_progress` wymaga protokołu odzyskiwania po awarii wykonawcy; sam znacznik w cache nie jest dowodem wykonania zmiany.

## Drugi przykład

Ten program modeluje jedną portmonetkę oraz atomowe wykonanie w obrębie procesu. Mutex chroni sprawdzenie klucza, przydzielenie wyniku i zmianę salda. Rekord powstaje przed niezgłaszającą zmianą liczb, więc błąd alokacji mapy nie pozostawi wykonanego efektu bez rekordu. Nie zapewnia to odporności na utratę procesu: trwały wariant wymaga transakcji obejmującej rekord i saldo.

~~~cpp
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <map>
#include <mutex>
#include <stdexcept>
#include <string>
#include <utility>

class Wallet {
    struct Record { std::int64_t amount; std::int64_t balance_after; };
    std::mutex mutex_;
    std::int64_t balance_ = 0;
    std::map<std::pair<std::string, std::string>, Record> records_;
public:
    std::int64_t credit(const std::string& tenant, const std::string& key,
                        std::int64_t amount) {
        if (key.empty() || amount <= 0) throw std::invalid_argument("request");
        std::lock_guard lock(mutex_);
        auto id = std::make_pair(tenant, key);
        if (auto it = records_.find(id); it != records_.end()) {
            if (it->second.amount != amount)
                throw std::invalid_argument("idempotency key conflict");
            return it->second.balance_after;
        }
        if (amount > std::numeric_limits<std::int64_t>::max() - balance_)
            throw std::overflow_error("balance");
        const auto next = balance_ + amount;
        records_.emplace(std::move(id), Record{amount, next});
        balance_ = next;
        return next;
    }
};

int main() {
    Wallet wallet;
    auto first = wallet.credit("shop-a", "operation-7", 500);
    auto replay = wallet.credit("shop-a", "operation-7", 500);
    assert(first == 500 && replay == first); // Utraconą odpowiedź odtwarzamy.
    auto next = wallet.credit("shop-a", "operation-8", 200);
    assert(next == 700);
    bool conflict = false;
    try { (void)wallet.credit("shop-a", "operation-7", 900); }
    catch (const std::invalid_argument&) { conflict = true; }
    assert(conflict);
    std::cout << "first=" << first << " replay=" << replay
              << " next=" << next << '\n';
}
~~~

Wynik duplikatu to zapisany wynik pierwszej operacji, nawet gdy aktualne saldo jest już inne. Gdybyśmy zwracali bieżące saldo, ponowienie otrzymałoby informację o późniejszych operacjach zamiast odtworzenia odpowiedzi. W rozbudowanym API zapis może obejmować status, identyfikator utworzonego obiektu i stabilną reprezentację odpowiedzi, z określonym zakresem danych wrażliwych.

## Porównanie i decyzje

Naturalnie idempotentne „ustaw wartość na 12” jest prostsze od „zwiększ o 12”, ale może nadpisać równoległą zmianę. Numer wersji lub warunek wstępny rozwiązuje inny problem: chroni przed zapisaniem decyzji opartej na starym stanie. Nie zastępuj deduplikacji kontrolą wersji bez analizy zachowania po utracie odpowiedzi.

Przechowywanie rekordu i skutku w tej samej bazie pozwala połączyć je jedną transakcją. Jeżeli skutkiem jest wywołanie obcego operatora płatności, lokalny COMMIT nie obejmuje tego operatora. Przekaż mu stabilny klucz albo zastosuj protokół uzgadniania wyniku. Outbox zapewnia atomowość lokalnego zapisu i zamiaru wysłania, ale odbiorca nadal musi obsłużyć wielokrotne dostarczenie.

Retencja rekordu określa granicę gwarancji. Usunięcie klucza po godzinie oznacza, że duplikat po dwóch godzinach może wykonać efekt ponownie. Dobierz retencję do maksymalnego czasu redelivery, retry klienta i odzyskiwania po awarii. Sam hash treści jako klucz może przypadkowo scalić dwa celowo identyczne zakupy; identyczne dane nie zawsze oznaczają tę samą intencję.

Przy brokerze przyjrzyj się dokładnej granicy potwierdzenia. Jeżeli konsument zatwierdzi zmianę w bazie, a następnie umrze przed ACK, broker może dostarczyć komunikat ponownie. Inbox zapisany w tej samej transakcji co zmiana pozwala rozpoznać ten przebieg. Odwrócenie kolejności, czyli ACK przed zmianą, usuwa duplikat kosztem ryzyka utraty pracy. Żadna kolejność dwóch niezależnych operacji nie tworzy automatycznie jednej transakcji rozproszonej.

Budżet pojedynczego wywołania klienta może się skończyć wcześniej niż życie zlecenia w tle. Wtedy zwróć identyfikator operacji i jawny stan oczekiwania, zamiast uruchamiać coraz dłuższe synchroniczne retry. Dalsze dostarczenia nadal używają tego samego klucza i mają własne ograniczenia retencji oraz czasu wykonania. Rozróżnienie deadline odpowiedzi od terminu ważności zlecenia jest decyzją domenową, którą trzeba zapisać w kontrakcie.

## Ćwiczenia

1. Klient po timeout zmienia klucz operacji i ponawia to samo obciążenie. Serwer ma poprawną tabelę idempotencji. Czy zapobiegnie duplikatowi?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Nie. Nowy klucz opisuje nową operację, więc serwer nie ma podstaw do scalenia żądań. Zachowaj klucz przez wszystkie próby i odtwarzanie operacji, a zmianę treści pod tym kluczem traktuj jako konflikt.

</details>

2. Limit backoff wynosi maksymalną wartość typu. Dlaczego `min(cap, delay * 2)` może być błędne?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Mnożenie zachodzi przed minimum. Typ bez znaku zawinie wartość, a przepełnienie typu ze znakiem naruszy reguły języka. Sprawdź `delay > cap / 2` przed mnożeniem i w tym przypadku zwróć cap, tak jak w programie.

</details>

## Powiązane tematy

- [Kolejki, brokerzy i delivery](01_kolejki_brokerzy_i_delivery.md)
- [Outbox, inbox i deduplikacja](05_outbox_inbox_i_deduplication.md)
- [Klient HTTP](../21_sieci_protokoly_i_api/05_klient_http_timeouty_retry_i_pooling.md)
