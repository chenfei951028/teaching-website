# _*_ coding: utf-8 _*_
from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

from .models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin

# Create your views here.


class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by("-add_time")
        hot_courses = Course.objects.all().order_by("-click_nums")[:3]
        # 课程搜素
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) |
                                             Q(detail__icontains=search_keywords))
        # 课程排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_courses = all_courses.order_by('-students')
            elif sort == 'hot':
                all_courses = all_courses.order_by('-click_nums')
        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, 3, request=request)
        courses = p.page(page)
        return render(request, 'course-list.html',{
            'all_courses': courses,
            'sort': sort,
            'hot_courses': hot_courses,


        })


class VideoPlayView(View):
    """视频播放页面"""
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        course.students += 1
        course.save()
        # 查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse.objects.filter(user=request.user, course=course)
            user_course.save()
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        # 获取学过该用户学过其他的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)

        return render(request, 'course-play.html', {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
            'video': video,
        })


class CourseDetailView(View):
    def get(self, request, course_id):
        # 此处的id为表默认为我们添加的值。
        course = Course.objects.get(id = int(course_id))
        # 增加课程点击数
        course.click_nums += 1
        course.save()

        # 是否收藏课程
        has_fav_course = False
        has_fav_org = False

        # 必须是用户已登录我们才需要判断。
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True
        # 取出标签找到标签相同的course
        tag = course.tag
        if tag:
            # 从1开始否则会推荐自己
            relate_courses = Course.objects.filter(tag=tag)[1:2]
        else:
            relate_courses = []
        return render(request, "course-detail.html", {
            "course":course,
            "relate_courses": relate_courses,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org,
        })


class CourseInfoView(LoginRequiredMixin,View):
    """
    课程章节信息
    """
    def get(self,request,course_id):
        course = Course.objects.get(id=int(course_id)) # 通过课程id获得课程对象
        course.students += 1
        course.save()
        # 查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user,course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user,course=course)
            user_course.save()
        user_courses = UserCourse.objects.filter(course=course)  # 通过课程对象筛选所有选这个课程的用户关联数据对象
        user_ids = [user_course.user.id for user_course in user_courses]  # 取出所有选择了此课程的用户id
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)  # 获得选择了此课程的用户们，还选了些什么课程
        #  取出所有课程id
        course_ids = [user_course.course.id for user_course in all_user_courses]  # 将这些课程的id取出来
        # 获取学过该用户学过其他的所有课程
        relate_courses = Course.objects.filter(id__in = course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request,"course-video.html",{
            "course":course,
            "all_resources":all_resources,
            "relate_courses":relate_courses,
        })


class CourseCommentsView(LoginRequiredMixin, View):
    """课程评论"""

    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all().order_by('-add_time')
        return render(request, 'course-comment.html', {
            'course': course,
            'all_resources': all_resources,
            'all_comments':  all_comments,
        })


class AddCommentsView(View):
    """
    用户添加课程评论
    """
    def post(self,request):
        if not request.user.is_authenticated():
            # 判断用户登录状态
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        course_id = request.POST.get("course_id",0)
        comments = request.POST.get("comments","")
        if course_id > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id = int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')



