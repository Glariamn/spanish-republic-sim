# src\content\game_data.py

# --- 1. CONSTANTS (IDs) ---
# Big Four Parties (Playable)
PARTY_PSOE = "psoe"          # Partido Socialista Obrero Español
PARTY_AR   = "accion_rep"    # Accción Republicana
PARTY_PRR  = "radicals"      # Partido Republicano Radical (Lerroux)
PARTY_DLR  = "right_rep"     # Derechos Laborales (Derechos Humanos)
PARTY_PRRS = "rad_socialists"# Partido Rep. Radical Socialista (Linksliberale)

# Named Parties
PARTY_CEDA = "ceda"          # Confederación de Derechos Autónomas (Gil-Robles) - Sammelbecken ab 1933
PARTY_PCE  = "communist"     # Partido Comunista Español
PARTY_CNT  = "anarchist"     # Confederación Nacional de Trabajadores - Non-voters
PARTY_FAL  = "falange"       # Falange (Fascist)
PARTY_ERC  = "esquerra"      # Esquerra Republicana de Catalunya
PARTY_LLIGA= "lliga"         # Lliga Regionalista
PARTY_PNV  = "pnv"           # Partido Nacionalista Vasco
PARTY_MON  = "monarchists"   # Renovación Española (Alfonsinos/Carlisten)
PARTY_PA   = "agrarian"      # Partido Agrario Español (Generisch, für Koalitionen)

# Others (Minor Parties)
PARTY_MARXIST_OTHER = "marxist_other"
PARTY_LEFT_REP_OTHER = "left_republican_other"
PARTY_CENTRE_REP_OTHER = "centre_republican_other"
PARTY_RIGHT_REP_OTHER = "right_republican_other"
PARTY_CATHOLIC_OTHER = "catholic_other"
PARTY_FAR_RIGHT_OTHER = "far_right_other"
PARTY_REGIONALIST_OTHER = "regionalist_other"

# Organisationen
UGT = "ugt"                  # Gewerkschaft der Sozialisten
CNT = "cnt"                  # Anarcho-Syndikalistische Gewerkschaft
FAI = "fai"                  # Anarchistische Fraktion innerhalb der CNT
ACC_CAT = "acc_cat"          # CEDA organization
SIN_CAT = "sin_cat"          # Catholic labour clubs
JS_PSOE = "js_psoe"          # Socialist youth
JUV_LIB = "juv_lib"          # Anarchist youth
ATENEOS = "ateneos"          # Intelligentia clubs

# --- 2. THE MINISTRIES (Power Centers) ---
# Historical Cabinet of the Provisional Government (April 1931)
MINISTRIES = {
    "president_republic": {
        "name": "Presidente de la República",
        "holder": "Niceto Alcalá-Zamora",
        "party": PARTY_DLR,
        "desc": "Head of State. Elected by parliament. Not a cabinet position — cannot be claimed in the draft."
    },
    "prime_minister": {
        "name": "Presidente del Gobierno",
        "holder": "Niceto Alcalá-Zamora",
        "party": PARTY_DLR,
        "desc": "Head of Government. Confirmed by investiture vote."
    },
    "war": {
        "name": "Ministerio de la Guerra",
        "holder": "Manuel Azaña",
        "party": PARTY_AR,
        "desc": "Controls the Army. Key for keeping the generals in check."
    },
    "labor": {
        "name": "Ministerio de Trabajo",
        "holder": "Largo Caballero",
        "party": PARTY_PSOE,
        "desc": "Controls labor laws. Can authorize or crush strikes."
    },
    "interior": {
        "name": "Gobernación (Interior)",
        "holder": "Miguel Maura",
        "party": PARTY_DLR,
        "desc": "Controls the Guardia Civil. Responsible for public order and repression."
    },
    "finance": {
        "name": "Hacienda (Finance)",
        "holder": "Indalecio Prieto",
        "party": PARTY_PSOE,
        "desc": "Manages the Budget and the Peseta value."
    },
    "state": {
        "name": "Estado (Foreign Affairs)",
        "holder": "Alejandro Lerroux",
        "party": PARTY_PRR,
        "desc": "Diplomatic relations and international loans."
    },
    "justice": {
        "name": "Gracia y Justicia",
        "holder": "Fernando de los Ríos",
        "party": PARTY_PSOE,
        "desc": "Responsible for church-state separation and legal reforms."
    }
}

