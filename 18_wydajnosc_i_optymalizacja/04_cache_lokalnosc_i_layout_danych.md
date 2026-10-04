[← Mapa działu](README.md) · [Główny spis treści](../README.md)

# Cache lokalność i layout danych

Temat „cache lokalność i layout danych” jest częścią praktyki, w której celem jest prowadzić proces pomiar–hipoteza–zmiana–weryfikacja zamiast optymalizować na podstawie intuicji. Nie zaczynamy od wyboru produktu ani od kopiowania konfiguracji. Najpierw nazywamy chronioną własność, obserwowalne zachowanie i granicę odpowiedzialności. W tym obszarze trzeba pamiętać, że wynik zależy od danych, sprzętu, toolchainu, obciążenia i zakłóceń, a latencja, przepustowość oraz pamięć są różnymi metrykami. To rozróżnienie chroni przed przeniesieniem lokalnej obserwacji na wszystkie platformy oraz przed uznaniem zielonego narzędzia za dowód poprawności całego systemu.

Cache pracuje na liniach, a nie na obiektach języka. Układ AoS i SoA oceniaj według wzorca dostępu, rozmiaru working set i fałszywego współdzielenia, nie według samej notacji złożoności.

Najmniejszy przykład modeluje kontrolę jako dane. Kod jest samowystarczalny, nie wykonuje operacji uprzywilejowanych i nie celowo wywołuje błędów środowiska. W projekcie produkcyjnym nazwy kontroli pochodzą z modelu domenowego, a wynik jest przekazywany jako typowana wartość zamiast ginąć w logu.

~~~cpp
#include <array>
#include <cassert>
#include <string_view>

struct Topic04CachelokalnoscilCheck {
    std::string_view name;
    bool passed;
};

constexpr bool accepted(std::array<Topic04CachelokalnoscilCheck, 3> checks) {
    for (const auto& check : checks) {
        if (!check.passed) return false;
    }
    return true;
}

int main() {
    constexpr std::array checks{
        Topic04CachelokalnoscilCheck{"wejście rozpoznane", true},
        Topic04CachelokalnoscilCheck{"limit określony", true},
        Topic04CachelokalnoscilCheck{"wynik sprawdzony", true},
    };
    static_assert(accepted(checks));
    assert(accepted(checks));
}
~~~

## Jak to działa krok po kroku

Pierwszy krok dla zagadnienia „cache lokalność i layout danych” to zapisanie scenariusza sukcesu i co najmniej trzech klas awarii. Osobno potraktuj błąd danych, błąd zależności oraz przekroczenie limitu czasu lub zasobu. Każda klasa powinna mieć właściciela decyzji: odrzucenie wejścia, ponowienie, degradację, zatrzymanie procesu albo alarm. Bez tego kod zaczyna przypadkowo mieszać politykę biznesową z detalem biblioteki.

Drugi krok polega na znalezieniu granicy, na której informacja jest jeszcze pełna. Walidacja powinna działać przed utratą kontekstu, a błąd powinien zachować przyczynę bez ujawniania sekretów. Jeśli operacja tworzy zasób, od razu ustal ownership, czas życia i sposób zwalniania. Jeśli dotyka świata zewnętrznego, dodaj deadline, limit rozmiaru oraz kontrolę anulowania. Domyślna wartość ma być bezpieczna i widoczna w konfiguracji.

Trzeci krok to zbudowanie testu dla kontraktu, nie dla prywatnego układu funkcji. Test obejmuje poprawny przypadek, granicę i reprezentatywną awarię. Dla zachowania zależnego od platformy zapisujemy macierz środowisk zamiast warunku, który zawsze przechodzi na komputerze autora. Wynik narzędzia archiwizujemy tylko wtedy, gdy pomaga odtworzyć decyzję.

Na końcu integrujemy kontrolę z lokalnym przepływem pracy. Szybki test działa często, pełna weryfikacja działa przed wysłaniem, a CI odtwarza ją w czystym środowisku. Każdy eksperyment ma wariant bazowy, kontrolę usunięcia kodu przez optymalizator i zapis środowiska. Wynik lokalny nie staje się obietnicą uniwersalnego przyspieszenia.

## Pogłębienie mechanizmu

Zagadnienie „cache lokalność i layout danych” ma co najmniej trzy poziomy kontraktu. Poziom języka mówi, co gwarantuje C++ i biblioteka standardowa. Poziom narzędzia obejmuje flagi kompilatora, bibliotekę zewnętrzną, format albo runtime. Poziom operacyjny obejmuje konfigurację procesu, uprawnienia, dane i zachowanie zależności. Błąd dokumentacji często powstaje wtedy, gdy gwarancję jednego poziomu przypisuje się innemu.

