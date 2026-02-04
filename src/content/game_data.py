# game_data.py

# --- 1. CONSTANTS (IDs) ---
# Big Four Parties (Playable)
PARTY_PSOE = "psoe"          # Sozialisten
PARTY_AR   = "accion_rep"    # Azaña (Später IR)
PARTY_PRR  = "radicals"      # Lerroux (Zentrum/Rechts)
PARTY_DLR  = "right_rep"     # Alcalá-Zamora (Konservative Republikaner)
PARTY_PRRS = "rad_socialists"# Linksliberale

# Die "Kommenden" & Kleinen
PARTY_CEDA = "ceda"          # Katholische Rechte (Gil-Robles) - Sammelbecken ab 1933
PARTY_PCE  = "communist"     # Kommunisten
PARTY_CNT  = "anarchist"     # Wählen eigentlich nicht, aber wir tracken Sympathie
PARTY_FAL  = "falange"       # Faschisten (Primo de Rivera)
PARTY_ERC  = "esquerra"      # Katalanische Linke
PARTY_LLIGA= "lliga"         # Katalanische Rechte
PARTY_PNV  = "pnv"           # Baskische Nationalisten
PARTY_MON  = "monarchists"   # Renovación Española (Alfonsinos/Carlisten)

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
        "funds_int": 5,          
        "members": 20000,
        "factions": {
            "reformist": 30,     # Besteiro
            "centrist": 40,      # Prieto
            "revolutionary": 30  # Caballero
        },
        "relations": {
            PARTY_AR: 75,
            PARTY_PRR: 40,
            PARTY_DLR: 25,
            "church": 5,
            "army": 10
        }
    },
    
    PARTY_AR: {
        "name": "Acción Rep.",
        "full_name": "Acción Republicana",
        "color": "#7B3F00",      # Braun/Dunkelrot
        "ideology_index": 3,     # Mitte-Links
        "funds_int": 4,
        "members": 5000,
        "factions": {"intellectuals": 90, "jacobins": 10},
        "relations": {
            PARTY_PSOE: 70,
            PARTY_DLR: 40,
            "church": 10,
            "army": 30
        }
    },
    
    PARTY_DLR: {
        "name": "DLR",
        "full_name": "Derecha Liberal Republicana",
        "color": "#004488",      # Blau
        "ideology_index": 7,     # Mitte-Rechts
        "funds_int": 8,          
        "members": 3000,
        "factions": {"catholics": 80, "liberals": 20},
        "relations": {
            PARTY_PSOE: 25,
            "church": 60,
            "army": 60
        }
    },
    
    PARTY_PRR: { 
        "name": "Radicals (PRR)",
        "full_name": "Partido Republicano Radical",
        "color": "#F7A800",      # Orange
        "ideology_index": 5,     # Exakte Mitte
        "funds_int": 6,
        "members": 10000,
        "factions": {"opportunists": 90, "ideologues": 10},
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
        "members": 4000,
        "factions": {"left": 50, "right": 50},
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
        "factions": {"stalinists": 100},
        "relations": {PARTY_PSOE: 40} # Kritisch gegenüber Sozialdemokraten
    },
    
    PARTY_ERC: {
        "name": "Esquerra",
        "full_name": "Esquerra Republicana de Catalunya",
        "color": "#FFD700",      # Gelb/Gold
        "ideology_index": 2.5,   # Links-Regional
        "funds_int": 3,
        "members": 15000, # Sehr stark in Katalonien
        "factions": {"separatists": 60, "federalists": 40},
        "relations": {PARTY_AR: 60, "army": 5}
    },
    
    PARTY_PNV: {
        "name": "PNV",
        "full_name": "Partido Nacionalista Vasco",
        "color": "#008000",      # Grün
        "ideology_index": 6,     # Christdemokratisch-Regional
        "funds_int": 5,
        "members": 10000,
        "factions": {"autonomists": 100},
        "relations": {"church": 90}
    },
    
    PARTY_LLIGA: {
        "name": "Lliga",
        "full_name": "Lliga Regionalista",
        "color": "#B8860B",      # Dark Goldenrod
        "ideology_index": 7.5,   # Konservativ-Katalanisch
        "funds_int": 10,         # Sehr reich (Industrielle)
        "members": 5000,
        "factions": {"conservatives": 100},
        "relations": {PARTY_DLR: 60}
    },

    PARTY_CEDA: {
        "name": "CEDA",
        "full_name": "Confederación Española de Derechas Autónomas",
        "color": "#000000",      # Schwarz
        "ideology_index": 8,     # Rechts-Konservativ
        "funds_int": 15,         # Massiv finanziert von Landbesitzern
        "members": 50000,        # Wird zur Massenpartei
        "factions": {"legalists": 60, "extremists": 40},
        "relations": {"church": 100, "army": 70, PARTY_PSOE: 0}
    },
    
    PARTY_MON: {
        "name": "Monarchists",
        "full_name": "Renovación Española / Comunión Tradicionalista",
        "color": "#4B0082",      # Indigo/Royal Purple
        "ideology_index": 9,     # Reationär
        "funds_int": 20,         # Der alte Adel
        "members": 5000,
        "factions": {"alfonsinos": 50, "carlistas": 50},
        "relations": {"army": 90, "church": 90}
    },
    
    PARTY_FAL: {
        "name": "Falange",
        "full_name": "Falange Española",
        "color": "#202020",      # Fast Schwarz / Dunkelblau
        "ideology_index": 10,    # Faschistisch
        "funds_int": 2,          # Am Anfang arm
        "members": 200,          # Am Anfang winzig
        "factions": {"joseantonianos": 100},
        "relations": {"army": 50}
    },
    
    # Fallback
    "others": {
        "name": "Others", 
        "full_name": "Independientes", 
        "color": "#888888", 
        "ideology_index": 4.5,
        "funds_int": 0,
        "members": 0,
        "factions": {},
        "relations": {}
    }
}