# --- 3. PARTIES & STATS ---
PARTIES = {
    # --- DIE SPIELBAREN / REGIERUNGSPARTEIEN ---
    
    PARTY_PSOE: {
        "name": "PSOE",
        "full_name": "Partido Socialista Obrero Español",
        "color": "#E30613",      # Rot
        "ideology_index": 1,     # Für Sortierung (Links)
        "funds_int": 8,          
        "members": 300000,
        "institutionalization": 48, # Abstrahierung weil sonst zu dominant
        "factions": {
            "psoe_reformist": {
                "name": "Besteiristas", 
                "strength": 20, 
                "dissent": 45,       
                "tag": "moderate"
            },
            "psoe_centrist": {
                "name": "Prietistas",    
                "strength": 40, 
                "dissent": 10,        
                "tag": "center"
            },
            "psoe_revolutionary": {
                "name": "Caballeristas",  
                "strength": 40, 
                "dissent": 15,       
                "tag": "left"
            }
        },
        "relations": {
            PARTY_AR: 75,
            PARTY_PRR: 40,
            PARTY_DLR: 25,
            PARTY_PRRS: 70,
            PARTY_ERC: 65,
            PARTY_LLIGA: 25,
            PARTY_PNV: 35,
            PARTY_CNT: 10,
            PARTY_PCE: 10,
            PARTY_CEDA: 5,
            PARTY_FAL: 0,
            "church": 5,
            "army": 10
        },
        "preferred_portfolios": [ "labor", "finance", "justice" ]
    },
    
    PARTY_AR: {
        "name": "Acción Rep.",
        "full_name": "Acción Republicana",
        "color": "#800080",      # Lila
        "ideology_index": 3,     # Mitte-Links
        "funds_int": 3,
        "members": 5000,
        "institutionalization": 85,
        "factions": {
            "ar_intellectuals": {
                "name": "Ateneístas", 
                "strength": 80, 
                "dissent": 10,        
                "tag": "center"
            },
            "ar_jacobins": {
                "name": "Jacobinos", 
                "strength": 20, 
                "dissent": 30, 
                "tag": "left"
            }
        },
        "relations": {
            PARTY_PSOE: 80,
            PARTY_DLR: 45,
            PARTY_PRR: 40,
            PARTY_PRRS: 85,
            PARTY_ERC: 70,
            PARTY_LLIGA: 25,
            PARTY_PNV: 35,
            PARTY_CNT: 10,
            PARTY_PCE: 10,
            PARTY_CEDA: 5,
            PARTY_FAL: 0,
            "church": 10,
            "army": 30
        },
        "preferred_portfolios": [ "war", "president", "state"]
    },
    
    PARTY_DLR: {
        "name": "DLR",
        "full_name": "Derecha Liberal Republicana",
        "color": "#004488",      # Blau
        "ideology_index": 7,     # Mitte-Rechts
        "funds_int": 6,          
        "members": 15000,
        "institutionalization": 45,
        "factions": {
            "dlr_catholics": {
                "name": "Católicos Moderados", 
                "strength": 30, 
                "dissent": 20,        
                "tag": "catholic"
            },
            "dlr_liberals": {
                "name": "Liberal-Republicanos", 
                "strength": 70, 
                "dissent": 10, 
                "tag": "center"
            }
        },
        "relations": {
            PARTY_PSOE: 25,
            "church": 60,
            "army": 60
        },
        "preferred_portfolios": [ "president", "interior" ]
    },
    
    PARTY_PRR: { 
        "name": "Radicals (PRR)",
        "full_name": "Partido Republicano Radical",
        "color": "#1C1845",      # Dark Purple
        "ideology_index": 5,     # Centre-Right
        "funds_int": 7,
        "members": 100000,
        "institutionalization": 58,
        "factions": {
            "prr_lerrouxistas": {
                "name": "Lerrouxistas",
                "strength": 55,
                "dissent": 15,
                "tag": ["anticlerical", "center"]
            },
            "prr_jovenes": {
                "name": "Jóvenes Radicales",
                "strength": 25,
                "dissent": 20,
                "tag": ["center", "anticlerical", "populist"]
            },
            "prr_opportunists": {
                "name": "Oportunistas",
                "strength": 20,
                "dissent": 5,
                "tag": ["clientelist", "moderate"]
            }
        },
        "relations": {
            PARTY_PSOE: 30,
            PARTY_AR: 50,
            PARTY_DLR: 50,
            "church": 40,
            "army": 50
        },
        "preferred_portfolios": [ "state", "interior", "finance" ]
    },

    PARTY_PRRS: {
        "name": "Rad. Soc.",
        "full_name": "Partido Rep. Radical Socialista",
        "color": "#A020F0",      # Lila
        "ideology_index": 2,     # Links-Liberal
        "funds_int": 3,
        "members": 40000,
        "institutionalization": 60,
        "factions": {
            "prrs_radicals": {
                "name": "Izquierdistas",
                "strength": 40,
                "dissent": 25,
                "tag": ["left", "anticlerical"]
            },
            "prrs_moderates": {
                "name": "Reformistas",
                "strength": 35,
                "dissent": 10,
                "tag": ["center"]
            },
            "prrs_federalists": {
                "name": "Federalistas",
                "strength": 25,
                "dissent": 15,
                "tag": ["center", "regionalist"]
            }
        },
        "relations": {PARTY_AR: 80, PARTY_PSOE: 60},
        "preferred_portfolios": [ "agriculture", "state" ]
    },

    # --- DIE OPPOSITION / ANDERE PARTEIEN (Wichtig für Wahlergebnisse) ---
    
    PARTY_PCE: {
        "name": "PCE",
        "full_name": "Partido Comunista de España",
        "color": "#8B0000",      # Dunkelrot
        "ideology_index": 0,     # Linksaußen
        "funds_int": 1,
        "members": 800,
        "institutionalization": 10,
        "factions": {
            "pce_stalinists": {
                "name": "Stalinistas",
                "strength": 80,
                "dissent": 5,
                "tag": ["left", "anticlerical", "radical"]
            },
            "pce_left_opposition": {
                "name": "Oposición de Izquierda",
                "strength": 20,
                "dissent": 40,
                "tag": ["left", "anticlerical", "radical"]
            }
        },
        "relations": {PARTY_PSOE: 10}, # Kritisch gegenüber Sozialdemokraten
        "preferred_portfolios": [ "war ", "interior" ]
    },
    
    PARTY_ERC: {
        "name": "Esquerra",
        "full_name": "Esquerra Republicana de Catalunya",
        "color": "#FFD700",      # Gelb/Gold
        "ideology_index": 2.5,   # Links-Regional
        "funds_int": 5,
        "members": 15000, # Sehr stark in Katalonien
        "institutionalization": 65,
        "factions": {
            "erc_macia": {
                "name": "Macià faction",
                "strength": 45,
                "dissent": 20,
                "tag": ["nationalist", "left", "anticlerical"]
            },
            "erc_companys": {
                "name": "Companys faction",
                "strength": 40,
                "dissent": 10,
                "tag": ["center", "regionalist", "anticlerical"]
            },
            "erc_separatists": { 
                "name": "Estat Català", 
                "strength": 15, 
                "dissent": 30, 
                "tag": ["nationalist", "radical"] 
            }
        },
        "relations": {PARTY_AR: 60, "army": 5}
    },
    
    PARTY_PNV: {
        "name": "PNV",
        "full_name": "Partido Nacionalista Vasco",
        "color": "#008000",      # Grün
        "ideology_index": 7.0,     # Christdemokratisch-Regional
        "funds_int": 4,
        "members": 30000,
        "institutionalization": 65,
        "factions": {
            "pnv_traditionalists": {
                "name": "Aberrianos",
                "strength": 50,
                "dissent": 10,
                "tag": ["right", "clerical", "nationalist"]
            },
            "pnv_youth": {
                "name": "Jagi-Jagi",
                "strength": 30,
                "dissent": 30,
                "tag": ["nationalist", "radical"]
            },
            "pnv_moderates": {
                "name": "Bizkaitarras",
                "strength": 20,
                "dissent": 5,
                "tag": ["center", "regionalist"]
            }
        },
        "relations": {
            "church": 90,
            PARTY_PSOE: 15,
            PARTY_AR: 20
        }
    },
    
    PARTY_LLIGA: {
        "name": "Lliga",
        "full_name": "Lliga Regionalista",
        "color": "#B8860B",      # Dark Goldenrod
        "ideology_index": 7.5,   # Konservativ-Katalanisch
        "funds_int": 10,         # Sehr reich (Industrielle)
        "members": 20000,
        "institutionalization": 45,
        "factions": {
            "lliga_industrialists": {
                "name": "Cambonistas",
                "strength": 70,
                "dissent": 5,
                "tag": ["right", "urban_elite", "regionalist"]
            },
            "lliga_conservatives": {
                "name": "Regionalistas Tradicionales",
                "strength": 30,
                "dissent": 15,
                "tag": ["right", "clerical", "regionalist"]
            },
        },
        "relations": {
            PARTY_DLR: 60,
            "church": 80,
            PARTY_ERC: 10
        }
    },

    PARTY_PA: {
        "name": "PA",
        "full_name": "Partido Agrario Español",
        "color": "#485120",      # Grün-Braun
        "ideology_index": 8.5,     # Rechts-Konservativ
        "funds_int": 5,         
        "members": 50000,      
        "institutionalization": 40,  
        "factions": {
            "pa_landowners": {
                "name": "Terratenientes",
                "strength": 70,
                "dissent": 5,
                "tag": ["reactionary", "rural_elite"]
            },
            "pa_agrarians": {
                "name": "Católicos Rurales",
                "strength": 30,
                "dissent": 15,
                "tag": ["right", "clerical"]
            },
        },
        "relations": {"church": 80, "army": 80, PARTY_PSOE: 0}
    },

    PARTY_CEDA: {
        "name": "CEDA",
        "full_name": "Accíon Nacional / Confederación Española de Derechas Autónomas",
        "color": "#000000",      # Schwarz
        "ideology_index": 8,     # Rechts-Konservativ
        "funds_int": 2,         
        "members": 20000,        
        "institutionalization": 25,
        "factions": {
            "ceda_legalists": {
                "name": "Acción Católica",
                "strength": 70,
                "dissent": 5,
                "tag": ["right", "clerical", "urban_elite"]
            },
            "ceda_extremists": {
                "name": "Juventudes de Acción",
                "strength": 20,
                "dissent": 15,
                "tag": ["right", "radical", "clerical"]
            },
            "ceda_corporatists": {
                "name": "Corporatistas",
                "strength": 10,
                "dissent": 30,
                "tag": ["right", "corporatist", "clerical"]
            }
        },
        "relations": {"church": 100, "army": 70, PARTY_PSOE: 0}
    },
    
    PARTY_MON: {
        "name": "Monarchists",
        "full_name": "Renovación Española / Comunión Tradicionalista",
        "color": "#4B0082",      # Indigo/Royal Purple
        "ideology_index": 9.5,     # Reaktionär
        "funds_int": 20,         
        "members": 5000,
        "institutionalization": 15,
        "factions": {
            "mon_alfonsinos": {
                "name": "Acción Española",
                "strength": 40,
                "dissent": 20,
                "tag": ["monarchist", "reactionary"]
            },
            "mon_carlistas": {
                "name": "Comunión Tradicionalista",
                "strength": 60,
                "dissent": 10,
                "tag": ["right", "traditionalist", "clerical"]
            },
        },
        "relations": {"army": 90, "church": 90}
    },
    
    PARTY_FAL: {
        "name": "Falange",
        "full_name": "Juntas de Ofensiva Nacional-Sindicalista / Falange Española",
        "color": "#202020",      # Fast Schwarz / Dunkelblau
        "ideology_index": 10,    # Faschistisch
        "funds_int": 0,          
        "members": 50,   
        "institutionalization": 5,       
        "factions": {
            "fal_jons": {
                "name": "Juntas de Ofensiva Nacional-Sindicalista (Ledesma Ramos)",
                "strength": 70,
                "dissent": 20,
                "tag": ["fascist", "anticlerical", "syndicalist"]
            },
            "fal_joseantonianos": {
                "name": "Falangistas",
                "strength": 30,
                "dissent": 10,
                "tag": ["fascist", "urban_elite", "catholic"]
            },
        },
        "relations": {"army": 50}
    },

    PARTY_CNT: {
        "name": "CNT/FAI",
        "full_name": "Confederación Nacional del Trabajo",
        "color": "#000000",      # Schwarz
        "ideology_index": -1,      # Ultra links
        "funds_int": 2,
        "members": 500000,
        "institutionalization": 0,
        "factions": {
            "cnt_reformist": {
                "name": "Treintistas (Sindicalistas)", 
                "strength": 60, 
                "dissent": 10,       
                "tag": ["left", "moderate", "syndicalist"]
            },
            "cnt_anarchist": {
                "name": "Federación Anarquista Ibérica",    
                "strength": 40, 
                "dissent": 50,        
                "tag": "anarchist" # Hate everyone
            }
        },
        "relations": {}
    },

    PARTY_MARXIST_OTHER: {
        "name": "Marxist Left",
        "full_name": "Marxist and Left-Socialist Independents",
        "color": "#AA0000",
        "ideology_index": 1,
        "funds_int": 3,
        "members": 15000,
        "institutionalization": 5,
        "factions": {},
        "relations": {}
    },

    PARTY_LEFT_REP_OTHER: {
        "name": "Left Republican Bloc",
        "full_name": "Independent Left Republicans",
        "color": "#CC4444",
        "ideology_index": 3,
        "funds_int": 5,
        "members": 20000,
        "institutionalization": 60,
        "factions": {},
        "relations": {}
    },

    PARTY_CENTRE_REP_OTHER: {
        "name": "Republican Centre",
        "full_name": "Independent Moderate Republicans",
        "color": "#DD8844",
        "ideology_index": 5,
        "funds_int": 8,
        "members": 15000,
        "institutionalization": 40,
        "factions": {},
        "relations": {}
    },

    PARTY_RIGHT_REP_OTHER: {
        "name": "Conservative Republicans",
        "full_name": "Independent Conservative Republicans",
        "color": "#8888AA",
        "ideology_index": 7,
        "funds_int": 10,
        "members": 12000,
        "institutionalization": 50,
        "factions": {},
        "relations": {}
    },

    PARTY_CATHOLIC_OTHER: {
        "name": "Catholic Independents",
        "full_name": "Catholic and Local Conservative Independents",
        "color": "#AA8844",
        "ideology_index": 8,
        "funds_int": 6,
        "members": 18000,
        "institutionalization": 35,
        "factions": {},
        "relations": {}
    },

    PARTY_FAR_RIGHT_OTHER: {
        "name": "Far-Right Independents",
        "full_name": "Local Far-Right and Monarchist Independents",
        "color": "#444466",
        "ideology_index": 9,
        "funds_int": 4,
        "members": 8000,
        "institutionalization": 10,
        "factions": {},
        "relations": {}
    },

    PARTY_REGIONALIST_OTHER: {
        "name": "Regionalist Independents",
        "full_name": "Independent Regionalist and Localist Groups",
        "color": "#66AA88",
        "ideology_index": 4,
        "funds_int": 7,
        "members": 25000,
        "institutionalization": 75,
        "factions": {},
        "relations": {}
    },
    
    # Fallback
    "others": {
        "name": "Others", 
        "full_name": "Independientes", 
        "color": "#888888", 
        "ideology_index": 4.5,
        "funds_int": 0,
        "members": 0,
        "institutionalization": 0,
        "factions": {},
        "relations": {}
    }
}

