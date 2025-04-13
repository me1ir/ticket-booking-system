from django.test import TestCase
from django.urls import reverse
from tickets.models import Movie
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date


class ViewsTest(TestCase):
    def setUp(self):
        self.poster = SimpleUploadedFile(
            name='test_poster.jpg',
            content=b'smalljpgcontent',
            content_type='image/jpeg'
        )
        self.movie = Movie.objects.create(
            title="Avatar",
            description="An epic science fiction film.",
            director="James Cameron",
            actors="Sam Worthington, Zoe Saldana",
            release_date=date(2022, 12, 15),
            duration=162,
            rating=8.2,
            vote_count=1000,
            poster=self.poster
        )

    def test_home_view_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.movie.title)

    def test_movie_detail_view(self):
        response = self.client.get(reverse('movie_detail', args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.movie.title)
        self.assertContains(response, self.movie.description)
