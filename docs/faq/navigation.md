# ZMS TAL-Templating: API-Funktionen für Navigations-Elemente

*Erstellt mit Gemini Thinking-Modus, 26. März 2026*

---


In ZMS wird die Navigation meist über Zope Page Templates (ZPT) und die Template
Attribute Language (TAL) gerendert. Da ZMS-Objekte hierarchisch aufgebaut sind, greift
man für Navigations-Elemente auf spezifische API-Methoden der ZMS-Klassen zu.

Hier ist eine Liste der wichtigsten API-Funktionen für das TAL-Templating von Navigationen:

---

## Kern-Funktionen für die Navigation

### 1. `getNavNodes(request)`

Dies ist die Standard-Methode, um die Kind-Objekte für eine Navigationsebene abzurufen.

**Erklärung:** Sie gibt eine Liste von Objekten zurück, die im ZMS-Strukturbaum als
"in der Navigation anzeigen" markiert sind.

**TAL-Beispiel:**

```html
<li tal:repeat="node python:here.getNavNodes(request)">
    <a tal:attributes="href python:node.getHref2IndexHtml(request)" 
       tal:content="python:node.getTitlealt(request)">Title</a>
</li>
```

### 2. `getHref2IndexHtml(request)`

**Erklärung:** Erzeugt die korrekte URL zum Zielobjekt. Im Gegensatz zu einer einfachen
URL-Abfrage stellt diese Methode sicher, dass der Link zur `index_html` des Objekts führt,
was für die Konsistenz der Pfade wichtig ist.

### 3. `getTitlealt(request)`

**Erklärung:** Gibt den Navigationstitel (Titlealt) zurück. In ZMS gibt es oft einen langen
Haupttitel und einen kurzen Titel für Menüs; diese Methode priorisiert den kurzen Titel.

### 4. `getLevel()`

**Erklärung:** Gibt die numerische Ebene des aktuellen Objekts im Baum zurück
(z. B. `0` für die Root, `1` für die erste Ebene). Hilfreich für bedingte Formatierungen
oder Einrückungen.

### 5. `getParentNodes()`

**Erklärung:** Gibt eine Liste aller Eltern-Objekte bis zur Wurzel zurück.

**Nutzen:** Unverzichtbar für die Erstellung einer Breadcrumb-Navigation (Brotkrumenpfad).

---

## Status- und Kontroll-Methoden

Um Menüs dynamisch zu gestalten (z. B. "Active"-States), sind diese Funktionen wichtig:

| Funktion | Beschreibung |
|---|---|
| `is_selected(node)` | Prüft, ob der `node` im aktuellen Pfad liegt (um Menüpunkte optisch hervorzuheben). |
| `isActive(request)` | Gibt zurück, ob das Objekt aktuell veröffentlicht und für den User sichtbar ist. |
| `getPortalMaster()` | Springt zur obersten Ebene (Home) des ZMS-Portals, ideal für den "Home"-Link im Menü. |

---

## Fortgeschrittene Navigation (Sitemap & Filter)

### `getTreeNodes(request, [limit])`

Gibt den gesamten Baum (oder bis zu einer gewissen Tiefe) zurück. Das ist die Basis für
Sitemaps oder Dropdown-Menüs mit mehreren Ebenen.

### `getFilteredNodes(request, filter_name)`

Falls du nur bestimmte Inhaltstypen in der Navigation anzeigen möchtest (z. B. nur
"Folder" und keine "Dokumente"), kannst du über definierte Filter gehen.

---

## Breadcrumb-Beispiel in TAL

```html
<nav aria-label="Breadcrumb">
  <ol>
    <li tal:repeat="node python:here.getParentNodes()">
      <a tal:attributes="href python:node.getHref2IndexHtml(request)"
         tal:content="python:node.getTitlealt(request)">Ebene</a>
    </li>
    <li class="active" tal:content="python:here.getTitlealt(request)">Aktuelle Seite</li>
  </ol>
</nav>
```

> **Hinweis:** Da ZMS auf Zope basiert, ist der Kontext `here` (das aktuelle Objekt) im
> Template entscheidend. Fast alle Methoden erwarten das `request`-Objekt, um Parameter
> wie die aktuelle Sprache (`lang`) korrekt zu verarbeiten.

---

## 2-stufiges Dropdown-Menü

### Das TAL-Template

