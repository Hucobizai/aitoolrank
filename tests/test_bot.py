import unittest
from bot.research import parse_feed
class TestFeed(unittest.TestCase):
    def test_atom(self):
        xml=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>x1</id><title>Release 1</title><link href="https://example.com/release"/><updated>2026-10-15</updated></entry></feed>'
        results=parse_feed(xml, {'name':'test','category':'Vibe Coding'})
        self.assertEqual(len(results),1)
        self.assertEqual(results[0]['status'],'pending')
        self.assertEqual(results[0]['title'],'Release 1')
    def test_reject_insecure_link(self):
        xml=b'<rss><channel><item><title>x</title><link>http://example.com</link></item></channel></rss>'
        self.assertEqual(parse_feed(xml, {'name':'test','category':'AI Agents'}),[])
if __name__=='__main__': unittest.main()
