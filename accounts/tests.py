from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse


@override_settings(CACHES={
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
    'select2': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
})
class LogoutTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        user = get_user_model().objects.create_user(username='logout-test')
        self.client.force_login(user)

    def test_get_does_not_log_out(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)
        self.assertIn(SESSION_KEY, self.client.session)

    def test_navbar_post_logs_out_with_csrf(self):
        page = self.client.get(reverse('login'))
        self.assertContains(page, 'method="post" action="%s"' % reverse('logout'))
        self.assertEqual(self.client.post(reverse('logout')).status_code, 403)
        response = self.client.post(
            reverse('logout'),
            HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value,
        )
        self.assertRedirects(response, reverse('login'), fetch_redirect_response=False)
        self.assertNotIn(SESSION_KEY, self.client.session)
