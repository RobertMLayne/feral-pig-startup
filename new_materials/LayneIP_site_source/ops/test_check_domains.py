import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('check_domains', Path(__file__).with_name('check_domains.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class PublicDomainCheckTests(unittest.TestCase):
    def test_txt_segments_and_exact_owner_are_checked(self):
        name = '_openai-site-verification.layneip.com'
        payload = {'Status': 0, 'Answer': [
            {'name': name + '.', 'type': 16, 'data': '"openai-site-" "verification=value"'},
            {'name': 'other.layneip.com.', 'type': 16, 'data': '"wrong"'}]}
        result = checker.assess_dns(name, 'TXT', {'openai-site-verification=value'}, payload)
        self.assertEqual(result['status'], 'match')
        self.assertEqual(result['observed'], ['openai-site-verification=value'])

    def test_dns_failure_is_not_reported_as_missing(self):
        self.assertEqual(checker.assess_dns('layneip.tech', 'A', {'162.159.143.30'}, {'Status': 2})['status'], 'resolver_error')
        self.assertEqual(checker.assess_dns('layneip.tech', 'A', {'162.159.143.30'}, {'Status': 0})['status'], 'missing')
        result = checker.assess_dns('layneip.com', 'A', {'162.159.143.30'},
                                   {'Status': 0, 'Answer': [{'name': 'layneip.com', 'type': 1, 'data': '104.21.64.115'}]})
        self.assertEqual(result['status'], 'different_answers')
        self.assertIn('proxied', result['note'])
        result = checker.assess_dns('layneip.com', 'A', {'162.159.143.30'},
                                   {'Status': 0, 'Answer': [
                                       {'name': 'layneip.com', 'type': 1, 'data': '162.159.143.30'},
                                       {'name': 'layneip.com', 'type': 1, 'data': '192.0.2.1'}]})
        self.assertEqual(result['status'], 'different_answers')

    def test_redirect_checks_path_and_query_separately(self):
        source = 'https://www.layneip.com/services.html?source=domain-check'
        result = checker.assess_http(source, 301, 'https://layneip.com/s?source=domain-check')
        self.assertEqual(result['status'], 'other_redirect')
        self.assertFalse(result['path_preserved'])
        self.assertTrue(result['query_preserved'])
        self.assertEqual(checker.assess_http(source, 301, 'https://layneip.com/services.html?source=domain-check')['status'], 'canonical_redirect')
        self.assertEqual(checker.assess_http(source, 301, 'https://layneip.com/services.html')['status'], 'other_redirect')

    def test_unexpected_ipv6_answers_cannot_pass_launch_checks(self):
        good = checker.assess_dns('layneip.com', 'AAAA', set(), {'Status': 0, 'Answer': []})
        bad = checker.assess_dns('layneip.com', 'AAAA', set(), {'Status': 0, 'Answer': [
            {'name': 'layneip.com', 'type': 28, 'data': '2001:db8::1'}]})
        self.assertEqual(good['status'], 'match')
        self.assertEqual(bad['status'], 'different_answers')

    def test_access_errors_and_redirect_loops_are_visible(self):
        source = 'https://layneip.com/services.html?source=domain-check'
        self.assertEqual(checker.assess_http(source, 301, source)['status'], 'redirect_loop')
        self.assertEqual(checker.assess_http(source, 403, body='Cloudflare error 1014')['cloudflare_error'], '1014')
        self.assertEqual(checker.assess_http(source, 403)['status'], 'access_restricted_or_host_error')


if __name__ == '__main__':
    unittest.main()