# --- 6. CONSTITUENCIES 1931 (Circunscripciones) ---

CONSTITUENCIES_1931 = [
    # Galicia
    {"id":"la_coruna","name":"La Coruña","seats":16,"region":"galicia_rural"},
    {"id":"orense","name":"Orense","seats":7,"region":"galicia_rural"},
    {"id":"pontevedra","name":"Pontevedra","seats":12,"region":"galicia_rural"},
    {"id":"lugo","name":"Lugo","seats":10,"region":"galicia_rural"},

    # Asturias / Cantabria -> eher altkastilisch + Küste
    {"id":"oviedo","name":"Oviedo","seats":16,"region":"asturias_mining"},
    {"id":"santander","name":"Santander","seats":7,"region":"castilla_old_core"},

    # Castilla y León
    {"id":"leon","name":"León","seats":9,"region":"castilla_old_core"},
    {"id":"zamora","name":"Zamora","seats":6,"region":"castilla_old_core"},
    {"id":"salamanca","name":"Salamanca","seats":7,"region":"castilla_old_core"},
    {"id":"avila","name":"Ávila","seats":4,"region":"castilla_old_core"},
    {"id":"segovia","name":"Segovia","seats":4,"region":"castilla_old_core"},
    {"id":"soria","name":"Soria","seats":3,"region":"castilla_old_core"},
    {"id":"valladolid","name":"Valladolid","seats":6,"region":"castilla_old_core"},
    {"id":"palencia","name":"Palencia","seats":4,"region":"castilla_old_core"},
    {"id":"burgos","name":"Burgos","seats":8,"region":"castilla_old_core"},

    # País Vasco + Navarra
    {"id":"vizcaya_cap","name":"Bilbao (Vizcaya cap.)","seats":6,"region":"pais_vasco_industrial"},
    {"id":"vizcaya_prov","name":"Vizcaya provincia","seats":3,"region":"pais_vasco_rural"},
    {"id":"guipuzcoa","name":"Guipúzcoa","seats":6,"region":"pais_vasco_industrial"},
    {"id":"alava","name":"Álava","seats":2,"region":"pais_vasco_rural"},
    {"id":"navarra","name":"Navarra","seats":7,"region":"pais_vasco_rural"},

    # Aragón
    {"id":"zaragoza_cap","name":"Zaragoza (capital)","seats":4,"region":"aragon_mixed"},
    {"id":"zaragoza_prov","name":"Zaragoza provincia","seats":7,"region":"aragon_mixed"},
    {"id":"huesca","name":"Huesca","seats":5,"region":"aragon_mixed"},
    {"id":"teruel","name":"Teruel","seats":4,"region":"aragon_mixed"},

    # Catalunya
    {"id":"lleida","name":"Lleida","seats":6,"region":"catalonia_rural"},
    {"id":"girona","name":"Girona","seats":6,"region":"catalonia_rural"},
    {"id":"barcelona_cap","name":"Barcelona (capital)","seats":18,"region":"catalonia_urban"},
    {"id":"barcelona_prov","name":"Barcelona provincia","seats":15,"region":"catalonia_rural"},
    {"id":"tarragona","name":"Tarragona","seats":7,"region":"catalonia_rural"},

    # Baleares
    {"id":"baleares","name":"Baleares","seats":7,"region":"canarias_mixed"},

    # Valencia
    {"id":"castellon","name":"Castellón","seats":6,"region":"valencia_mixed"},
    {"id":"valencia_cap","name":"Valencia (capital)","seats":7,"region":"valencia_mixed"},
    {"id":"valencia_prov","name":"Valencia provincia","seats":13,"region":"valencia_mixed"},
    {"id":"alicante","name":"Alicante","seats":11,"region":"valencia_mixed"},

    # Murcia
    {"id":"murcia_cap","name":"Murcia (capital)","seats":4,"region":"valencia_mixed"},
    {"id":"cartagena","name":"Cartagena","seats":2,"region":"valencia_mixed"},

    # Castilla-La Mancha
    {"id":"albacete","name":"Albacete","seats":7,"region":"castilla_old_core"},
    {"id":"ciudad_real","name":"Ciudad Real","seats":11,"region":"castilla_old_core"},
    {"id":"toledo","name":"Toledo","seats":8,"region":"castilla_old_core"},
    {"id":"cuenca","name":"Cuenca","seats":4,"region":"castilla_old_core"},
    {"id":"guadalajara","name":"Guadalajara","seats":4,"region":"castilla_old_core"},

    # Madrid
    {"id":"madrid_cap","name":"Madrid (capital)","seats":18,"region":"madrid_urban"},
    {"id":"madrid_prov","name":"Madrid provincia","seats":9,"region":"castilla_old_core"},

    # Extremadura
    {"id":"badajoz","name":"Badajoz","seats":14,"region":"extremadura_latifundio"},
    {"id":"caceres","name":"Cáceres","seats":7,"region":"extremadura_latifundio"},

    # Andalucía
    {"id":"sevilla_cap","name":"Sevilla (capital)","seats":4,"region":"andalucia_urban"},
    {"id":"sevilla_prov","name":"Sevilla provincia","seats":8,"region":"andalucia_latifundio"},
    {"id":"cordoba","name":"Córdoba","seats":8,"region":"andalucia_latifundio"},
    {"id":"jaen","name":"Jaén","seats":9,"region":"andalucia_latifundio"},
    {"id":"granada_cap","name":"Granada (capital)","seats":2,"region":"andalucia_urban"},
    {"id":"granada_prov","name":"Granada provincia","seats":7,"region":"andalucia_latifundio"},
    {"id":"malaga_cap","name":"Málaga (capital)","seats":3,"region":"andalucia_urban"},
    {"id":"malaga_prov","name":"Málaga provincia","seats":6,"region":"andalucia_latifundio"},
    {"id":"cadiz","name":"Cádiz","seats":8,"region":"andalucia_urban"},
    {"id":"huelva","name":"Huelva","seats":5,"region":"andalucia_latifundio"},
    {"id":"almeria","name":"Almería","seats":5,"region":"andalucia_latifundio"},

    # Canarias
    {"id":"melilla","name":"Melilla","seats":1,"region":"canarias_mixed"},
    {"id":"ceuta","name":"Ceuta","seats":1,"region":"canarias_mixed"},
    {"id":"las_palmas","name":"Las Palmas","seats":4,"region":"canarias_mixed"},
    {"id":"santa_cruz","name":"Santa Cruz de Tenerife","seats":4,"region":"canarias_mixed"},

    # La Rioja
    {"id":"la_rioja","name":"La Rioja (Logroño)","seats":3,"region":"la_rioja_smallholder"}
]

