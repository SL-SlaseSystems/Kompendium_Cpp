[← Spis treści](../README.md)

# Testy kontraktowe

Test kontraktowy sprawdza zachowanie na granicy, na której współpracują dwie niezależne implementacje lub wersje komponentów. Konsument może oczekiwać, że brak rekordu jest odróżniany od awarii, kwota ma określoną jednostkę, a nieznane pole odpowiedzi nie przerywa odczytu. Zgodność nazw metod ani identyczna definicja struktury w dwóch repozytoriach nie dowodzi zgodności tych oczekiwań. Potrzebny jest wykonywalny przykład żądania, odpowiedzi i interpretacji wyniku.

Szczególnie zdradliwy jest fake napisany przez zespół konsumenta. Pomaga szybko testować logikę, ale często odtwarza życzenia autora zamiast rzeczywistego zachowania producenta. Ten sam zestaw przypadków powinien więc sprawdzać fake oraz prawdziwy adapter lub uruchomioną implementację producenta w kontrolowanym środowisku. W systemie sieciowym test konsumenta musi przejść przez rzeczywisty kod budujący żądanie i odczytujący odpowiedź.

## Jak to działa krok po kroku

Najpierw określamy obserwowalne własności. Dla odczytu stanu magazynu istniejący produkt zwraca nieujemną liczbę sztuk, brak produktu jest osobnym wynikiem, a ponowiony odczyt nie zmienia danych. Przygotowujemy nazwany stan producenta: produkt 42 ma siedem sztuk, produkt 99 nie istnieje. Zestaw testów nie powinien zależeć od przypadkowej zawartości współdzielonej bazy ani kolejności uruchamiania innych scenariuszy.

Poniższy przykład wykonuje kontrakt wobec fake i rzeczywistego adaptera plikowego. Adapter otwiera plik i parsuje zapis, więc obejmuje granicę, której mapa w pamięci nie sprawdzi. Każdy przebieg tworzy własny katalog, a RAII usuwa go po zakończeniu. To mały lokalny model: w usłudze HTTP analogiczny test używałby prawdziwego klienta i lokalnego serwera producenta.

~~~cpp
#include <cassert>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>

struct FakeStock {
    std::map<std::uint32_t, int> records{{42, 7}};
    std::optional<int> get(std::uint32_t id) const {
        const auto it = records.find(id);
        if (it == records.end()) return std::nullopt;
        return it->second;
    }
};

struct FileStock {
    std::filesystem::path root;
    std::optional<int> get(std::uint32_t id) const {
        const auto path = root / (std::to_string(id) + ".txt");
        if (!std::filesystem::exists(path)) return std::nullopt;
        std::ifstream input(path);
        int quantity{};
        if (!(input >> quantity) || quantity < 0) {
            throw std::runtime_error("invalid stock record");
        }
        input >> std::ws;
        if (!input.eof()) throw std::runtime_error("trailing data");
        return quantity;
    }
};

template<class Repository>
void stock_contract(const Repository& repository) {
    assert(repository.get(42) == 7);
    assert(!repository.get(99));
    assert(repository.get(42) == 7);
}

struct TempDirectory {
    std::filesystem::path path;
    ~TempDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path, ignored);
    }
};

int main() {
    const auto nonce = std::chrono::steady_clock::now()
                           .time_since_epoch().count();
    const auto path = std::filesystem::temp_directory_path()
                    / ("stock-contract-" + std::to_string(nonce));
    if (!std::filesystem::create_directory(path)) {
        throw std::runtime_error("test directory already exists");
    }
    const TempDirectory temporary{path};
    {
        std::ofstream output(path / "42.txt");
        if (!(output << "7\n")) throw std::runtime_error("fixture write failed");
    }
    stock_contract(FakeStock{});
    stock_contract(FileStock{path});
}
~~~

Wspólny test jest wartościowy tylko wtedy, gdy oba warianty otrzymują równoważny stan początkowy i znaczenie wyników. Fake nie musi odtwarzać formatu pliku; ma zachowywać kontrakt repozytorium używany przez domenę. Testy samego adaptera powinny dodatkowo obejmować uszkodzony zapis, odmowę dostępu i ustalone rozróżnienie błędów. Pokazany adapter nie rozwiązuje wyścigu między sprawdzeniem istnienia pliku a jego otwarciem; ten szczegół wymaga osobnego projektu obsługi I/O.

