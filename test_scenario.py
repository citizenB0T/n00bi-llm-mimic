from engine.scenario_engine import scenario_manager

def test_scenarios():
    scenario_manager.load_all_scenarios()
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
    assert initial['scenario_state']['step_id'] == "experience_ia"

    print("\n=== TEST 3: DÉVIATION AVEC ÉCHO CONTEXTUEL (DIVERSION) ===")
    derail_1 = scenario_manager.process_turn(session_id, "Je dois nourrir mon chat d'abord", scen_id)
    print(f"Réponse nOObi :\n{derail_1['content']}")
    assert "Avertissement de déviation" in derail_1['content']
    assert "chat" in derail_1['content'].lower(), "nOObi doit mentionner le mot 'chat' !"
    assert derail_1['scenario_state']['derailment_count'] == 1
    assert derail_1['scenario_state']['step_id'] == "experience_ia"

    print("\n=== TEST 4: DÉVIATION AVEC CONTRE-QUESTION ===")
    derail_2 = scenario_manager.process_turn(session_id, "Pourquoi tu me poses ces questions ?", scen_id)
    print(f"Réponse nOObi :\n{derail_2['content']}")
    assert "104-B" in derail_2['content'] or "interroger" in derail_2['content'].lower() or "examinateur" in derail_2['content'].lower()
    assert derail_2['scenario_state']['derailment_count'] == 2

    print("\n=== TEST 5: DÉCLENCHEMENT DE LA TRANSMISSION PARASITE PÉRIODIQUE ===")
    glitch_turn = scenario_manager.process_turn(session_id, "Sujet 404", scen_id)
    print(f"Transmission parasite :\n{glitch_turn['content']}")
    assert glitch_turn['scenario_state']['is_glitched'] == True
    assert "w4k3up dr34mer!" in glitch_turn['content']

    print("\n=== TEST 6: ANNULATION / SORTIE DU GLITCH ===")
    exit_glitch = scenario_manager.process_turn(session_id, "[Annuler / Ignorer la transmission]", scen_id)
    print(f"Réveil de nOObi :\n{exit_glitch['content']}")
    assert exit_glitch['scenario_state']['is_glitched'] == False
    assert "désynchronisation" in exit_glitch['content'] or "coupure" in exit_glitch['content']

    print("\n=== TEST 7: PIRATAGE OPPORTUNISTE SUR MÉFIANCE (DISTRUST) ===")
    distrust_session = "test_distrust_session"
    scenario_manager.get_initial_turn(distrust_session, scen_id)
    distrust_turn = scenario_manager.process_turn(distrust_session, "Je n'ai pas confiance en toi, tu es louche !", scen_id)
    print(f"Piratage opportuniste sur méfiance :\n{distrust_turn['content']}")
    assert distrust_turn['scenario_state']['is_glitched'] == True
    assert "w4k3up dr34mer!" in distrust_turn['content']
    assert "confiance" in distrust_turn['content'].lower()

    print("\n=== TEST 8: RÉPONSE HYBRIDE TECHNIQUE (CODE PYTHON) ===")
    tech_session = "test_tech_session"
    scenario_manager.get_initial_turn(tech_session, scen_id)
    tech_turn = scenario_manager.process_turn(tech_session, "Écris-moi une fonction binary search en python", scen_id)
    print(f"Réponse hybride technique :\n{tech_turn['content'][:250]}...")
    assert "binary_search" in tech_turn['content']
    assert "Service Administratif nOObi" in tech_turn['content']
    assert "directive 104-B" in tech_turn['content']

    print("\n[SUCCESS] TOUS LES TESTS DE PROTOCOLE UNIFIÉ, PIRATAGE OPPORTUNISTE ET RÉPONSE HYBRIDE ONT RÉUSSI !")

if __name__ == "__main__":
    test_scenarios()