# --- 4. GLOBAL STATE (Start Values - Expanded) ---

STATE_START = {
    "date": {"year": 1931, "month": 4},
    
    # WIRTSCHAFT & INFRASTRUKTUR
    "economy": {
        "inflation": 1.0,
        "peseta_value": 10_000_000, 
        "budget_int": 25,
        "bread_price": 0.55,
        "tax_revenue_int": 5,
        "unemployment": 12.5,
        "exchange_rate": 45.0,
        
        # NEU: Makroökonomie
        "global_economy_state": "Great Depression", # Text-Status
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
        "aristocracy": 20,          # Latifundistas (Hassen die Republik)
        "clergy": 15,               # Die Kirche (Fühlt sich bedroht)
        "bourgeoisie": 60,          # Mittelstand/Unternehmer (Azañas Basis)
        
        # Das Volk
        "workers_urban": 75,        # UGT/CNT Basis (Hoffnungsvoll)
        "workers_rural": 50,        # Campesinos (Warten auf Landreform)
        "soldiers": 55,             # Die einfachen Wehrpflichtigen (als soziale Schicht)
        
        # Regionale Nationalisten
        "catalans": 65,             # Wollen Autonomie
        "basques": 45               # Konservativ-Katholisch, aber wollen Fueros (Rechte)
    },

    # Wahl-Basis 1931
    # Summe pro Gruppe muss 1.0 ergeben!
    "election_demographics": {
        "aristocracy": {
            PARTY_MON: 0.650, 
            PARTY_DLR: 0.250, 
            PARTY_CEDA: 0.080, # Existiert formal noch nicht, aber als Strömung
            PARTY_PRR: 0.020
        },
        "clergy": {
            PARTY_MON: 0.400,
            PARTY_CEDA: 0.400,
            PARTY_DLR: 0.150,
            PARTY_PNV: 0.050   # Baskischer Klerus
        },
        "bourgeoisie": { # Das Bürgertum ist gespalten
            PARTY_AR: 0.250,   # Intellektuelle
            PARTY_PRR: 0.350,  # Geschäftsleute (Lerroux)
            PARTY_DLR: 0.200,  # Katholische Bürgerschicht
            PARTY_PSOE: 0.050, # Sympathisanten (Lehrer etc.)
            PARTY_ERC: 0.100,  # In Katalonien
            PARTY_MON: 0.050
        },
        "workers_urban": {
            PARTY_PSOE: 0.650,
            PARTY_PRRS: 0.100, # Linksliberale
            PARTY_PCE: 0.025,  # Noch sehr klein
            PARTY_AR: 0.050,   # Azaña Fans
            PARTY_ERC: 0.100,  # Katalanische Arbeiter
            PARTY_PRR: 0.075   # Lerroux war früher populär bei Arbeitern ("Kaiser der Paralelo")
        },
        "workers_rural": {
            PARTY_PSOE: 0.450, # Landarbeiter im Süden
            PARTY_CEDA: 0.300, # Kleinbauern im Norden (sehr katholisch!)
            PARTY_MON: 0.150,  # Durch Caciques gezwungen
            PARTY_CNT: 0.100   # Wählen oft gar nicht (Abstention), aber wir tracken es
        },
        "soldiers": { # Wehrpflichtige
            PARTY_PSOE: 0.400,
            PARTY_PRR: 0.300,
            PARTY_AR: 0.200,
            PARTY_PCE: 0.100
        }
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
        "judicial_loyalty": 20      # Richter
    },

    # SICHERHEIT
    "security": {
        "guardia_civil": {
            "name": "Guardia Civil", "manpower": 25000, "loyalty": 40, 
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

    # MILITÄR
    "military": {
        "army_peninsular": {
            "name": "Peninsular Army", "manpower": 120000, 
            "officer_loyalty": 30, "soldier_loyalty": 60, "equipment": 40
        },
        "army_africa": {
            "name": "Army of Africa", "manpower": 30000, 
            "officer_loyalty": 10, "soldier_loyalty": 20, "equipment": 95
        },
        "navy": {
            "name": "La Armada", "ships_heavy": 4, "ships_light": 15,
            "officer_loyalty": 15, "sailor_loyalty": 75, "readiness": 50
        },
        "air_force": {
            "name": "Fuerzas Aéreas", "planes": 100, 
            "loyalty": 70, "readiness": 60
        }
    },
    
    # PARAMILITÄRS
    "paramilitaries": {
        "cnt_fai": {"name": "Anarchists", "strength": 5000, "hidden": True},
        "falange": {"name": "Falange", "strength": 500, "hidden": True},
        "requetes": {"name": "Carlists", "strength": 8000, "hidden": True},
        "poum": {"name": "POUM", "strength": 0, "hidden": True}
    }
}