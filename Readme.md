1. Scannen
    - Handheld Rapid Scan mit Kamera-Modul
    - Texturescan
    - Ausrichtung: Über Textur
    - Betriebsmodus: Schnell
    - Auflösung Medium Details eventuell Niedrige Details
    - Startknopf auf Scanner betätigen zum Starten
    - Zweimal Startknopf betätigen um Helligkeit über zwei darunter befindliche Knöpfe anzupassen
2. Meshen
    - Punktwolke generieren auf der rechten Seite oben
    - Modell meshen
    - geschlossener Mesh
3. In Blender importieren
    - .Mtl und .Obj auswählen
    - Rauszoomen
    - Rechtsklick auf Objekt -> Set Origin -> Geometry to Origin
    - Rotieren (mit "rr" frei und mit "rx" um x-Achse)
    - Skalieren (m "s" skalieren)
    - Würfel hinzufügen (mit Shift+a)
    - Würfel skalieren, sodass ganzer Grundkörper verdeckt wird
    - Würfel auf gewünschte Höhe schieben mit "gz"
    - Scan auswählen
    - Add modifier Boolean (Difference)
    - Würfel auswählen
    - Apply
    - Decimate Modifier - Ratio 0.3
    - Apply
    - Export Wavefront
    - Textur an Export-Ort kopieren
5. Programm öffnen mit python main.py
    1. template.html auswählen - Weiter
    2. Obj. File und Texture auswählen - Weiter
    3. Ausgabeort des Resultates wählen
    4. Bestätigen