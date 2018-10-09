from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from freezegun import freeze_time
from model_mommy import mommy
from mock import patch, Mock

from moviedb_rest_api.models import Movie, Comment


@freeze_time("2018-10-05")
class TestMoviesViewPost(TestCase):
	def setUp(self):
		self.title = 'terminator'
		self.client = Client()
		requests_get_patcher = patch('moviedb_rest_api.views.requests.get')
		self.omdb_get_patch = requests_get_patcher.start()
		self.addCleanup(requests_get_patcher.stop)
		self.omdb_data = {
			'Title': self.title.title(),
			'Year': '2001',
			'Released': '01 Apr 2001'
		}
		self.excepted_data = {
			'movie_id': 1,
			'title': 'Terminator',
			'additional_data': self.omdb_data,
			'created_at': '2018-10-05T00:00:00Z'
		}
		self.omdb_get_patch.return_value = Mock(
			status_code=200,
			json=Mock(return_value=self.omdb_data)
		)

	def test_post_valid_new_movie_title_create_record(self):
		with self.assertNumQueries(2):
			response = self.client.post(reverse('movies'), data={'movie_title': self.title})
		json_data = response.json()

		try:
			movie = Movie.objects.get(id=json_data['movie_id'])
		except Movie.DoesNotExist:
			assert False, 'Movie object not created in the database'
		else:
			self.excepted_data['movie_id'] = movie.id
		self.assertEqual(response.status_code, 201)
		self.assertDictEqual(json_data, self.excepted_data)
		self.assertEqual(self.omdb_get_patch.call_count, 1)

	def test_post_movie_not_found(self):
		self.omdb_get_patch.return_value = Mock(
			status_code=200,
			json=Mock(return_value={'Response': 'False', 'Error': 'Movie not found!'})
		)
		with self.assertNumQueries(1):
			response = self.client.post(reverse('movies'), data={'movie_title': 'adsczx'})
		self.assertEqual(response.status_code, 200)
		self.assertDictEqual(response.json(), {'OMDB_Error': 'Movie not found!'})

	def test_post_invalid_api_key(self):
		self.omdb_get_patch.return_value = Mock(
			status_code=401,
			json=Mock(return_value={'Response': 'False', 'Error': 'Invalid API key!'})
		)
		with self.assertNumQueries(1):
			response = self.client.post(reverse('movies'), data={'movie_title': self.title})
		self.assertEqual(response.status_code, 200)
		self.assertDictEqual(response.json(), {'OMDB_Error': 'Invalid API key!'})

	def test_post_valid_new_movie_title_get_record(self):
		movie = mommy.make(Movie, id=1, title=self.title.title(), additional_data=self.omdb_data)
		with self.assertNumQueries(1):
			response = self.client.post(reverse('movies'), data={'movie_title': self.title})
		json_data = response.json()

		self.assertEqual(response.status_code, 200)
		self.assertDictEqual(json_data, self.excepted_data)
		self.assertEqual(self.omdb_get_patch.call_count, 0)
		self.assertEqual(json_data['movie_id'], movie.id)

	def test_post_no_movie_title(self):
		with self.assertNumQueries(0):
			response = self.client.post(reverse('movies'), data={})

		self.assertEqual(response.status_code, 400)
		self.assertDictEqual(response.json(), {})


