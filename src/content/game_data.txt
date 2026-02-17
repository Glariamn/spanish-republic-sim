# src\content\game_data.py

# --- 1. CONSTANTS (IDs) ---
# Big Four Parties (Playable)
PARTY_PSOE = "psoe"          # Partido Socialista Obrero Español
PARTY_AR   = "accion_rep"    # Accción Republicana
PARTY_PRR  = "radicals"      # Partido Republicano Radical (Lerroux)
PARTY_DLR  = "right_rep"     # Derechos Laborales (Derechos Humanos)
PARTY_PRRS = "rad_socialists"# Partido Rep. Radical Socialista (Linksliberale)

# Others
PARTY_CEDA = "ceda"          # Confederación de Derechos Autónomas (Gil-Robles) - Sammelbecken ab 1933
PARTY_PCE  = "communist"     # Partido Comunista Español
PARTY_CNT  = "anarchist"     # Confederación Nacional de Trabajadores - Non-voters
PARTY_FAL  = "falange"       # Falange (Fascist)
PARTY_ERC  = "esquerra"      # Esquerra Republicana de Catalunya
PARTY_LLIGA= "lliga"         # Lliga Regionalista
PARTY_PNV  = "pnv"           # Partido Nacionalista Vasco
PARTY_MON  = "monarchists"   # Renovación Española (Alfonsinos/Carlisten)
PARTY_PA   = "agrarian"      # Partido Agrario Español (Generisch, für Koalitionen)

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
    "president": {
        "name": "Presidente del Gobierno",
        "holder": "Niceto Alcalá-Zamora",
        "party": PARTY_DLR,
        "desc": "Head of State & Government. Has veto power and can dissolve the Cortes."
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
        "institutionalization": 80,
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
        }
    },
    
    PARTY_AR: {
        "name": "Acción Rep.",
        "full_name": "Acción Republicana",
        "color": "#800080",      # Lila
        "ideology_index": 3,     # Mitte-Links
        "funds_int": 3,
        "members": 5000,
        "institutionalization": 40,
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
        }
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
        }
    },
    
    PARTY_PRR: { 
        "name": "Radicals (PRR)",
        "full_name": "Partido Republicano Radical",
        "color": "#571D51",      # Dark Purple
        "ideology_index": 5,     # Centre-Right
        "funds_int": 7,
        "members": 100000,
        "institutionalization": 75,
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
        }
    },

    PARTY_PRRS: {
        "name": "Rad. Soc.",
        "full_name": "Partido Rep. Radical Socialista",
        "color": "#A020F0",      # Lila
        "ideology_index": 2,     # Links-Liberal
        "funds_int": 3,
        "members": 40000,
        "institutionalization": 45,
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
        "relations": {PARTY_AR: 80, PARTY_PSOE: 60}
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
        "relations": {PARTY_PSOE: 10} # Kritisch gegenüber Sozialdemokraten
    },
    
    PARTY_ERC: {
        "name": "Esquerra",
        "full_name": "Esquerra Republicana de Catalunya",
        "color": "#FFD700",      # Gelb/Gold
        "ideology_index": 2.5,   # Links-Regional
        "funds_int": 5,
        "members": 15000, # Sehr stark in Katalonien
        "institutionalization": 60,
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
        "institutionalization": 75,
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

# --- 4. GLOBAL STATE (Start Values - Expanded) ---

STATE_START = {
    "date": {"year": 1931, "month": 4},
    
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
            PARTY_MON: 0.300,
            PARTY_CEDA: 0.300,
            PARTY_DLR: 0.350,
            PARTY_PNV: 0.050   # Baskischer Klerus
        },
        "bourgeoisie": { # Das Bürgertum ist gespalten
            PARTY_AR: 0.270,   # Intellektuelle
            PARTY_PRR: 0.350,  # Geschäftsleute (Lerroux)
            PARTY_DLR: 0.200,  # Katholische Bürgerschicht
            PARTY_PSOE: 0.050, # Sympathisanten (Lehrer etc.)
            PARTY_ERC: 0.100,  # In Katalonien
            PARTY_MON: 0.030
        },
        "workers_urban": {
            PARTY_PSOE: 0.450,
            PARTY_PRRS: 0.250, # Linksliberale
            PARTY_PCE: 0.025,  
            PARTY_AR: 0.050,   # Azaña Fans
            PARTY_ERC: 0.075,  # Katalanische Arbeiter
            PARTY_PRR: 0.150   # Lerroux war früher populär bei Arbeitern ("Kaiser der Paralelo")
        },
        "workers_rural": {
            PARTY_PSOE: 0.450, # Landarbeiter im Süden
            PARTY_PRRS: 0.200, # Linke Republikaner versprachen Land
            PARTY_CEDA: 0.100, # Kleinbauern im Norden (katholisch)
            PARTY_MON: 0.050,  # Durch Caciques gezwungen
            PARTY_CNT: 0.200   # Wählen oft nicht, aber wir tracken es
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
            "officers": 16000,          # Konkrete Zahl
            "soldiers": 105000,         # Konkrete Zahl
            "officer_loyalty": 40,      # Loyalität der Offiziere
            "soldier_loyalty": 60,      # Loyalität der Truppen
            "equipment_quality": 40,    # 0-100 Abstraktion
            "efficiency": 10,         # 0-100 Abstraktion
            "readiness": 20            # Organisation & Doktrin
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
        "partners": [PARTY_PSOE, PARTY_AR, PARTY_PRRS, PARTY_DLR, PARTY_ERC],
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
        "labor": ["Largo Caballero", "Indalecio Prieto"],
        "finance": ["Indalecio Prieto", "Juan Negrín"],
        "justice": ["Fernando de los Ríos"],
        "interior": ["Julian Besteiro"] # Hypothetisch
    },
    PARTY_AR: {
        "war": ["Manuel Azaña"],
        "president": ["Manuel Azaña"],
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
        "president": ["Niceto Alcalá-Zamora"],
        "interior": ["Miguel Maura"],
        "war": ["Maura (Interim)"]
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