"""Hand-written bilingual hazard lexicon (general language knowledge only, no incident records).

Each class has a "strong" tier (words that name the hazard itself) and a "weak" tier (words that
usually go with it). Terms are comma separated; a term of one token is a unigram, two tokens a
bigram, three or more tokens give all their adjacent bigrams. Surface forms are listed by hand
(French inflections, plurals) because the fingerprint hashes exact lowercased tokens.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lib import CLASSES, bucket, tokens  # noqa: E402

LEX = {
    "flood": {
        "strong": """
flood, floods, flooded, flooding, floodwater, floodwaters, flash flood, flash flooding, flood waters,
inundated, inundation, ice jam, ice jams, ice-jam, freshet, spring freshet, high water, high waters,
overflowed, overflowing, burst its banks, over its banks, its banks, dike, dikes, dyke, dykes,
sandbag, sandbags, sandbagging, sandbagged, crest, crested, cresting, floodway, flood plain,
river rose, rising water, rising waters, water levels, under water, underwater, submerged, swollen,
inondation, inondations, inondé, inondée, inondés, inondées, inonde, inondent, inonder,
crue, crues, crue printanière, crue subite, débordement, débordements, déborde, débordé, débordée,
débordent, sort de son lit, de son lit, digue, digues, sacs de sable, embâcle, embâcles, débâcle,
montée des eaux, hautes eaux, niveau de l'eau, sous l'eau, submergé, submergée, submergés,
submergées, eaux, les eaux
""",
        "weak": """
river, rivers, creek, lake, lakeshore, banks, basement, basements, sewer, sewers, sewage backed,
runoff, run-off, snowmelt, spring runoff, rain, rainfall, heavy rain, days of rain, washed out,
breach, breached, levee, pumps, pumping, boats, canoes, rowboats, rowboat, evacuated, flats,
lowlands, low-lying, valley, delta, water, waters, mm of rain,
rivière, rivières, fleuve, ruisseau, lac, berges, rives, sous-sols, sous-sol, égouts, refoulement,
fonte des neiges, fonte, pluie, pluies, pluies abondantes, pluies diluviennes, ponceaux, barques,
chaloupes, canots, pompes, basses terres, vallée, l'eau, rupture de la digue
""",
    },
    "storm": {
        "strong": """
thunderstorm, thunderstorms, thunder, lightning, hail, hailstorm, hailstones, hailstone, tornado,
tornadoes, tornados, twister, funnel cloud, funnel clouds, hurricane, hurricanes, tropical storm,
tropical, post-tropical, windstorm, windstorms, wind storm, gale, gales, gale-force, storm surge,
downburst, downbursts, microburst, squall, squalls, cyclone, derecho, wind gusts, gusts, gusting,
high winds, violent winds, strong winds, rainstorm, cloudburst, golf balls, golf-ball,
orage, orages, orageux, orageuse, orageuses, tempête tropicale, tropicale, post-tropicale,
tornade, tornades, grêle, grêlons, grêlon, ouragan, ouragans, rafales, rafale, foudre, éclairs,
éclair, tonnerre, onde de tempête, marée de tempête, vents violents, forts vents, vents de, cyclone,
trombe, trombes, entonnoir, nuage en entonnoir, balles de golf, des rafales
""",
        "weak": """
storm, storms, wind, winds, km/h, gust, blown, blew, blown down, torn, ripped, uprooted, flattened,
roofs, roof, shingles, toppled, trees, downed, power lines, heavy rain, waves, surge, swath, path,
touched down, cloud, clouds, sky, rainfall,
tempête, tempêtes, vent, toits, toit, toitures, toiture, arrachés, arrachées, arraché, déracinés,
déracinés, renversés, arbres, abattus, lignes électriques, vagues, pluies torrentielles, averses,
touche terre, nuages, ciel
""",
    },
    "winter": {
        "strong": """
snowstorm, snowstorms, snow storm, blizzard, blizzards, snowfall, snowfalls, snow, snowdrifts,
snowdrift, drifts, drifting snow, freezing rain, freezing drizzle, ice storm, ice-storm, sleet,
glaze, frostbite, frostbitten, hypothermia, extreme cold, cold snap, cold wave, bitter cold,
wind chill, windchill, below zero, sub-zero, whiteout, whiteouts, snowbound, snowed in, snowplows,
snowplough, snowploughs, snow plows, ice-coated, ice-covered, coated with ice, of ice, cm of snow,
tempête de neige, tempêtes de neige, de neige, neige, neiges, poudrerie, blizzard, verglas,
pluie verglaçante, verglaçante, bruine verglaçante, grésil, froid extrême, vague de froid,
grand froid, froid intense, froid sibérien, engelures, hypothermie, congères, congère,
chasse-neige, déneigement, sous zéro, refroidissement éolien, chutes de neige, bordée, bordée de neige,
tempête hivernale, de glace, cm de neige, recouverts de glace
""",
        "weak": """