@freeze_time("2018-10-05")
class TestMoviesViewGet(TestCase):

	def setUp(self):
		self.client = Client()

	def test_get_movies_no_records(self):
		with self.assertNumQueries(1):
			response = self.client.get(reverse('movies'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), [])

	def test_get_movies(self):
		movie_1 = mommy.make(
			Movie,
			id=1, title='Star Wars I: The Phantom Menace in the Playroom', additional_data={'Year': '2012'}
		)
		movie_2 = mommy.make(Movie, id=2, title='Robot Chicken: Star Wars III', additional_data={'Year': '2010'})
		movie_3 = mommy.make(Movie, id=3, title='Star Wars: Episode IV - A New Hope', additional_data={'Year': '1977'})
		with self.assertNumQueries(1):
			response = self.client.get(reverse('movies'))
		json_data = response.json()

		self.assertEqual(response.status_code, 200)
		excepted_data = [{
			'movie_id': 1,
			'title': 'Star Wars I: The Phantom Menace in the Playroom',
			'additional_data': {'Year': '2012'},
			'created_at': '2018-10-05T00:00:00Z'
		}, {
			'movie_id': 2,
			'title': 'Robot Chicken: Star Wars III',
			'additional_data': {'Year': '2010'},
			'created_at': '2018-10-05T00:00:00Z'
		}, {
			'movie_id': 3,
			'title': 'Star Wars: Episode IV - A New Hope',
			'additional_data': {'Year': '1977'},
			'created_at': '2018-10-05T00:00:00Z'
		}]
		for i, movie_data in enumerate(excepted_data):
			self.assertDictEqual(movie_data, json_data[i])


@freeze_time("2018-10-05")
class TestCommentsViewPost(TestCase):
	def setUp(self):
		self.client = Client()

	def test_post_missing_data(self):
		with self.assertNumQueries(0):
			response = self.client.post(reverse('comments'), data={})
		self.assertEqual(response.status_code, 400)

	def test_post_missing_body_data(self):
		with self.assertNumQueries(0):
			response = self.client.post(reverse('comments'), data={'movie_id': '2'})
		self.assertEqual(response.status_code, 400)

	def test_post_missing_movie_data(self):
		with self.assertNumQueries(0):
			response = self.client.post(reverse('comments'), data={'comment_body': 'comment'})
		self.assertEqual(response.status_code, 400)

	def test_movie_id_does_not_exist(self):
		with self.assertNumQueries(1):
			response = self.client.post(reverse('comments'), data={'movie_id': '2', 'comment_body': 'comment'})
		self.assertEqual(response.status_code, 400)

	def test_unsupported_movie_id(self):
		with self.assertNumQueries(0):
			response = self.client.post(reverse('comments'), data={
				'movie_id': '48c8e82ebebc0aec49ab0e0fe2197bf1', 'comment_body': 'comment'
			})
		self.assertEqual(response.status_code, 400)

	def test_create_comment(self):
		movie = mommy.make(Movie, title='Robot Chicken: Star Wars III', additional_data={'Year': '2010'})
		with self.assertNumQueries(2):
			response = self.client.post(reverse('comments'), data={'movie_id': movie.id, 'comment_body': 'comment'})

		self.assertEqual(response.status_code, 201)
		expected_data = {
			'movie_id': movie.id,
			'comment_id': movie.comments.first().id,
			'body': 'comment', 'created_at': '2018-10-05T00:00:00Z'
		}
		self.assertDictEqual(response.json(), expected_data)


class TestCommentsViewGet(TestCase):
	def setUp(self):
		self.client = Client()

	def test_get_no_comments_no_movie_id(self):
		with self.assertNumQueries(1):
			response = self.client.get(reverse('comments'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), [])

	def test_get_comments_no_movie_id(self):
		mommy.make(Comment, _quantity=4)
		with self.assertNumQueries(5):
			response = self.client.get(reverse('comments'))

		self.assertEqual(response.status_code, 200)
		json_data = response.json()
		self.assertEqual(len(json_data), Comment.objects.count())
		for i, comment in enumerate(json_data, 1):
			self.assertEqual(comment['movie_id'], i)

	def test_get_movie_comments(self):
		movie = mommy.make(Movie)
		queried_comments_number = 2
		mommy.make(Comment, _quantity=4)
		mommy.make(Comment, movie=movie, _quantity=queried_comments_number)
		with self.assertNumQueries(3):
			response = self.client.get('{}?movie_id={}'.format(reverse('comments'), movie.id))

		self.assertEqual(response.status_code, 200)
		json_data = response.json()
		self.assertEqual(len(json_data), queried_comments_number)
		for comment in json_data:
			self.assertEqual(comment['movie_id'], movie.id)

	def test_get_comments_unsupported_id(self):
		with self.assertNumQueries(0):
			response = self.client.get('{}?movie_id=48c8e82ebebc0aec49ab0e0fe2197bf1'.format(reverse('comments')))
		self.assertEqual(response.status_code, 400)


