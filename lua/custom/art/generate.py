#!/usr/bin/env python3
"""Regenerate the ASCII gallery used by the WesCode start screen.

For every entry in MANIFEST this script fetches the lead image of the
artwork's English Wikipedia article, converts it with `ascii-image-converter`
(brew install TheZoraiz/ascii-image-converter/ascii-image-converter) and writes
lua/custom/art/gallery/h<rows>/<slug>.txt, one file per size tier, in the
format the start screen expects:

    line 1: title
    line 2: artist / origin
    rest  : the artwork, as braille cells coloured with 24-bit ANSI escapes
            (`cat` a file in a truecolor terminal to preview it)

The start screen picks the tallest tier that fits the current window.

Usage:
    python3 lua/custom/art/generate.py            # everything
    python3 lua/custom/art/generate.py mona-lisa  # just these slugs
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
GALLERY = os.path.join(HERE, "gallery")
CACHE = os.path.join(HERE, ".cache")
UA = "WesCodeNvimArt/1.0 (personal nvim config)"
HEIGHTS = [12, 18, 24, 32]       # size tiers, in rows
MAX_WIDTH = 140                   # cap columns at any tier
THUMB = 960                       # one of Wikimedia's pre-rendered thumbnail widths
QUANT = 16                        # round colour channels to multiples of this
MAX_TALL = 1.5     # crop images taller than this h/w ratio
MAX_WIDE = 3.0     # crop images wider than this w/h ratio

# (slug, wikipedia article, display title, artist / origin[, commons file])
# The optional fifth field names a Wikimedia Commons file to use instead of
# the article's lead image (for articles whose lead image is a logo, missing,
# or otherwise unsuitable).
MANIFEST = [
    # ---- paintings ------------------------------------------------------
    ("starry-night", "The Starry Night", "The Starry Night", "Vincent van Gogh, 1889"),
    ("mona-lisa", "Mona Lisa", "Mona Lisa", "Leonardo da Vinci, c. 1503"),
    ("the-scream", "The Scream", "The Scream", "Edvard Munch, 1893"),
    ("girl-with-a-pearl-earring", "Girl with a Pearl Earring", "Girl with a Pearl Earring", "Johannes Vermeer, c. 1665"),
    ("persistence-of-memory", "The Persistence of Memory", "The Persistence of Memory", "Salvador Dalí, 1931"),
    ("great-wave", "The Great Wave off Kanagawa", "The Great Wave off Kanagawa", "Katsushika Hokusai, c. 1831"),
    ("last-supper", "The Last Supper (Leonardo)", "The Last Supper", "Leonardo da Vinci, c. 1495"),
    ("birth-of-venus", "The Birth of Venus", "The Birth of Venus", "Sandro Botticelli, c. 1485"),
    ("american-gothic", "American Gothic", "American Gothic", "Grant Wood, 1930"),
    ("nighthawks", "Nighthawks (Hopper)", "Nighthawks", "Edward Hopper, 1942"),
    ("the-kiss-klimt", "The Kiss (Klimt)", "The Kiss", "Gustav Klimt, 1908"),
    ("guernica", "Guernica (Picasso)", "Guernica", "Pablo Picasso, 1937"),
    ("creation-of-adam", "The Creation of Adam", "The Creation of Adam", "Michelangelo, c. 1512"),
    ("sunflowers", "Sunflowers (Van Gogh series)", "Sunflowers", "Vincent van Gogh, 1888"),
    ("water-lilies", "Water Lilies (Monet series)", "Water Lilies", "Claude Monet, c. 1906"),
    ("impression-sunrise", "Impression, Sunrise", "Impression, Sunrise", "Claude Monet, 1872"),
    ("whistlers-mother", "Whistler's Mother", "Whistler's Mother", "James McNeill Whistler, 1871"),
    ("son-of-man", "The Son of Man", "The Son of Man", "René Magritte, 1964"),
    ("composition-mondrian", "Composition with Red, Blue and Yellow", "Composition with Red, Blue and Yellow", "Piet Mondrian, 1930"),
    ("campbells-soup-cans", "Campbell's Soup Cans", "Campbell's Soup Cans", "Andy Warhol, 1962"),
    ("las-meninas", "Las Meninas", "Las Meninas", "Diego Velázquez, 1656"),
    ("night-watch", "The Night Watch", "The Night Watch", "Rembrandt, 1642"),
    ("liberty-leading-the-people", "Liberty Leading the People", "Liberty Leading the People", "Eugène Delacroix, 1830"),
    ("wanderer-above-the-sea-of-fog", "Wanderer above the Sea of Fog", "Wanderer above the Sea of Fog", "Caspar David Friedrich, 1818"),
    ("grande-jatte", "A Sunday Afternoon on the Island of La Grande Jatte", "A Sunday Afternoon on La Grande Jatte", "Georges Seurat, 1886"),
    ("garden-of-earthly-delights", "The Garden of Earthly Delights", "The Garden of Earthly Delights", "Hieronymus Bosch, c. 1500"),
    ("christinas-world", "Christina's World", "Christina's World", "Andrew Wyeth, 1948"),
    ("arnolfini-portrait", "Arnolfini Portrait", "The Arnolfini Portrait", "Jan van Eyck, 1434"),
    ("cafe-terrace-at-night", "Café Terrace at Night", "Café Terrace at Night", "Vincent van Gogh, 1888"),
    ("bedroom-in-arles", "Bedroom in Arles", "Bedroom in Arles", "Vincent van Gogh, 1888"),
    ("self-portrait-bandaged-ear", "Self-Portrait with Bandaged Ear", "Self-Portrait with Bandaged Ear", "Vincent van Gogh, 1889"),
    ("treachery-of-images", "The Treachery of Images", "The Treachery of Images", "René Magritte, 1929"),
    ("napoleon-crossing-the-alps", "Napoleon Crossing the Alps", "Napoleon Crossing the Alps", "Jacques-Louis David, 1801"),
    ("death-of-marat", "The Death of Marat", "The Death of Marat", "Jacques-Louis David, 1793"),
    ("washington-crossing-the-delaware", "Washington Crossing the Delaware (1851 paintings)", "Washington Crossing the Delaware", "Emanuel Leutze, 1851"),
    ("raft-of-the-medusa", "The Raft of the Medusa", "The Raft of the Medusa", "Théodore Géricault, 1819"),
    ("hay-wain", "The Hay Wain", "The Hay Wain", "John Constable, 1821"),
    ("fighting-temeraire", "The Fighting Temeraire", "The Fighting Temeraire", "J. M. W. Turner, 1839"),
    ("ophelia", "Ophelia (painting)", "Ophelia", "John Everett Millais, 1852", "John Everett Millais - Ophelia - Google Art Project.jpg"),
    ("lady-of-shalott", "The Lady of Shalott (painting)", "The Lady of Shalott", "John William Waterhouse, 1888"),
    ("moulin-de-la-galette", "Bal du moulin de la Galette", "Bal du moulin de la Galette", "Pierre-Auguste Renoir, 1876"),
    ("dance-class", "The Dance Class (Degas, Musée d'Orsay)", "The Dance Class", "Edgar Degas, 1874", "Edgar Degas - The Ballet Class - Google Art Project.jpg"),
    ("card-players", "The Card Players", "The Card Players", "Paul Cézanne, c. 1895"),
    ("where-do-we-come-from", "Where Do We Come From? What Are We? Where Are We Going?", "Where Do We Come From? What Are We? Where Are We Going?", "Paul Gauguin, 1897"),
    ("sleeping-gypsy", "The Sleeping Gypsy", "The Sleeping Gypsy", "Henri Rousseau, 1897"),
    ("the-dream-rousseau", "The Dream (Rousseau painting)", "The Dream", "Henri Rousseau, 1910"),
    ("broadway-boogie-woogie", "Broadway Boogie-Woogie", "Broadway Boogie-Woogie", "Piet Mondrian, 1943"),
    ("black-square", "Black Square", "Black Square", "Kazimir Malevich, 1915"),
    ("composition-viii", "Composition VIII", "Composition VIII", "Wassily Kandinsky, 1923", "Vassily Kandinsky, 1923 - Composition 8, huile sur toile, 140 cm x 201 cm, Musée Guggenheim, New York.jpg"),
    ("two-fridas", "The Two Fridas", "The Two Fridas", "Frida Kahlo, 1939"),
    ("thorn-necklace", "Self-Portrait with Thorn Necklace and Hummingbird", "Self-Portrait with Thorn Necklace and Hummingbird", "Frida Kahlo, 1940"),
    ("no-5-1948", "No. 5, 1948", "No. 5, 1948", "Jackson Pollock, 1948"),
    ("marilyn-diptych", "Marilyn Diptych", "Marilyn Diptych", "Andy Warhol, 1962"),
    ("whaam", "Whaam!", "Whaam!", "Roy Lichtenstein, 1963"),
    ("flag-johns", "Flag (painting)", "Flag", "Jasper Johns, 1954"),
    ("anatomy-lesson", "The Anatomy Lesson of Dr. Nicolaes Tulp", "The Anatomy Lesson of Dr. Nicolaes Tulp", "Rembrandt, 1632"),
    ("demoiselles-davignon", "Les Demoiselles d'Avignon", "Les Demoiselles d'Avignon", "Pablo Picasso, 1907"),
    ("old-guitarist", "The Old Guitarist", "The Old Guitarist", "Pablo Picasso, 1903"),
    ("weeping-woman", "The Weeping Woman", "The Weeping Woman", "Pablo Picasso, 1937"),
    ("adele-bloch-bauer", "Portrait of Adele Bloch-Bauer I", "Portrait of Adele Bloch-Bauer I", "Gustav Klimt, 1907"),
    ("tower-of-babel", "The Tower of Babel (Bruegel)", "The Tower of Babel", "Pieter Bruegel the Elder, 1563"),
    ("hunters-in-the-snow", "The Hunters in the Snow", "The Hunters in the Snow", "Pieter Bruegel the Elder, 1565"),
    ("the-ambassadors", "The Ambassadors (Holbein)", "The Ambassadors", "Hans Holbein the Younger, 1533"),
    ("lady-with-an-ermine", "Lady with an Ermine", "Lady with an Ermine", "Leonardo da Vinci, c. 1490"),
    ("vitruvian-man", "Vitruvian Man", "Vitruvian Man", "Leonardo da Vinci, c. 1490"),
    ("saturn-devouring-his-son", "Saturn Devouring His Son", "Saturn Devouring His Son", "Francisco Goya, c. 1823"),
    ("third-of-may-1808", "The Third of May 1808", "The Third of May 1808", "Francisco Goya, 1814"),
    ("the-milkmaid", "The Milkmaid (Vermeer)", "The Milkmaid", "Johannes Vermeer, c. 1658"),
    ("view-of-delft", "View of Delft", "View of Delft", "Johannes Vermeer, c. 1660"),
    ("the-swing", "The Swing (Fragonard)", "The Swing", "Jean-Honoré Fragonard, 1767"),
    ("rain-steam-and-speed", "Rain, Steam and Speed – The Great Western Railway", "Rain, Steam and Speed", "J. M. W. Turner, 1844"),
    ("bathers-at-asnieres", "Bathers at Asnières", "Bathers at Asnières", "Georges Seurat, 1884"),
    ("folies-bergere", "A Bar at the Folies-Bergère", "A Bar at the Folies-Bergère", "Édouard Manet, 1882"),
    ("dejeuner-sur-lherbe", "Le Déjeuner sur l'herbe", "Le Déjeuner sur l'herbe", "Édouard Manet, 1863"),
    ("luncheon-of-the-boating-party", "Luncheon of the Boating Party", "Luncheon of the Boating Party", "Pierre-Auguste Renoir, 1881"),
    ("fall-of-icarus", "Landscape with the Fall of Icarus", "Landscape with the Fall of Icarus", "Pieter Bruegel the Elder, c. 1560"),
    ("primavera", "Primavera (Botticelli)", "Primavera", "Sandro Botticelli, c. 1480"),
    ("school-of-athens", "The School of Athens", "The School of Athens", "Raphael, 1511"),
    ("sistine-madonna", "Sistine Madonna", "Sistine Madonna", "Raphael, 1512"),
    ("judith-slaying-holofernes", "Judith Slaying Holofernes (Artemisia Gentileschi, Naples)", "Judith Slaying Holofernes", "Artemisia Gentileschi, c. 1612"),
    ("calling-of-saint-matthew", "The Calling of Saint Matthew", "The Calling of Saint Matthew", "Caravaggio, 1600"),
    ("girl-with-balloon", "Girl with Balloon", "Girl with Balloon", "Banksy, 2002"),
    ("the-dance-matisse", "Dance (Matisse)", "Dance", "Henri Matisse, 1910"),
    ("blue-horse", "Blue Horse I", "Blue Horse I", "Franz Marc, 1911"),
    ("flaming-june", "Flaming June", "Flaming June", "Frederic Leighton, 1895"),
    ("the-nightmare", "The Nightmare", "The Nightmare", "Henry Fuseli, 1781"),
    ("paris-street-rainy-day", "Paris Street; Rainy Day", "Paris Street; Rainy Day", "Gustave Caillebotte, 1877"),
    ("gross-clinic", "The Gross Clinic", "The Gross Clinic", "Thomas Eakins, 1875"),
    ("gulf-stream", "The Gulf Stream (painting)", "The Gulf Stream", "Winslow Homer, 1899"),
    ("twittering-machine", "Twittering Machine", "Twittering Machine", "Paul Klee, 1922"),
    ("red-fuji", "Fine Wind, Clear Morning", "Fine Wind, Clear Morning", "Katsushika Hokusai, c. 1830"),
    ("sudden-shower", "Sudden Shower over Shin-Ōhashi bridge and Atake", "Sudden Shower over Shin-Ōhashi Bridge", "Utagawa Hiroshige, 1857"),
    ("boulevard-montmartre", "The Boulevard Montmartre at Night", "The Boulevard Montmartre at Night", "Camille Pissarro, 1897", "Camille Pissarro, The Boulevard Montmartre at Night, 1897.jpg"),
    ("wheatfield-with-crows", "Wheatfield with Crows", "Wheatfield with Crows", "Vincent van Gogh, 1890"),
    ("irises", "Irises (painting)", "Irises", "Vincent van Gogh, 1889"),
    ("almond-blossoms", "Almond Blossoms", "Almond Blossoms", "Vincent van Gogh, 1890"),
    ("starry-night-over-the-rhone", "Starry Night Over the Rhône", "Starry Night Over the Rhône", "Vincent van Gogh, 1888"),
    ("gassed", "Gassed (painting)", "Gassed", "John Singer Sargent, 1919"),
    ("madame-x", "Portrait of Madame X", "Portrait of Madame X", "John Singer Sargent, 1884"),
    ("storm-on-the-sea-of-galilee", "The Storm on the Sea of Galilee", "The Storm on the Sea of Galilee", "Rembrandt, 1633"),
    ("the-gleaners", "The Gleaners", "The Gleaners", "Jean-François Millet, 1857"),
    ("the-angelus", "The Angelus (painting)", "The Angelus", "Jean-François Millet, 1859"),
    ("the-magpie", "The Magpie (Monet)", "The Magpie", "Claude Monet, 1869"),
    ("woman-with-a-parasol", "Woman with a Parasol – Madame Monet and Her Son", "Woman with a Parasol", "Claude Monet, 1875"),
    ("the-oxbow", "The Oxbow", "The Oxbow", "Thomas Cole, 1836"),
    ("nocturne-falling-rocket", "Nocturne in Black and Gold – The Falling Rocket", "Nocturne in Black and Gold: The Falling Rocket", "James McNeill Whistler, 1875"),
    ("the-blue-boy", "The Blue Boy", "The Blue Boy", "Thomas Gainsborough, c. 1770"),
    ("the-jewish-bride", "The Jewish Bride", "The Jewish Bride", "Rembrandt, c. 1667"),
    # ---- sculpture ------------------------------------------------------
    ("david", "David (Michelangelo)", "David", "Michelangelo, 1504"),
    ("the-thinker", "The Thinker", "The Thinker", "Auguste Rodin, 1904"),
    ("venus-de-milo", "Venus de Milo", "Venus de Milo", "Alexandros of Antioch, c. 130 BC"),
    ("winged-victory", "Winged Victory of Samothrace", "Winged Victory of Samothrace", "Unknown, c. 190 BC"),
    ("pieta", "Pietà (Michelangelo)", "Pietà", "Michelangelo, 1499"),
    ("the-kiss-rodin", "The Kiss (Rodin sculpture)", "The Kiss", "Auguste Rodin, 1882"),
    ("nefertiti-bust", "Nefertiti Bust", "Bust of Nefertiti", "Thutmose, c. 1345 BC"),
    ("discobolus", "Discobolus", "Discobolus", "Myron, c. 450 BC"),
    ("moai", "Moai", "Moai", "Rapa Nui, c. 1250-1500"),
    ("terracotta-army", "Terracotta Army", "Terracotta Army", "Qin dynasty, c. 210 BC"),
    ("great-sphinx", "Great Sphinx of Giza", "Great Sphinx of Giza", "Old Kingdom Egypt, c. 2500 BC"),
    ("statue-of-liberty", "Statue of Liberty", "Statue of Liberty", "Frédéric Auguste Bartholdi, 1886"),
    ("christ-the-redeemer", "Christ the Redeemer (statue)", "Christ the Redeemer", "Paul Landowski, 1931"),
    ("cloud-gate", "Cloud Gate", "Cloud Gate", "Anish Kapoor, 2006"),
    ("love-sculpture", "Love (sculpture)", "LOVE", "Robert Indiana, 1970"),
    ("balloon-dog", "Balloon Dog", "Balloon Dog", "Jeff Koons, 1994"),
    ("little-mermaid", "The Little Mermaid (statue)", "The Little Mermaid", "Edvard Eriksen, 1913"),
    ("laocoon", "Laocoön and His Sons", "Laocoön and His Sons", "Hellenistic, c. 1st century BC"),
    ("bird-in-space", "Bird in Space", "Bird in Space", "Constantin Brâncuși, 1923"),
    ("manneken-pis", "Manneken Pis", "Manneken Pis", "Jérôme Duquesnoy the Elder, 1619"),
    ("augustus-of-prima-porta", "Augustus of Prima Porta", "Augustus of Prima Porta", "Roman, 1st century AD"),
    ("capitoline-wolf", "Capitoline Wolf", "Capitoline Wolf", "Etruscan or medieval, Rome"),
    ("ecstasy-of-saint-teresa", "Ecstasy of Saint Teresa", "Ecstasy of Saint Teresa", "Gian Lorenzo Bernini, 1652"),
    ("charging-bull", "Charging Bull", "Charging Bull", "Arturo Di Modica, 1989"),
    ("spoonbridge-and-cherry", "Spoonbridge and Cherry", "Spoonbridge and Cherry", "Claes Oldenburg & Coosje van Bruggen, 1988"),
    ("fearless-girl", "Fearless Girl", "Fearless Girl", "Kristen Visbal, 2017"),
    # ---- architecture ---------------------------------------------------
    ("eiffel-tower", "Eiffel Tower", "Eiffel Tower", "Gustave Eiffel, Paris, 1889", "Tour Eiffel Wikimedia Commons.jpg"),
    ("taj-mahal", "Taj Mahal", "Taj Mahal", "Agra, 1653"),
    ("parthenon", "Parthenon", "Parthenon", "Athens, 438 BC"),
    ("great-pyramid", "Great Pyramid of Giza", "Great Pyramid of Giza", "Egypt, c. 2560 BC"),
    ("colosseum", "Colosseum", "Colosseum", "Rome, 80 AD"),
    ("sydney-opera-house", "Sydney Opera House", "Sydney Opera House", "Jørn Utzon, 1973"),
    ("golden-gate-bridge", "Golden Gate Bridge", "Golden Gate Bridge", "San Francisco, 1937"),
    ("big-ben", "Big Ben", "Big Ben", "London, 1859"),
    ("leaning-tower-of-pisa", "Leaning Tower of Pisa", "Leaning Tower of Pisa", "Pisa, 1372"),
    ("stonehenge", "Stonehenge", "Stonehenge", "Wiltshire, c. 3000 BC"),
    ("notre-dame", "Notre-Dame de Paris", "Notre-Dame de Paris", "Paris, 1345"),
    ("sagrada-familia", "Sagrada Família", "Sagrada Família", "Antoni Gaudí, Barcelona"),
    ("fallingwater", "Fallingwater", "Fallingwater", "Frank Lloyd Wright, 1939"),
    ("guggenheim", "Solomon R. Guggenheim Museum", "Guggenheim Museum", "Frank Lloyd Wright, 1959"),
    ("burj-khalifa", "Burj Khalifa", "Burj Khalifa", "Dubai, 2010"),
    ("itsukushima-torii", "Itsukushima Shrine", "Itsukushima Shrine", "Miyajima, Japan"),
    ("great-wall", "Great Wall of China", "Great Wall of China", "China"),
    ("chichen-itza", "El Castillo, Chichen Itza", "El Castillo, Chichen Itza", "Maya, c. 800-1200"),
    ("petra", "Al-Khazneh", "Al-Khazneh, Petra", "Nabataean, 1st century AD"),
    ("angkor-wat", "Angkor Wat", "Angkor Wat", "Khmer Empire, 12th century"),
    ("brooklyn-bridge", "Brooklyn Bridge", "Brooklyn Bridge", "John A. Roebling, 1883"),
    ("empire-state-building", "Empire State Building", "Empire State Building", "New York, 1931"),
    ("saint-basils", "Saint Basil's Cathedral", "Saint Basil's Cathedral", "Moscow, 1561"),
    ("hagia-sophia", "Hagia Sophia", "Hagia Sophia", "Istanbul, 537"),
    ("machu-picchu", "Machu Picchu", "Machu Picchu", "Inca, c. 1450"),
    ("pantheon", "Pantheon, Rome", "Pantheon", "Rome, 126 AD"),
    ("arc-de-triomphe", "Arc de Triomphe", "Arc de Triomphe", "Paris, 1836"),
    ("space-needle", "Space Needle", "Space Needle", "Seattle, 1962"),
    ("louvre-pyramid", "Louvre Pyramid", "Louvre Pyramid", "I. M. Pei, 1989"),
    ("mount-rushmore", "Mount Rushmore", "Mount Rushmore", "Gutzon Borglum, 1941"),
    ("brandenburg-gate", "Brandenburg Gate", "Brandenburg Gate", "Berlin, 1791"),
    ("neuschwanstein", "Neuschwanstein Castle", "Neuschwanstein Castle", "Bavaria, 1886"),
    ("chrysler-building", "Chrysler Building", "Chrysler Building", "New York, 1930", "Chrysler Building by David Shankbone Retouched.jpg"),
    ("tower-bridge", "Tower Bridge", "Tower Bridge", "London, 1894"),
    ("himeji-castle", "Himeji Castle", "Himeji Castle", "Japan, 1609"),
    ("florence-cathedral", "Florence Cathedral", "Florence Cathedral", "Brunelleschi, 1436"),
    ("st-peters-basilica", "St. Peter's Basilica", "St. Peter's Basilica", "Vatican City, 1626"),
    ("flatiron-building", "Flatiron Building", "Flatiron Building", "New York, 1902"),
    ("gateway-arch", "Gateway Arch", "Gateway Arch", "Eero Saarinen, 1965"),
    ("blue-mosque", "Blue Mosque, Istanbul", "Blue Mosque", "Istanbul, 1616"),
    ("potala-palace", "Potala Palace", "Potala Palace", "Lhasa, 1649"),
    ("alhambra", "Alhambra", "Alhambra", "Granada"),
    ("mont-saint-michel", "Mont-Saint-Michel", "Mont-Saint-Michel", "Normandy"),
]


def get(url):
    """GET with a polite delay and a retry on HTTP 429."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        time.sleep(1.5)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 3:
                raise
            time.sleep(10 * (attempt + 1))


