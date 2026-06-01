from django.shortcuts import redirect


# Пути, доступные СММ-пользователям
CMS_ALLOWED = ('/cms/', '/accounts/login/', '/accounts/logout/', '/logout/')

# Пути внутренней системы (бухгалтерия/управление), закрытые для СММ
BLOCKED_FOR_CMS = (
    '/s/', '/students/', '/incomes/', '/expenses/',
    '/reports/', '/employees/', '/salary-report/',
    '/salary-payments/', '/admin/',
)


def _is_cms_only(user):
    return getattr(getattr(user, 'profile', None), 'is_cms_user', False)


class CmsUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and _is_cms_only(user):
            path = request.path
            # Если пытается открыть страницу системы учёта — перенаправляем в CMS
            if any(path.startswith(p) for p in BLOCKED_FOR_CMS):
                return redirect('/cms/')
        return self.get_response(request)
