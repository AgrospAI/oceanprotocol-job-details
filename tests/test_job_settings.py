from oceanprotocol_job_details.settings import JobSettings


class TestJobSettings:
    def test_job_settings_list_string_did(self, settings):
        assert len(settings.dids) == 1
        assert settings.dids[0].startswith("17feb69")

    def test_job_settings_list_did(self, config):
        config.update({"dids": ["test1", "test2"]})
        settings = JobSettings(**config)

        assert len(settings.dids) == 2
        assert settings.dids[0] == "test1"
        assert settings.dids[1] == "test2"

    def test_empty_dids(self, config):
        config.update({"dids": "[]"})
        settings = JobSettings(**config)

        assert len(settings.dids)
