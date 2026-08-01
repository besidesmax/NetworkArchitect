# Network Architect

Ein Windows-Desktop-Puzzlespiel, inspiriert von **Hashiwokakero** und neu interpretiert im Netzwerktechnik-Thema. Statt
Inseln und Brücken werden Netzwerkknoten (Server, Router, Firewall, Client) mit Datenverbindungen (Ethernet, WLAN,
Glasfaser) verbunden — unter Budgetgrenze und nach klaren Validierungsregeln.

---

## Inhaltsverzeichnis

- [Über das Projekt](#über-das-projekt)
- [Features](#features)
- [Spielprinzip](#spielprinzip)
- [Technologie-Stack](#technologie-stack)
- [Architektur](#architektur)
- [Installation](#installation)
- [Ausführen](#ausführen)
- [Tests](#tests)
- [Build / Packaging](#build--packaging)
- [Projektstruktur](#projektstruktur)
- [Dokumentation](#dokumentation)
- [Autor](#autor)

---

## Über das Projekt

Ziel des Projekts ist es, den vollständigen Software-Engineering-Lebenszyklus praktisch durchzuführen: Requirements
Engineering, Spezifikation, Architektur, Implementierung, Test, Packaging und Reflexion. Neben dem lauffähigen Produkt
stehen nachvollziehbare Engineering-Entscheidungen, Dokumentationsqualität und Qualitätssicherung im Vordergrund.

**Zielgruppe:** primär Puzzle-Begeisterte, sekundär IT-Studierende, die Netzwerkkonzepte spielerisch erkunden möchten.

## Features

- Desktop-Anwendung für Windows 10/11
- Logik-Puzzles nach Hashiwokakero-Verbindungsregeln
- Netzwerkthematische Knotentypen: Server, Client, Firewall, Router
- Mehrere Verbindungstypen mit unterschiedlichen Eigenschaften (Ethernet, WLAN, Glasfaser)
- Budgetbasiertes Gameplay mit Lösungsvalidierung
- Kennzahlen **Redundanz** und **Performance** zur Bewertung der Lösung
- Spieler- und Levelauswahl mit Fortschrittsspeicherung
- Statistikansicht mit den Reitern *Spielerstatistik* und *Levelstatistik*
- Lokale Persistenz über SQLite
- Automatisierte Tests mit pytest
- Standalone-Windows-Executable via PyInstaller

## Spielprinzip

Der Spielbildschirm gliedert sich in drei Bereiche: Steuerung, GameBoard (zentral, levelabhängig) und Auswahl des
Verbindungstyps.

**Verbindungsregeln (Auszug)**

- Eine Verbindung wird durch Auswahl zweier Punkte gesetzt; der zweite Node bzw. GridPoint muss zum ersten benachbart
  sein.
- Verbindungen dürfen sich nicht kreuzen.
- Jeder Knoten besitzt eine vorgegebene Anzahl an Verbindungen, die exakt erfüllt werden muss.
- Das verfügbare Budget darf nicht überschritten werden.

**Bewertungskennzahlen**

| Kennzahl    | Definition                                                                                                            |
|-------------|-----------------------------------------------------------------------------------------------------------------------|
| Redundanz   | Anzahl der Verbindungen, die entfernt werden können, ohne dass das Level unlösbar wird                                |
| Performance | Durchschnittliche Qualität des besten Pfades von jedem Client zum Server; bester Pfad = höchste Bottleneck-Bandbreite |

Beide Kennzahlen werden durch zwei vollständig getrennte Algorithmen berechnet.

**Bedienung**

- *Hilfe* prüft die aktuelle Lösung und zeigt das Ergebnis an.
- *Weiter spielen* verbleibt im aktuellen Level, um Performance und Redundanz bei verbleibendem Budget weiter zu
  optimieren.
- *Nächstes Level* startet unmittelbar das nächste Level.
- *Reset* setzt Spielstand und Zeit zurück und startet das Level neu.
- Beim Wechsel zur Levelauswahl oder zum Hauptmenü erscheint eine Warnung, dass der aktuelle Fortschritt verloren geht.
- Ist kein Level ausgewählt, ist der Button *Spiel starten* deaktiviert und ausgegraut.

## Technologie-Stack

| Bereich           | Technologie                 |
|-------------------|-----------------------------|
| Sprache           | Python                      |
| GUI               | PySide6 / QGraphicsView     |
| Architektur       | MVVM (Model-View-ViewModel) |
| Datenbank         | SQLite                      |
| Tests             | pytest                      |
| Packaging         | PyInstaller                 |
| Versionskontrolle | Git / GitHub                |

## Architektur

Die Anwendung folgt dem MVVM-Muster, um Präsentationslogik, Geschäftslogik und Persistenz sauber zu trennen. Das
verbessert Wartbarkeit und Testbarkeit und hält Spielregeln unabhängig von der GUI.

- **Model:** `GameSession`, `Level`, `Network`, `Node`, `Bridge` sowie unterstützende Typen
  wie `NodeType`, `BridgeType`, `NodeConfig`
- **ViewModel:** `LevelSelectionViewModel`, `GameViewModel`, `StatisticsViewModel`
- **View:** `MainMenuView`, `LevelSelectionView`, `GameView`, `StatisticsView`
- **Persistenz:** `DatabaseService` (SQLite-Zugriff)

## Installation

Voraussetzung: Python 3.11 oder neuer sowie Git.

```bash
git clone https://github.com/<user>/network-architect.git
cd network-architect

python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Ausführen

```bash
python main.py
```

Alternativ steht unter *Releases* eine gepackte `NetworkArchitect.exe` bereit, die ohne separate Python-Installation
lauffähig ist.

## Tests

Die Qualitätssicherung erfolgt über pytest auf den Teststufen Unit, Integration und System.

```bash
pytest                      # alle Tests
pytest --cov=src            # mit Coverage-Report
pytest tests/unit           # nur Unit-Tests
```

## Build / Packaging

```bash
pyinstaller --onefile --windowed --name NetworkArchitect main.py
```

Das Ergebnis liegt anschließend unter `dist/NetworkArchitect.exe`.

## Projektstruktur

```
network-architect/
├── src/
│   ├── model/          # Domänenmodell und Spiellogik
│   ├── viewmodel/      # ViewModels (MVVM)
│   ├── view/           # PySide6-Views
│   └── persistence/    # DatabaseService, SQLite-Zugriff
├── tests/
│   ├── unit/
│   ├── integration/
│   └── system/
├── docs/               # Projektdokumentation
├── resources/          # Icons, Logo, Leveldaten
├── main.py
├── requirements.txt
└── README.md
```

## Dokumentation

Im Ordner `docs/` finden sich die Deliverables der drei Projektphasen:

- Projektdokumentation mit Benutzerhandbuch
- Anforderungsdokumentation und Spezifikation
- Architekturdokumentation
- Testdokument und Testprotokolle
- Abstract