Nie wystarczy opisać ścieżki sukcesu. Dobra implementacja określa stan po częściowym wykonaniu: które efekty już zaszły, co można bezpiecznie powtórzyć, co trzeba posprzątać i jak odróżnić brak wyniku od wyniku pustego. RAII pomaga zamknąć zasób lokalny, ale nie cofa automatycznie efektu w obcym procesie. Transakcja lub protokół kompensacji są osobną decyzją.

Obserwowalność projektujemy razem z kontraktem. Zdarzenie powinno zawierać stabilny rodzaj operacji, wynik i identyfikator korelacji, lecz nie kopiować nieograniczonego wejścia. Metryka pokazuje trend, log zachowuje kontekst pojedynczego zdarzenia, a ślad łączy pracę przez granice. Każdy sygnał ma koszt i politykę retencji. Wrażliwe dane redagujemy przed przekazaniem do warstwy telemetrycznej.

Wydajność oceniamy dopiero na reprezentatywnym obciążeniu. Usprawnienie, które pomija walidację, limit albo raportowanie błędu, zmienia kontrakt i nie jest równoważną optymalizacją. Najpierw zapisujemy bazę pomiarową, następnie jedną hipotezę i kryterium odrzucenia. Dzięki temu decyzja dotycząca „cache lokalność i layout danych” pozostaje sprawdzalna po zmianie sprzętu lub toolchainu.

## Drugi przykład

Przed implementacją przydaje się krótka karta decyzji. Nie jest ona składnią konkretnego produktu; to przenośny zapis warunków, który później można odwzorować na kod, konfigurację i testy.

~~~text
temat: cache lokalność i layout danych
wejście: nazwane, ograniczone, walidowane na granicy
sukces: mierzalny efekt i jawny właściciel wyniku
awarie: dane / zależność / czas / zasób / anulowanie
cleanup: idempotentny albo chroniony stanem
telemetria: wynik bez sekretów i nieograniczonej cardinality
testy: sukces, granica, błąd, częściowe wykonanie
~~~

Kartę trzeba skonfrontować z realnym API. Jeżeli biblioteka nie pozwala ustawić deadline, decyzja może wymagać innej biblioteki albo izolacji procesu. Jeżeli typ błędu gubi kod przyczyny, adapter powinien przetłumaczyć go na słownik aplikacji. Jeśli cleanup może zawieść, destruktor nie jest dobrym miejscem na raportowanie jedynego śladu; potrzebna jest jawna operacja zamknięcia i bezpieczny fallback RAII.

Drugi test powinien zakładać, że zależność odpowie w najgorszym dozwolonym momencie. Sprawdź budżet czasu całej operacji, a nie tylko pojedynczego wywołania. Następnie wprowadź kontrolowany błąd i potwierdź stan końcowy. To ćwiczenie ujawnia ukryte założenia znacznie wcześniej niż rozbudowany test end-to-end uruchamiany dopiero przed wydaniem.

## Porównanie i decyzje

Najprostsze rozwiązanie dla „cache lokalność i layout danych” jest dobrym punktem startowym, jeśli zachowuje kontrakt i daje się obserwować. Rozbudowana warstwa abstrakcji ma sens, gdy izoluje rzeczywistą zmienność: platformę, bibliotekę, protokół albo politykę. Abstrakcja dodana wyłącznie „na przyszłość” zwiększa liczbę stanów i może ukryć istotne ograniczenia zewnętrznego API.

Automatyczna kontrola daje szybki, powtarzalny sygnał, natomiast review ocenia kontekst i konsekwencje. Test potwierdza wybrane przypadki, analiza statyczna bada model bez uruchomienia, a monitoring pokazuje zachowanie prawdziwego obciążenia. Dojrzały proces łączy te perspektywy i jawnie dokumentuje obszary, których aktualnie nie potrafi udowodnić.

Decyzję zapisujemy wraz z warunkiem ponownej oceny: wzrostem wolumenu, nową platformą, zmianą ABI, innym profilem zagrożeń albo wymaganiem zgodności. Dzięki temu kompromis nie zamienia się w przypadkową tradycję. Źródło pierwotne dla tego działu stanowi [Google Benchmark User Guide](https://github.com/google/benchmark/blob/main/docs/user_guide.md); dokładne opcje zawsze sprawdzaj dla używanej wersji narzędzia.

## Powiązane tematy

- [Mapa działu](README.md)
- [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)
- [Google Benchmark User Guide](https://github.com/google/benchmark/blob/main/docs/user_guide.md)
