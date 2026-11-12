[← Mapa działu](../02_podstawy_jezyka/README.md) · [Spis treści](../README.md)

# Ćwiczenia: semantyka, której nie zastąpi intuicja

Dla każdego przypadku najpierw zapisz typy i regułę. Fragmentów z niezdefiniowanym zachowaniem nie uruchamiaj jako eksperymentu mającego rozstrzygnąć, co gwarantuje język. Wynik jednego wykonania nie jest taką gwarancją.

## 1. Porównanie zmieniające znak

**Wejście:** `int a = -1; unsigned int b = 1;` oraz warunek `a < b`. **Oddaj:** wynik, typ porównywanych operandów i poprawny sposób porównania wartości matematycznych. Zbadaj także zero i największą wartość `unsigned int`, bez zakładania konkretnej szerokości `int`. **Wskazówka:** przypisanie `a` do `long` nie musi rozwiązać problemu na każdej platformie.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Operandy mają tę samą rangę, więc `a` zostaje skonwertowane do `unsigned int`; otrzymana największa wartość nie jest mniejsza od 1. Do porównań mieszanych użyj `std::cmp_less` z `<utility>` albo jawnie rozdziel przypadek ujemny. Ślepy rzut na inny typ całkowity wymaga sprawdzenia zakresu. [Konwersje](../02_podstawy_jezyka/04_operatory_i_konwersje.md).

</details>

## 2. Klamry jako część kontraktu

**Wejście:** `std::vector<int> a(3, 7)`, `b{3, 7}` i próba `c{3.5}`. **Oddaj:** zawartości dwóch pierwszych wektorów oraz klasyfikację trzeciej deklaracji. Zaprojektuj nazwane fabryki tworzące „trzy siódemki” i „dwa podane elementy”. Kryterium: intencja nie zależy od pamiętania przeciążeń konstruktora. **Wskazówka:** klamry nie są wyłącznie inną pisownią nawiasów.

<details><summary>Rozwiązanie i uzasadnienie</summary>

`a` zawiera 7, 7, 7; `b` zawiera 3, 7. Dla `c` wybór konstruktora z `initializer_list<int>` prowadzi do niedozwolonego zawężenia, więc deklaracja jest niepoprawna. Fabryki mogą nazywać operacje `filled(count, value)` i `from_values(...)`, delegując do właściwej konstrukcji. [Inicjalizacja](../02_podstawy_jezyka/08_inicjalizacja_i_initializer_list.md).

</details>

## 3. Trzy różne relacje kolejności

**Wejście:** każdorazowo startuj od `int i = 0`: A `f(i++, i++)`; B `i++ + i++`; C `std::cout << i++ << i++`. Przyjmij C++23 i zwykłą funkcję `f(int,int)`. **Oddaj:** możliwe argumenty, ocenę zdefiniowania i wynik C. **Wskazówka:** argumenty funkcji i operandy dodawania mają inne reguły.

<details><summary>Rozwiązanie i uzasadnienie</summary>

W A inicjalizacje argumentów są nieokreślenie sekwencjonowane: `f` otrzyma `(0,1)` albo `(1,0)`, a `i` wyniesie 2. B ma niesekwencjonowane modyfikacje tego samego obiektu, więc zachowanie jest niezdefiniowane. W C lewy operand operatora przesunięcia jest sekwencjonowany przed prawym: wypisane zostanie `01`, końcowe `i` to 2. [Sequencing](../02_podstawy_jezyka/09_kolejnosc_ewaluacji_i_sequencing.md).

</details>

## 4. Kontrola sumy bez przepełnienia kontroli

**Wejście:** API dodaje dwa `int` i ma zwracać brak wyniku, jeśli matematyczna suma jest poza zakresem. **Oddaj:** pseudokod sprawdzenia przed dodawaniem oraz przypadki dla minimum, maksimum, zera i operandów przeciwnych znaków. Zabronione jest obliczenie sumy w `int` przed walidacją. **Wskazówka:** odejmuj tylko w gałęzi zapewniającej bezpieczeństwo odejmowania.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Dla `b > 0` odrzuć `a > max - b`; dla `b < 0` odrzuć `a < min - b`. Pozostałe przypadki pozwalają obliczyć `a + b`. Oba wyrażenia progowe mieszczą się w zakresie w swoich gałęziach. Przykłady: `(max,1)` i `(min,-1)` odrzucone, `(min,max)` daje -1, `(max,0)` daje maksimum. [Arytmetyka](../02_podstawy_jezyka/10_arytmetyka_przepelnienia_i_float.md).

</details>

## 5. Tolerancja to wymaganie dziedziny

**Wejście:** pomiar powinien akceptować błąd bezwzględny `10^-6` i względny `10^-8`; test porównuje wartości około zera i około `10^9`. **Oddaj:** predykat porównania oraz politykę dla NaN i nieskończoności. Kryterium: nie dzielisz przez zero i nie akceptujesz NaN. **Wskazówka:** stałe `epsilon()` opisuje reprezentację, nie wymagany błąd pomiaru.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Najpierw zaakceptuj dokładną równość, co obsługuje identyczne nieskończoności; odrzuć pozostałe argumenty niefinitywne. Dla skończonych sprawdzaj `abs(a-b) <= max(abs_tol, rel_tol * max(abs(a),abs(b)))`, kontrolując zakres obliczeń dla całej domeny. Blisko zera działa próg bezwzględny, przy dużej skali względny. To nie jest relacja równoważności odpowiednia na klucz zbioru. [Liczby zmiennoprzecinkowe](../02_podstawy_jezyka/10_arytmetyka_przepelnienia_i_float.md).

</details>

## 6. Typ wyniku nie ratuje przeciążenia

**Wejście:** istnieją `pick(long)` i `pick(double)`, obie zwracają różne typy. Klient pisze `long result = pick(1);`. **Oddaj:** diagnozę wywołania i dwie poprawki oddające konkretną intencję klienta. Zbadaj także argument `1L`. **Wskazówka:** lewa strona przypisania nie wybiera funkcji po typie wyniku.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Dla argumentu `int` obie ścieżki są konwersjami standardowymi o tym samym rankingu, więc wywołanie jest niejednoznaczne. `1L` wybiera `pick(long)` przez dokładne dopasowanie. Użyj literału lub jawnej konwersji odpowiadającej dziedzinie; alternatywnie rozdziel nazwy operacji, jeżeli mają odmienne znaczenie. [Przeciążanie](../02_podstawy_jezyka/05_funkcje_i_przeciazanie.md).

</details>
