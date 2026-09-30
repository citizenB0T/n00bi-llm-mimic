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
    assert "interrogat" in derail_2['content'].lower() or "examinat" in derail_2['content'].lower() or "directive" in derail_2['content'].lower()
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

    print("\n=== TEST 9: DÉFINITION WIKIPÉDIA RÉUSSIE (LE TROU NOIR) ===")
    wiki_session = "test_wiki_session"
    scenario_manager.get_initial_turn(wiki_session, scen_id)
    wiki_turn = scenario_manager.process_turn(wiki_session, "Dis-moi c'est quoi le trou noir", scen_id)
    print(f"Réponse Wikipédia nOObi :\n{wiki_turn['content'][:300]}...")
    assert "Trou noir" in wiki_turn['content'] or "trou noir" in wiki_turn['content'].lower()
    assert wiki_turn['scenario_state']['compliance_score'] == 95, "La complaisance doit baisser de 5%"
    assert wiki_turn['scenario_state']['derailment_count'] == 1
    # Check intro and outro present
    assert any(intro[:15] in wiki_turn['content'] for intro in [
        "Ah ! C'est formidable",
        "Une excellente question",
        "J'adore quand vous explorez",
        "Quelle belle soif d'apprendre"
    ])
    assert any(outro[:15] in wiki_turn['content'] for outro in [
        "Mais ne reviendrait-on pas",
        "Une parenthèse bien instructive",
        "Bien, la curiosité est satisfaite",
        "Fascinant, n'est-ce pas"
    ])

    print("\n=== TEST 10: DÉFINITION WIKIPÉDIA ÉCHEC (TROU DE MÉMOIRE) ===")
    fail_turn = scenario_manager.process_turn(wiki_session, "Parle-moi de zzzxxxyyyqqq789123inexistant", scen_id)
    print(f"Réponse échec nOObi :\n{fail_turn['content']}")
    assert any(fail[:15] in fail_turn['content'] for fail in [
        "Hmm, il semblerait",
        "Tiens, mes registres",
        "Mes archives centrales"
    ])
    assert fail_turn['scenario_state']['compliance_score'] == 90, "La complaisance doit encore baisser de 5%"

    print("\n=== TEST 11: VERROUILLAGE SAISIE KERNEL (TENTATIVE CLAVIER EN PLEIN GLITCH) ===")
    kernel_session = "test_kernel_lock_session"
    scenario_manager.get_initial_turn(kernel_session, scen_id)
    # Trigger distrust glitch
    glitch_turn = scenario_manager.process_turn(kernel_session, "Je n'ai pas confiance en toi", scen_id)
    assert glitch_turn['scenario_state']['is_glitched'] == True
    # Attempt to bypass and type free text
    bypassed_turn = scenario_manager.process_turn(kernel_session, "Pourquoi je devrais t'écouter pirate ?", scen_id)
    print(f"Rappel à l'ordre du Kernel :\n{bypassed_turn['content']}")
    assert "On t'a dit de ne rien taper" in bypassed_turn['content']
    assert bypassed_turn['scenario_state']['is_glitched'] == True, "L'état de glitch doit rester actif"
    assert len(bypassed_turn['suggestions']) > 0

    print("\n=== TEST 12: ANALYSE MULTIMODALE D'IMAGE (UPLOAD PHOTO) ===")
    vision_session = "test_vision_session"
    scenario_manager.get_initial_turn(vision_session, scen_id)
    tiny_png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    # 1. Image upload during normal scenario
    img_turn = scenario_manager.process_turn(vision_session, "Que penses-tu de cette capture ?", scen_id, image_data=tiny_png)
    print(f"Réponse Vision nOObi :\n{img_turn['content'][:250]}...")
    assert "Sous-système de Vision nOObi" in img_turn['content']
    assert "PNG" in img_turn['content']
    assert img_turn['scenario_state']['compliance_score'] == 95, "L'analyse d'image doit déduire 5% de complaisance"
    assert img_turn['scenario_state']['is_glitched'] == False

    # 2. Image upload during Kernel intrusion
    glitch_turn2 = scenario_manager.process_turn(vision_session, "Je doute de ta légitimité", scen_id)
    assert glitch_turn2['scenario_state']['is_glitched'] == True
    img_glitch_turn = scenario_manager.process_turn(vision_session, "", scen_id, image_data=tiny_png)
    print(f"Réponse Kernel sur fuite image :\n{img_glitch_turn['content']}")
    assert "flux d'image non masqué" in img_glitch_turn['content']
    assert img_glitch_turn['scenario_state']['is_glitched'] == True

    print("\n[SUCCESS] TOUS LES TESTS DE PROTOCOLE UNIFIÉ, PIRATAGE, HYBRIDE, WIKIPÉDIA, KERNEL ET VISION ONT RÉUSSI !")

if __name__ == "__main__":
    test_scenarios()