REGION_MODIFIERS = {
    "catalonia_urban": {
        "workers_urban": 1.30,
        "bourgeoisie": 1.20
    },
    "catalonia_rural": {
        "workers_rural": 1.10,
        "clergy": 1.05
    },
    "madrid_urban": {
        "workers_urban": 1.30,
        "bourgeoisie": 1.10
    },
    "castilla_old_core": {
        "clergy": 1.10,
        "bourgeoisie": 1.05
    },
    "andalucia_latifundio": {
        "workers_rural": 1.35,
        "aristocracy": 1.15
    },
    "andalucia_urban": {
        "workers_rural": 1.20,
        "workers_urban": 1.10
    },
    "galicia_rural": {
        "clergy": 1.15,
        "workers_rural": 1.10
    },
    "pais_vasco_industrial": {
        "bourgeoisie": 1.15,
        "workers_urban": 1.10,
        "clergy": 1.10
    },
    "pais_vasco_rural": {
        "clergy": 1.20,
        "workers_rural": 1.05
    },
    "extremadura_latifundio": {
        "workers_rural": 1.30,
        "aristocracy": 1.10
    },
    "valencia_mixed": {
        "workers_urban": 1.15,
        "workers_rural": 1.10
    },
    "canarias_mixed": {
        "bourgeoisie": 1.10,
        "workers_rural": 1.05
    },
    "la_rioja_smallholder": {
        "workers_rural": 1.10,
        "bourgeoisie": 1.05
    },
    "asturias_mining": {
        "workers_urban": 1.40, # Bergarbeiter
        "bourgeoisie": 0.80    # Schwaches Bürgertum
    },
    "aragon_mixed": {
        "workers_rural": 1.10,
        "bourgeoisie": 1.10
    }
}

