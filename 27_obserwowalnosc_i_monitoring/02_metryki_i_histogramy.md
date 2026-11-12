[← Spis treści](../README.md)

# Metryki i histogramy

Metryka kompresuje wiele zdarzeń do szeregu czasowego. Ta kompresja jest przydatna, jeżeli zachowuje informację potrzebną do decyzji: jak szybko rośnie liczba błędów, ile pracy czeka oraz jaki odsetek żądań kończy się przed progiem opóźnienia. Nie zachowuje pełnej historii pojedynczych żądań. Wybór instrumentu decyduje, które pytania będą później możliwe do zadania.

Zacznij od semantyki pomiaru. „Czas żądania” może oznaczać czas od zaakceptowania do wysłania ostatniego bajtu albo tylko czas działania funkcji obsługi. Jeżeli kolejka jest poza pomiarem, serwis może raportować dobre opóźnienia mimo długiego oczekiwania klientów. Nazwa, jednostka, moment rozpoczęcia i zakończenia pomiaru są częścią kontraktu, podobnie jak typ C++ funkcji.

## Jak to działa krok po kroku

Counter opisuje narastającą liczbę zdarzeń, na przykład zakończonych prób. Po restarcie procesu może rozpocząć się od nowa, więc do natężenia ruchu potrzebna jest funkcja uwzględniająca reset. Gauge opisuje stan, na przykład aktualną liczbę zadań w kolejce; może rosnąć i maleć. Histogram zapisuje rozkład obserwacji, umożliwiając ocenę ogona opóźnień. Nie używaj bieżącej wartości countera jako „żądań na sekundę”.

Pierwszy program pokazuje jednowątkowy akumulator klasycznego histogramu i jego tekstową reprezentację. Granice są podane w sekundach, a przedziały wewnętrzne są rozłączne. Eksport zamienia je na kubełki kumulacyjne: obserwacja 0,05 s należy do wszystkich kubełków o większej granicy. To dwa różne sposoby reprezentacji tych samych czterech pomiarów.

~~~cpp
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string_view>

class Histogram {
    static constexpr std::array<double, 3> bounds_{0.1, 0.3, 1.0};
    std::array<std::uint64_t, 4> bins_{};
    double sum_ = 0;
public:
    void observe(double seconds) {
        if (!std::isfinite(seconds) || seconds < 0)
            throw std::invalid_argument("invalid duration");
        std::size_t bucket = 0;
        while (bucket < bounds_.size() && seconds > bounds_[bucket]) ++bucket;
        ++bins_[bucket];
        sum_ += seconds;
    }
    std::array<std::uint64_t, 4> cumulative() const {
        auto result = bins_;
        for (std::size_t i = 1; i < result.size(); ++i) result[i] += result[i-1];
        return result;
    }
    void expose(std::ostream& out) const {
        constexpr std::array<std::string_view, 4> labels{"0.1", "0.3", "1", "+Inf"};
        const auto counts = cumulative();
        out << "# TYPE request_duration_seconds histogram\n";
        for (std::size_t i = 0; i < counts.size(); ++i)
            out << "request_duration_seconds_bucket{le=\"" << labels[i]
                << "\"} " << counts[i] << '\n';
        out << "request_duration_seconds_count " << counts.back() << '\n';
        out << "request_duration_seconds_sum " << sum_ << '\n';
    }
};

int main() {
    Histogram histogram;
    for (double x : {0.05, 0.3, 0.9, 1.5}) histogram.observe(x);
    assert((histogram.cumulative() == std::array<std::uint64_t, 4>{1, 2, 3, 4}));
    histogram.expose(std::cout);
}
~~~

Wynik `le="0.3"` ma wartość dwa, ponieważ obejmuje 0,05 i dokładnie 0,3. Kubełek `+Inf` zgadza się z count. Suma granic kubełków nie jest sumą obserwacji; sumę trzeba akumulować osobno. Średnia tych danych wynosi 2,75/4, lecz nie mówi, że jedno z czterech żądań trwało 1,5 sekundy.

Program nie udostępnia endpointu, scrape, retencji ani alertów. Wypisanie poprawnie wyglądających serii na stdout nie uruchamia monitoringu. Produkcyjna biblioteka musi zapewnić synchronizację zapisu i zbierania danych, bezpieczne rejestrowanie instrumentów oraz obsługę eksportu. Użycie osobnego atomika dla każdego pola może dać niespójny snapshot count i kubełków; projekt zbierania wymaga osobnej analizy.

