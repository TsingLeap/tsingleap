from django.core.management.base import BaseCommand
from forum.models import *
from users.models import User
from competitions.models import Competition, Participant
from tag.models import Tag, TagType
import random
from faker import Faker
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = '生成测试数据'

    USER_NUM = 5000
    POST_NUM = 10000
    COMPETITION_NUM = 10000
    PARTICIPANT_NUM = 5000
    TAG_NUM = 200

    def handle(self, *args, **options):
        # 清空数据库
        self.stdout.write('清空数据库...')
        Competition.objects.all().delete()
        Participant.objects.all().delete()
        Post.objects.all().delete()
        User.objects.all().delete()
        Tag.objects.all().delete()
        self.stdout.write('数据库已清空')

        fake = Faker()
        Faker.seed(0)  # 设置随机种子，确保每次生成的数据相同

        # 生成 TAG_NUM 个标签
        self.stdout.write('开始生成标签...')
        tags = []
        tag_types = [TagType.SPORTS, TagType.DEPARTMENT, TagType.EVENT, TagType.HIGHLIGHT, TagType.DEFAULT]
        for i in range(self.TAG_NUM):
            tag_type = random.choice(tag_types)
            tag = Tag.objects.create(
                name=fake.word(),
                tag_type=tag_type,
                is_post_tag=random.choice([True, False]),
                is_competition_tag=random.choice([True, False])
            )
            tags.append(tag)
            if (i + 1) % 10 == 0:
                self.stdout.write(f'已生成 {i + 1} 个标签')

        # 生成 USER_NUM 个用户
        self.stdout.write('开始生成用户...')
        users = []
        for i in range(self.USER_NUM):
            username = f"user_{i}"
            email = f"user_{i}_fake_email@mails.tsinghua.edu.cn"
            user = User.objects.create(
                username=username,
                nickname=fake.name(),
                password="dummy_password_hash",  # 使用一个假的密码哈希
                email=email
            )
            users.append(user)
            if (i + 1) % 100 == 0:
                self.stdout.write(f'已生成 {i + 1} 个用户')

        # 生成 POST_NUM 个帖子
        self.stdout.write('开始生成帖子...')
        for i in range(self.POST_NUM):
            author = random.choice(users)
            post = Post.objects.create(
                title=fake.sentence(),
                content=fake.paragraph(nb_sentences=5),
                author=author,
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            # 随机选择1-5个帖子标签
            post_tags = [tag for tag in tags if tag.is_post_tag]
            if post_tags:
                selected_tags = random.sample(post_tags, min(random.randint(1, 5), len(post_tags)))
                post.tags.set(selected_tags)
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'已生成 {i + 1} 个帖子')

        # 生成 PARTICIPANT_NUM 个参与者
        self.stdout.write('开始生成参与者...')
        participants = []
        for i in range(self.PARTICIPANT_NUM):
            participant = Participant.objects.create(
                name=fake.name(),
                score=random.randint(0, 100)
            )
            participants.append(participant)
            if (i + 1) % 100 == 0:
                self.stdout.write(f'已生成 {i + 1} 个参与者')

        # 生成 COMPETITION_NUM 个比赛
        self.stdout.write('开始生成比赛...')
        sports = ['篮球', '足球', '排球', '网球', '乒乓球', '羽毛球', '游泳', '田径', '体操', '举重']
        for i in range(self.COMPETITION_NUM):
            comp = Competition.objects.create(
                name=f"{random.choice(sports)}比赛 #{i+1}",
                sport=random.choice(sports),
                is_finished=random.choice([True, False]),
                time_begin=timezone.now() - timedelta(days=random.randint(0, 365))
            )
            # 随机选2-4个参与者
            selected_participants = random.sample(participants, random.randint(2, 4))
            comp.participants.set(selected_participants)
            
            # 随机选择1-5个比赛标签
            comp_tags = [tag for tag in tags if tag.is_competition_tag]
            if comp_tags:
                selected_tags = random.sample(comp_tags, min(random.randint(1, 5), len(comp_tags)))
                comp.tags.set(selected_tags)

            if (i + 1) % 100 == 0:
                self.stdout.write(f'已生成 {i + 1} 个比赛')

        self.stdout.write(self.style.SUCCESS('测试数据生成完成！'))