REGIONAL_DEMOGRAPHICS = {

    # --- GALICIA (katholisch, konservativ, ländlich) ---
    "galicia_rural": {
        "aristocracy": {
            PARTY_MON: 0.30, PARTY_DLR: 0.25, PARTY_CEDA: 0.15, PARTY_PRR: 0.15,
            "catholic_other": 0.05, "regionalist_other": 0.20
        },
        "clergy": {
            PARTY_DLR: 0.35, PARTY_CEDA: 0.25, PARTY_MON: 0.20, PARTY_PNV: 0.05,
            "catholic_other": 0.15
        },
        "bourgeoisie": {
            "regionalist_other": 0.60,
            PARTY_DLR: 0.20,
            PARTY_AR: 0.10,
            PARTY_PRR: 0.10
        },
        "workers_urban": {
            PARTY_PSOE: 0.25, PARTY_PRR: 0.20, PARTY_PRRS: 0.10, PARTY_PCE: 0.05, PARTY_AR: 0.10,
            "left_republican_other": 0.15, "regionalist_other": 0.30
        },
        "workers_rural": {
            "regionalist_other": 0.50,
            PARTY_PRRS: 0.05, PARTY_PSOE: 0.15, PARTY_MON: 0.10, PARTY_CNT: 0.10,
            "catholic_other": 0.05
        },
        "soldiers": {
            "regionalist_other": 0.35, PARTY_PRR: 0.30, PARTY_PSOE: 0.20,PARTY_AR: 0.15
        }
    },

    # In REGIONAL_DEMOGRAPHICS["castilla_old_core"] in src/content/game_data.py

    "castilla_old_core": {
        "aristocracy": {
            PARTY_PA: 0.45, 
            PARTY_DLR: 0.25, 
            PARTY_MON: 0.20, 
            PARTY_CEDA: 0.10
        },
        "clergy": {
            PARTY_DLR: 0.45,
            PARTY_CEDA: 0.25, 
            PARTY_PA: 0.20, 
            PARTY_MON: 0.10
        },
        "bourgeoisie": {
            PARTY_PRR: 0.30, PARTY_DLR: 0.20, PARTY_AR: 0.15, PARTY_PA: 0.20,
            PARTY_PSOE: 0.10, PARTY_CEDA: 0.05, "centre_republican_other": 0.10
        },
        "workers_urban": {
            PARTY_PSOE: 0.45,
            PARTY_PRR: 0.15,
            PARTY_PRRS: 0.35,
            PARTY_PCE: 0.05,
            PARTY_AR: 0.10,
            "left_republican_other": 0.15
        },
        "workers_rural": {
            PARTY_PA: 0.35, PARTY_CEDA: 0.20, PARTY_DLR: 0.05, PARTY_MON: 0.05, PARTY_PSOE: 0.15, PARTY_PRRS: 0.10,
            "catholic_other": 0.10
        },
        "soldiers": {
            PARTY_PRR: 0.35,
            PARTY_PSOE: 0.25,
            PARTY_PA: 0.20,
            PARTY_AR: 0.15,
            PARTY_PCE: 0.05,
            "catholic_other": 0.10
        }
    },

    # --- ASTURIAS (Die Rote Hochburg / Minenarbeiter) ---
    # Massive Dominanz der Linkskoalition. PCE ungewöhnlich stark.
    # Charakteristik: Hochburg der UGT (PSOE) und signifikante kommunistische Präsenz.
    "asturias_mining": {
        "aristocracy": {
            # Die wenigen Reichen wählen Agrarier oder Monarchisten als Schutz
            PARTY_PA: 0.35, 
            PARTY_DLR: 0.25, 
            PARTY_MON: 0.25, 
            PARTY_CEDA: 0.10,
            "right_republican_other": 0.05
        },
        "clergy": {
            PARTY_CEDA: 0.40, 
            PARTY_PA: 0.25, 
            PARTY_DLR: 0.25, 
            PARTY_MON: 0.10
        },
        "bourgeoisie": {
            # Starker Rückhalt für linke Republikaner (Teodomiro Menéndez etc.)
            PARTY_PRRS: 0.30,       # Radical Socialists stark
            PARTY_AR: 0.25,         # Azaña
            PARTY_PRR: 0.20,        # Lerroux
            PARTY_DLR: 0.15,
            PARTY_PSOE: 0.10        # Sympathisanten
        },
        "workers_urban": {
            PARTY_PSOE: 0.60,       # UGT Dominanz
            PARTY_PCE: 0.15,        # 12k Stimmen -> ~15% des linken Lagers hier
            PARTY_PRRS: 0.10, 
            PARTY_PRR: 0.10,
            "marxist_other": 0.05
        },
        "workers_rural": {
            # Auch auf dem Land (Minendörfer) sehr links
            PARTY_PSOE: 0.50, 
            PARTY_CNT: 0.20,        # Anarchisten präsent
            PARTY_PCE: 0.10, 
            PARTY_PA: 0.15,         # Konservative Bauern (Minderheit)
            "left_republican_other": 0.05
        },
        "soldiers": {
            PARTY_PSOE: 0.40,       # Soldaten aus Arbeiterfamilien
            PARTY_PRR: 0.30, 
            PARTY_AR: 0.20, 
            PARTY_PCE: 0.10
        }
    },

    # --- PAÍS VASCO RURAL (Navarra, Alava, Vizcaya Provinz) ---
    # PDF: "Se impone la coalición... PNV y tradicionalistas [Carlisten]"
    # Navarra: 46k für Estella-Koalition vs 27k für Linke.
    # Charakteristik: Tief katholisch, konservativ, für "Fueros" (regionale Rechte).
    "pais_vasco_rural": {
        "aristocracy": {
            # Carlisten (MON) und PNV dominieren
            PARTY_MON: 0.40,        # Carlisten (Tradionalisten)
            PARTY_PNV: 0.40, 
            PARTY_CEDA: 0.10, 
            PARTY_DLR: 0.10
        },
        "clergy": {
            # Der Klerus hier war extrem nationalistisch/carlistisch
            PARTY_PNV: 0.50, 
            PARTY_MON: 0.40, 
            PARTY_CEDA: 0.10
        },
        "bourgeoisie": {
            # Ländliches Bürgertum wählt PNV
            PARTY_PNV: 0.60, 
            PARTY_MON: 0.15, 
            PARTY_DLR: 0.10, 
            PARTY_PRR: 0.10,
            "regionalist_other": 0.05
        },
        "workers_urban": {
            # Auch hier gibt es einige Linke, aber PNV ist stark (christliche Gewerkschaften ELA)
            PARTY_PSOE: 0.35, 
            PARTY_PNV: 0.35, 
            PARTY_PRRS: 0.15, 
            "catholic_other": 0.15
        },
        "workers_rural": {
            # Anders als im Rest Spaniens: Katholische Bauern wählen PNV/Carlisten
            PARTY_PNV: 0.45, 
            PARTY_MON: 0.30, 
            PARTY_PSOE: 0.15,
            PARTY_PA: 0.10
        },
        "soldiers": {
            PARTY_MON: 0.30,        # Requetés (Carlisten-Miliz) Rekrutierungspotenzial
            PARTY_PNV: 0.30, 
            PARTY_PRR: 0.20, 
            PARTY_PSOE: 0.20
        }
    },

    # --- PAÍS VASCO INDUSTRIAL (Bilbao, Guipúzcoa) ---
    # PDF Bilbao: Linke (Prieto) gewinnt gegen PNV.
    # Charakteristik: Starke Industrie, starke PSOE, aber auch starkes PNV-Bürgertum.
    "pais_vasco_industrial": {
        "aristocracy": {
            PARTY_PNV: 0.40, PARTY_MON: 0.30, PARTY_PRR: 0.20, PARTY_DLR: 0.10
        },
        "clergy": {
            PARTY_PNV: 0.50, PARTY_MON: 0.30, PARTY_CEDA: 0.20
        },
        "bourgeoisie": {
            # Die Industrie-Magnaten von Bilbao (Neguri)
            PARTY_PNV: 0.45,        # Baskischer Nationalismus
            PARTY_PRR: 0.25,        # Republikanische Ordnung
            PARTY_AR: 0.15, 
            PARTY_DLR: 0.10,
            "right_republican_other": 0.05
        },
        "workers_urban": {
            # Indalecio Prietos Hochburg
            PARTY_PSOE: 0.55,       # Starke UGT
            PARTY_PCE: 0.10,        # Kommunisten
            PARTY_PNV: 0.15,        # Christliche Arbeiter (ELA)
            "left_republican_other": 0.10, # ANV (Linksnationalisten)
            PARTY_PRRS: 0.10
        },
        "workers_rural": {
            PARTY_PNV: 0.40, PARTY_PSOE: 0.30, PARTY_MON: 0.20, PARTY_PRRS: 0.10
        },
        "soldiers": {
            PARTY_PSOE: 0.40, PARTY_PNV: 0.30, PARTY_PRR: 0.20, PARTY_MON: 0.10
        }
    },

    # --- ARAGON (Die Festung der Radikalen / Lerrouxismus) ---
    # PDF: "Desunión de las izquierdas... PR Radical domina."
    # Charakteristik: Urbanes Bürgertum und Arbeiter wählen Lerroux. 
    # Auf dem Land starke Anarchisten (Abstention), was die PSOE schwächt.
    "aragon_mixed": {
        "aristocracy": {
            PARTY_PA: 0.30,        # Agrarier (ländlicher Adel)
            PARTY_DLR: 0.30,       # Alcalá-Zamora war in Zaragoza Provinz beliebt
            PARTY_PRR: 0.20,       # Ordnungsorientierte Radikale
            PARTY_MON: 0.20
        },
        "clergy": {
            PARTY_CEDA: 0.40, 
            PARTY_DLR: 0.30, 
            PARTY_PA: 0.20,
            PARTY_MON: 0.10
        },
        "bourgeoisie": {
            # Das ist Lerroux' Kernwählerschaft
            PARTY_PRR: 0.55,       # Absolute Dominanz der Radikalen
            PARTY_PRRS: 0.15, 
            PARTY_AR: 0.15, 
            PARTY_DLR: 0.15
        },
        "workers_urban": {
            # Hier wählen Arbeiter NICHT automatisch PSOE
            PARTY_PRR: 0.35,       # Lerroux' populistischer Appeal
            PARTY_PSOE: 0.25,      # Historisch schwach in Zaragoza Stadt
            PARTY_PRRS: 0.20, 
            PARTY_PCE: 0.10,
            PARTY_CNT: 0.10        # Einige wählen trotz Boykott
        },
        "workers_rural": {
            # CNT-Gebiet. Wer wählt, wählt oft Radikal-Sozialistisch
            PARTY_PRRS: 0.30, 
            PARTY_CNT: 0.40,       # MASSIVE ABSTENTION (simuliert durch Gewichtung)
            PARTY_PRR: 0.15, 
            PARTY_PSOE: 0.10,
            PARTY_PA: 0.05
        },
        "soldiers": {
            PARTY_PRR: 0.60,       # Militärs in Aragon waren oft "Lerrouxistas"
            PARTY_PSOE: 0.20, 
            PARTY_AR: 0.20
        }
    },

    # --- CATALONIA URBAN (Barcelona Stadt) ---
    # PDF: Erdrutschsieg für Macià (ERC). Lliga und PSOE fast bedeutungslos.
    # Charakteristik: Massives urbanes Proletariat (CNT-Sympathisanten), das taktisch ERC wählt.
    "catalonia_urban": {
        "aristocracy": {
            # Der katalanische Adel (Industrielle) wählt Lliga
            PARTY_LLIGA: 0.50, 
            PARTY_DLR: 0.20, 
            PARTY_MON: 0.20,
            "regionalist_other": 0.10
        },
        "clergy": {
            PARTY_LLIGA: 0.60, 
            PARTY_CEDA: 0.20, 
            PARTY_DLR: 0.20
        },
        "bourgeoisie": {
            # Das Kleinbürgertum (Botiguers) wählt ERC, die Großbürger Lliga
            PARTY_ERC: 0.45, 
            PARTY_LLIGA: 0.30, 
            PARTY_AR: 0.15, 
            PARTY_PRR: 0.10
        },
        "workers_urban": {
            # MASSIVE ABSTENTION durch CNT möglich, aber 1931 wählten sie ERC!
            PARTY_ERC: 0.60,       # Katalanischer Linksnationalismus als Arbeiterersatz
            PARTY_PRR: 0.15,       # "Lerrouxistas" in den Elendsvierteln (Parallel)
            PARTY_CNT: 0.15,       # Hardcore-Nichtwähler
            PARTY_PSOE: 0.05,      # Historisch fast irrelevant in Barcelona
            PARTY_PCE: 0.05
        },
        "workers_rural": {
            PARTY_ERC: 0.60, 
            PARTY_LLIGA: 0.20, 
            PARTY_PRRS: 0.20
        },
        "soldiers": {
            PARTY_ERC: 0.40, 
            PARTY_PRR: 0.30, 
            PARTY_PSOE: 0.20, 
            PARTY_AR: 0.10
        }
    },

    # --- CATALONIA RURAL (Girona, Lleida, Tarragona) ---
    # PDF: "ERC vence en todas las circunscripciones."
    # Charakteristik: Konservativer als Barcelona, aber ERC dominiert durch das "Statut"-Versprechen.
    "catalonia_rural": {
        "aristocracy": {
            PARTY_LLIGA: 0.60, PARTY_MON: 0.20, PARTY_DLR: 0.20
        },
        "clergy": {
            PARTY_LLIGA: 0.70, PARTY_CEDA: 0.20, "catholic_other": 0.10
        },
        "bourgeoisie": {
            PARTY_ERC: 0.40, 
            PARTY_LLIGA: 0.40,      # Kopf an Kopf auf dem Land
            PARTY_PRR: 0.10, 
            "regionalist_other": 0.10
        },
        "workers_urban": {
            PARTY_ERC: 0.50, PARTY_PSOE: 0.20, PARTY_PRR: 0.20, PARTY_PCE: 0.10
        },
        "workers_rural": {
            # Bauern im Hinterland (Rabassaires) hassen die Lliga-Vermieter
            PARTY_ERC: 0.55,       # Rabassaires-Gewerkschaft war ERC-nah
            PARTY_LLIGA: 0.25, 
            PARTY_PRRS: 0.20
        },
        "soldiers": {
            PARTY_ERC: 0.40, PARTY_PRR: 0.30, PARTY_PSOE: 0.30
        }
    },

    # --- MADRID URBAN (Zentrum der Macht / UGT-Bastion) ---
    # PDF: Überwältigender Sieg der Conjunción (133k Stimmen).
    # Charakteristik: Massives, gewerkschaftlich organisiertes Proletariat (PSOE/UGT) 
    # und eine starke republikanische Intelligenzija (Azaña/AR).
    "madrid_urban": {
        "aristocracy": {
            # In der Hauptstadt ist der Adel isoliert, wählt defensiv
            PARTY_MON: 0.35,        # Alfonsinos
            PARTY_DLR: 0.25,        # Liberale Monarchisten-Überläufer
            PARTY_PRR: 0.20, 
            "right_republican_other": 0.15,
            PARTY_AR: 0.05
        },
        "clergy": {
            # Starker Widerstand gegen den Antiklerikalismus der Hauptstadt
            PARTY_CEDA: 0.40,       # Acción Nacional (Herrera Oria)
            PARTY_DLR: 0.25,        # Maura-Flügel
            PARTY_MON: 0.25,
            PARTY_AR: 0.10
        },
        "bourgeoisie": {
            # Zentrum der republikanischen Beamten und Intellektuellen
            PARTY_AR: 0.35,         # Azañas Kernwählerschaft (Ateneístas)
            PARTY_PRR: 0.25,        # Lerroux
            PARTY_DLR: 0.15, 
            "centre_republican_other": 0.15, # Unabhängige Liberale
            PARTY_PSOE: 0.10        # Linke Intellektuelle
        },
        "workers_urban": {
            # Herzland der UGT. Die PSOE dominiert das Proletariat fast vollständig.
            PARTY_PSOE: 0.65,       # Absolute Dominanz (Caballero/Besteiro)
            PARTY_PRRS: 0.10,       # Radikal-Sozialisten
            PARTY_AR: 0.10,         # Reformistische Arbeiter
            PARTY_PCE: 0.05,        # Kleine, laute Minderheit
            PARTY_PRR: 0.05,
            "marxist_other": 0.05
        },
        "workers_rural": {
            # Madrid Umland (Tageslöhner)
            PARTY_PSOE: 0.50, 
            PARTY_PRRS: 0.30, 
            "left_republican_other": 0.20
        },
        "soldiers": {
            # Die Garnison von Madrid schwankt zwischen Disziplin und Revolte
            PARTY_PSOE: 0.40, 
            PARTY_PRR: 0.30, 
            PARTY_AR: 0.20, 
            PARTY_MON: 0.10         # Alte Garde im Offizierskorps
        }
    },

    # --- ANDALUCÍA LATIFUNDIO (Ländliches Hinterland: Jaén, Córdoba, Badajoz-Stil) ---
    # PDF: PSOE-ASR holt in Jaén 83k Stimmen, in Córdoba Prov. 71k. 
    # Charakteristik: Herrschaft der Caciques vs. massivste sozialistische Mobilisierung.
    "andalucia_latifundio": {
        "aristocracy": {
            # Die Latifundistas wählen die Agrarier (PA) oder Monarchisten
            PARTY_PA: 0.45,         # Schutz des Eigentums
            PARTY_MON: 0.25,        # Traditionelle Ordnung
            PARTY_DLR: 0.20,        # Alcala-Zamora Anhänger
            PARTY_CEDA: 0.10
        },
        "clergy": {
            PARTY_DLR: 0.40,        # Katholisch-Republikanisch (Zamora-Einfluss)
            PARTY_CEDA: 0.30, 
            PARTY_MON: 0.30
        },
        "bourgeoisie": {
            # Das ländliche Bürgertum wählt PRR oder DLR
            PARTY_PRR: 0.40, 
            PARTY_DLR: 0.30, 
            PARTY_AR: 0.15, 
            PARTY_PSOE: 0.15        # Liberale Gutsbesitzer
        },
        "workers_urban": {
            # In den Bergwerken und Manufakturen dominiert die UGT
            PARTY_PSOE: 0.60, 
            PARTY_PRRS: 0.20, 
            PARTY_PCE: 0.10,        # Erste starke Zellen in Sevilla/Málaga
            PARTY_PRR: 0.10
        },
        "workers_rural": {
            # Das "Sorgenkind" der Republik: Landlose Tagelöhner
            PARTY_PSOE: 0.55,       # Enorme UGT-Basis
            PARTY_CNT: 0.30,        # MASSIVE ABSTENTION (Boykottgefahr)
            PARTY_PRRS: 0.10,       # Versprechen der Landreform
            PARTY_PA: 0.05          # Durch Caciques erzwungene Stimmen
        },
        "soldiers": {
            PARTY_PSOE: 0.45, 
            PARTY_PRR: 0.35, 
            PARTY_DLR: 0.20
        }
    },

    # --- ANDALUCÍA URBAN (Sevilla Stadt, Málaga Stadt, Cádiz) ---
    # PDF Sevilla: PRR (Martínez Barrio) dominiert mit 30k Stimmen.
    # Charakteristik: Starker republikanischer Mittelstand und antiklerikale Arbeiter.
    "andalucia_urban": {
        "aristocracy": {
            PARTY_MON: 0.40, PARTY_DLR: 0.30, PARTY_PRR: 0.20, PARTY_CEDA: 0.10
        },
        "clergy": {
            PARTY_DLR: 0.40, PARTY_CEDA: 0.30, PARTY_MON: 0.30
        },
        "bourgeoisie": {
            # Hochburg der Radikalen Partei (PRR)
            PARTY_PRR: 0.50,        # Die Partei von Martínez Barrio
            PARTY_AR: 0.20, 
            PARTY_PRRS: 0.15, 
            PARTY_DLR: 0.10,
            PARTY_PSOE: 0.05
        },
        "workers_urban": {
            # Kampf zwischen PRR-Populismus und Sozialismus
            PARTY_PSOE: 0.45, 
            PARTY_PRR: 0.25,        # Lerroux/Barrio waren hier populär
            PARTY_PRRS: 0.15, 
            PARTY_PCE: 0.10,        # Málaga war sehr radikal
            "marxist_other": 0.05
        },
        "workers_rural": {
            PARTY_PSOE: 0.40, PARTY_CNT: 0.35, PARTY_PRRS: 0.25
        },
        "soldiers": {
            PARTY_PRR: 0.50, PARTY_PSOE: 0.30, PARTY_AR: 0.20
        }
    },

    # --- LEVANTE BLASQUISTA (Valencia & Alicante) ---
    # PDF: "El PURA se integró en el P. Radical... el ala izquierda en el Radical Socialista."
    # Charakteristik: Populistischer, urbaner Republikanismus. Extrem antiklerikal.
    "valencia_mixed": {
        "aristocracy": {
            PARTY_DLR: 0.40, PARTY_PRR: 0.30, PARTY_MON: 0.20, PARTY_CEDA: 0.10
        },
        "clergy": {
            PARTY_DLR: 0.40, PARTY_CEDA: 0.30, PARTY_PRR: 0.20, PARTY_MON: 0.10
        },
        "bourgeoisie": {
            # Hochburg der Radikalen (PURA-Einfluss)
            PARTY_PRR: 0.55,       # Dominanz der Lerrouxistas/Blasquistas
            PARTY_PRRS: 0.20,      # Starker linker Flügel
            PARTY_AR: 0.15, 
            PARTY_DLR: 0.10
        },
        "workers_urban": {
            # Blasquismo war eine echte Volksbewegung
            PARTY_PRR: 0.40,       # Arbeiter wählen hier oft Radikal
            PARTY_PSOE: 0.35, 
            PARTY_PRRS: 0.15, 
            PARTY_PCE: 0.10
        },
        "workers_rural": {
            PARTY_PRRS: 0.35,      # Linke Republikaner versprechen Landreform
            PARTY_PSOE: 0.30, 
            PARTY_PRR: 0.20, 
            PARTY_CEDA: 0.15
        },
        "soldiers": {
            PARTY_PRR: 0.60, PARTY_PSOE: 0.20, PARTY_AR: 0.20
        }
    },

    # --- LA RIOJA SMALLHOLDER (Logroño) ---
    # PDF: Sieg der Izquierdas (PRRS & PSOE).
    # Charakteristik: Republikanische Kleinbauern.
    "la_rioja_smallholder": {
        "aristocracy": {
            PARTY_PA: 0.40, PARTY_MON: 0.30, PARTY_DLR: 0.30
        },
        "clergy": {
            PARTY_DLR: 0.40, PARTY_CEDA: 0.30, PARTY_PA: 0.30
        },
        "bourgeoisie": {
            PARTY_PRRS: 0.35,      # Marcelino Domingo (PRRS) war hier populär
            PARTY_PRR: 0.30, 
            PARTY_AR: 0.20, 
            PARTY_DLR: 0.15
        },
        "workers_urban": {
            PARTY_PSOE: 0.50, PARTY_PRRS: 0.30, PARTY_PRR: 0.20
        },
        "workers_rural": {
            # Kleinbauern wählen links-republikanisch
            PARTY_PRRS: 0.40, 
            PARTY_PSOE: 0.30, 
            PARTY_PA: 0.20, 
            PARTY_CEDA: 0.10
        },
        "soldiers": {
            PARTY_PRRS: 0.40, PARTY_PSOE: 0.30, PARTY_PRR: 0.30
        }
    },

    # --- CANARIAS MIXED ---
    "canarias_mixed": {
        "aristocracy": {
            PARTY_PRR: 0.40, PARTY_MON: 0.30, PARTY_DLR: 0.30
        },
        "clergy": {
            PARTY_DLR: 0.50, PARTY_CEDA: 0.30, PARTY_MON: 0.20
        },
        "bourgeoisie": {
            # Kanarisches Bürgertum wählte Martínez Barrio (PRR)
            PARTY_PRR: 0.50, PARTY_AR: 0.20, PARTY_PRRS: 0.20, PARTY_DLR: 0.10
        },
        "workers_urban": {
            # Starke Spaltung zwischen PSOE und PRR (Tenerife)
            PARTY_PSOE: 0.35, PARTY_PRR: 0.35, PARTY_PRRS: 0.20, PARTY_AR: 0.10
        },
        "workers_rural": {
            # Bauern wählten oft PRR oder PRRS
            PARTY_PRR: 0.40, PARTY_PRRS: 0.30, PARTY_PSOE: 0.20, PARTY_CEDA: 0.10
        },
        "soldiers": {
            PARTY_PRR: 0.60, PARTY_PSOE: 0.20, PARTY_AR: 0.20
        }
    },
}

