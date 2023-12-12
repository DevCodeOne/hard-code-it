1. Scannen
    - Ausrichtung über Textur
2. Meshen
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