cold, colder, frost, freezing, froze, frozen, freeze, icy, ice, temperatures plunged, degrees below,
below, minus, plows, plow, ploughs, stranded, motorists, drifts, winter, january, february, december,
furnace, furnaces, heating, frozen pipes, warming centres, warming centers, sanding, salt,
froid, gel, gelé, gelée, gelés, gelées, glace, glacé, glacée, glacées, glaciale, glacial, hiver,
hivernale, hivernal, janvier, février, décembre, chauffage, sous la neige, moins, degrés sous zéro,
centres de réchauffement, routes glacées, sablage
""",
    },
    "wildfire": {
        "strong": """
wildfire, wildfires, forest fire, forest fires, bush fire, bush fires, bushfire, bushfires,
grass fire, grass fires, grassfire, grassfires, prairie fire, prairie fires, brush fire, brush fires,
water bombers, waterbombers, water bomber, fire crews, firebreak, firebreaks, fireguard, fireguards,
fire line, fire lines, hectares burned, burned hectares, out of control, timber, forest, forests,
woods, bush, smoke, embers, wind-driven, lightning-caused, forest rangers, fire rangers,
feu de forêt, feux de forêt, incendie de forêt, incendies de forêt, de forêt, forêt, forêts,
feux de brousse, feu de brousse, brousse, feu de broussailles, broussailles, bombardiers d'eau,
bombardier d'eau, bombardiers, pompiers forestiers, sopfeu, coupe-feu, pare-feu, fumée, boisés,
boisé, zone boisée, hectares de forêt, garde-feu, tisons, braises
""",
        "weak": """
fire, fires, blaze, blazes, flames, burned, burnt, burning, hectares, acres, firefighters, crews,
evacuation, evacuated, spread, spreading, trees, dry, lightning, smoke-filled, haze, ash, ashes,
cabins, cottages, sawmill, homesteads, settlers, rangers, jumped, contained, perimeter,
incendie, incendies, feu, feux, flammes, brasier, brûlé, brûlés, brûlée, brûlées, hectares, acres,
pompiers, évacuation, évacués, propage, chalets, cendres, braise, maîtrisé, maîtrise,
hors de contrôle, périmètre
""",
    },
    "drought": {
        "strong": """
drought, droughts, drought-stricken, dry spell, dry spells, dryness, dust storm, dust storms,
dust bowl, heat wave, heat waves, heatwave, heatwaves, heat stroke, heatstroke, heat-related,
heat exhaustion, humidex, crop failure, crop failures, crops failed, parched, scorching, sweltering,
lack of rain, no rain, without rain, water shortage, water shortages, dried up, wells dried,
record heat, extreme heat, grasshoppers, soil drifting, drifting soil,
sécheresse, sécheresses, temps sec, période sèche, canicule, canicules, vague de chaleur,
vagues de chaleur, chaleur extrême, chaleur accablante, coup de chaleur, coups de chaleur, humidex,
manque de pluie, absence de pluie, pénurie d'eau, pénuries d'eau, sans pluie, taries, tari, taris,
asséchés, asséchée, asséché, tempête de poussière, tempêtes de poussière, sauterelles, aride,
aridité, mauvaises récoltes, récoltes perdues, perte des récoltes
""",
        "weak": """
dry, drier, heat, hot, hottest, temperatures, degrees, crops, crop, harvest, harvests, wheat, grain,
yields, yield, pasture, pastures, hay, feed, livestock, cattle, farmers, farms, soil, dust, wells,
dugouts, relief, prairies, prairie, summer, july, august, rainfall, irrigation, reservoirs,
dehydration, elderly, air conditioning, cooling centres, cooling centers,
sec, sèche, sèches, secs, chaleur, chaud, chaude, chaudes, températures, degrés, récolte, récoltes,
cultures, céréales, blé, rendements, pâturages, foin, fourrage, bétail, agriculteurs, fermiers,
sols, poussière, puits, été, juillet, août, irrigation, réservoirs, déshydratation, personnes âgées,
climatisation, centres de rafraîchissement
""",
    },
    "ground": {
        "strong": """
