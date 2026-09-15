import asyncio
import unittest

from event_stream import Session


class SessionRegressionTests(unittest.TestCase):
    def test_close_before_start_is_safe(self):
        async def scenario():
            session = Session()
            await session.close()
            await session.close()
            return session.active, session.cleanup_count

        self.assertEqual(asyncio.run(scenario()), (False, 0))


if __name__ == "__main__":
    unittest.main()
