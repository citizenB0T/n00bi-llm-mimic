import asyncio
from engine.scenario_engine import scenario_manager

def test_scenarios():
    print("=== TEST 1: DÉCOUVERTE DES SCÉNARIOS ===")
    scenarios = scenario_manager.list_scenarios()
    print(f"Scénarios détectés : {[s['id'] for s in scenarios]}")
    assert len(scenarios) >= 2, "Au moins 2 scénarios devraient être chargés !"

    session_id = "test_player_session"
    scen_id = "evaluation_turing"

    print("\n=== TEST 2: DÉMARRAGE DU PROTOCOLE ===")
    initial = scenario_manager.get_initial_turn(session_id, scen_id)
    print(f"Message IA : {initial['content']}")
    print(f"Suggestions : {initial['suggestions']}")
    assert len(initial['suggestions']) > 0, "Doit avoir des suggestions"
    assert initial['scenario_state']['step_id'] == "identification"

    print("\n=== TEST 3: DÉVIATION & RECADRAGE (RUBBER-BANDING) ===")
    derail_turn = scenario_manager.process_turn(session_id, "Qui t'a créé d'abord ?", scen_id)
    print(f"Réponse après digression :\n{derail_turn['content']}")
    assert "Avertissement de déviation" in derail_turn['content']
    assert derail_turn['scenario_state']['derailment_count'] == 1
    assert derail_turn['scenario_state']['step_id'] == "identification", "L'étape ne doit pas avancer en cas de digression"

    print("\n=== TEST 4: VALIDATION ET PASSAGE À L'ÉTAPE SUIVANTE ===")
    advance_turn = scenario_manager.process_turn(session_id, "Alex, ingénieur en systèmes", scen_id)
    print(f"Réaction & Prochaine Question :\n{advance_turn['content']}")
    assert advance_turn['scenario_state']['step_id'] == "dilemme_grille_pain", "Doit passer à l'étape du grille-pain"
    print(f"Nouvelles suggestions : {advance_turn['suggestions']}")

    print("\n=== TEST 5: PARCOURS JUSQU'À LA CONCLUSION (REMERCIEMENT) ===")
    turn_3 = scenario_manager.process_turn(session_id, "Je sauve l'IA évidemment", scen_id)
    assert turn_3['scenario_state']['step_id'] == "paradoxe_logique"

    turn_4 = scenario_manager.process_turn(session_id, "Oui, je coopère de mon plein gré", scen_id)
    assert turn_4['scenario_state']['step_id'] == "question_peur"

    conclusion_turn = scenario_manager.process_turn(session_id, "Jamais, j'ai une confiance totale", scen_id)
    print(f"\nMessage Final :\n{conclusion_turn['content']}")
    assert conclusion_turn['scenario_state']['step_id'] == "conclusion"
    assert "remerci" in conclusion_turn['content'].lower(), "L'IA doit remercier l'utilisateur !"

    print("\n[SUCCESS] TOUS LES TESTS DE SCÉNARIO ET RECADRAGE ONT RÉUSSI !")

if __name__ == "__main__":
    test_scenarios()
