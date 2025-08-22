from bulletin_builder.app_core.importer import parse_announcements_csv

def test_parse_announcements_csv_synonyms_bom_semicolon():
    csv_text = "\ufeffSubject;Message;URL;CTA\n" \
               "Title A;Body A;https://x.test;Read more\n" \
               "Title B;Body B;;\n" \
               ";;https://y.test;\n"
    rows = parse_announcements_csv(csv_text)
    assert len(rows) == 3
    assert rows[0] == {
        "title": "Title A",
        "body": "Body A",
        "link": "https://x.test",
        "link_text": "Read more",
    }
    assert rows[1]["title"] == "Title B"
    assert rows[1]["body"] == "Body B"
    assert rows[2]["link"] == "https://y.test"
    assert rows[2]["link_text"] == "Learn more"
