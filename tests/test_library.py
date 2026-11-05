"""Behaviour of the library scenario."""

from fastapi.testclient import TestClient

from api import app
from engine.scenario_manager import describe, load_scenarios
from scenarios.library.books import Book
from scenarios.library.members import Member

URL = "/api/scenarios/library"


def act(client, action, target):
    response = client.post(f"{URL}/actions/{action}", json={"target": target})
    assert response.status_code == 200, response.text
    return response.json()


def calls(result):
    return [step["method"] for step in result["steps"] if step["kind"] == "call"]


def test_two_actor_columns_and_four_actions():
    library = load_scenarios()["library"]
    data = describe(library, library.build())
    assert [panel["title"] for panel in data["panels"]] == ["Member", "Library"]
    assert [action["id"] for action in data["actions"]] == ["borrow", "return", "renew", "check"]


def test_books_start_available():
    with TestClient(app) as client:
        state = client.post(f"{URL}/reset").json()
        for label in ("BOOK001", "BOOK002"):
            assert state[label] == {"name": state[label]["name"], "borrowed_by": None,
                                    "renewals": 0, "available": True}


def test_borrowing_one_book_leaves_the_other_alone():
    member, book_a, book_b = Member("Member"), Book("Book A"), Book("Book B")
    assert book_a.borrow(member) is True
    assert book_a.available is False
    assert book_b.available is True and book_b.borrowed_by is None


def test_borrow_runs_through_library_to_the_book():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        result = act(client, "borrow", "BOOK001")
        assert result["result"] is True
        assert calls(result) == ["Member.borrow", "Library.lend", "Book.borrow", "Book.available"]
        assert result["after"]["BOOK001"]["borrowed_by"] == "member"
        assert result["after"]["BOOK001"]["available"] is False
        assert result["after"]["BOOK002"]["available"] is True


def test_a_book_on_loan_cannot_be_borrowed_again():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        act(client, "borrow", "BOOK001")
        result = act(client, "borrow", "BOOK001")
        assert result["result"] is False
        assert result["summary"]["story"] == "Member A cannot borrow Book A because it is already borrowed."
        assert result["before"] == result["after"]


def test_a_loan_can_be_renewed_once():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        act(client, "borrow", "BOOK001")
        first = act(client, "renew", "BOOK001")
        assert first["result"] is True and first["after"]["BOOK001"]["renewals"] == 1
        second = act(client, "renew", "BOOK001")
        assert second["result"] is False and second["after"]["BOOK001"]["renewals"] == 1


def test_returning_clears_the_loan():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        act(client, "borrow", "BOOK001")
        act(client, "renew", "BOOK001")
        after = act(client, "return", "BOOK001")["after"]["BOOK001"]
        assert after["borrowed_by"] is None and after["renewals"] == 0 and after["available"] is True


def test_returning_a_book_that_is_not_borrowed_changes_nothing():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        result = act(client, "return", "BOOK002")
        assert result["result"] is False
        assert result["before"] == result["after"]


def test_check_answers_with_a_string_through_the_property():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        assert act(client, "check", "BOOK001")["summary"]["story"] == "City Library reports that Book A is available."
        act(client, "borrow", "BOOK001")
        result = act(client, "check", "BOOK001")
        assert result["result"] == "On loan"
        assert result["summary"]["story"] == "City Library reports that Book A is on loan."
        routes = [step["route"] for step in result["steps"] if step["kind"] == "call"]
        assert {"from": "Library.check", "to": "Book.available", "kind": "property"}.items() <= routes[-1].items()


def test_state_is_kept_per_scenario_and_reset_only_affects_the_active_one():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        act(client, "borrow", "BOOK002")
        client.post("/api/scenarios/cybersecurity/actions/malware", json={"target": "DEV001"})

        assert client.get(URL).json()["state"]["BOOK002"]["available"] is False
        client.post("/api/scenarios/cybersecurity/reset")
        assert client.get(URL).json()["state"]["BOOK002"]["available"] is False
        assert client.post(f"{URL}/reset").json()["BOOK002"]["available"] is True