```html
<nav class="navbar">
  <ul class="nav-main" tal:define="portal_master python:here.getPortalMaster()">
    
    <li tal:repeat="item1 python:portal_master.getNavNodes(request)"
        tal:attributes="class python:'nav-item' + (here.is_selected(item1) and ' active' or '')">
      
      <a tal:attributes="href python:item1.getHref2IndexHtml(request)"
         tal:content="python:item1.getTitlealt(request)">Ebene 1</a>

      <ul class="nav-dropdown" 
          tal:define="children python:item1.getNavNodes(request)"
          tal:condition="children">
        
        <li tal:repeat="item2 children"
            tal:attributes="class python:'nav-subitem' + (here == item2 and ' current' or '')">
          
          <a tal:attributes="href python:item2.getHref2IndexHtml(request)"
             tal:content="python:item2.getTitlealt(request)">Ebene 2</a>
        </li>
      </ul>
      
    </li>
  </ul>
</nav>
```

### Die Logik dahinter

- **`getPortalMaster()`:** Damit stellen wir sicher, dass das Menü immer von der obersten
  Ebene (Home) gerendert wird, egal auf welcher Unterseite sich der User gerade befindet.
- **`getNavNodes(request)`:** Filtert automatisch alle Objekte aus, bei denen der Haken
  "In Navigation anzeigen" im ZMS-Backend nicht gesetzt ist.
- **`is_selected(item1)`:** Diese Methode ist Gold wert. Sie gibt `True` zurück, wenn das
  Objekt `item1` entweder die aktuelle Seite ist oder ein Elternteil der aktuellen Seite.
  So bleibt der Hauptmenüpunkt optisch aktiv, während man in den Unterseiten surft.
- **`tal:condition="children"`:** Verhindert, dass leere `<ul>`-Tags gerendert werden,
  wenn ein Menüpunkt keine Unterseiten hat.

### CSS für Hover-Dropdown

```css
.nav-main { list-style: none; display: flex; gap: 20px; }
.nav-item { position: relative; }
.nav-dropdown { 
  display: none; 
  position: absolute; 
  top: 100%; 
  left: 0; 
  background: #fff; 
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  list-style: none;
  padding: 10px;
}

/* Zeige Dropdown bei Hover */
.nav-item:hover .nav-dropdown {
  display: block;
}

.nav-item.active > a { font-weight: bold; color: blue; }
```

---

## Rekursives Makro für unbegrenzte Menü-Tiefen

Rekursion ist in der Welt von Zope und ZMS der "Königsweg", um Baumstrukturen abzubilden.
Anstatt für jede Ebene den Code zu kopieren, definieren wir ein METAL-Makro, das sich
einfach selbst aufruft, solange Unterseiten vorhanden sind.

### 1. Das rekursive Makro (TAL/METAL)

```html
<div tal:omit-tag="" metal:define-macro="nav_recurse">
  <ul tal:define="children python:node.getNavNodes(request)"
      tal:condition="children">
      
    <li tal:repeat="child children"
        tal:attributes="class python:'nav-level-' + str(child.getLevel()) + (here.is_selected(child) and ' active' or '')">
      
      <a tal:attributes="href python:child.getHref2IndexHtml(request)"
         tal:content="python:child.getTitlealt(request)">Seitentitel</a>

      <div tal:omit-tag="" 
           tal:define="node child" 
           metal:use-macro="python:here.get_self().absolute_url() + '/macros/nav_recurse'">
      </div>

    </li>
  </ul>
</div>
```

### 2. Der initiale Aufruf

```html
<nav class="recursive-menu" 
     tal:define="node python:here.getPortalMaster()">
     
  <div tal:omit-tag="" metal:use-macro="python:here.get_self().absolute_url() + '/macros/nav_recurse'"></div>
  
</nav>
```

### Funktionsweise erklärt

- **`metal:define-macro="nav_recurse"`:** Erstellt einen wiederverwendbaren Baustein.
- **`tal:define="node child"`:** Das ist der entscheidende Trick. Bevor das Makro erneut
  aufgerufen wird, setzen wir die Variable `node` auf das aktuelle Kind-Element. Das Makro
  arbeitet dann in der nächsten Ebene mit diesem neuen Kontext.
- **`tal:omit-tag=""`:** Verhindert, dass unnötige `<div>`-Container das HTML-Layout
  zerschießen. Nur die `<ul>` und `<li>` bleiben übrig.
