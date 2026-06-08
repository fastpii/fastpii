import pytest
from fastapi.testclient import TestClient

from cpg.integrations.fastapi import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestFastAPIIntegration:
    def test_detect_endpoint_rodne_cislo(self, client):
        response = client.post("/detect", json={
            "text": "Jan Novák, RČ: 8001011234",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["text"] == "Jan Novák, RČ: 8001011234"
        assert len(data["findings"]) >= 1
        assert data["findings"][0]["type"] == "rodne_cislo"
        assert "800101" in data["findings"][0]["value"]
        assert data["processing_time_ms"] >= 0

    def test_detect_endpoint_ico(self, client):
        response = client.post("/detect", json={
            "text": "Company IČO: 25596641",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["findings"]) >= 1
        assert data["findings"][0]["type"] == "ico"
        assert data["findings"][0]["value"] == "25596641"

    def test_detect_endpoint_multiple_identifiers(self, client):
        response = client.post("/detect", json={
            "text": "Jan Novák, RČ: 8001011234, IČO: 25596641",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["findings"]) >= 2
        types = {f["type"] for f in data["findings"]}
        assert "rodne_cislo" in types
        assert "ico" in types

    def test_detect_endpoint_specific_detector(self, client):
        response = client.post("/detect", json={
            "text": "IČO: 25596641, RČ: 8001011234",
            "regions": ["cz"],
            "detector_names": ["ico"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["findings"]) >= 1
        assert all(f["type"] == "ico" for f in data["findings"])

    def test_detect_endpoint_no_pii(self, client):
        response = client.post("/detect", json={
            "text": "Hello world, no PII here",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["findings"]) == 0
        assert len(data["detector_names"]) == 0

    def test_validate_endpoint_rodne_cislo_valid(self, client):
        response = client.post("/validate", json={
            "value": "8001011234",
            "detector_name": "rodne_cislo",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["detector"] == "rodne_cislo"
        assert data["value"] == "8001011234"
        assert data["is_valid"] is True
        assert "birth_date" in data["metadata"]
        assert "gender" in data["metadata"]

    def test_validate_endpoint_ico_valid(self, client):
        response = client.post("/validate", json={
            "value": "25596641",
            "detector_name": "ico",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_valid"] is True
        assert data["metadata"]["checksum_valid"] is True

    def test_validate_endpoint_invalid(self, client):
        response = client.post("/validate", json={
            "value": "invalid_identifier",
            "detector_name": "rodne_cislo",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_valid"] is False

    def test_validate_endpoint_nonexistent_detector(self, client):
        response = client.post("/validate", json={
            "value": "8001011234",
            "detector_name": "nonexistent_detector",
            "regions": ["cz"]
        })
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_list_detectors_endpoint(self, client):
        response = client.get("/detectors", params={"regions": ["cz"]})
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 6
        
        detector_names = {d["name"] for d in data}
        assert "rodne_cislo" in detector_names
        assert "ico" in detector_names
        assert "dic" in detector_names
        assert "bank_account" in detector_names
        assert "postal_code" in detector_names
        assert "phone" in detector_names

    def test_health_endpoint(self, client):
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_detect_with_all_czech_detectors(self, client):
        text = """
        Jan Novák, RČ: 8001011234
        Firma s.r.o., IČO: 25596641
        DIČ: CZ25596641
        Účet: 19-2000145399/0800
        PSČ: 110 00
        Tel: +420 777 123 456
        """
        
        response = client.post("/detect", json={
            "text": text.strip(),
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["findings"]) >= 6
        
        types = {f["type"] for f in data["findings"]}
        assert "rodne_cislo" in types
        assert "ico" in types
        assert "dic" in types
        assert "bank_account" in types
        assert "postal_code" in types
        assert "phone" in types

    def test_metadata_extraction_rodne_cislo(self, client):
        response = client.post("/detect", json={
            "text": "RČ: 8001011234",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        finding = data["findings"][0]
        assert "birth_date" in finding["metadata"]
        assert "gender" in finding["metadata"]
        assert "article_9" in finding["metadata"]
        assert finding["metadata"]["gender"] in ["male", "female"]

    def test_metadata_extraction_bank_account(self, client):
        response = client.post("/detect", json={
            "text": "Účet: 19-2000145399/0800",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        finding = data["findings"][0]
        assert "bank_code" in finding["metadata"]
        assert finding["metadata"]["bank_code"] == "0800"

    def test_metadata_extraction_phone(self, client):
        response = client.post("/detect", json={
            "text": "Tel: +420 777 123 456",
            "regions": ["cz"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        finding = data["findings"][0]
        assert "phone_type" in finding["metadata"]
        assert "operator" in finding["metadata"]
        assert finding["metadata"]["phone_type"] in ["mobile", "landline"]