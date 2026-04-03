import time


def test_add_and_get_all(store):
    store.add("hello")
    store.add("world")
    entries = store.get_all()
    contents = [e["content"] for e in entries]
    assert "hello" in contents
    assert "world" in contents


def test_get_all_order_newest_first(store):
    store.add("first")
    store.add("second")
    entries = store.get_all()
    assert entries[0]["content"] == "second"
    assert entries[1]["content"] == "first"


def test_add_deduplication_moves_to_top(store):
    store.add("first")
    store.add("second")
    store.add("first")  # re-add — should move to top
    entries = store.get_all()
    assert entries[0]["content"] == "first"


def test_add_empty_content_is_ignored(store):
    result = store.add("")
    assert result is None
    assert store.get_all() == []


def test_add_whitespace_only_is_ignored(store):
    result = store.add("   \n\t  ")
    assert result is None
    assert store.get_all() == []


def test_add_returns_id(store):
    entry_id = store.add("hello")
    assert isinstance(entry_id, int)
    assert entry_id > 0


def test_get_all_returns_correct_fields(store):
    store.add("hello")
    entries = store.get_all()
    assert len(entries) == 1
    entry = entries[0]
    assert entry["content"] == "hello"
    assert entry["content_type"] == "text"
    assert "id" in entry
    assert "created_at" in entry
    assert entry["pinned"] is False


def test_get_all_limit(store):
    for i in range(10):
        store.add(f"entry {i}")
    entries = store.get_all(limit=5)
    assert len(entries) == 5


def test_delete(store):
    entry_id = store.add("to delete")
    store.delete(entry_id)
    assert store.get_all() == []


def test_delete_only_removes_target(store):
    store.add("keep")
    entry_id = store.add("remove")
    store.delete(entry_id)
    entries = store.get_all()
    assert len(entries) == 1
    assert entries[0]["content"] == "keep"


def test_clear_removes_unpinned(store):
    store.add("one")
    store.add("two")
    store.clear()
    assert store.get_all() == []


def test_clear_keeps_pinned(store):
    entry_id = store.add("pinned entry")
    store.connection.execute(
        "UPDATE entries SET pinned = 1 WHERE id = ?", (entry_id,)
    )
    store.connection.commit()
    store.add("unpinned entry")

    store.clear()

    entries = store.get_all()
    assert len(entries) == 1
    assert entries[0]["content"] == "pinned entry"
    assert entries[0]["pinned"] is True