## Pogłębienie mechanizmu

Klasyczne kubełki Prometheus są kumulacyjne względem granicy `le`; szeregi `_sum` i `_count` zachowują sumę oraz liczbę obserwacji. Kwantyle obliczane z histogramu są przybliżone, a ich dokładność zależy od granic. Kwantyle podsumowań wyliczone lokalnie nie dają się po prostu zagregować do kwantyla całej usługi. [Prometheus: histogramy i podsumowania](https://prometheus.io/docs/practices/histograms/).

Nie myl kumulacji po granicach z kumulacją w czasie. Histogram może obejmować obserwacje od startu procesu albo przyrost od ostatniego okresu eksportu. OpenTelemetry opisuje obie temporalności, a jego jawne bucket counts odnoszą się do rozłącznych przedziałów. Konwersja do klasycznej reprezentacji Prometheus wymaga sum prefiksowych. [OpenTelemetry: model danych metryk](https://opentelemetry.io/docs/specs/otel/metrics/data-model/).

Do pytania o ostatnie pięć minut potrzebujesz przyrostu w tym oknie. Dla klasycznej reprezentacji typowe wyrażenie PromQL wygląda następująco; zakłada metrykę o podanej nazwie i odpowiednie etykiety w rzeczywistym backendzie:

~~~text
histogram_quantile(
  0.99,
  sum by (le, service) (
    rate(request_duration_seconds_bucket[5m])
  )
)
~~~

Najpierw obliczasz rate poszczególnych serii, aby wykrywać ich restarty, a następnie sumujesz po instancjach z zachowaniem `le`. Dopiero z połączonego rozkładu wyliczasz kwantyl. Próg SLO 300 ms warto umieścić dokładnie w granicach: udział żądań spełniających warunek można wtedy policzyć z kubełka 0,3 i count, bez interpolowania wartości kwantyla.

Dobieraj granice gęściej tam, gdzie wynik ma wpływać na decyzję. Jeśli jedyny kubełek ogona obejmuje 1–10 sekund, p99 w tym przedziale pozostaje mało precyzyjne. Zwiększanie liczby kubełków kosztuje jednak pamięć i liczbę serii. Histogram nie odtwarza surowych danych; żadna funkcja zapytania nie odzyska dokładności, której nie zachowano podczas pomiaru.

## Drugi przykład

Dwie instancje mogą mieć bardzo różny ruch. Pierwsza obsługuje tysiąc żądań po 0,1 s, druga dziesięć po 2 s. Średnia lokalnych p99 wynosi 1,05 s, lecz globalne p99 metodą najbliższej rangi wynosi 0,1 s: tysiąc szybkich odpowiedzi wystarcza do pokrycia 99% populacji 1010 zdarzeń.

Program scala zgodne kubełki. Zwraca górną granicę kubełka zawierającego szukaną rangę, a nie implementację interpolacji `histogram_quantile`. W tych konkretnych danych znamy surowe wartości i możemy również wskazać dokładny kwantyl. W ogólnym przypadku kubełek daje jedynie przedział możliwych wyników.

~~~cpp
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>

struct Snapshot {
    std::array<std::uint64_t, 3> cumulative;
    std::uint64_t count;
};

Snapshot merge(const Snapshot& a, const Snapshot& b) {
    Snapshot result{{}, a.count + b.count};
    for (std::size_t i = 0; i < result.cumulative.size(); ++i)
        result.cumulative[i] = a.cumulative[i] + b.cumulative[i];
    return result;
}

double upper_bound(const Snapshot& h, double quantile) {
    constexpr std::array<double, 3> bounds{0.1, 0.5, 2.0};
    assert(h.count > 0 && quantile > 0 && quantile <= 1);
    const auto rank = static_cast<std::uint64_t>(std::ceil(quantile * h.count));
    for (std::size_t i = 0; i < bounds.size(); ++i)
        if (h.cumulative[i] >= rank) return bounds[i];
    return std::numeric_limits<double>::infinity();
}

int main() {
    const Snapshot fast{{1000, 1000, 1000}, 1000};
    const Snapshot slow{{0, 0, 10}, 10};
    const auto all = merge(fast, slow);
    const double wrong = (upper_bound(fast, 0.99) + upper_bound(slow, 0.99)) / 2;
    const double combined = upper_bound(all, 0.99);
    assert(all.count == 1010 && combined == 0.1 && wrong > 1);
    std::cout << "average_of_p99=" << wrong
              << " merged_p99_bucket_upper=" << combined << '\n';
}
~~~

Scalanie wymaga tej samej jednostki, znaczenia pomiaru i zgodnego układu granic. Samo dodanie trzeciego elementu dwóch tablic nie jest poprawne, jeżeli jedna konfiguracja ma tam 0,3 s, a druga 1 s. Przy zmianie schematu zaplanuj zgodność i migrację zapytań. Nie interpretuj także brakującej serii jako wartości zero bez określonego kontraktu zbierania.

## Porównanie i decyzje

Każda kombinacja etykiet tworzy odrębny szereg. Przy dziesięciu instancjach, czterech metodach, pięćdziesięciu trasach i pięciu klasach statusu masz dziesięć tysięcy kombinacji, zanim pomnożysz je przez liczbę kubełków, sum i count. To obliczenie górnej granicy pomaga ocenić koszt przed uruchomieniem, choć rzeczywista liczba zależy od występujących kombinacji.

Etykieta `route="/orders/{id}"` ma ograniczony słownik, a `path="/orders/abc123"` może rosnąć z każdym zamówieniem. Identyfikatory użytkowników, trace ID i teksty wyjątków należą do innych sygnałów. Dokumentacja Prometheus odradza nieograniczone wymiary etykiet. [Nazwy metryk i etykiet](https://prometheus.io/docs/practices/naming/). Przypisanie identyfikatora do exemplara może zachować odnośnik do śladu bez tworzenia nowego szeregu dla każdego żądania.

Counter wybieraj dla zakończonych zdarzeń, gauge dla bieżącego stanu, histogram dla rozkładu. Osobno mierz powodzenie operacji i liczbę prób, aby retry nie zawyżało pozornego ruchu biznesowego. Sprawdzaj też koszt pomiaru na gorącej ścieżce: dynamiczne tworzenie etykiet i rejestrowanie instrumentu przy każdym żądaniu może być droższe niż sama aktualizacja wartości.

Zdefiniuj populację także dla błędów i anulowania. Jeśli histogram zapisujesz wyłącznie przy sukcesie, najwolniejsze timeouty znikną z rozkładu i poprawią raportowane p99 podczas awarii. Możesz obserwować czas wszystkich zakończonych prób z ograniczoną etykietą wyniku oraz osobno czas całej operacji. Do oceny dostępności nadal potrzebujesz counterów sukcesu i błędu; sam rozkład czasu nie rozstrzyga jakości wyniku.

Nie mieszaj ponadto danych o innych granicach pomiaru: czas po stronie klienta obejmuje drogę przez sieć, a czas handlera może jej nie obejmować. Różnica pomiędzy tymi rozkładami sugeruje obszar do badania, lecz nie daje automatycznie rozkładu czasu sieci. Odejmowanie dwóch p99 nie jest p99 różnicy, ponieważ kwantyle mogą pochodzić z innych żądań.

## Ćwiczenia

1. Kubełki `le=0.1`, `le=0.3`, `le=+Inf` mają wartości 4, 9 i 12. Ile obserwacji było większych niż 0,1 i nie większych niż 0,3?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Pięć: 9−4. Kubełek 0,3 zawiera również cztery obserwacje pierwszego kubełka. Dodanie wszystkich trzech wartości policzyłoby część obserwacji wielokrotnie.

</details>

2. Dashboard uśrednia p99 dwudziestu replik. Czy ważenie tych wartości liczbą żądań naprawi wynik?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Nie. Nawet ważona średnia kwantyli nie odtwarza rozkładu. Scal odpowiednie kubełki lub inną reprezentację rozkładu, a dopiero potem oblicz kwantyl. Lokalne p99 tracą informację o pozostałych obserwacjach.

</details>

## Powiązane tematy

- [Logi strukturalne i korelacja](01_logi_strukturalne_i_korelacja.md)
- [Tracing i OpenTelemetry](03_tracing_i_opentelemetry.md)
- [Health, readiness i liveness](04_health_readiness_i_liveness.md)
