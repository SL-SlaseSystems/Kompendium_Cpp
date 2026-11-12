[← Mapa działu](../04_klasy_i_model_obiektowy/README.md) · [Spis treści](../README.md)

# Ćwiczenia: typ jako granica poprawności

Nie zaczynaj od wyboru wzorca. Najpierw wypisz dozwolone stany, operacje i obserwacje klienta. W rozwiązaniu pokaż, czy niedozwolony stan odrzuca kompilator, konstruktor czy dopiero kod korzystający z obiektu.

## 1. Procent, którego nie da się zepsuć

**Wejście:** `Discount` przechowuje całkowitą liczbę punktów bazowych od 0 do 10000. Obecnie publiczne pole pozwala przypisać 12000. **Oddaj:** interfejs tworzenia i odczytu oraz politykę błędnej wartości. Sprawdź -1, 0, 10000 i 10001; uwzględnij niejawne przekazanie zwykłego `int`. **Wskazówka:** walidacja w konstruktorze nie chroni publicznego mutowalnego pola.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Ukryj reprezentację, waliduj przed utworzeniem wartości i udostępnij obserwator bez możliwości zapisu. Konstruktor z `int` powinien być `explicit`; alternatywnie nazwany kreator może zwracać błąd. Zaakceptuj tylko 0 i 10000 z podanych granic. Jeśli dodasz setter, musi zachować poprzedni stan przy błędzie. [Enkapsulacja](../04_klasy_i_model_obiektowy/01_struct_class_i_enkapsulacja.md).

</details>

## 2. Polimorfizm zgubiony w kontenerze

**Wejście:** `Circle : Shape` nadpisuje wirtualne `area`; klient wkłada koło do `std::vector<Shape>`. Baza jest konkretna. **Oddaj:** opis przechowywanego obiektu i reprezentację kolekcji zachowującą różne typy figur. Zdecyduj, czy kolekcja jest kopiowalna. **Wskazówka:** wirtualność nie zmienia typu elementu wektora.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Skopiowany zostaje podobiekt `Shape`; dodatkowy stan koła ulega slicingowi. Wektor właścicieli `unique_ptr<Shape>` zachowuje dynamiczny typ, ale wymaga wirtualnego destruktora bazy przy takim usuwaniu i nie daje automatycznego kopiowania kolekcji. Jeśli kopie są potrzebne, określ protokół `clone` albo zastosuj jawny typ wartościowy oparty na wariancie. [Dziedziczenie](../04_klasy_i_model_obiektowy/04_dziedziczenie_i_polimorfizm.md).

</details>

## 3. Wirtualna metoda podczas konstrukcji

**Wejście:** konstruktor `Base` wywołuje nieczysto wirtualne `name`, zdefiniowane w bazie; `Derived` nadpisuje metodę i używa pola inicjalizowanego w swoim konstruktorze. **Oddaj:** kolejność inicjalizacji i wybór funkcji podczas konstrukcji bazy oraz po skonstruowaniu całości. **Wskazówka:** obietnica polimorfizmu nie oznacza gotowości nieistniejących jeszcze części obiektu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Podczas konstruktora `Base` wywołanie wirtualne dociera do wersji `Base`; podobiekt `Derived` i jego pola nie są jeszcze gotowe. Po zakończeniu konstrukcji wywołanie przez referencję bazy wybiera nadpisanie `Derived`. Nie projektuj inicjalizacji bazy wymagającej zachowania pochodnej. Dane konieczne bazie przekaż jawnie jako argumenty. [Konstruktory](../04_klasy_i_model_obiektowy/02_konstruktory_i_destruktory.md).

</details>

## 4. Trzy stany zamiast sprzecznych flag

**Wejście:** wynik importu ma `bool loading`, `bool failed`, `string error` i `Document value`. Powstaje stan „loading i failed z gotowym dokumentem”. **Oddaj:** model rozłączny oraz obsługę każdego stanu. Ustal, czy brak błędu oznacza sukces i czy dokument domyślny jest prawdziwym wynikiem. **Wskazówka:** osobne flagi tworzą więcej kombinacji niż opisuje dziedzina.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Użyj `variant<Loading, ImportError, Document>`, gdzie każdy typ przechowuje tylko swój stan. `visit` wymusza obsługę wszystkich alternatyw; nie wnioskuj sukcesu z pustego komunikatu. Rozważ też politykę `valueless_by_exception`, jeśli operacje na alternatywach mogą rzucać. Wyłącz niedozwolone przejścia interfejsem, zamiast liczyć na dyscyplinę użytkownika. [Warianty](../04_klasy_i_model_obiektowy/06_enum_union_i_variant.md).

</details>

## 5. Domyślne porównanie nie zawsze daje porządek

**Wejście:** `Measurement` zawiera `double value` i domyślny operator `<=>`. Wejście może zawierać NaN. **Oddaj:** kategorię porównania i politykę pozwalającą bezpiecznie sortować pomiary. Przetestuj dwie zwykłe wartości, równe wartości i NaN. **Wskazówka:** „nie mniejsze” nie musi znaczyć „większe lub równe”.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Porównanie składowej `double` prowadzi do `partial_ordering`; NaN jest nieuporządkowane. Zwykłe `<` dla całej domeny z NaN nie daje wymaganego przez sortowanie ścisłego słabego porządku. Odrzuć NaN podczas tworzenia typu albo napisz comparator z jawną klasą NaN, np. wszystkie NaN równoważne i umieszczane na końcu. [Porównania](../04_klasy_i_model_obiektowy/07_silne_typy_porownania_i_hash.md).

</details>

## 6. Ten sam użytkownik, inna pisownia

**Wejście:** klucz składa się z identyfikatora dzierżawcy i loginu ASCII; loginy ignorują wielkość liter. `operator==` stosuje tę regułę, hasher haszuje oryginalny tekst. **Oddaj:** kontrprzykład i spójną definicję klucza. Uwzględnij różnych dzierżawców oraz puste loginy. **Wskazówka:** dozwolone kolizje nie usprawiedliwiają różnych hashy równych kluczy.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Dla tego samego dzierżawcy `Alice` i `alice` są równe, więc muszą mieć ten sam hash. Kanonizuj ASCII raz podczas konstrukcji i porównuj oraz haszuj tę samą reprezentację wraz z dzierżawcą. Zdefiniuj osobno dopuszczalność pustego loginu; nie wynika ona z mechanizmu haszowania. Różne klucze mogą mieć jednakowe hashe. [Równość i hash](../04_klasy_i_model_obiektowy/07_silne_typy_porownania_i_hash.md).

</details>
