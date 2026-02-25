class TestFiles:
    def test_files_detection(self, job_details):
        """Verifies file structure detection logic."""
        assert len(job_details.files) == 1
        file = job_details.files[0]
        assert file.did.startswith("17feb697")
        assert file.ddo.exists()

    def test_yielding_files_iterator(self, job_details):
        """Tests the inputs() generator yields (did, path) tuples."""
        files = list(job_details.inputs())
        assert len(files) == 1
        did, path = files[0]
        assert isinstance(did, str)
        assert path.is_file()
