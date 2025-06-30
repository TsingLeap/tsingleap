import json
import secrets
from django.test import TestCase, RequestFactory
from django.utils import timezone
from tag.models import Tag, TagType
from users.models import User
from settings.models import UserPermission
from competitions.models import Competition, Participant, Focus, Like
from competitions.views import (
    create_competition, get_competition_list, get_competition_info,
    update_competition, delete_competition, add_participant,
    delete_participant, update_participant, get_participant_list,
    get_competition_admin_list, add_competition_focus,
    del_competition_focus, get_tag_list_by_competition,
    like_participant, unlike_participant, get_like_count
)
from utils.utils_request import BAD_METHOD
from utils.utils_competition import TAG_NUM_LIMIT, MAX_COMPETITION_LIST_LENGTH

class ViewsTestCase(TestCase):
    def setUp(self):
        # 初始化 RequestFactory 和基础测试数据
        self.factory = RequestFactory()
        # 创建测试用户
        pwd1 = secrets.token_urlsafe(12)  # 大约 16 字符，URL 安全
        pwd2 = secrets.token_urlsafe(12)
        self.user1 = User.objects.create(
            username='user1',
            nickname='nick1',
            password=pwd1,
            email='u1@test.com',
        )
        self.user2 = User.objects.create(
            username='user2',
            nickname='nick2',
            password=pwd2,
            email='u2@test.com',
        )
        # 创建赛事标签和非赛事标签
        self.comp_tags = [
            Tag.objects.create(
                name=f"tag{i}", tag_type=TagType.SPORTS,
                is_competition_tag=True, is_post_tag=False
            ) for i in range(3)
        ]
        self.non_comp_tag = Tag.objects.create(
            name="not_comp", tag_type=TagType.HIGHLIGHT,
            is_competition_tag=False, is_post_tag=True
        )

    # --------- create_competition ---------
    def test_create_competition_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(create_competition(self.factory.get('/create/')), BAD_METHOD)

    def test_create_competition_missing_fields(self):
        """缺少必填字段返回错误码"""
        resp = create_competition(self.factory.post('/create/', data=json.dumps({}), content_type='application/json'))
        code = json.loads(resp.content)['code']
        self.assertNotEqual(code, 0)

    def test_create_competition_bad_tag(self):
        """使用非赛事标签返回 1111"""
        body = {'name':'C1','sport':'S1','is_finished':False,
                'time_begin':timezone.now().isoformat(), 'tag_ids':[self.non_comp_tag.id]}
        code = json.loads(create_competition(self.factory.post('/create/', data=json.dumps(body), content_type='application/json')).content)['code']
        self.assertEqual(code, 1111)

    def test_create_competition_too_many_tags(self):
        """去重后唯一标签数超过限制返回 1112"""
        extra = [Tag.objects.create(name=f'x{i}', tag_type=TagType.SPORTS, is_competition_tag=True, is_post_tag=False) for i in range(TAG_NUM_LIMIT+1)]
        tag_ids = [t.id for t in extra]
        body = {'name':'C2','sport':'S2','is_finished':True,
                'time_begin':timezone.now().isoformat(), 'tag_ids':tag_ids}
        code = json.loads(create_competition(self.factory.post('/create/', data=json.dumps(body), content_type='application/json')).content)['code']
        self.assertEqual(code, 1112)

    def test_create_competition_duplicate_tags_allowed(self):
        """重复标签但唯一数未超限允许创建"""
        tid = self.comp_tags[0].id
        tag_ids = [tid] * (TAG_NUM_LIMIT + 5)
        body = {'name':'Cdup','sport':'Sdup','is_finished':False,
                'time_begin':timezone.now().isoformat(), 'tag_ids':tag_ids}
        code = json.loads(create_competition(self.factory.post('/create/', data=json.dumps(body), content_type='application/json')).content)['code']
        self.assertEqual(code, 0)
        self.assertTrue(Competition.objects.filter(name='Cdup').exists())

    def test_create_competition_success(self):
        """合法请求成功创建赛事"""
        tag_ids = [t.id for t in self.comp_tags]
        body = {'name':'C3','sport':'S3','is_finished':False,
                'time_begin':timezone.now().isoformat(), 'tag_ids':tag_ids}
        resp = create_competition(self.factory.post('/create/', data=json.dumps(body), content_type='application/json'))
        data = json.loads(resp.content)
        self.assertEqual(data['code'], 0)
        self.assertTrue(Competition.objects.filter(id=data['data']['id']).exists())

    # --------- get_competition_list ---------
    def test_get_competition_list_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(get_competition_list(self.factory.get('/list/')), BAD_METHOD)

    def test_get_competition_list_empty(self):
        """无符合条件返回 1100 空列表"""
        body = {'user_id':self.user1.id,'tag_list':[],'search_text':'',
                'before_time':'','before_id':-1,'is_finished':False,'filter_focus':False}
        data = json.loads(get_competition_list(self.factory.post('/list/', data=json.dumps(body), content_type='application/json')).content)
        self.assertEqual(data['code'], 1100)
        self.assertEqual(data['data']['competition_list'], [])

    def test_get_competition_list_with_results(self):
        """测试标签和搜索过滤"""
        now = timezone.now()
        c1 = Competition.objects.create(id=1,name='A',sport='X',is_finished=False,time_begin=now)
        c2 = Competition.objects.create(id=2,name='B',sport='Y',is_finished=False,time_begin=now)
        c1.tags.set([self.comp_tags[0]]); c2.tags.set([self.comp_tags[1]])
        body = {'user_id':self.user1.id,'tag_list':[self.comp_tags[0].id],
                'search_text':'A','before_time':'','before_id':-1,
                'is_finished':False,'filter_focus':False}
        data = json.loads(get_competition_list(self.factory.post('/list/', data=json.dumps(body), content_type='application/json')).content)
        self.assertEqual(data['code'], 0)
        self.assertEqual(len(data['data']['competition_list']), 1)

    def test_get_competition_list_filter_focus(self):
        """filter_focus=True 返回关注赛事"""
        c = Competition.objects.create(id=3,name='C',sport='Z',is_finished=False,time_begin=timezone.now())
        Focus.objects.create(user=self.user1,competition=c)
        body = {'user_id':self.user1.id,'tag_list':[],'search_text':'',
                'before_time':'','before_id':-1,'is_finished':False,'filter_focus':True}
        data = json.loads(get_competition_list(self.factory.post('/list/', data=json.dumps(body), content_type='application/json')).content)
        self.assertTrue(data['data']['competition_list'][0]['is_focus'])

    # --------- get_competition_info ---------
    def test_get_competition_info_wrong_method(self):
        """非 GET 请求返回 BAD_METHOD"""
        self.assertEqual(get_competition_info(self.factory.post('/info/')), BAD_METHOD)

    def test_get_competition_info_not_found(self):
        """查询不存在返回 1101"""
        data = json.loads(get_competition_info(self.factory.get('/info/', {'id':999})).content)
        self.assertEqual(data['code'], 1101)

    def test_get_competition_info_success(self):
        """正确查询返回详情"""
        c = Competition.objects.create(id=4,name='D',sport='W',is_finished=True,time_begin=timezone.now())
        data = json.loads(get_competition_info(self.factory.get('/info/', {'id':c.id})).content)
        self.assertEqual(data['data']['competition']['id'], c.id)

    # --------- update_competition ---------
    def test_update_competition_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(update_competition(self.factory.get('/upd/')), BAD_METHOD)

    def test_update_competition_not_found(self):
        """更新不存在返回 1102"""
        data = json.loads(update_competition(self.factory.post('/upd/', data=json.dumps({'id':999}), content_type='application/json')).content)
        self.assertEqual(data['code'], 1102)

    def test_update_competition_bad_tag(self):
        """传入非赛事标签返回 1113"""
        c = Competition.objects.create(id=5,name='E',sport='V',is_finished=False,time_begin=timezone.now())
        body = {'id':c.id,'name':'E2','sport':'V2','is_finished':False,
                'time_begin':timezone.now().isoformat(),'tag_ids':[self.non_comp_tag.id]}
        data = json.loads(update_competition(self.factory.post('/upd/', data=json.dumps(body), content_type='application/json')).content)
        self.assertEqual(data['code'], 1113)

    def test_update_competition_too_many_tags(self):
        """唯一标签数超限返回 1114"""
        c = Competition.objects.create(id=6,name='F',sport='U',is_finished=False,time_begin=timezone.now())
        extra = [Tag.objects.create(name=f'x{i}',tag_type=TagType.SPORTS,is_competition_tag=True,is_post_tag=False) for i in range(TAG_NUM_LIMIT+1)]
        ids = [t.id for t in extra]
        data = json.loads(update_competition(self.factory.post('/upd/', data=json.dumps({'id':c.id,'name':'F2','sport':'U2','is_finished':True,'time_begin':timezone.now().isoformat(),'tag_ids':ids}), content_type='application/json')).content)
        self.assertEqual(data['code'], 1114)

    def test_update_competition_success(self):
        """合法更新返回 0 并生效"""
        c = Competition.objects.create(id=7,name='G',sport='T',is_finished=False,time_begin=timezone.now())
        ids = [t.id for t in self.comp_tags]
        data = json.loads(update_competition(self.factory.post('/upd/', data=json.dumps({'id':c.id,'name':'G2','sport':'T2','is_finished':True,'time_begin':timezone.now().isoformat(),'tag_ids':ids}), content_type='application/json')).content)
        c.refresh_from_db()
        self.assertEqual(data['code'], 0)
        self.assertEqual(c.name, 'G2')

    # --------- delete_competition ---------
    def test_delete_competition_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(delete_competition(self.factory.get('/del/')), BAD_METHOD)

    def test_delete_competition_not_found(self):
        """删除不存在返回 1103"""
        data = json.loads(delete_competition(self.factory.post('/del/', data=json.dumps({'id':999}), content_type='application/json')).content)
        self.assertEqual(data['code'], 1103)

    def test_delete_competition_success(self):
        """删除赛事并删除权限返回 0"""
        c = Competition.objects.create(id=8,name='H',sport='Q',is_finished=False,time_begin=timezone.now())
        UserPermission.objects.create(user=self.user1,permission='match.update_match_info',permission_info=str(c.id))
        data = json.loads(delete_competition(self.factory.post('/del/', data=json.dumps({'id':c.id}), content_type='application/json')).content)
        self.assertEqual(data['code'], 0)
        self.assertFalse(Competition.objects.filter(id=c.id).exists())

    # --------- add_/delete/update participant ---------
    def test_add_participant_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(add_participant(self.factory.get('/part/')), BAD_METHOD)

    def test_add_participant_comp_not_found(self):
        """往不存在赛事添加返回 1118"""
        body = {'competition_id':999,'participants':[{'name':'P','score':1}]}
        data = json.loads(add_participant(self.factory.post('/part/', data=json.dumps(body), content_type='application/json')).content)
        self.assertEqual(data['code'], 1118)

    def test_add_participant_missing_fields(self):
        """缺少 name 或 score 返回 1119"""
        c=Competition.objects.create(name='AP',sport='S',is_finished=False,time_begin=timezone.now())
        body={'competition_id':c.id,'participants':[{}]}
        data = json.loads(add_participant(self.factory.post('/part/', data=json.dumps(body), content_type='application/json')).content)
        self.assertEqual(data['code'], 1119)

    def test_add_participant_success(self):
        """添加参赛者成功"""
        c=Competition.objects.create(name='AP2',sport='S',is_finished=False,time_begin=timezone.now())
        body={'competition_id':c.id,'participants':[{'name':'P2','score':20}]}
        data = json.loads(add_participant(self.factory.post('/part/', data=json.dumps(body), content_type='application/json')).content)
        self.assertEqual(data['code'], 0)
        self.assertTrue(Participant.objects.filter(name='P2', score=20).exists())

    def test_delete_participant_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(delete_participant(self.factory.get('/part/del/')), BAD_METHOD)

    def test_delete_participant_success(self):
        """批量删除参赛者成功"""
        p1 = Participant.objects.create(name='X',score=1)
        p2 = Participant.objects.create(name='Y',score=2)
        body={'participant_ids':[p1.id,p2.id]}
        delete_participant(self.factory.post('/part/del/', data=json.dumps(body), content_type='application/json'))
        self.assertFalse(Participant.objects.filter(id__in=[p1.id,p2.id]).exists())

    def test_update_participant_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(update_participant(self.factory.get('/part/upd/')), BAD_METHOD)

    def test_update_participant_missing_fields(self):
        """缺少 id/name/score 返回 1124"""
        body={'participants':[{'id':1}]}        
        data = json.loads(update_participant(self.factory.post('/part/upd/', data=json.dumps(body), content_type='application/json')).content)
        self.assertEqual(data['code'], 1124)

    def test_update_participant_success(self):
        """更新参赛者信息成功"""
        p = Participant.objects.create(name='Old',score=0)
        body={'participants':[{'id':p.id,'name':'New','score':5}]}
        data=json.loads(update_participant(self.factory.post('/part/upd/', data=json.dumps(body), content_type='application/json')).content)
        self.assertEqual(data['code'], 0)
        p.refresh_from_db(); self.assertEqual(p.name,'New')

    # --------- get_participant_list ---------
    def test_get_participant_list_wrong_method(self):
        """非 GET 请求返回 BAD_METHOD"""
        self.assertEqual(get_participant_list(self.factory.post('/part/list/')), BAD_METHOD)

    def test_get_participant_list_not_found(self):
        """查询不存在赛事返回 1120"""
        data = json.loads(get_participant_list(self.factory.get('/part/list/', {'user_id':self.user1.id,'competition_id':999})).content)
        self.assertEqual(data['code'], 1120)

    def test_get_participant_list_success(self):
        """正确获取参赛者及点赞状态"""
        c=Competition.objects.create(name='L',sport='S',is_finished=False,time_begin=timezone.now())
        p=Participant.objects.create(name='Z',score=10)
        c.participants.add(p)
        Like.objects.create(user=self.user1,participant=p)
        data=json.loads(get_participant_list(self.factory.get('/part/list/', {'user_id':self.user1.id,'competition_id':c.id})).content)
        self.assertEqual(data['code'], 0)
        item = data['data']['participant_list'][0]
        self.assertTrue(item['like']); self.assertEqual(item['like_count'], 1)

    # --------- get_competition_admin_list ---------
    def test_get_competition_admin_list_wrong_method(self):
        """非 GET 请求返回 BAD_METHOD"""
        self.assertEqual(get_competition_admin_list(self.factory.post('/admin/list/')), BAD_METHOD)

    def test_get_competition_admin_list_not_found(self):
        """查询不存在返回 1104"""
        data=json.loads(get_competition_admin_list(self.factory.get('/admin/list/', {'id':999})).content)
        self.assertEqual(data['code'], 1104)

    def test_get_competition_admin_list_success(self):
        """正确获取赛事管理员列表"""
        c=Competition.objects.create(name='A',sport='S',is_finished=False,time_begin=timezone.now())
        UserPermission.objects.create(user=self.user1,permission='match.update_match_info',permission_info=str(c.id))
        data=json.loads(get_competition_admin_list(self.factory.get('/admin/list/', {'id':c.id})).content)
        self.assertEqual(data['code'], 0)
        self.assertGreaterEqual(len(data['data']['admin_list']),1)

    # --------- add/del competition focus ---------
    def test_add_competition_focus_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(add_competition_focus(self.factory.get('/focus/add/')), BAD_METHOD)

    def test_add_competition_focus_not_found(self):
        """关注不存在赛事返回 1105"""
        data=json.loads(add_competition_focus(self.factory.post('/focus/add/', data=json.dumps({'competition_id':999,'user_id':self.user1.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],1105)

    def test_add_competition_focus_already(self):
        """重复关注返回 1106"""
        c=Competition.objects.create(name='F',sport='S',is_finished=False,time_begin=timezone.now())
        Focus.objects.create(user=self.user1,competition=c)
        data=json.loads(add_competition_focus(self.factory.post('/focus/add/', data=json.dumps({'competition_id':c.id,'user_id':self.user1.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],1106)

    def test_add_competition_focus_success(self):
        """关注成功"""
        c=Competition.objects.create(name='F2',sport='S2',is_finished=False,time_begin=timezone.now())
        data=json.loads(add_competition_focus(self.factory.post('/focus/add/', data=json.dumps({'competition_id':c.id,'user_id':self.user1.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],0)

    def test_del_competition_focus_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(del_competition_focus(self.factory.get('/focus/del/')), BAD_METHOD)

    def test_del_competition_focus_not_found(self):
        """取消关注不存在赛事返回 1107"""
        data = json.loads(del_competition_focus(self.factory.post(
            '/focus/del/',
            data=json.dumps({'competition_id': 9999, 'user_id': self.user1.id}),
            content_type='application/json'
        )).content)
        self.assertEqual(data['code'], 1107)

    def test_del_competition_focus_not_following(self):
        """取消未关注赛事返回 1108"""
        c=Competition.objects.create(name='F4',sport='S4',is_finished=False,time_begin=timezone.now())
        data=json.loads(del_competition_focus(self.factory.post('/focus/del/', data=json.dumps({'competition_id':c.id,'user_id':self.user1.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],1108)

    def test_del_competition_focus_success(self):
        """取消关注成功"""
        c=Competition.objects.create(name='F5',sport='S5',is_finished=False,time_begin=timezone.now())
        Focus.objects.create(user=self.user1,competition=c)
        data=json.loads(del_competition_focus(self.factory.post('/focus/del/', data=json.dumps({'competition_id':c.id,'user_id':self.user1.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],0)

    # --------- get_tag_list_by_competition ---------
    def test_get_tag_list_by_competition_wrong_method(self):
        """非 GET 请求返回 BAD_METHOD"""
        self.assertEqual(get_tag_list_by_competition(self.factory.post('/tag/list/')), BAD_METHOD)

    def test_get_tag_list_by_competition_not_found(self):
        """查询不存在赛事返回 1109"""
        data=json.loads(get_tag_list_by_competition(self.factory.get('/tag/list/', {'competition_id':999})).content)
        self.assertEqual(data['code'],1109)

    def test_get_tag_list_by_competition_success(self):
        """正确获取赛事标签并按优先级排序"""
        c=Competition.objects.create(name='T',sport='S',is_finished=False,time_begin=timezone.now())
        t_s = Tag.objects.create(name='S',tag_type=TagType.SPORTS,is_competition_tag=True,is_post_tag=False)
        t_d = Tag.objects.create(name='D',tag_type=TagType.DEPARTMENT,is_competition_tag=True,is_post_tag=False)
        t_e = Tag.objects.create(name='E',tag_type=TagType.EVENT,is_competition_tag=True,is_post_tag=False)
        c.tags.set([t_e,t_s,t_d])
        data=json.loads(get_tag_list_by_competition(self.factory.get('/tag/list/', {'competition_id':c.id})).content)
        ids=[tg['id'] for tg in data['data']['tag_list']]
        # 确认 SPORTS(0) < DEPARTMENT(1) < EVENT(2)
        self.assertEqual(ids, sorted(ids))

    # --------- like/unlike participant ---------
    def test_like_participant_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(like_participant(self.factory.get('/like/')), BAD_METHOD)

    def test_like_participant_not_found(self):
        """点赞不存在参赛者返回 1115"""
        data=json.loads(like_participant(self.factory.post('/like/', data=json.dumps({'user_id':self.user1.id,'participant_id':999}), content_type='application/json')).content)
        self.assertEqual(data['code'],1115)

    def test_like_participant_user_not_found(self):
        """点赞不存在用户返回 1116"""
        p=Participant.objects.create(name='L',score=1)
        data=json.loads(like_participant(self.factory.post('/like/', data=json.dumps({'user_id':999,'participant_id':p.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],1116)

    def test_like_participant_already(self):
        """重复点赞返回 1117"""
        p=Participant.objects.create(name='L2',score=2)
        Like.objects.create(user=self.user1,participant=p)
        data=json.loads(like_participant(self.factory.post('/like/', data=json.dumps({'user_id':self.user1.id,'participant_id':p.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],1117)

    def test_like_participant_success(self):
        """点赞成功"""
        p=Participant.objects.create(name='L3',score=3)
        data=json.loads(like_participant(self.factory.post('/like/', data=json.dumps({'user_id':self.user1.id,'participant_id':p.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],0)

    def test_unlike_participant_wrong_method(self):
        """非 POST 请求返回 BAD_METHOD"""
        self.assertEqual(unlike_participant(self.factory.get('/unlike/')), BAD_METHOD)

    def test_unlike_participant_not_found(self):
        """取消点赞不存在参赛者返回 1121"""
        data=json.loads(unlike_participant(self.factory.post('/unlike/', data=json.dumps({'user_id':self.user1.id,'participant_id':999}), content_type='application/json')).content)
        self.assertEqual(data['code'],1121)

    def test_unlike_participant_user_not_found(self):
        """取消点赞不存在用户返回 1122"""
        p=Participant.objects.create(name='L4',score=4)
        data=json.loads(unlike_participant(self.factory.post('/unlike/', data=json.dumps({'user_id':999,'participant_id':p.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],1122)

    def test_unlike_participant_not_liked(self):
        """取消未点赞返回 1123"""
        p=Participant.objects.create(name='L5',score=5)
        data=json.loads(unlike_participant(self.factory.post('/unlike/', data=json.dumps({'user_id':self.user1.id,'participant_id':p.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],1123)

    def test_unlike_participant_success(self):
        """取消点赞成功"""
        p=Participant.objects.create(name='L6',score=6)
        like=Like.objects.create(user=self.user1,participant=p)
        data=json.loads(unlike_participant(self.factory.post('/unlike/', data=json.dumps({'user_id':self.user1.id,'participant_id':p.id}), content_type='application/json')).content)
        self.assertEqual(data['code'],0)
        self.assertFalse(Like.objects.filter(id=like.id).exists())

    # --------- get_like_count ---------
    def test_get_like_count_wrong_method(self):
        """非 GET 请求返回 BAD_METHOD"""
        self.assertEqual(get_like_count(self.factory.post('/like/count/')), BAD_METHOD)

    def test_get_like_count_not_found(self):
        """获取点赞数不存在参赛者返回 1125"""
        data=json.loads(get_like_count(self.factory.get('/like/count/', {'user_id':self.user1.id,'participant_id':999})).content)
        self.assertEqual(data['code'],1125)

    def test_get_like_count_success(self):
        """正确获取点赞状态和数量"""
        p=Participant.objects.create(name='LC',score=7)
        Like.objects.create(user=self.user1,participant=p)
        data=json.loads(get_like_count(self.factory.get('/like/count/', {'user_id':self.user1.id,'participant_id':p.id})).content)
        self.assertEqual(data['code'],0)
        self.assertTrue(data['data']['is_like'])
        self.assertEqual(data['data']['like_count'],1)
