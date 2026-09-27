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

    print("\n=== TEST 7: AVANCEMENT DU TUTORIEL (EXPÉRIENCE IA) ===")
    advance_turn = scenario_manager.process_turn(session_id, "Oui, je les utilise très régulièrement !", scen_id)
    print(f"Réaction & Étape suivante :\n{advance_turn['content'][:150]}...")
    assert advance_turn['scenario_state']['step_id'] == "explication_interaction"

    print("\n=== TEST 8: AVANCEMENT VERS LE TEST N°1 (PROMPTING) ===")
    step_prompting = scenario_manager.process_turn(session_id, "Je clique sur cette puce pour tester le bouton !", scen_id)
    assert step_prompting['scenario_state']['step_id'] == "test_1_prompting"

    print("\n=== TEST 9: AVANCEMENT VERS LE TEST N°2 (ESPRIT CRITIQUE) ===")
    step_critique = scenario_manager.process_turn(session_id, "Explique-moi les API comme si j'avais 5 ans (ELI5)", scen_id)
    assert step_critique['scenario_state']['step_id'] == "test_2_esprit_critique"

    print("\n=== TEST 10: AVANCEMENT VERS LE TEST N°3 (MÉTHODE) ===")
    step_collab = scenario_manager.process_turn(session_id, "C'est faux ! Quicksort a été inventé par Tony Hoare vers 1960", scen_id)
    assert step_collab['scenario_state']['step_id'] == "test_3_collaboration"

    print("\n=== TEST 11: CONCLUSION DU TUTORIEL ===")
    step_conclusion = scenario_manager.process_turn(session_id, "Découper le projet en sous-étapes et valider chaque étape", scen_id)
    assert step_conclusion['scenario_state']['step_id'] == "conclusion"
    assert step_conclusion['scenario_state']['is_finished'] == True

    print("\n[SUCCESS] TOUS LES TESTS D'ÉCHO CONTEXTUEL, RECADRAGE, GLITCH ET PARCOURS TUTORIEL ONT RÉUSSI !")

if __name__ == "__main__":
    test_scenarios()
