from django.test import Client, TestCase
from django.urls import reverse
from users.models import User
from forum.models import Post, Comment, Report
from tag.models import Tag, TagType
from settings.models import UserPermission
from utils.utils_permission import PERMISSION_FORUM_POST, PERMISSION_FORUM_MANAGE_FORUM, PERMISSION_FORUM_POST_HIGHLIGHT
from utils.utils_require import ErrorCode
import unittest
import json
CONTENT_TYPE = "application/json"

# Create your tests here.
class ForumTests(TestCase):
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
            permission=PERMISSION_FORUM_POST
        )
        self.user_permission.save()

        self.manage_permission = UserPermission.objects.create(
            user=self.user,
            permission=PERMISSION_FORUM_MANAGE_FORUM
        )
        self.manage_permission.save()

    def test_create_post_bad_method(self):
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 405)

    def test_create_post_lack_params(self):
        response = self.client.post(reverse('create_post'), {})
        self.assertEqual(response.status_code, 400)

    def test_create_post_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "title": "Test Post",
            "content": "This is a test post"
        }
        response = self.client.post(
            reverse('create_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_create_post_no_permission(self):
        data = {
            "username": self.no_permission_username,
            "title": "Test Post",
            "content": "This is a test post"
        }
        response = self.client.post(
            reverse('create_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_create_post_title_too_long(self):
        data = {
            "username": self.username,
            "title": "This is a test post that is too long to be a valid title ha" * 100,
            "content": "This is a test post"
        }
        response = self.client.post(
            reverse('create_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1022)
        self.assertEqual(data["msg"], "Title is too long")

    def test_create_post_success(self):
        data = {
            "username": self.username,
            "title": "Test Post",
            "content": "This is a test post"
        }
        response = self.client.post(
            reverse('create_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Post created successfully")
        
    def test_create_post_with_tag_bad_method(self):
        response = self.client.get(reverse('create_post_with_tag'))
        self.assertEqual(response.status_code, 405)

    def test_create_post_with_tag_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "title": "Test Post",
            "content": "This is a test post",
            "tag_ids": [1]
        }
        response = self.client.post(
            reverse('create_post_with_tag'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)
    
    def test_create_post_with_tag_no_permission(self):
        data = {
            "username": self.no_permission_username,
            "title": "Test Post",
            "content": "This is a test post",
            "tag_ids": [1]
        }
        response = self.client.post(
            reverse('create_post_with_tag'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_create_post_with_tag_title_too_long(self):
        data = {
            "username": self.username,
            "title": "This is a test post that is too long to be a valid title ha" * 100,
            "content": "This is a test post",
            "tag_ids": [1]
        }
        response = self.client.post(
            reverse('create_post_with_tag'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1022)
        self.assertEqual(data["msg"], "Title is too long")

    def test_create_post_with_tag_too_many_tags(self):
        data = {
            "username": self.username,
            "title": "Test Post",
            "content": "This is a test post",
            "tag_ids": [1, 2, 3, 4, 5, 6, 7, 8]
        }
        response = self.client.post(
            reverse('create_post_with_tag'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1045)
        self.assertEqual(data["msg"], "Too many tags")

    def test_create_post_with_tag_invalid_tag_id(self):
        data = {
            "username": self.username,
            "title": "Test Post",
            "content": "This is a test post",
            "tag_ids": [2013]
        }
        response = self.client.post(
            reverse('create_post_with_tag'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1046)
        self.assertEqual(data["msg"], "Invalid tag id: 2013")

    def test_create_post_with_tag_tag_not_post_tag(self):
        tag = Tag.objects.create(
            name="Tag 1",
            tag_type=TagType.SPORTS,
            is_post_tag=False,
            is_competition_tag=False
        )
        tag.save()
        data = {
            "username": self.username,
            "title": "Test Post",
            "content": "This is a test post",
            "tag_ids": [tag.id]
        }
        response = self.client.post(
            reverse('create_post_with_tag'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1047)
        self.assertEqual(data["msg"], "Tag Tag 1 is not a post tag")

    def test_create_post_with_tag_highlight_tag_no_permission(self):
        tag = Tag.objects.create(
            name="Highlight Tag",
            tag_type=TagType.HIGHLIGHT,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag.save()
        data = {
            "username": self.username,
            "title": "Test Post",
            "content": "This is a test post",
            "tag_ids": [tag.id]
        }
        response = self.client.post(
            reverse('create_post_with_tag'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1048)
        self.assertEqual(data["msg"], "No permission for highlight tag")

    def test_create_post_with_tag_success(self):
        tag1 = Tag.objects.create(
            name="Tag 1",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag1.save()
        tag2 = Tag.objects.create(
            name="Tag 2",
            tag_type=TagType.DEPARTMENT,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag2.save()
        data = {
            "username": self.username,
            "title": "Test Post",
            "content": "This is a test post",
            "tag_ids": [tag1.id, tag2.id]
        }
        response = self.client.post(
            reverse('create_post_with_tag'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Post created successfully")
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().tags.count(), 2)
        self.assertIn(tag1, Post.objects.first().tags.all())
        self.assertIn(tag2, Post.objects.first().tags.all())

    def test_add_tag_to_post_bad_method(self):
        response = self.client.get(reverse('add_tag_to_post'))
        self.assertEqual(response.status_code, 405)

    def test_add_tag_to_post_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "post_id": 1,
            "tag_id": 1
        }
        response = self.client.post(
            reverse('add_tag_to_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_add_tag_to_post_post_not_found(self):
        data = {
            "username": self.username,
            "post_id": 1,
            "tag_id": 1
        }
        response = self.client.post(
            reverse('add_tag_to_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.POST_DOES_NOT_EXIST)
    
    def test_add_tag_to_post_tag_not_found(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        data = {
            "username": self.username,
            "post_id": test_post.post_id,
            "tag_id": 1
        }
        response = self.client.post(
            reverse('add_tag_to_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1046)
        self.assertEqual(data["msg"], "Invalid tag id: 1")

    def test_add_tag_to_post_no_permission(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        tag = Tag.objects.create(
            name="Tag 1",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag.save()
        data = {
            "username": self.no_permission_username,
            "post_id": test_post.post_id,
            "tag_id": tag.id
        }
        response = self.client.post(
            reverse('add_tag_to_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_add_tag_to_post_no_permission_for_highlight_tag(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        tag = Tag.objects.create(
            name="Highlight Tag",
            tag_type=TagType.HIGHLIGHT,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag.save()
        data = {
            "username": self.username,
            "post_id": test_post.post_id,
            "tag_id": tag.id
        }
        response = self.client.post(
            reverse('add_tag_to_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1048)
        self.assertEqual(data["msg"], "No permission for highlight tag")
    
    def test_add_tag_to_post_too_many_tags(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        tag_list = []
        for i in range(6):
            tag = Tag.objects.create(
                name=f"Tag {i}",
                tag_type=TagType.SPORTS,
                is_post_tag=True,
                is_competition_tag=False
            )
            tag.save()
            if i < 5:
                test_post.tags.add(tag)
            tag_list.append(tag)
        test_post.save()
        data = {
            "username": self.username,
            "post_id": test_post.post_id,
            "tag_id": tag_list[5].id
        }
        response = self.client.post(
            reverse('add_tag_to_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1045)
        self.assertEqual(data["msg"], "Too many tags")

    def test_add_tag_to_post_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        tag = Tag.objects.create(
            name="Tag 1",
            tag_type=TagType.HIGHLIGHT,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag.save()
        UserPermission.objects.create(
            user=self.user,
            permission=PERMISSION_FORUM_POST_HIGHLIGHT
        )
        data = {
            "username": self.username,
            "post_id": test_post.post_id,
            "tag_id": tag.id
        }
        response = self.client.post(
            reverse('add_tag_to_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Tag added to post successfully")
        self.assertEqual(test_post.tags.count(), 1)
        self.assertIn(tag, test_post.tags.all())

    def test_remove_tag_from_post_bad_method(self):
        response = self.client.get(reverse('remove_tag_from_post'))
        self.assertEqual(response.status_code, 405)

    def test_remove_tag_from_post_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "post_id": 1,
            "tag_id": 1
        }
        response = self.client.post(
            reverse('remove_tag_from_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_remove_tag_from_post_post_not_found(self):
        data = {
            "username": self.username,
            "post_id": 1,
            "tag_id": 1
        } 
        response = self.client.post(
            reverse('remove_tag_from_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.POST_DOES_NOT_EXIST)

    def test_remove_tag_from_post_tag_not_found(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        data = {
            "username": self.username,
            "post_id": test_post.post_id,
            "tag_id": 1
        }
        response = self.client.post(
            reverse('remove_tag_from_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1046)
        self.assertEqual(data["msg"], "Invalid tag id: 1")

    def test_remove_tag_from_post_tag_not_in_post(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        tag = Tag.objects.create(
            name="Tag 1",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag.save()
        data = {
            "username": self.username,
            "post_id": test_post.post_id,
            "tag_id": tag.id
        }
        response = self.client.post(
            reverse('remove_tag_from_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1050)
        self.assertEqual(data["msg"], "Tag is not in the post")

    def test_remove_tag_from_post_no_permission(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        tag = Tag.objects.create(
            name="Tag 1",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag.save()
        test_post.tags.add(tag)
        test_post.save()
        data = {
            "username": self.no_permission_username,
            "post_id": test_post.post_id,
            "tag_id": tag.id
        }
        response = self.client.post(
            reverse('remove_tag_from_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_remove_tag_from_post_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        tag = Tag.objects.create(
            name="Tag 1",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag.save()
        test_post.tags.add(tag)
        test_post.save()
        data = {
            "username": self.username,
            "post_id": test_post.post_id,
            "tag_id": tag.id
        }
        response = self.client.post(
            reverse('remove_tag_from_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Tag removed from post successfully")
        self.assertEqual(test_post.tags.count(), 0)
        
    def test_get_tag_list_by_post_id_bad_method(self):
        response = self.client.post(reverse('get_tag_list_by_post_id'))
        self.assertEqual(response.status_code, 405)

    def test_get_tag_list_by_post_id_not_found(self):
        response = self.client.get(reverse('get_tag_list_by_post_id'), {
            "post_id": 1
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.POST_DOES_NOT_EXIST)

    def test_get_tag_list_by_post_id_success(self):
        tag1 = Tag.objects.create(
            name="Tag 1",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag1.save()
        tag2 = Tag.objects.create(
            name="Tag 2",
            tag_type=TagType.DEPARTMENT,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag2.save()
        test_post1 = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        test_post1.tags.add(tag1)
        test_post1.tags.add(tag2)
        test_post1.save()

        response = self.client.get(reverse('get_tag_list_by_post_id'), {
            "post_id": test_post1.post_id
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["data"]), 2)

    def test_get_post_list_bad_method(self):
        response = self.client.post(reverse('get_post_list'))
        self.assertEqual(response.status_code, 405)

    def test_get_post_list_out_of_range(self):
        response = self.client.get(reverse('get_post_list'), {
            "page": 100000,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.PAGE_OUT_OF_RANGE)

    def test_get_post_list_success(self):
        post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        post2 = Post.objects.create(
            title="Test Post 2",
            content="This is a test post 2",
            author=self.user
        )
        tag = Tag.objects.create(
            name="Tag 1",
            tag_type=TagType.SPORTS,
            is_post_tag=True,
            is_competition_tag=False
        )
        tag.save()
        post.tags.add(tag)
        post.save()
        response = self.client.get(reverse('get_post_list'), {
            "tag_list": [tag.id],
            "keyword": "Test",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["total_pages"], 1)
        self.assertEqual(data["data"]["total_posts"], 1)

        response = self.client.get(reverse('get_post_list'), {
            "tag_list": [],
            "keyword": "test",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["total_pages"], 1)
        self.assertEqual(data["data"]["total_posts"], 2)
        
    def test_get_post_detail_bad_method(self):
        response = self.client.post(reverse('get_post_detail_by_id'))
        self.assertEqual(response.status_code, 405)

    def test_get_post_detail_not_found(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        response = self.client.get(reverse('get_post_detail_by_id'), {
            "post_id": test_post.post_id + 1
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.POST_DOES_NOT_EXIST)

    def test_get_post_detail_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        response = self.client.get(reverse('get_post_detail_by_id'), {
            "post_id": test_post.post_id
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["title"], "Test Post")
        self.assertEqual(data["data"]["content"], "This is a test post")
        self.assertEqual(data["data"]["author"], self.username)
    
    def test_create_comment_bad_method(self):
        response = self.client.get(reverse('create_comment'))
        self.assertEqual(response.status_code, 405)

    def test_create_comment_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "post_id": 1,
            "content": "This is a test comment"
        }
        response = self.client.post(
            reverse('create_comment'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_create_comment_no_permission(self):
        data = {
            "username": self.no_permission_username,
            "post_id": 1,
            "content": "This is a test comment"
        }
        response = self.client.post(
            reverse('create_comment'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_create_comment_post_not_found(self):
        data = {
            "username": self.username,
            "post_id": 1,
            "content": "This is a test comment"
        }
        response = self.client.post(
            reverse('create_comment'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.POST_DOES_NOT_EXIST)
    
    def test_create_comment_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        data = {
            "username": self.username,
            "post_id": test_post.post_id,
            "content": "This is a test comment"
        }
        response = self.client.post(
            reverse('create_comment'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Comment created successfully")

    def test_delete_post_bad_method(self):
        response = self.client.get(reverse('delete_post'))
        self.assertEqual(response.status_code, 405)

    def test_delete_post_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "post_id": 1
        }
        response = self.client.post(
            reverse('delete_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)
        
    def test_delete_post_post_not_found(self):
        data = {
            "username": self.username,
            "post_id": 1
        }
        response = self.client.post(
            reverse('delete_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.POST_DOES_NOT_EXIST)

    def test_delete_post_no_permission(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        data = {
            "username": self.no_permission_username,
            "post_id": test_post.post_id
        }
        response = self.client.post(
            reverse('delete_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_delete_post_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        data = {
            "username": self.username,
            "post_id": test_post.post_id
        }
        response = self.client.post(
            reverse('delete_post'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Post deleted successfully")
        self.assertEqual(Post.objects.count(), 0)

    def test_get_comment_list_by_post_id_bad_method(self):
        response = self.client.post(reverse('get_comment_list_by_post_id'))
        self.assertEqual(response.status_code, 405)

    def test_get_comment_list_by_post_id_not_found(self):
        response = self.client.get(reverse('get_comment_list_by_post_id'), {
            "post_id": 1,
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.POST_DOES_NOT_EXIST)

    def test_get_comment_list_by_post_id_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_post
        )
        response = self.client.get(reverse('get_comment_list_by_post_id'), {
            "post_id": test_post.post_id,
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["total_pages"], 1)
        self.assertEqual(data["data"]["total_comments"], 1)

    def test_create_comment_of_object_bad_method(self):
        response = self.client.get(reverse('create_comment_of_object'))
        self.assertEqual(response.status_code, 405)

    def test_create_comment_of_object_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "content_type": "Post",
            "object_id": 1,
            "content": "This is a test comment",
            "allow_reply": True
        }
        response = self.client.post(
            reverse('create_comment_of_object'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_create_comment_of_object_no_permission(self):
        data = {
            "username": self.no_permission_username,
            "content_type": "Post",
            "object_id": 1,
            "content": "This is a test comment",
            "allow_reply": True
        }
        response = self.client.post(
            reverse('create_comment_of_object'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_create_comment_of_object_invalid_content_type(self):
        data = {
            "username": self.username,
            "content_type": "Invalid",
            "object_id": 1,
            "content": "This is a test comment",
            "allow_reply": True
        }
        response = self.client.post(
            reverse('create_comment_of_object'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1031)
        self.assertEqual(data["msg"], "Invalid content type")
    
    def test_create_comment_of_object_object_not_found(self):
        data = {
            "username": self.username,
            "content_type": "Post",
            "object_id": 1,
            "content": "This is a test comment",
            "allow_reply": True
        }
        response = self.client.post(
            reverse('create_comment_of_object'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1032)
        self.assertEqual(data["msg"], "Object does not exist")
        
    def test_create_comment_of_object_object_not_allow_reply(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        test_comment = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_post,
            allow_reply=False
        )
        data = {
            "username": self.username,
            "content_type": "Comment",
            "object_id": test_comment.comment_id,
            "content": "This is a test reply",
            "allow_reply": True
        }
        response = self.client.post(
            reverse('create_comment_of_object'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1033)
        self.assertEqual(data["msg"], "Object does not allow reply")

    def test_create_comment_of_object_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        test_comment = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_post,
            allow_reply=True
        )
        data = {
            "username": self.username,
            "content_type": "Comment",
            "object_id": test_comment.comment_id,
            "content": "This is a test reply",
            "allow_reply": True
        }
        response = self.client.post(
            reverse('create_comment_of_object'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Comment created successfully")
        self.assertEqual(Comment.objects.count(), 2)

    def test_get_comment_list_of_object_bad_method(self):
        response = self.client.post(reverse('get_comment_list_of_object'))
        self.assertEqual(response.status_code, 405)

    def test_get_comment_list_of_object_invalid_content_type(self):
        data = {
            "content_type": "Invalid",
            "object_id": 1,
            "page": 1,
            "page_size": 10
        }
        response = self.client.get(reverse('get_comment_list_of_object'), data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1031)
        self.assertEqual(data["msg"], "Invalid content type")

    def test_get_comment_list_of_object_not_found(self):
        response = self.client.get(reverse('get_comment_list_of_object'), {
            "content_type": "Post",
            "object_id": 1,
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1032)
        self.assertEqual(data["msg"], "Object does not exist")

    def test_get_comment_list_of_object_out_of_range(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        response = self.client.get(reverse('get_comment_list_of_object'), {
            "content_type": "Post",
            "object_id": test_post.post_id,
            "page": 100000,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.PAGE_OUT_OF_RANGE)

    def test_get_comment_list_of_object_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_post,
            allow_reply=True
        )
        response = self.client.get(reverse('get_comment_list_of_object'), {
            "content_type": "Post",
            "object_id": test_post.post_id,
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["total_pages"], 1)
        self.assertEqual(data["data"]["total_comments"], 1)

    def test_get_reply_list_of_comment_bad_method(self):
        response = self.client.post(reverse('get_reply_list_of_comment'))
        self.assertEqual(response.status_code, 405)

    def test_get_reply_list_of_comment_not_found(self):
        response = self.client.get(reverse('get_reply_list_of_comment'), {
            "comment_id": 1,
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.COMMENT_DOES_NOT_EXIST)

    def test_get_reply_list_of_comment_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user)
        test_comment1 = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_post,
            allow_reply=True
        )
        test_comment2 = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_comment1,
            allow_reply=True
        )
        test_comment3 = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_comment2,
            allow_reply=True
        )
        response = self.client.get(reverse('get_reply_list_of_comment'), {
            "comment_id": test_comment1.comment_id,
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["data"]), 3)
        self.assertEqual(data["data"][0]["comment_id"], test_comment1.comment_id)
        self.assertEqual(data["data"][1]["comment_id"], test_comment2.comment_id)
        self.assertEqual(data["data"][2]["comment_id"], test_comment3.comment_id)
        self.assertEqual(data["data"][0]["father_object_id"], test_post.post_id)
        self.assertEqual(data["data"][1]["father_object_id"], test_comment1.comment_id)
        self.assertEqual(data["data"][2]["father_object_id"], test_comment2.comment_id)
        
    def test_delete_comment_bad_method(self):
        response = self.client.get(reverse('delete_comment'))
        self.assertEqual(response.status_code, 405)

    def test_delete_comment_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "comment_id": 1
        }
        response = self.client.post(
            reverse('delete_comment'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_delete_comment_comment_not_found(self):
        data = {
            "username": self.username,
            "comment_id": 1
        }
        response = self.client.post(
            reverse('delete_comment'),
            data = json.dumps(data), 
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.COMMENT_DOES_NOT_EXIST)

    def test_delete_comment_no_permission(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        test_comment = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_post,
            allow_reply=True
        )
        data = {
            "username": self.no_permission_username,
            "comment_id": test_comment.comment_id
        }
        response = self.client.post(
            reverse('delete_comment'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_delete_comment_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        test_comment = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_post,
            allow_reply=True
        )
        test_comment2 = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_comment,
            allow_reply=True
        )
        data = {
            "username": self.username,
            "comment_id": test_comment.comment_id
        }
        response = self.client.post(
            reverse('delete_comment'),
            data = json.dumps(data),
            content_type = CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Comment deleted successfully")
        self.assertEqual(Comment.objects.count(), 0)

    def test_search_post_by_keyword_bad_method(self):
        response = self.client.post(reverse('search_post_by_keyword'))
        self.assertEqual(response.status_code, 405)

    def test_search_post_by_keyword_out_of_range(self):
        response = self.client.get(reverse('search_post_by_keyword'), {
            "keyword": "test",
            "page": 100000,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.PAGE_OUT_OF_RANGE)

    def test_search_post_by_keyword_success(self):
        test_post1 = Post.objects.create(
            title="Test Post 1",
            content="This is a test post",
            author=self.user
        )
        test_post2 = Post.objects.create(
            title="Test Post 2",
            content="This is a test post",
            author=self.user
        )
        test_post3 = Post.objects.create(
            title="Post 3",
            content="This is a post",
            author=self.user
        )
        response = self.client.get(reverse('search_post_by_keyword'), {
            "keyword": "test",
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["total_pages"], 1)
        self.assertEqual(data["data"]["total_posts"], 2)
        self.assertEqual(data["data"]["posts"][0]["post_id"], test_post2.post_id)
        self.assertEqual(data["data"]["posts"][1]["post_id"], test_post1.post_id)

    def test_get_comment_detail_by_id_bad_method(self):
        response = self.client.post(reverse('get_comment_detail_by_id'))
        self.assertEqual(response.status_code, 405)

    def test_get_comment_detail_by_id_not_found(self):
        response = self.client.get(reverse('get_comment_detail_by_id'), {
            "comment_id": 1
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.COMMENT_DOES_NOT_EXIST)

    def test_get_comment_detail_by_id_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        test_comment = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_post,
            allow_reply=True
        )
        response = self.client.get(reverse('get_comment_detail_by_id'), {
            "comment_id": test_comment.comment_id
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["comment_id"], test_comment.comment_id)
        self.assertEqual(data["data"]["content"], test_comment.content)
        self.assertEqual(data["data"]["author"], test_comment.author.username)
        self.assertEqual(data["data"]["allow_reply"], test_comment.allow_reply)
        self.assertEqual(data["data"]["object_id"], test_post.post_id)
        self.assertEqual(data["data"]["content_type"], "Post")

    def test_create_report_bad_method(self):
        response = self.client.get(reverse('create_report'))
        self.assertEqual(response.status_code, 405)

    def test_create_report_user_not_exists(self):
        data = {
            "reporter": "nonexistentuser",
            "content_type": "Post",
            "object_id": 1,
            "reason": "This is a test reason"
        }
        response = self.client.post(reverse('create_report'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_create_report_invalid_content_type(self):
        data = {
            "reporter": self.username,
            "content_type": "Invalid",
            "object_id": 1,
            "reason": "This is a test reason"
        }
        response = self.client.post(reverse('create_report'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1031)
        self.assertEqual(data["msg"], "Invalid content type")

    def test_create_report_object_not_found(self):
        data = {
            "reporter": self.username,
            "content_type": "Post",
            "object_id": 1,
            "reason": "This is a test reason"
        }
        response = self.client.post(reverse('create_report'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1032)
        self.assertEqual(data["msg"], "Object does not exist")

    def test_create_report_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        data = {
            "reporter": self.username,
            "content_type": "Post",
            "object_id": test_post.post_id,
            "reason": "This is a test reason"
        }
        response = self.client.post(reverse('create_report'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Report created successfully")
        self.assertEqual(Report.objects.count(), 1)

    def test_modify_report_solved_state_bad_method(self):
        response = self.client.get(reverse('modify_report_solved_state'))
        self.assertEqual(response.status_code, 405)

    def test_modify_report_solved_state_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "report_id": 1,
            "solved_state": True
        }
        response = self.client.post(reverse('modify_report_solved_state'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_modify_report_solved_state_no_permission(self):
        data = {
            "username": self.no_permission_username,
            "report_id": 1,
            "solved_state": True
        }
        response = self.client.post(reverse('modify_report_solved_state'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_modify_report_solved_state_report_not_found(self):
        data = {
            "username": self.username,
            "report_id": 1,
            "solved_state": True
        }
        response = self.client.post(reverse('modify_report_solved_state'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1036)
        self.assertEqual(data["msg"], "Report does not exist")

    def test_modify_report_solved_state_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        report = Report.objects.create(
            reporter=self.user,
            reported_user=self.user,
            reported_content=test_post.content,
            content_object=test_post,
            reason="This is a test reason"
        )
        data = {
            "username": self.username,
            "report_id": report.report_id,
            "solved_state": True
        }
        response = self.client.post(reverse('modify_report_solved_state'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Report solved state modified successfully")
        report.refresh_from_db()
        self.assertEqual(report.solved, True)

    def test_get_report_list_bad_method(self):
        response = self.client.post(reverse('get_report_list'))
        self.assertEqual(response.status_code, 405)

    def test_get_report_list_out_of_range(self):
        response = self.client.get(reverse('get_report_list'), {
            "page": 100000,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.PAGE_OUT_OF_RANGE)

    def test_get_report_list_success(self):
        test_post1 = Post.objects.create(
            title="Test Post 1",
            content="This is a test post",
            author=self.user
        )
        test_comment1 = Comment.objects.create(
            content="This is a test comment",
            author=self.user,
            content_object=test_post1,
            allow_reply=True
        )
        report1 = Report.objects.create(
            reporter=self.user,
            reported_user=test_post1.author,
            reported_content=test_post1.content,
            content_object=test_post1,
            reason="This is a test reason",
            solved=True
        )
        report2 = Report.objects.create(
            reporter=self.user,
            reported_user=test_comment1.author,
            reported_content=test_comment1.content,
            content_object=test_comment1,
            reason="This is a test reason",
            solved=False
        )

        response = self.client.get(reverse('get_report_list'), {
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["total_pages"], 1)
        self.assertEqual(data["data"]["total_reports"], 2)

        response = self.client.get(reverse('get_report_list'), {
            "solved_state": False,
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["total_pages"], 1)
        self.assertEqual(data["data"]["total_reports"], 1)
        self.assertEqual(data["data"]["reports"][0]["report_id"], report2.report_id)
        self.assertEqual(data["data"]["reports"][0]["reporter"], report2.reporter.username)
        self.assertEqual(data["data"]["reports"][0]["content_type"], "Comment")

        response = self.client.get(reverse('get_report_list'), {
            "solved_state": True,
            "page": 1,
            "page_size": 10
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["total_pages"], 1)
        self.assertEqual(data["data"]["total_reports"], 1)
        self.assertEqual(data["data"]["reports"][0]["report_id"], report1.report_id)
        self.assertEqual(data["data"]["reports"][0]["reporter"], report1.reporter.username)
        self.assertEqual(data["data"]["reports"][0]["content_type"], "Post")

    def test_delete_reported_object_bad_method(self):
        response = self.client.get(reverse('delete_reported_object'))
        self.assertEqual(response.status_code, 405)

    def test_delete_reported_object_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "report_id": 1
        }
        response = self.client.post(reverse('delete_reported_object'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_delete_reported_object_no_permission(self):
        data = {
            "username": self.no_permission_username,
            "report_id": 1
        }
        response = self.client.post(reverse('delete_reported_object'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_delete_reported_object_report_not_found(self):
        data = {
            "username": self.username,
            "report_id": 1
        }
        response = self.client.post(reverse('delete_reported_object'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1036)
        self.assertEqual(data["msg"], "Report does not exist")

    def test_delete_reported_object_object_not_found(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        report = Report.objects.create(
            reporter=self.user,
            reported_user=test_post.author,
            reported_content=test_post.content,
            content_object=test_post,
            reason="This is a test reason"
        )
        test_post.delete()
        data = {
            "username": self.username,
            "report_id": report.report_id
        }
        response = self.client.post(reverse('delete_reported_object'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1032)
        self.assertEqual(data["msg"], "Object already deleted")

    def test_delete_reported_object_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        report = Report.objects.create(
            reporter=self.user,
            reported_user=test_post.author,
            reported_content=test_post.content,
            content_object=test_post,
            reason="This is a test reason"
        )
        data = {
            "username": self.username,
            "report_id": report.report_id
        }
        response = self.client.post(reverse('delete_reported_object'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Reported object deleted successfully")
        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(Report.objects.count(), 1)

    def test_ban_reported_user_bad_method(self):
        response = self.client.get(reverse('ban_reported_user'))
        self.assertEqual(response.status_code, 405)

    def test_ban_reported_user_user_not_exists(self):
        data = {
            "username": "nonexistentuser",
            "report_id": 1
        }
        response = self.client.post(reverse('ban_reported_user'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.USER_DOES_NOT_EXIST)

    def test_ban_reported_user_report_not_found(self):
        data = {
            "username": self.username,
            "report_id": 1
        }
        response = self.client.post(reverse('ban_reported_user'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 1036)
        self.assertEqual(data["msg"], "Report does not exist")

    def test_ban_reported_user_no_permission(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        test_report = Report.objects.create(
            reporter=self.user,
            reported_user=test_post.author,
            reported_content=test_post.content,
            content_object=test_post,
            reason="This is a test reason"
        )
        data = {
            "username": self.no_permission_username,
            "report_id": test_report.report_id
        }
        response = self.client.post(reverse('ban_reported_user'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, ErrorCode.NO_PERMISSION)

    def test_ban_reported_user_success(self):
        test_post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            author=self.user
        )
        test_report = Report.objects.create(
            reporter=self.user,
            reported_user=test_post.author,
            reported_content=test_post.content,
            content_object=test_post,
            reason="This is a test reason"
        )
        data = {
            "username": self.username,
            "report_id": test_report.report_id
        }
        response = self.client.post(reverse('ban_reported_user'), data=json.dumps(data), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["msg"], "Permission removed successfully")
        self.assertEqual(UserPermission.objects.filter(user=test_report.reporter, permission=PERMISSION_FORUM_POST).exists(), False)