def fetch(url, dest):
    data = get(url)          # fetch first so a failure leaves no stale file
    with open(dest, "wb") as f:
        f.write(data)


def image_url(article):
    api = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(article.replace(" ", "_"))
    data = json.loads(get(api))
    thumb = data.get("thumbnail", {}).get("source")
    if not thumb:
        raise RuntimeError("article has no lead image")
    thumb = thumb.split("?")[0]
    return re.sub(r"/\d+px-", f"/{THUMB}px-", thumb)


def preprocess(src, dest):
    """Equalise luminance (keeping colour) so mid-tones survive conversion."""
    img = Image.open(src).convert("RGB")
    # Centre-crop extreme aspect ratios so tall images still get enough
    # columns and panoramas enough rows within WIDTH x HEIGHT.
    w, h = img.size
    if h > w * MAX_TALL:
        top = (h - int(w * MAX_TALL)) // 2
        img = img.crop((0, top, w, top + int(w * MAX_TALL)))
    elif w > h * MAX_WIDE:
        left = (w - int(h * MAX_WIDE)) // 2
        img = img.crop((left, 0, left + int(h * MAX_WIDE), h))
    y, cb, cr = img.convert("YCbCr").split()
    y = ImageOps.equalize(ImageOps.autocontrast(y, cutoff=1))
    img = Image.merge("YCbCr", (y, cb, cr)).convert("RGB")
    img = ImageOps.autocontrast(img, cutoff=1)
    img.save(dest, "PNG")


