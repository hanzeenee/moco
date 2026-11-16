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
        for slug in ['sma-cross-ea', 'sma-cross-indicator']:
            item = RESOURCES[slug]
            self.programs[slug] = EAProgram.objects.create(code=item['program'], name=item['title'], program_type=item['type'])
            (Path(self.directory.name) / item['filename']).write_bytes(('private-ex5-' + slug).encode())
        response = self.client.post(reverse('utility-login'), json.dumps({'account_number': self.account.account_number}), content_type='application/json')
        self.client.defaults['HTTP_X_MOCONIX_LIBRARY_TOKEN'] = response.json()['tab_token']

    def items(self):
        return self.client.get(reverse('utility-library-data')).json()['items']

    def test_catalog_separates_two_release_types_and_exposes_only_ex5_attachments(self):
        items = self.items()
        self.assertEqual([(item['id'], item['type']) for item in items], [('sma-cross-ea', 'ea'), ('sma-cross-indicator', 'indicator')])
        self.assertNotIn(self.directory.name, json.dumps(items))
        self.assertNotIn('program', items[0])
        for item in items:
            self.assertTrue(item['filename'].endswith('.ex5'))
            self.assertNotIn('version', item)
            response = self.client.get(item['download_url'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b''.join(response.streaming_content), ('private-ex5-' + item['id']).encode())
            self.assertIn('attachment; filename=\"' + item['filename'] + '\"', response['Content-Disposition'])
            if item['id'].startswith('sma-cross-'):
                prefix = 'MOCO_EA_' if item['type'] == 'ea' else 'MOCO_indi_'
                self.assertTrue(item['filename'].startswith(prefix))
            self.assertIn('no-store', response['Cache-Control'])
        for name in ['MOCONIX_UTBot.mq5', 'MOCONIX_BreakoutMartingale.mq5', 'MoconixLicense.mqh', 'MOCO_EA_SMA_Cross.mq5', 'MOCO_indi_SMA_Cross.mq5', 'MoconixSMACrossEA.mqh', '../ut-bot', 'rsi-arrow']:
            self.assertEqual(self.client.get('/api/utilities/download/' + name + '/').status_code, 404)

    def test_disabled_wrong_kind_and_missing_binary_cannot_be_listed_or_downloaded(self):
        program = self.programs['sma-cross-indicator']
        for fields in [{'is_active': False}, {'is_active': True, 'program_type': 'ea'}]:
            for key, value in fields.items():
                setattr(program, key, value)
            program.save()
            self.assertEqual([item['id'] for item in self.items()], ['sma-cross-ea'])
            self.assertEqual(self.client.get(reverse('utility-download', args=['sma-cross-indicator'])).status_code, 404)
        program.program_type = 'indicator'
        program.save()
        (Path(self.directory.name) / RESOURCES['sma-cross-indicator']['filename']).unlink()
        self.assertEqual([item['id'] for item in self.items()], ['sma-cross-ea'])
        self.assertEqual(self.client.get(reverse('utility-download', args=['sma-cross-indicator'])).status_code, 404)

    def test_retired_releases_stay_unavailable_even_if_private_artifacts_remain(self):
        for slug, filename, code, kind in [
            ('breakout-martingale', 'MOCONIX_BreakoutMartingale.ex5', 'moconix-breakout-martingale-v1', 'ea'),
            ('ut-bot', 'MOCONIX_UTBot.ex5', 'moconix-utbot-v1', 'indicator'),
        ]:
            EAProgram.objects.create(code=code, name='Retired release', program_type=kind)
            (Path(self.directory.name) / filename).write_bytes(b'retired-private-ex5')
            self.assertNotIn(slug, RESOURCES)
            self.assertEqual(self.client.get(reverse('utility-download', args=[slug])).status_code, 404)
            self.assertEqual(self.client.get('/api/utilities/download/' + filename + '/').status_code, 404)
        self.assertEqual([item['id'] for item in self.items()], ['sma-cross-ea', 'sma-cross-indicator'])

    def test_all_downloads_require_current_registered_session(self):
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