# --- 4. GLOBAL STATE (Start Values - Expanded) ---

STATE_START = {
    "date": {"year": 1931, "month": 4},

    "constituencies": CONSTITUENCIES_1931,
    "regional_demographics": REGIONAL_DEMOGRAPHICS,
    
    # WIRTSCHAFT & INFRASTRUKTUR
    "economy": {
        "inflation": 0.5,
        "peseta_value": 10_000_000, 
        "budget_int": 25,
        "bread_price": 0.55,
        "tax_revenue_int": 230,
        "unemployment": 12.5,
        "exchange_rate": 45.0,
        "monthly_expenses_int": 250,
        
        "global_economy_state": "Great Depression", # Text-Status
        "arable_land": 20.5, 
        "industrial_output": 40,    # 0-100 (Katalonien/Baskenland sind das Herz)
        "trade_balance": -5         # Negativ = Importüberschuss
    },

    # DEMOGRAPHIE (Langsame Stats)
    "demographics": {
        "population_real": 23_563_000, # Echter Wert (Hidden)
        "census_1930": 23_563_000,     # Angezeigter Wert (Statisch)
        "urbanization": 32.0,
        "literacy": 68.5
    },

    # SOCIETY (Zustimmung der Schichten 0-100)
    "society": {
        # Die Eliten
        "aristocracy": 20,          # Latifundistas
        "clergy": 15,               # Die Kirche
        "bourgeoisie": 60,          # Mittelstand/Unternehmer (Azañas Basis)
        
        # Das Volk
        "workers_urban": 75,        # UGT/CNT Basis
        "workers_rural": 50,        # Campesinos (Warten auf Landreform)
        "soldiers": 55,             # Die einfachen Wehrpflichtigen
        
        # Regionale Nationalisten
        "catalans": 65,             # Wollen Autonomie
        "basques": 45               # Konservativ-Katholisch, aber wollen Fueros (Rechte)
    },

    # Wahl-Basis 1931
    # Summe pro Gruppe muss 1.0 ergeben!
    "election_demographics": {
        "aristocracy": {
            PARTY_MON: 0.400,
            PARTY_DLR: 0.350,
            PARTY_CEDA: 0.080,
            PARTY_PRR: 0.170
        },
        "clergy": {
            PARTY_DLR: 0.50,
            PARTY_CATHOLIC_OTHER: 0.15,
            PARTY_CEDA: 0.15,
            PARTY_MON: 0.10,
            PARTY_PNV: 0.10
        },
        "bourgeoisie": { 
            PARTY_DLR: 0.30,
            PARTY_AR: 0.30,
            PARTY_PRR: 0.20,
            PARTY_CENTRE_REP_OTHER: 0.10,
            PARTY_PSOE: 0.05,
            PARTY_ERC: 0.05
        },
        "workers_urban": {
            PARTY_PSOE: 0.30,
            PARTY_PRRS: 0.30,
            PARTY_AR: 0.20,
            PARTY_LEFT_REP_OTHER: 0.10,
            PARTY_PCE: 0.05,
            PARTY_PRR: 0.05
        },
        "workers_rural": {
            PARTY_PSOE: 0.38,   
            PARTY_PRRS: 0.25,   
            PARTY_CNT: 0.20,    
            PARTY_CEDA: 0.10, 
            PARTY_MON: 0.05,
            "catholic_other": 0.02
        },
        "soldiers": { # Wehrpflichtige
            PARTY_PSOE: 0.300,
            PARTY_PRR: 0.400,
            PARTY_AR: 0.250,
            PARTY_PCE: 0.050
        }
    },

    "government": {
        "coalition": [PARTY_PSOE, PARTY_AR, PARTY_DLR, PARTY_PRR],
        "is_minority": False,
        "next_election_date": {"year": 1931, "month": 6},
        "term_length": 48
    },

    "history": {
        "last_election_seats": {},
    },

    # Das Parlament (Las Cortes Generales)
    # Startet leer, da April 1931 noch per Dekret regiert wurde
    "parliament": {
        "total_seats": 470,
        "seats": {
            PARTY_PSOE: 0,
            PARTY_AR: 0,
            PARTY_PRR: 0,
            PARTY_DLR: 0,
            "monarchists": 0, # CEDA / Alfonsinos (später)
            "others": 0
        }
    },

    # DIPLOMATIE (Beziehungen 0-100)
    "diplomacy": {
        "uk": 50,           # Neutral / Wary
        "france": 60,       # Sympathisch (aber noch konservative Regierung)
        "usa": 50,          # Isolationistisch
        "germany": 45,      # Weimarer Republik (noch)
        "italy": 30,        # Mussolini (mag keine Demokraten)
        "ussr": 20,         # Keine offiziellen Beziehungen
        "vatican": 10       # Feindselig wegen Säkularisierung
    },

    # KERN-METRIKEN (Abstrakt)
    "metrics": {
        "public_order": 60,
        "judicial_loyalty": 20,      # Richter
        "coalition_stability": 50 
    },

    # SICHERHEIT
    "security": {
        "guardia_civil": {
            "name": "Guardia Civil", "manpower": 28000, "loyalty": 40, 
            "equipment": 80, "readiness": 90
        },
        "assault_guard": {
            "name": "Guardia de Asalto", "manpower": 0, "loyalty": 100, 
            "equipment": 0, "readiness": 0
        },
        "carabineros": {
            "name": "Carabineros", "manpower": 15000, "loyalty": 50, 
            "equipment": 40, "readiness": 60
        }
    },

    "land_ownership": {
        "latifundios": 65.0,    # Großgrundbesitz (Aristokratie/Kirche)
        "minifundios": 25.0,    # Kleinbauern (oft im Norden)
        "collectivized": 0.0,   # Reform-Land / Kollektive (Ziel der Linken)
        "state_owned": 10.0     # Gemeindeland / Staatlich
    },

    # MILITÄR
    "military": {
        "army_peninsular": {
            "name": "Peninsular Army", 
            "officers": 16000,          # Konkrete Zahl (~1 officer per 6.5 soldiers — bloated from colonial era)
            "soldiers": 105000,         # Konkrete Zahl
            "officer_loyalty": 40,      # Loyalität der Offiziere (0–100)
            "soldier_loyalty": 60,      # Loyalität der Truppen (0–100)
            "equipment_quality": 40,    # 0-100 Abstraktion
            "efficiency": 10,           # 0-100 Abstraktion
            "readiness": 20,            # Organisation & Doktrin
            "reform_progress": 0,       # 0–100: unlocks sequential reform cards
            "capitanias_active": True,  # Capitanías Generales still exist
            "zaragoza_open": True,      # Academia General Militar still open
        },
        "army_africa": {
            "name": "Army of Africa",
            "officers": 2500,
            "soldiers": 27500,
            "officer_loyalty": 30, 
            "soldier_loyalty": 40,
            "equipment_quality": 50,
            "efficiency": 45,
            "readiness": 70
        },
        "navy": {
            "name": "La Armada", 
            "ships_heavy": 4, "ships_light": 15,
            "officers": 2000, "sailors": 10000,
            "officer_loyalty": 15, "sailor_loyalty": 75, "readiness": 50
        },
        "air_force": {
            "name": "Fuerzas Aéreas", 
            "planes": 100, 
            "officers": 1000, "soldiers": 10000,
            "loyalty": 70, "readiness": 60
        }
    },
    
    # PARAMILITÄRS
    "paramilitaries": {
        "cnt_fai": {
            "name": "FAI Grupos de Afinidad", 
            "strength": 5000, 
            "armament": 25, 
            "organization": 10, 
            "readiness": 50,
            "hidden": True
        },
        "ugt_militias": {
            "name": "UGT Militias", 
            "strength": 3000, 
            "armament": 15, 
            "organization": 30, 
            "readiness": 30,
            "hidden": True
        },
        "republican_militias": {
            "name": "Republican Militias", 
            "strength": 1500, 
            "armament": 10, 
            "organization": 15, 
            "readiness": 20,
            "hidden": True
        },
        "falange_militias": {
            "name": "Falange Combat Groups", 
            "strength": 500, 
            "armament": 5, 
            "organization": 20, 
            "readiness": 40,
            "hidden": True
        },
        "requetes": {
            "name": "Requeté Battalions", 
            "strength": 8000, 
            "armament": 15, 
            "organization": 40, 
            "readiness": 70,
            "hidden": True
        },
        "monarchist_youth": {
            "name": "Alfonsist Action Groups", 
            "strength": 1000, 
            "armament": 10, 
            "organization": 25, 
            "readiness": 25,
            "hidden": True
        },
        "poum_militias": {
            "name": "POUM Militias", 
            "strength": 0, 
            "armament": 0, 
            "organization": 0, 
            "readiness": 0,
            "hidden": True
        }
    },

    "organizations": {
        UGT: {
            "name": "Unión General de Trabajadores",
            "members": 1200000,
            "mobilization": 40,
            "militarization": 5,
            "republic_relation": 70,
            "relations": {
                PARTY_PSOE: 85,
                PARTY_PCE: 20,
                CNT: 40
            }
        },

        CNT: {
            "name": "Confederación Nacional del Trabajo",
            "members": 1500000,
            "mobilization": 75,
            "militarization": 20,
            "republic_relation": 20,
            "relations": {
                FAI: 90,
                PARTY_PCE: 5,
                UGT: 40
            }
        },

        FAI: {
            "name": "Federación Anarquista Ibérica",
            "members": 50000,
            "mobilization": 90,
            "militarization": 35,
            "republic_relation": 10,
            "relations": {
                CNT: 90,
                PARTY_PCE: 0,
                UGT: 40
            }
        },

        ACC_CAT: {
            "name": "Acción Católica",
            "members": 500000,
            "mobilization": 30,
            "militarization": 0,
            "republic_relation": 20,
            "relations": {
                PARTY_CEDA: 70,
                PARTY_MON: 60,
                UGT: 0,
                CNT: 0
            }
        },

        SIN_CAT: {
            "name": "Sindicatos Católicos",
            "members": 200000,
            "mobilization": 20,
            "militarization": 0,
            "republic_relation": 30,
            "relations": {
                PARTY_CEDA: 60,
                PARTY_MON: 50,
                UGT: 10
            }
        },

        JS_PSOE: {
            "name": "Juventudes Socialistas",
            "members": 50000,
            "mobilization": 60,
            "militarization": 10,
            "republic_relation": 80,
            "relations": {
                PARTY_PSOE: 90,
                UGT: 70,
                CNT: 20
            }
        },

        JUV_LIB: {
            "name": "Juventudes Libertarias",
            "members": 30000,
            "mobilization": 85,
            "militarization": 25,
            "republic_relation": 15,
            "relations": {
                CNT: 80,
                FAI: 90,
                UGT: 20
            }
        },

        ATENEOS: {
            "name": "Ateneos Republicanos",
            "members": 80000,
            "mobilization": 40,
            "militarization": 0,
            "republic_relation": 90,
            "relations": {
                PARTY_AR: 80,
                PARTY_PRR: 50,
                UGT: 30
            }
        }
    }
}

