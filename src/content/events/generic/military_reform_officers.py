import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd

class MilitaryReformOfficersEvent(GameEvent):
    
    def should_trigger(self):
        overdimensioned_army = self.state.metrics['military.army_peninsular.officers'] / self.state.metrics['military.army_peninsular.soldiers'] < 1 / 100 # pseudocode, zu viele offiziere
        war_minister = self.state.ministers['military.war_minister'] # muss nicht azana sein, sollte aber wahrscheinlicher sein
        return overdimensioned_army and war_minister is not None

    def get_data(self):
        return {
            "id": "officer_question_generic", # sollte anfangs die einzige option sein, passiert nichts ohne das. wiederholt sich wieder 
            "title": "The Officer Question", 
            "text": f"""Minister of War {self.state.ministers['military.war_minister'].name} 
            is putting forward the proposal to all officers to retire early with full pensions. This would reduce our financial burden
            and begin the process of modernizing the army. However, this would cause distrust against the Republic among the privileged traditionalist officers.""",
            "choices": [
                {
                    "text": f"We support the implementation of the Ley {self.state.ministers['military.war_minister'].name}, mehr text",
                    "success": {
                        "msg": "We offered a full pension to all willing officers. Let's see how many are willing to take it up.",
                        "effects": {"budget_int": -3, "military.army_peninsular.officer_loyalty": +5} # add: reduce right wing relations, move officer/soldier vote support for specific parties (apathic ones leave).
                        # reduce army size based off politization in it, aka with more ceda/far right support less will retire under republic leadership. reduziert monthly expenses proportional
                        # verbessert einen neuen wert. was soll es sein? ein neuer wert: offizierzahl von soldatenzahl trennen und dann officer/soldier ratio berechnen? oder lieber abstrahieren
                        # als officer_ratio. was ist mit equipment. wenn sie retiren geht er nicht hoch. es steht nur mehr pro soldat zur verfügung.
                        # ganz zahlen? also anzahl gewehre, anzahl geschütze, usw oder abstraktes equipment quality, organization efficiency, usw.
                        # sowohl nicht ambitionierte offiziere, die ok mit retirement sind
                        # und unzufriedene offiziere verlassen das korps. wie war es historisch? gab es mehr republiktreue retirees oder.
                        # für loyalität
                    }
                }
            ],
            "choices": [
                {
                    "text": "Not now", # generische ablehnung/statis quo, macht wenig außer eigene leute etwsa unzufrieden
                    "success": {
                        "msg": "Ok.",
                        "effects": { } # zeugs nichts passiert  praktisch, armee ist  kacke und im kriegsfall (falls wir so was implemetieren, großes falls, klappt sofort zusammen)
                    }
                }
            ],
            "choices": [ # verfügbar nachdem offizierszahl durch wiederholte option oben auf managebare zahl sank.woran sollte diese abhängig sein? wurden die offiziere über einen zeitraum entlassen oder direkt im mai 1931? 
                {
                    "text": "Abolish the General staff, mehr text", # alternativ eine weitere option, replace the general staff??
                    "success": {
                        "msg": "Ok.",
                        "effects": { } # viel weniger army loyalty, ermöglicht die restlichen reformen. wie modellieren wir dass die politisierung bzw der nepotistische privilegienstand abnimmt?
                    }
                }
            ],
            "choices": [ 
                {
                    "text": "Abolish the Capitanias Generales, mehr text", # klingt notwendig
                    "success": {
                        "msg": "Ok.",
                        "effects": { } # weniger army loyalty, mehr unrest, drift richtung ermöglicht reformen zu direkten regionalen armee formationen statt nur der zentrale. 
                    }
                }
            ],
            "choices": [ # verfügbar nachdem offizierszahl durch wiederholte option oben auf managebare zahl sank.woran sollte diese abhängig sein? wurden die offiziere über einen zeitraum entlassen oder direkt im mai 1931? 
                {
                    "text": "Restructure the army into divisions, mehr text", # wow echt, klingt notwendig
                    "success": {
                        "msg": "Ok.",
                        "effects": { } # verursacht vorerst chaos? macht armee effizienter. sonstiges
                    }
                }
            ],
            "choices": [ # verfügbar nachdem offizierszahl durch wiederholte option oben auf managebare zahl sank.woran sollte diese abhängig sein? wurden die offiziere über einen zeitraum entlassen oder direkt im mai 1931? 
                {
                    "text": "Close the Zaragoza military academy, usw...",
                    "success": {
                        "msg": "Ok.",
                        "effects": { } # viel weniger army loyalty, viel weniger relations mit armee, rechten usw. loyalty drift sollte positiv sein. wahl tendenzen sollten zu gleichmäßigerem equilibrium tendieren, bisheriges equilibrium sollte monarchisch? konservativ? usw sein.
                    }
                }
            ]
            # guardia asalto erstellung sollte separat passieren, aber erst nachdem man paar armeereformeen hat
            # zuletzt endentscheidung: Reorganisation der Kolonialtruppen in Marokko (ab 1932). 
            # art  größtes hindernis revoltrisiko, peninsular army vs colonial army? abhängig von vielen faktoren
        }