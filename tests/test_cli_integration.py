import subprocess
import json
import pytest


class TestCLIIntegration:
    def test_cli_detect_rodne_cislo(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "detect", "Jan Novák, RČ: 8001011234"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "rodne_cislo" in result.stdout or "RODNE_CISLO" in result.stdout
        
    def test_cli_detect_ico(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "detect", "IČO: 25596641"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "ico" in result.stdout.lower() or "25596641" in result.stdout

    def test_cli_detect_from_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("Jan Novák, RČ: 8001011234")
        
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "detect", "--file", str(test_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "rodne_cislo" in result.stdout.lower() or "8001011234" in result.stdout

    def test_cli_detect_json_output(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "detect", "IČO: 25596641", "--format", "json"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        output = json.loads(result.stdout)
        assert "findings" in output
        assert len(output["findings"]) >= 1

    def test_cli_validate_rodne_cislo_valid(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "validate", "8001011234", "--detector", "rodne_cislo"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "VALID" in result.stdout or "True" in result.stdout

    def test_cli_validate_rodne_cislo_invalid(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "validate", "invalid_number", "--detector", "rodne_cislo"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "INVALID" in result.stdout or "False" in result.stdout

    def test_cli_validate_detector_not_found(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "validate", "test", "--detector", "nonexistent"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "not found" in result.stderr

    def test_cli_list_detectors(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "list-detectors"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "rodne_cislo" in result.stdout
        assert "ico" in result.stdout
        assert "dic" in result.stdout

    def test_cli_list_detectors_json_format(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "list-detectors", "--format", "json"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        output = json.loads(result.stdout)
        assert isinstance(output, list)
        assert len(output) >= 6
        
        detector_names = {d["name"] for d in output}
        assert "rodne_cislo" in detector_names
        assert "ico" in detector_names

    def test_cli_output_to_file(self, tmp_path):
        output_file = tmp_path / "output.json"
        
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "detect", "IČO: 25596641", "--format", "json", "--output", str(output_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert output_file.exists()
        
        content = json.loads(output_file.read_text())
        assert "findings" in content

    def test_cli_regions_parameter(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "detect", "RČ: 8001011234", "--regions", "cz"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
    def test_cli_no_text_provided(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "detect"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        
    def test_cli_help(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "detect" in result.stdout
        assert "validate" in result.stdout
        assert "list-detectors" in result.stdout

    def test_cli_detect_help(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "detect", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "--file" in result.stdout
        assert "--regions" in result.stdout
        assert "--format" in result.stdout

    def test_cli_validate_help(self):
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "validate", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "--detector" in result.stdout
        assert "--regions" in result.stdout

    def test_cli_multiple_identifiers(self):
        text = "RČ: 8001011234, IČO: 25596641"
        result = subprocess.run(
            ["python", "-m", "cpg.cli", "detect", text, "--format", "json"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        output = json.loads(result.stdout)
        assert len(output["findings"]) >= 2