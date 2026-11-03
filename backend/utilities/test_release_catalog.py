import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import EAProgram, UtilityAccessAccount
from .resources import RESOURCES


@override_settings(SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=['testserver'])
class PublishedReleaseTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        settings = override_settings(MOCONIX_UTILITY_DOWNLOAD_DIR=self.directory.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.account = UtilityAccessAccount.objects.create(account_number='77112233')
        self.programs = {}
        for slug in ['breakout-martingale', 'ut-bot']:
            item = RESOURCES[slug]
            self.programs[slug] = EAProgram.objects.create(code=item['program'], name=item['title'], program_type=item['type'])
            (Path(self.directory.name) / item['filename']).write_bytes(('private-ex5-' + slug).encode())
        self.client.post(reverse('utility-login'), json.dumps({'account_number': self.account.account_number}), content_type='application/json')

    def items(self):
        return self.client.get(reverse('utility-library-data')).json()['items']

    def test_catalog_separates_two_release_types_and_exposes_only_ex5_attachments(self):
        items = self.items()
        self.assertEqual([(item['id'], item['type']) for item in items], [('breakout-martingale', 'ea'), ('ut-bot', 'indicator')])
        self.assertNotIn(self.directory.name, json.dumps(items))
        self.assertNotIn('program', items[0])
        for item in items:
            self.assertTrue(item['filename'].endswith('.ex5'))
            self.assertNotIn('version', item)
            response = self.client.get(item['download_url'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b''.join(response.streaming_content), ('private-ex5-' + item['id']).encode())
            self.assertIn('attachment;', response['Content-Disposition'])
            self.assertIn('no-store', response['Cache-Control'])
        for name in ['MOCONIX_UTBot.mq5', 'MOCONIX_BreakoutMartingale.mq5', 'MoconixLicense.mqh', '../ut-bot', 'rsi-arrow']:
            self.assertEqual(self.client.get('/api/utilities/download/' + name + '/').status_code, 404)

    def test_disabled_wrong_kind_and_missing_binary_cannot_be_listed_or_downloaded(self):
        program = self.programs['ut-bot']
        for fields in [{'is_active': False}, {'is_active': True, 'program_type': 'ea'}]:
            for key, value in fields.items():
                setattr(program, key, value)
            program.save()
            self.assertEqual([item['id'] for item in self.items()], ['breakout-martingale'])
            self.assertEqual(self.client.get(reverse('utility-download', args=['ut-bot'])).status_code, 404)
        program.program_type = 'indicator'
        program.save()
        (Path(self.directory.name) / RESOURCES['ut-bot']['filename']).unlink()
        self.assertEqual([item['id'] for item in self.items()], ['breakout-martingale'])
        self.assertEqual(self.client.get(reverse('utility-download', args=['ut-bot'])).status_code, 404)

    def test_both_downloads_require_current_registered_session(self):
        for mode in ['disabled', 'logged-out']:
            if mode == 'disabled':
                self.account.is_active = False
                self.account.save()
            else:
                self.account.is_active = True
                self.account.save()
                self.client.post(reverse('utility-logout'))
            self.assertEqual(self.client.get(reverse('utility-library-data')).status_code, 401)
            for slug in self.programs:
                self.assertEqual(self.client.get(reverse('utility-download', args=[slug])).status_code, 401)