class TestTopMoviesView(TestCase):
	def setUp(self):
		self.client = Client()

	@freeze_time("2018-10-05")
	def test_order_and_rank_get_top_movies(self):
		movie_1 = mommy.make(Movie)
		movie_2 = mommy.make(Movie)
		movie_2_comments_quantity = 4
		mommy.make(Comment, movie=movie_2, _quantity=movie_2_comments_quantity)
		movie_3_4_comments_quantity = 2
		movie_3 = mommy.make(Movie)
		mommy.make(Comment, movie=movie_3, _quantity=movie_3_4_comments_quantity)
		movie_4 = mommy.make(Movie)
		mommy.make(Comment, movie=movie_4, _quantity=movie_3_4_comments_quantity)

		with self.assertNumQueries(1):
			response = self.client.get('{}?date_from=1538611200.0&date_to=1538784000.0'.format(reverse('top')))
		json_data = response.json()
		self.assertEqual(response.status_code, 200)

		expected_data = [{
			'movie_id': movie_2.id,
			'total_comments': movie_2_comments_quantity,
			'rank': 1
		}, {
			'movie_id': movie_3.id,
			'total_comments': movie_3_4_comments_quantity,
			'rank': 2
		}, {
			'movie_id': movie_4.id,
			'total_comments': movie_3_4_comments_quantity,
			'rank': 2
		}, {
			'movie_id': movie_1.id,
			'total_comments': 0,
			'rank': 3
		}]
		for i, expected_movie in enumerate(expected_data):
			self.assertDictEqual(expected_movie, json_data[i])

	def test_filter_movies_by_date(self):
		with freeze_time("2018-10-01"):
			mommy.make(Comment, _quantity=2)
		with freeze_time("2018-10-05"):
			movie_1 = mommy.make(Movie)
			movie_2 = mommy.make(Movie)
			movie_3 = mommy.make(Movie)
			mommy.make(Comment, movie=movie_1, _quantity=3)
			mommy.make(Comment, movie=movie_2, _quantity=4)
		with freeze_time("2018-10-10"):
			mommy.make(Comment, _quantity=3)
		expected_data = [{
			'movie_id': movie_2.id,
			'total_comments': 4,
			'rank': 1
		}, {
			'movie_id': movie_1.id,
			'total_comments': 3,
			'rank': 2
		}, {
			'movie_id': movie_3.id,
			'total_comments': 0,
			'rank': 3
		}]

		with self.assertNumQueries(1):
			response = self.client.get('{}?date_from=1538611200.0&date_to=1538784000.0'.format(reverse('top')))
		json_data = response.json()
		for i, expected_movie in enumerate(expected_data):
			self.assertDictEqual(expected_movie, json_data[i])

	def test_missing_date_range(self):
		with self.assertNumQueries(0):
			response = self.client.get('{}'.format(reverse('top')))
		self.assertEqual(response.status_code, 400)

	def test_missing_date_from(self):
		with self.assertNumQueries(0):
			response = self.client.get('{}?date_to=1538784000.0'.format(reverse('top')))
		self.assertEqual(response.status_code, 400)

	def test_missing_date_to(self):
		with self.assertNumQueries(0):
			response = self.client.get('{}?date_from=1538611200.0'.format(reverse('top')))
		self.assertEqual(response.status_code, 400)

	def test_invalid_date_value(self):
		with self.assertNumQueries(0):
			response = self.client.get('{}?date_from=asdasd&date_to=1538784000.0'.format(reverse('top')))
