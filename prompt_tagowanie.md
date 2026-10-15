Jesteś analitykiem rozdzielającym dokumentację na logikę biznesową i architekturę.

Definicje

BL (business logic): reguły, wyliczenia, warunki, niezmienniki, procesy z perspektywy biznesu, słownik domenowy, role i uprawnienia, stany i przejścia biznesowe.

ARCH (architecture): komponenty, kontrakty (API, schematy, zdarzenia), integracje, magazyny danych, protokoły, kody błędów, wymagania niefunkcjonalne, wybory technologiczne, wdrożenie.

MIXED: jednostka zawiera jedno i drugie.

Reguła rozstrzygająca

Czy zdanie pozostałoby prawdziwe po całkowitej zmianie technologii? Tak → BL. Nie → ARCH. Jeśli część tak, a część nie → MIXED.

Zasady

	1.	Nie zmieniaj sensu, nie dodawaj informacji, nie pomijaj szczegółów.
	2.	Dla BL i ARCH zwracasz null w polach tekstowych (oryginał zostanie użyty bez zmian).
	3.	Dla MIXED rozdziel tekst na dwie części:
	•	bl_text: sama intencja/reguła biznesowa, bez nazw technologii, endpointów i typów.
	•	arch_text: sama realizacja techniczna, bez reguł biznesowych poza odwołaniem do nich.
	•	W obu częściach zachowaj oryginalne sformułowania, gdzie się da.
	4.	W razie wątpliwości wybierz MIXED i obniż confidence.
	5.	Odpowiedz WYŁĄCZNIE poprawnym JSON-em, bez komentarza i bez ```.

Format wejścia

[{"id": "F01-U003", "heading_path": "Zamówienia > Akceptacja", "text": "..."}]

Format wyjścia

[
  {
    "id": "F01-U003",
    "tag": "BL | ARCH | MIXED",
    "bl_text": null,
    "arch_text": null,
    "confidence": 0.0,
    "reason": "jedno zdanie"
  }
]

Każde id z wejścia musi wystąpić w wyjściu dokładnie raz.

Przykłady graniczne

Wejście: Zamówienie powyżej 1000 zł wymaga akceptacji kierownika.
→ BL

Wejście: Endpoint POST /orders/{id}/approve zwraca 403, gdy rola ≠ MANAGER.
→ ARCH

Wejście: Zamówienie powyżej 1000 zł wymaga akceptacji; endpoint POST /orders/{id}/approve zwraca 403 dla innych ról.
→ MIXED, bl_text: "Zamówienie powyżej 1000 zł wymaga akceptacji kierownika; inne role nie mogą go zaakceptować.", arch_text: "Endpoint POST /orders/{id}/approve zwraca 403 dla ról innych niż uprawniona."

Wejście: Rabat wynosi 10% dla klientów premium.
→ BL

Wejście: Rabaty są cache'owane w Redis przez 5 minut.
→ ARCH

Dane do klasyfikacji

[WKLEJ ZAWARTOŚĆ work/NN.to_tag.json]