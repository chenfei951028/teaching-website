# _*_ coding: utf-8 _*_
__author__ = 'chenfei'
__date__ = '2018/11/3 20:07'
import xadmin
from .models import Course, Lesson, Video, CourseResource, BannerCourse


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'add_time']
    search_fields = ['name', 'desc', 'detail', 'detail', 'degree', 'students', 'fav_nums']
    list_filter = ['name', 'desc', 'detail', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'add_time']
    readonly_fields = ['fav_nums', 'click_nums', 'students']
    list_editable = ['degree', 'desc']
    inlines = [LessonInline]

    def queryset(self):
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)
        return qs


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'add_time']
    search_fields = ['name', 'desc', 'detail', 'detail', 'degree', 'students', 'fav_nums']
    list_filter = ['name', 'desc', 'detail', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'add_time']
    readonly_fields = ['fav_nums', 'click_nums', 'students']
    inlines = [LessonInline]

    def queryset(self):
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)
        return qs


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course', 'name', 'download', 'add_time']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
