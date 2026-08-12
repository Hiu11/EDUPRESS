import pathlib
import unittest


SERVER_ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = SERVER_ROOT.parent


class MigrationSetupTest(unittest.TestCase):
    def test_backend_startup_does_not_create_schema(self):
        main_source = (SERVER_ROOT / "app" / "main.py").read_text(encoding="utf-8")
        init_source = (SERVER_ROOT / "app" / "db" / "init_db.py").read_text(encoding="utf-8")

        self.assertNotIn("create_all", main_source)
        self.assertNotIn("init_db()", main_source)
        self.assertNotIn("create_all", init_source)
        self.assertNotIn("ALTER TABLE", init_source)

    def test_alembic_files_are_present(self):
        self.assertTrue((SERVER_ROOT / "alembic.ini").exists())
        self.assertTrue((SERVER_ROOT / "migrations" / "env.py").exists())
        versions = list((SERVER_ROOT / "migrations" / "versions").glob("*.py"))

        self.assertTrue(versions)

    def test_deploy_and_docs_run_migrations_explicitly(self):
        dockerfile = (SERVER_ROOT / "Dockerfile").read_text(encoding="utf-8")
        backend_readme = (SERVER_ROOT / "README.md").read_text(encoding="utf-8")
        root_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        for content in (dockerfile, backend_readme, root_readme):
            self.assertIn("alembic upgrade head", content)


if __name__ == "__main__":
    unittest.main()