def commons_url(filename):
    return ("https://commons.wikimedia.org/wiki/Special:FilePath/"
            + urllib.parse.quote(filename) + f"?width={THUMB}")


CELL_RE = re.compile(r"\x1b\[38;2;(\d+);(\d+);(\d+)m(.*?)\x1b\[0m")


def compact(line):
    """Quantise colours and emit an escape only when the colour changes."""
    out, current = [], None
    for r, g, b, text in CELL_RE.findall(line):
        color = tuple(min(255, round(int(v) / QUANT) * QUANT) for v in (r, g, b))
        if color != current:
            out.append("\x1b[38;2;%d;%d;%dm" % color)
            current = color
        out.append(text)
    out.append("\x1b[0m")
    return "".join(out)


def run_converter(image, *size):
    out = subprocess.run(
        ["ascii-image-converter", "-C", "-b", "--dither", *size, image],
        capture_output=True, text=True, check=True,
    ).stdout
    return out.rstrip("\n").split("\n")


def convert(image, rows):
    """Colour braille art `rows` tall (narrower if MAX_WIDTH would be hit)."""
    lines = run_converter(image, "-H", str(rows))
    width = len(re.sub(r"\x1b\[[0-9;]*m", "", lines[0]))
    if width > MAX_WIDTH:
        lines = run_converter(image, "-W", str(MAX_WIDTH))
    return [compact(line) for line in lines]


def main(only):
    os.makedirs(CACHE, exist_ok=True)
    for rows in HEIGHTS:
        os.makedirs(os.path.join(GALLERY, f"h{rows}"), exist_ok=True)
    ok, failed = 0, []
    for slug, article, title, artist, *commons in MANIFEST:
        if only and slug not in only:
            continue
        try:
            image = os.path.join(CACHE, slug + ".img")
            if not os.path.exists(image):
                url = commons_url(commons[0]) if commons else image_url(article)
                fetch(url, image)
            prepped = os.path.join(CACHE, slug + ".png")
            preprocess(image, prepped)
            for rows in HEIGHTS:
                lines = convert(prepped, rows)
                with open(os.path.join(GALLERY, f"h{rows}", slug + ".txt"), "w") as f:
                    f.write(title + "\n" + artist + "\n" + "\n".join(lines) + "\n")
            ok += 1
            print(f"ok    {slug}")
        except Exception as e:  # noqa: BLE001
            failed.append((slug, str(e)))
            print(f"FAIL  {slug}: {e}")
    print(f"\n{ok} written, {len(failed)} failed")
    for slug, err in failed:
        print(f"  {slug}: {err}")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
