from django.test import Client, TestCase
from django.urls import reverse
from users.models import User
from forum.models import Post
from tag.models import Tag, TagType
from settings.models import UserPermission
from utils.utils_permission import PERMISSION_TAG_MANAGE_TAG
import unittest
import json
CONTENT_TYPE = "application/json"

class TagTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.username = "testuser"
        self.password = "password123"
        self.email = "testuser@mails.tsinghua.edu.cn"
        self.no_permission_username = "no_permission_user"
        self.no_permission_email = "no_permission_user@mails.tsinghua.edu.cn"

        self.user = User.objects.create(
            username=self.username,
            password=self.password,
            email=self.email,
            nickname=self.username
        )
        self.user.save()

        self.no_permission_user = User.objects.create(
            username=self.no_permission_username,
            password=self.password,
            email=self.no_permission_email,
            nickname=self.no_permission_username
        )
        self.no_permission_user.save()

        self.user_permission = UserPermission.objects.create(
            user=self.user,
            permission=PERMISSION_TAG_MANAGE_TAG
        )
        self.user_permission.save()

    def test_create_tag_bad_method(self):
        response = self.client.get(reverse('create_tag'))
        self.assertEqual(response.status_code, 405)

    def test_create_tag_lack_params(self):
        response = self.client.post(reverse('create_tag'), {})
        self.assertEqual(response.status_code, 400)

    def test_create_tag_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "name": "Test Tag",
            "tag_type": "sports",
            "is_post_tag": True,
            "is_competition_tag": False
        }
        response = self.client.post(
            reverse('create_tag'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1021)
        self.assertEqual(data["msg"], "User does not exist")

    def test_create_tag_no_permission(self):
        data = {
            "username": self.no_permission_username,
            "name": "Test Tag",
            "tag_type": "sports",
            "is_post_tag": True,
            "is_competition_tag": False
        }
        response = self.client.post(
            reverse('create_tag'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1020)
        self.assertEqual(data["msg"], "No permission")

    def test_create_tag_invalid_type(self):
        data = {
            "username": self.username,
            "name": "Test Tag",
            "tag_type": "invalid_type",
            "is_post_tag": True,
            "is_competition_tag": False
        }
        response = self.client.post(
            reverse('create_tag'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1040)
        self.assertEqual(data["msg"], "Invalid tag type")

    def test_create_tag_already_exists(self):
        Tag.objects.create(
            name="Test Tag",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        data = {
            "username": self.username,
            "name": "Test Tag",
            "tag_type": "sports",
            "is_post_tag": True,
            "is_competition_tag": False
        }
        response = self.client.post(
            reverse('create_tag'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1041)
        self.assertEqual(data["msg"], "Tag already exists")

    def test_create_tag_success(self):
        data = {
            "username": self.username,
            "name": "Test Tag",
            "tag_type": "sports",
            "is_post_tag": True,
            "is_competition_tag": False
        }
        response = self.client.post(
            reverse('create_tag'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Tag created successfully")
        self.assertEqual(Tag.objects.count(), 1)

    def test_delete_tag_bad_method(self):
        response = self.client.get(reverse('delete_tag'))
        self.assertEqual(response.status_code, 405)

    def test_delete_tag_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "tag_id": 1
        }
        response = self.client.post(
            reverse('delete_tag'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1021)
        self.assertEqual(data["msg"], "User does not exist")

    def test_delete_tag_no_permission(self):
        test_tag = Tag.objects.create(
            name="Test Tag",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        data = {
            "username": self.no_permission_username,
            "tag_id": test_tag.id
        }
        response = self.client.post(
            reverse('delete_tag'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1020)
        self.assertEqual(data["msg"], "No permission")

    def test_delete_tag_not_found(self):
        data = {
            "username": self.username,
            "tag_id": 1
        }
        response = self.client.post(
            reverse('delete_tag'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1042)
        self.assertEqual(data["msg"], "Tag does not exist")

    def test_delete_tag_success(self):
        test_tag = Tag.objects.create(
            name="Test Tag",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        data = {
            "username": self.username,
            "tag_id": test_tag.id
        }
        response = self.client.post(
            reverse('delete_tag'),
            data=json.dumps(data),
            content_type=CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Tag deleted successfully")
        self.assertEqual(Tag.objects.count(), 0)

    def test_get_tag_list_bad_method(self):
        response = self.client.post(reverse('get_tag_list'))
        self.assertEqual(response.status_code, 405)

    def test_get_tag_list_success(self):
        Tag.objects.create(
            name="Test Tag 1",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        Tag.objects.create(
            name="Test Tag 2",
            tag_type=TagType.DEPARTMENT,
            is_post_tag=False,
            is_competition_tag=True
        )
        response = self.client.get(reverse('get_tag_list'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Tag list fetched successfully")
        self.assertEqual(len(data["data"]), 2)

    def test_get_post_list_by_tag_bad_method(self):
        response = self.client.post(reverse('get_post_list_by_tag'))
        self.assertEqual(response.status_code, 405)

    def test_get_post_list_by_tag_tag_not_found(self):
        data = {
            "tag_id": 1,
            "page": 1,
            "page_size": 10
        }
        response = self.client.get(
            reverse('get_post_list_by_tag'),
            data = data
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1042)
        self.assertEqual(data["msg"], "Tag does not exist")

    def test_get_post_list_by_tag_page_out_of_range(self):
        tag = Tag.objects.create(
            name="Test Tag",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        post.tags.add(tag)
        post.save()
        data = {
            "tag_id": tag.id,
            "page": 10,
            "page_size": 10
        }
        response = self.client.get(
            reverse('get_post_list_by_tag'),
            data = data
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1023)
        self.assertEqual(data["msg"], "Page out of range")

    def test_get_post_list_by_tag_success(self):
        tag = Tag.objects.create(
            name="Test Tag",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        post.tags.add(tag)
        post.save()
        data = {
            "tag_id": tag.id,
            "page": 1,
            "page_size": 10
        }
        response = self.client.get(
            reverse('get_post_list_by_tag'),
            data = data
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Post list fetched successfully")
        self.assertEqual(len(data["data"]["posts"]), 1)
        self.assertEqual(data["data"]["posts"][0]["id"], post.post_id)
        self.assertEqual(data["data"]["posts"][0]["title"], post.title)
        self.assertEqual(data["data"]["posts"][0]["content"], post.content)
        self.assertEqual(data["data"]["posts"][0]["author"], self.user.username)