- **`child.getLevel()`:** Damit bekommt jede Ebene eine eigene CSS-Klasse
  (z. B. `.nav-level-1`, `.nav-level-2`), was das Styling von eingerückten Untermenüs
  massiv erleichtert.

### Wann sollte man das nutzen?

| Szenario | Empfehlung |
|---|---|
| Klassische Top-Nav | Meist fix 2 Ebenen (ohne Rekursion einfacher zu stylen). |
| Sidebar-Menü | Rekursion ideal, da die Tiefe oft variiert. |
| Sitemap | Rekursion zwingend erforderlich, um alles abzubilden. |

> **Fallstrick:** Bei extrem großen Seitenbäumen (Tausende von Objekten) kann eine
> unbegrenzte Rekursion die Performance drücken. In solchen Fällen begrenzt man die Tiefe
> mit einer zusätzlichen Bedingung:
> `tal:condition="python:child.getLevel() < 4"`

---

## Erweiterung: FontAwesome-Icons aus ZMS-Contentklassen

In ZMS ist die Einbindung von Icons sehr elegant gelöst, da jedes Objekt (jede
Contentklasse) bereits eine Icon-Definition in seiner Metadaten-Konfiguration besitzt.
Seit ZMS5 wird hierfür standardmäßig FontAwesome verwendet.

Um die Icons in die Navigation zu integrieren, nutzt man die Methode `getIcon(request)`.
Diese gibt bereits den fertigen HTML-Tag (z. B. `<i class="fas fa-folder"></i>`) zurück.

### Das erweiterte TAL-Makro mit Icons

Der entscheidende Teil ist die Verwendung von `tal:replace="structure ..."` – das sorgt
dafür, dass Zope den HTML-Code des Icons nicht als Text maskiert, sondern als echtes HTML
ausgibt.

```html
<div tal:omit-tag="" metal:define-macro="nav_recurse">
  <ul tal:define="children python:node.getNavNodes(request)"
      tal:condition="children">
      
    <li tal:repeat="child children"
        tal:attributes="class python:'nav-level-' + str(child.getLevel()) + (here.is_selected(child) and ' active' or '')">
      
      <a tal:attributes="href python:child.getHref2IndexHtml(request)">
        <span class="nav-icon" 
              tal:replace="structure python:child.getIcon(request)">
          <i class="fas fa-file"></i>
        </span>
        
        <span class="nav-label" 
              tal:content="python:child.getTitlealt(request)">Seitentitel</span>
      </a>

      <div tal:omit-tag="" 
           tal:define="node child" 
           metal:use-macro="python:here.get_self().absolute_url() + '/macros/nav_recurse'">
      </div>

    </li>
  </ul>
</div>
```

### Was hat sich geändert?

- **`child.getIcon(request)`:** Diese Methode schaut in der ZMS-Konfiguration nach, welches
  Icon für den Content-Typ (z. B. Folder, Document, News) hinterlegt ist.
- **`structure`-Keyword:** In TAL verhindert `structure`, dass Zeichen wie `<` oder `>` in
  `&lt;` umgewandelt werden. Da `getIcon()` einen kompletten `<i>`-Tag zurückgibt, ist
  dies zwingend erforderlich.
- **Klassentrennung:** Das Icon und der Text sind in separate `<span>`-Tags gepackt
  (`nav-icon` und `nav-label`). Das macht das Styling via CSS wesentlich einfacher.

### CSS für Icon-Ausrichtung

```css
.nav-level-1 a, .nav-level-2 a {
  display: flex;
  align-items: center; /* Vertikale Zentrierung */
  text-decoration: none;
  padding: 5px 0;
}

.nav-icon {
  margin-right: 8px; /* Abstand zwischen Icon und Text */
  width: 20px;       /* Fixe Breite für saubere Ausrichtung untereinander */
  text-align: center;
  display: inline-block;
}

/* Optional: Icons in der Navigation etwas dezenter färben */
.nav-icon i {
  color: #666;
}

.active > a .nav-icon i {
  color: #0056b3; /* Icon-Farbe für den aktiven Pfad */
}
```

> **Performance-Tipp:** Wenn du die Icons direkt als CSS-Klasse haben möchtest (ohne den
> fertigen Tag von ZMS zu nutzen), könntest du auch
> `python:child.getMetaobj().get('icon_clazz')` verwenden. Die Methode `getIcon(request)`
> ist jedoch sicherer, da sie auch Fallbacks (z. B. für Bilder-Icons) berücksichtigt.