# src/content/game_data.py

# --- 5. COALITION DEFINITIONS (Historische Vorlagen) ---
COALITION_DEFINITIONS = [
    {
        "id": "republican_socialist",
        "name": "Conjunción Republicano-Socialista",
        "partners": [PARTY_PSOE, PARTY_AR, PARTY_PRRS, PARTY_DLR, PARTY_ERC, PARTY_LEFT_REP_OTHER, PARTY_REGIONALIST_OTHER],
        "ideology_range": (1, 6),
        "historical_period": "1931-1933"
    },
    {
        "id": "radical_ceda",
        "name": "Center-Right Pact (Lerroux-Gil Robles)",
        "partners": [PARTY_PRR, PARTY_CEDA, PARTY_DLR, PARTY_LLIGA, PARTY_PA], # PA = Agrarians (Generic)
        "ideology_range": (5, 9),
        "historical_period": "1933-1935"
    },
    {
        "id": "popular_front",
        "name": "Frente Popular",
        "partners": [PARTY_PSOE, PARTY_PCE, PARTY_AR, PARTY_PRRS, PARTY_ERC, PARTY_CNT], # CNT support
        "ideology_range": (0, 3),
        "historical_period": "1936"
    },
    {
        "id": "national_bloc",
        "name": "Bloque Nacional",
        "partners": [PARTY_CEDA, PARTY_MON, PARTY_FAL],
        "ideology_range": (8, 10),
        "historical_period": "1936"
    },
    # Hypothetical Templates
    {
        "id": "republican_center",
        "name": "Republican Center Coalition",
        "partners": [PARTY_AR, PARTY_PRR, PARTY_PRRS, PARTY_DLR, PARTY_ERC],
        "ideology_range": (2, 6),
        "historical_period": "1931-1933 (plausible)"
    },
    {
        "id": "left_republican_bloc",
        "name": "Left Republican Bloc",
        "partners": [PARTY_AR, PARTY_PRRS, PARTY_ERC, PARTY_PCE],
        "ideology_range": (1, 4),
        "historical_period": "1931-1936 (plausible)"
    },
    {
        "id": "moderate_right",
        "name": "Moderate Right Coalition",
        "partners": [PARTY_CEDA, PARTY_PRR, PARTY_LLIGA, PARTY_PA],
        "ideology_range": (5, 8),
        "historical_period": "1933-1936 (plausible)"
    },
    {
        "id": "catalan_republican_pact",
        "name": "Catalan-Republican Pact",
        "partners": [PARTY_ERC, PARTY_AR, PARTY_PRRS],
        "ideology_range": (1, 5),
        "historical_period": "1931-1936 (regional)"
    },
    # Fictional Templates
    {
        "id": "grand_coalition",
        "name": "PSOE-CEDA Grand Coalition",
        "partners": [PARTY_PSOE, PARTY_CEDA],
        "ideology_range": (3, 8),
        "historical_period": "hypothetical"
    },
    {
        "id": "workers_alliance",
        "name": "Workers' Alliance",
        "partners": [PARTY_PSOE, PARTY_CNT, PARTY_PCE],
        "ideology_range": (0, 3),
        "historical_period": "1934 (hypothetical)"
    }
]