## Pogłębienie mechanizmu

W kontrakcie sieciowym sprawdzamy metodę, ścieżkę, istotne nagłówki, kod statusu i strukturę odpowiedzi. Dokładne porównanie całego dokumentu bywa zbyt restrykcyjne, jeśli kolejność pól lub dodatkowe pola nie wpływają na konsumenta. Z drugiej strony matcher „dowolny string” jest zbyt słaby dla pola, którego klient używa jako URL albo rozpoznaje ograniczony zestaw wartości. Asercje powinny wynikać z rzeczywistych założeń kodu odczytującego dane.

Test konsumenta i weryfikacja producenta pełnią różne role. Pierwszy uruchamia prawdziwy adapter konsumenta wobec kontrolowanej odpowiedzi oraz zapisuje jego oczekiwania. Drugi odtwarza te oczekiwania wobec prawdziwej implementacji producenta, z przygotowanym stanem początkowym. Jeżeli na obu etapach podstawimy tę samą ręcznie napisaną odpowiedź, sprawdzimy zgodność dwóch dubli i pominiemy faktyczną integrację. Taki podział opisują pierwotne materiały Pact: [testy konsumenta](https://docs.pact.io/consumer) oraz [weryfikacja producenta](https://docs.pact.io/provider).

Producent może zastąpić swoje dalsze zależności kontrolowanymi implementacjami, lecz punkt podmiany nie powinien omijać parsowania i walidacji żądania objętego kontraktem. Inaczej test zaakceptuje żądanie, którego rzeczywisty endpoint nigdy nie przyjmie. Testowanie prawdziwego routera, serializatora i adaptera ma inny zakres dowodu niż bezpośrednie wywołanie prywatnej funkcji domenowej. W raporcie warto tę granicę nazwać dosłownie.

Kontrakt jest wersjonowanym artefaktem, powiązanym z konkretną wersją konsumenta i wynikiem weryfikacji producenta. Sam napis „zgodne z v2” jest zbyt mało precyzyjny przy stopniowym wdrożeniu, gdy część procesów nadal używa v1. Macierz powinna obejmować wersje aktualnie wdrożone oraz kandydatów do wdrożenia. Usunięcie starego kontraktu jest decyzją po wycofaniu ostatniego konsumenta, a nie automatycznym skutkiem wydania nowego API.

## Drugi przykład

Zgodność schematów jest kierunkowa. Stary konsument może zignorować nowe opcjonalne pole, ale nowy konsument wymagający tego pola nie przeczyta starej odpowiedzi. Poniższy kompletny program modeluje dokument po dekodowaniu formatu transportowego. Nie implementuje JSON: celowo bada reguły interpretacji pól, aby nie pomylić tego testu z testem parsera JSON.

~~~cpp
#include <cassert>
#include <charconv>
#include <map>
#include <optional>
#include <string>
#include <string_view>
#include <system_error>

using Document = std::map<std::string, std::string>;
struct Quote { int cents; std::string currency; };

std::optional<int> read_cents(const Document& document) {
    const auto it = document.find("amount_cents");
    if (it == document.end() || it->second.empty()) return std::nullopt;
    const std::string_view text = it->second;
    int value{};
    const auto [end, error] = std::from_chars(
        text.data(), text.data() + text.size(), value);
    if (error != std::errc{} || end != text.data() + text.size()
        || value < 0) return std::nullopt;
    return value;
}

std::optional<Quote> consumer_v1(const Document& document) {
    const auto cents = read_cents(document);
    if (!cents) return std::nullopt;
    return Quote{*cents, "PLN"}; // v1 zaklada jedna walute.
}

std::optional<Quote> consumer_v2(const Document& document) {
    const auto cents = read_cents(document);
    const auto currency = document.find("currency");
    if (!cents || currency == document.end()
        || currency->second != "PLN") return std::nullopt;
    return Quote{*cents, currency->second};
}

int main() {
    const Document provider_v1{{"amount_cents", "1250"}};
    const Document provider_v2{{"amount_cents", "1250"},
                               {"currency", "PLN"}};
    const Document changed_units{{"amount", "12.50"}};
    assert(consumer_v1(provider_v1));
    assert(consumer_v1(provider_v2));
    assert(!consumer_v2(provider_v1));
    const auto quote = consumer_v2(provider_v2);
    assert(quote && quote->cents == 1250 && quote->currency == "PLN");
    assert(!consumer_v1(changed_units));
    assert(!consumer_v2(Document{{"amount_cents", "1250x"},
                                {"currency", "PLN"}}));
}
~~~

Dodatkowe pole jest bezpieczne dla v1 wyłącznie przy zachowaniu jego znaczenia. Producent v2 nie może zacząć zwracać EUR, ponieważ v1 nadal interpretuje kwotę jako PLN. Możliwa migracja to utrzymanie starego endpointu z jego semantyką i udostępnienie nowej wersji osobno. Inna opcja wymaga najpierw wdrożenia konsumentów, które potrafią rozpoznać walutę. „Dodawanie pól jest zawsze kompatybilne” jest zbyt szeroką regułą.

Zmiana opcjonalności wymaga sprawdzenia również wartości pustych i braku pola. W wielu formatach brak klucza, jawne `null`, pusty napis i zero są czterema różnymi stanami. Adapter, który sprowadza je do jednej wartości domyślnej, może ukryć błąd migracji. Podobnie akceptowanie dowolnej liczby zmiennoprzecinkowej nie zapewnia zgodności z kwotą wyrażoną w całkowitych groszach. Jednostki, zakres i reguła zaokrąglania powinny mieć konkretne przykłady w kontrakcie.

Weryfikacja błędów powinna badać interpretację po stronie konsumenta. Kod 404 może oznaczać brak zasobu, ale również nieistniejący endpoint; sam numer statusu bywa niewystarczający bez uzgodnionego formatu błędu. Kod 409 nie zawsze uzasadnia automatyczne ponowienie operacji. Dodajemy przypadki, które faktycznie sterują decyzją klienta, i sprawdzamy ich mapowanie na typowane wyniki adaptera. Test kontraktowy staje się wtedy ochroną zachowania aplikacji, a nie kolekcją przykładowych dokumentów.

Przy asynchronicznych komunikatach sam kształt pojedynczej wiadomości nie ustala reguł dostarczania. Konsument może poprawnie odczytać schemat, lecz nie obsłużyć powtórzenia, opóźnienia albo zmiany kolejności. Test kontraktowy powinien utrwalić identyfikator i pola potrzebne do takiej obsługi, natomiast zachowanie wobec duplikatów wymaga również testów przepływu i stanu. Weryfikacja deserializacji nie dowodzi semantyki exactly-once. Granice dowodu zapisujemy przy scenariuszu, aby zielony wynik nie był interpretowany szerzej niż wykonane sprawdzenie.

## Porównanie i decyzje

Test kontraktowy daje dowód dla sprawdzonych interakcji i wersji. Nie dowodzi pełnej poprawności biznesowej producenta, wydajności, odporności na awarie sieci ani zgodności dowolnych przyszłych danych. Nie zastępuje też testu autoryzacji w rzeczywistym środowisku, jeśli tokeny były podstawione. Test integracyjny sprawdza konkretną współpracę elementów, a end-to-end pełny przepływ; kontrakt uzupełnia te poziomy szybszym sygnałem o zmianie granicy.

**Zadanie 1.** Fake zwraca brak produktu jako zero sztuk, a prawdziwy adapter jako brak wartości. Co powinien zawierać wspólny kontrakt?

<details><summary>Rozwiązanie</summary>

Osobno przetestuj istniejący produkt z ilością zero oraz nieistniejący identyfikator. Oba warianty muszą zachować to rozróżnienie. Następnie popraw fake i sprawdź, czy logika domenowa przypadkiem nie polegała na jego dotychczasowym uproszczeniu.

</details>

**Zadanie 2.** Producent dodaje status `paused`, a stary klient rozpoznaje tylko `active` i `closed`. Czy poprawny schemat wystarcza do wdrożenia?

<details><summary>Rozwiązanie</summary>

Nie. Trzeba zweryfikować zachowanie starego adaptera wobec nowej wartości i ustalić zgodną politykę. Test typu string nie wykryje założenia o zamkniętym zbiorze statusów. Rozszerz kontrakt o ten przypadek i wybierz kolejność wdrożenia zachowującą działanie aktualnych konsumentów.

</details>

## Powiązane tematy

- [Mapa działu](README.md)
- [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)
- [Testy integracyjne i E2E](02_testy_integracyjne_i_e2e.md)
- [Fake, mock, stub i seams](04_fake_mock_stub_i_seams.md)
