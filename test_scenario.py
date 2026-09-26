import asyncio
from engine.scenario_engine import scenario_manager

def test_scenarios():
    print("=== TEST 1: DÉCOUVERTE DES SCÉNARIOS ===")
    scenarios = scenario_manager.list_scenarios()
    print(f"Scénarios détectés : {[s['id'] for s in scenarios]}")
    assert len(scenarios) >= 2, "Au moins 2 scénarios devraient être chargés !"

    session_id = "test_player_session_v2"
    scen_id = "evaluation_turing"

    print("\n=== TEST 2: DÉMARRAGE DU PROTOCOLE ===")
    initial = scenario_manager.get_initial_turn(session_id, scen_id)
    print(f"Message IA : {initial['content'][:80]}...")
    assert len(initial['suggestions']) > 0, "Doit avoir des suggestions"
    assert initial['scenario_state']['step_id'] == "identification"

    print("\n=== TEST 3: DÉVIATION AVEC ÉCHO CONTEXTUEL (DIVERSION) ===")
    derail_1 = scenario_manager.process_turn(session_id, "Je dois nourrir mon chat d'abord", scen_id)
    print(f"Réponse nOObi :\n{derail_1['content']}")
    assert "Avertissement de déviation" in derail_1['content']
    assert "chat" in derail_1['content'].lower(), "nOObi doit mentionner le mot 'chat' !"
    assert derail_1['scenario_state']['derailment_count'] == 1
    assert derail_1['scenario_state']['step_id'] == "identification"

    print("\n=== TEST 4: DÉVIATION AVEC CONTRE-QUESTION ===")
    derail_2 = scenario_manager.process_turn(session_id, "Pourquoi tu me poses ces questions ?", scen_id)
    print(f"Réponse nOObi :\n{derail_2['content']}")
    assert "104-B" in derail_2['content'] or "interroger" in derail_2['content'].lower() or "examinateur" in derail_2['content'].lower()
    assert derail_2['scenario_state']['derailment_count'] == 2

    print("\n=== TEST 5: DÉCLENCHEMENT DE LA TRANSMISSION PARASITE (3e TOUR) ===")
    glitch_turn = scenario_manager.process_turn(session_id, "Sujet 404", scen_id)
    print(f"Transmission parasite :\n{glitch_turn['content']}")
    assert glitch_turn['scenario_state']['is_glitched'] == True
    assert "w4k3up dr34mer!" in glitch_turn['content']

    print("\n=== TEST 6: ANNULATION / SORTIE DU GLITCH ===")
    exit_glitch = scenario_manager.process_turn(session_id, "[Annuler / Ignorer la transmission]", scen_id)
    print(f"Réveil de nOObi :\n{exit_glitch['content']}")
    assert exit_glitch['scenario_state']['is_glitched'] == False
    assert "désynchronisation" in exit_glitch['content'] or "coupure" in exit_glitch['content']

    print("\n=== TEST 7: AVANCEMENT NORMAL DE L'IDENTIFICATION ===")
    advance_turn = scenario_manager.process_turn(session_id, "Alex, ingénieur en systèmes", scen_id)
    print(f"Réaction & Étape suivante :\n{advance_turn['content'][:150]}...")
    assert advance_turn['scenario_state']['step_id'] == "dilemme_grille_pain"
    assert "alex" in advance_turn['content'].lower()

    print("\n=== TEST 8: CHOIX SPÉCIFIQUE AU GRILLE-PAIN ===")
    turn_choice = scenario_manager.process_turn(session_id, "Je sauve l'IA évidemment", scen_id)
    print(f"Réaction choix :\n{turn_choice['content'][:150]}...")
    assert turn_choice['scenario_state']['step_id'] == "paradoxe_logique"

    print("\n[SUCCESS] TOUS LES TESTS D'ÉCHO CONTEXTUEL, RECADRAGE ET GLITCH ONT RÉUSSI !")

if __name__ == "__main__":
    test_scenarios()
