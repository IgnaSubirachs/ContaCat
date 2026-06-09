import json
import unittest
from unittest.mock import MagicMock, patch

from app.domain.system_status import _check_java_backend


class SystemStatusTest(unittest.TestCase):
    @patch("app.domain.system_status.urlopen")
    @patch("app.domain.system_status.socket.create_connection")
    def test_java_backend_requires_healthy_actuator_status(self, mock_socket, mock_urlopen):
        mock_socket.return_value.__enter__.return_value = object()
        response = MagicMock()
        response.read.return_value = json.dumps({"status": "UP"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = response

        ok, detail = _check_java_backend()

        self.assertTrue(ok)
        self.assertEqual(detail, "Backend comptable disponible")

    @patch("app.domain.system_status.urlopen")
    @patch("app.domain.system_status.socket.create_connection")
    def test_java_backend_is_degraded_when_health_endpoint_fails(self, mock_socket, mock_urlopen):
        mock_socket.return_value.__enter__.return_value = object()
        mock_urlopen.side_effect = RuntimeError("boom")

        ok, detail = _check_java_backend()

        self.assertFalse(ok)
        self.assertEqual(detail, "Backend Java respon per port pero no esta operatiu")


if __name__ == "__main__":
    unittest.main()