# --- 6. POLITICIANS (Minister-Pool) ---
# Wer kann welches Amt bekleiden?
# Format: "PartyID": {"MinistryKey": ["Name1", "Name2"]}
PARTY_MINISTERS = {
    PARTY_PSOE: {
        "prime_minister": ["Indalecio Prieto", "Julián Besteiro"],  # PSOE historically refused the PM role
        "labor": ["Largo Caballero", "Indalecio Prieto"],
        "finance": ["Indalecio Prieto", "Juan Negrín"],
        "justice": ["Fernando de los Ríos"],
        "interior": ["Julian Besteiro"]
    },
    PARTY_AR: {
        "prime_minister": ["Manuel Azaña"],
        "war": ["Manuel Azaña"],
        "state": ["Claudio Sánchez-Albornoz"],
        "finance": ["Jaime Carner"]
    },
    PARTY_PRR: { # Radicals
        "state": ["Alejandro Lerroux"],
        "interior": ["Rafael Salazar Alonso", "Diego Martínez Barrio", "Ricardo Samper"],
        "finance": ["Joaquín Chapaprieta"],
        "justice": ["Cantos"]
    },
    PARTY_DLR: {
        "president_republic": ["Niceto Alcalá-Zamora"],
        "prime_minister": ["Niceto Alcalá-Zamora"],
        "interior": ["Miguel Maura"],
        "war": ["Maura (Interim)"]
    },
    PARTY_PRRS: {
        "prime_minister": ["Marcelino Domingo", "Álvaro de Albornoz"],
        "agriculture": ["Marcelino Domingo", "Álvaro de Albornoz"],
        "justice": ["Álvaro de Albornoz"],
        "state": ["Marcelino Domingo"],
        "interior": ["Santiago Casares Quiroga"]
    },
    PARTY_CEDA: {
        "war": ["Gil-Robles"],
        "agriculture": ["Giménez Fernández"],
        "labor": ["Salmón"]
    },
    # Fallbacks für Generics
    "others": {
        "all": ["Technocrat", "Independent"]
    }
}

# FOR DEBUGGING & BALANCING
TARGET_1931 = {
    PARTY_PSOE: 115,
    PARTY_PRR: 90,
    PARTY_PRRS: 60,
    PARTY_AR: 30,
    PARTY_DLR: 25,
    PARTY_PA: 20,
    PARTY_PCE: 5,
    "others": 125
}