landslide, landslides, land slide, rock slide, rock slides, rockslide, rockslides, mudslide,
mudslides, mud slide, mud slides, debris flow, debris flows, avalanche, avalanches, earthquake,
earthquakes, quake, tremor, tremors, seismic, magnitude, epicentre, epicenter, aftershock,
aftershocks, richter, tsunami, tsunamis, tidal wave, subsidence, sinkhole, sinkholes, rockfall,
rockfalls, slope failure, landslip, leda clay, earth tremor, slide, slides,
glissement, glissements, glissement de terrain, glissements de terrain, de terrain, éboulement,
éboulements, éboulis, coulée de boue, coulées de boue, coulée, coulées, avalanche, avalanches,
séisme, séismes, tremblement de terre, tremblements de terre, tremblement, secousse, secousses,
sismique, sismiques, magnitude, épicentre, répliques, réplique, tsunami, raz-de-marée,
raz de marée, affaissement, affaissements, effondrement du sol, gouffre, argile, glaise, talus
""",
        "weak": """
slid, mud, boulders, rocks, rock, debris, buried, cliff, slope, slopes, hillside, mountainside,
clay, earth, ground, shaking, shook, cracks, cracked, skiers, snowmobilers, backcountry, snowpack,
slab, pass, highway, crevasse, ravine, escarpment, riverbank,
boue, rochers, roches, pierres, débris, ensevelis, ensevelie, enseveli, ensevelies, falaise, pente,
pentes, flanc, colline, montagne, sol, secoué, fissures, lézardes, skieurs, motoneigistes, ravin,
escarpement
""",
    },
    "industrial": {
        "strong": """
explosion, explosions, exploded, blast, blasts, factory, refinery, warehouse, chemical, chemicals,
spill, spilled, spills, spilt, leak, leaked, leaking, leaks, gas leak, toxic, hazardous, ammonia,
chlorine, propane, natural gas, pipeline, oil spill, mine, mines, miners, mining, colliery, coal,
firedamp, methane, cave-in, collapse, collapsed, bridge collapse, dam failure, dam break, power outage,
power outages, blackout, blackouts, substation, transformer, boiler, dynamite, munitions,
explosives, fumes, grain elevator, apartment building, hotel fire, building fire, fire broke out,
gutted, three-alarm, four-alarm, five-alarm, sawmill fire, plant,
explosion, explosions, explose, explosé, déflagration, usine, usines, entrepôt, entrepôts,
raffinerie, déversement, déversements, déversé, fuite, fuites, fuite de gaz, toxique, toxiques,
produits chimiques, chimique, chimiques, ammoniac, chlore, propane, gaz naturel, gaz, pipeline,
oléoduc, gazoduc, réservoir, mine, mines, mineurs, minière, minier, charbon, coup de grisou, grisou,
méthane, effondrement, effondré, effondrée, effondrés, s'effondre, barrage, rupture du barrage,
panne de courant, panne d'électricité, pannes de courant, panne générale, réseau électrique,
immeuble, immeubles, édifice, hôtel, dynamite, munitions, explosifs, émanations, fumées toxiques,
silo, chaudière, ravagé par les flammes, l'incendie
""",
        "weak": """
fire, fires, blaze, flames, building, buildings, store, stores, downtown, block, mill, plant,
workers, worker, shift, shaft, pit, underground, gas, oil, tank, tanks, tanker, pipe, pipes, bridge,
dam, grid, hydro, electricity, outage, firemen, firefighters, fire department, smoke, residents,
hospital, school, church, theatre, rink, arena, tenement, apartments, contaminated,
incendie, incendies, feu, flammes, bâtiment, bâtiments, magasin, magasins, centre-ville, moulin,
travailleurs, ouvriers, ouvrier, puits, galerie, galeries, souterrain, pétrole, citerne, pont,
électricité, pompiers, brigade, hôpital, école, église, théâtre, aréna, logements, contaminé
""",
    },
    "transport": {
        "strong": """
train, trains, railway, railroad, derailment, derailed, derails, locomotive, locomotives,
freight train, passenger train, collision, collided, crash, crashed, crashes, plane, airplane,
aircraft, plane crash, airliner, flight, airport, runway, pilot, pilots, ship, ships, vessel,
vessels, steamer, steamship, ferry, ferries, schooner, tug, tugboat, freighter, sank, sinking,
sunk, foundered, capsized, ran aground, aground, wreck, wrecked, shipwreck, lifeboat, lifeboats,
bus, pile-up, pileup, head-on, level crossing, helicopter, floatplane, float plane, coast guard,
trawler, fishing vessel, fishing boat, on board, aboard, passengers, crew members,
ferroviaire, chemin de fer, voie ferrée, déraillement, déraillé, déraille, locomotive,
locomotives, wagons, wagon, collision, entre en collision, s'écrase, écrasé, écrasement, avion,
avions, aéronef, aéroport, piste, pilote, équipage, passagers, à bord, navire, navires, bateau,
bateaux, traversier, traversiers, goélette, remorqueur, cargo, chalutier, a coulé, coule, sombré,
sombre, naufrage, chavire, chaviré, s'échoue, échoué, épave, canot de sauvetage, autobus,
carambolage, passage à niveau, hélicoptère, hydravion, garde côtière, bateau de pêche, vapeur
""",
        "weak": """
