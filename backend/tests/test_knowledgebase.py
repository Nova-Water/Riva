from app.tools.knowledgebase import reindex_knowledge_base, search_knowledge_base


def test_reindex_and_search_knowledge_base(tmp_path):
    nova_tech_dir = tmp_path / "nova-tech"
    nova_tech_dir.mkdir()
    (nova_tech_dir / "about.md").write_text(
        "Nova Tech Ltd is a Samoan-owned technology company offering CCTV installation and IT support."
    )
    for category in ["myska-pay", "novacore", "procedures"]:
        (tmp_path / category).mkdir()

    count = reindex_knowledge_base(tmp_path)
    assert count == 1

    results = search_knowledge_base("CCTV")
    assert len(results) >= 1
    assert results[0]["category"] == "nova-tech"


def test_search_knowledge_base_returns_empty_for_no_match(tmp_path):
    for category in ["nova-tech", "myska-pay", "novacore", "procedures"]:
        (tmp_path / category).mkdir()
    reindex_knowledge_base(tmp_path)
    results = search_knowledge_base("zzzznonexistenttermzzzz")
    assert results == []