rail, track, tracks, cars, coaches, engineer, conductor, crossing, highway, road, car, truck,
trucks, vehicle, vehicles, driver, drivers, motorist, collision, harbour, harbor, port, gulf, strait,
sea, waters, sailors, seamen, fishermen, cargo, hull, mayday, rescue, survivors, bodies, drowned,
search, wreckage, take-off, takeoff, landing, flights,
rail, voie, voies, voitures, mécanicien, conducteur, route, routière, autoroute, camion, camions,
véhicule, véhicules, automobile, voiture, port, golfe, détroit, mer, marins, pêcheurs, coque,
sauvetage, survivants, corps, noyés, noyé, recherches, débris, décollage, atterrissage, vol
""",
    },
    "epidemic": {
        "strong": """
epidemic, epidemics, outbreak, outbreaks, pandemic, pandemics, disease, diseases, influenza, flu,
spanish flu, smallpox, typhoid, cholera, diphtheria, polio, poliomyelitis, measles, tuberculosis,
scarlet fever, meningitis, coli, listeria, listeriosis, salmonella, legionnaires, legionella, sars,
covid, coronavirus, virus, viral, infected, infection, infections, contagious, contagion, quarantine,
quarantined, vaccine, vaccines, vaccination, vaccinated, immunization, public health,
medical officer, health officials, gastroenteritis, plague, whooping cough, mumps, hepatitis,
west nile, pertussis, sanatorium, confirmed cases, of cases, cases,
épidémie, épidémies, éclosion, éclosions, pandémie, maladie, maladies, grippe, grippe espagnole,
variole, typhoïde, fièvre typhoïde, choléra, diphtérie, polio, poliomyélite, rougeole, tuberculose,
scarlatine, méningite, listériose, salmonellose, salmonelle, légionellose, légionnaires, sras,
infectés, infectées, infecté, infectée, infection, infections, contagieuse, contagieux, quarantaine,
cas, cas confirmés, vaccin, vaccins, vaccination, vaccinés, santé publique, médecin hygiéniste,
gastroentérite, peste, coqueluche, oreillons, hépatite, virus du nil, sanatorium, de cas
""",
        "weak": """
patients, sick, illness, ill, fever, symptoms, hospitalized, hospitalised, isolation, mortality,
deaths, doctors, nurses, physicians, health, medical, schools closed, closed schools, children,
mosquitoes, contaminated, water supply, drinking water, boil-water, boil water, masks, wave,
patients, malades, malade, fièvre, symptômes, hospitalisés, hospitalisées, isolement, mortalité,
décès, médecins, infirmières, santé, médical, médicale, écoles fermées, enfants, moustiques,
contaminée, eau potable, faire bouillir, masques, vague
""",
    },
}

TIER_W = {"strong": 2.0, "weak": 1.0}


def term_list(cls, tier):
    out = []
    for raw in LEX[cls][tier].replace("\n", " ").split(","):
        t = raw.strip()
        if t:
            out.append(t)
    return out


# bigrams of a phrase made only of these words carry no hazard meaning ("de la", "out of")
GENERIC = set("""of the a an in on at to with its by for and from de la le les des du en à au aux par
sous sur et son sa ses l'eau out hors centres centre coup coups days mm cm broke vague vagues niveau
chutes entre passage rupture""".split())


def term_buckets(term):
    """Fingerprint features a lexicon term maps to: its unigram, or the bigrams of a phrase."""
    toks = tokens(term)
    if len(toks) == 1:
        return [toks[0]]
    return [a + " " + b for a, b in zip(toks, toks[1:]) if not (a in GENERIC and b in GENERIC)]


def lexicon_features():
    """{feature string -> {class index -> weight}} (max weight per class over all its terms)."""
    feats = {}
    for ci, c in enumerate(CLASSES):
        for tier, w in TIER_W.items():
            for t in term_list(c, tier):
                for f in term_buckets(t):
                    d = feats.setdefault(f, {})
                    d[ci] = max(d.get(ci, 0.0), w)
    return feats


if __name__ == "__main__":
    feats = lexicon_features()
    bks = {bucket(f) for f in feats}
    print(f"{len(feats)} features, {len(bks)} buckets")
    for c in CLASSES:
        n = sum(len(term_list(c, t)) for t in TIER_W)
        print(c, n)
